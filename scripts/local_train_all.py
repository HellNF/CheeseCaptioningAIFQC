"""
Local training script: train all 9 new models on RTX 4060 Laptop (8GB VRAM).

Specifiche GPU verificate:
  - NVIDIA GeForce RTX 4060 Laptop GPU (sm_89, Ada Lovelace)
  - 8 GB VRAM
  - PyTorch 2.6.0 + CUDA 12.4, cuDNN 9.1
  - AMP (fp16) supportato

VRAM misurata (forward+backward):
  M1-FT  bs=16: ~1.5 GB    | M5a-FT bs=16: ~2 GB
  M2-FT  bs=16: ~2 GB      | M5b-FT bs=16: 4.5 GB
  M3-FT  bs=8:  ~3 GB      | M5c-FT bs=8:  5.0 GB (bs=16 sfora a 8.8 GB!)

Usage:
  python scripts/local_train_all.py
  python scripts/local_train_all.py --only m1-ft m5a
  python scripts/local_train_all.py --only m5c-ft --beam-size 5
"""
from __future__ import annotations
import argparse
import json
import os
import subprocess
import sys
import time
from datetime import datetime
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
MODELS_DIR = REPO_ROOT / "models"
REPORT_PATH = REPO_ROOT / "reports" / "local_training_report.md"

ATTRIBUTO = "Struttura_della_Pasta"

# Risultati precedenti per confronto
PRIOR_RESULTS = {
    "M1":       {"bleu1": 0.2138, "bleu4": 0.0472, "meteor": 0.2309, "rouge_l": 0.2130},
    "M2":       {"bleu1": 0.2104, "bleu4": 0.0405, "meteor": 0.2286, "rouge_l": 0.2084},
    "M3":       {"bleu1": 0.2022, "bleu4": 0.0445, "meteor": 0.2289, "rouge_l": 0.2048},
    "M4 BLIP":  {"bleu1": 0.2298, "bleu4": 0.0483, "meteor": 0.2712, "rouge_l": 0.2301},
    "Baseline (retrieval)":      {"bleu1": 0.1312, "bleu4": 0.0213, "meteor": 0.1548, "rouge_l": 0.1322},
    "Baseline (freq-weighted)":  {"bleu1": 0.0937, "bleu4": 0.0068, "meteor": 0.1129, "rouge_l": 0.0924},
}

FACTORIAL_GRID = {
    "frozen_scratch":  ["M1", "M2", "M3"],
    "frozen_geppetto": ["M5a", "M5b", "M5c"],
    "ft_scratch":      ["M1-FT", "M2-FT", "M3-FT"],
    "ft_geppetto":     ["M5a-FT", "M5b-FT", "M5c-FT"],
}

# (label, model_flag, finetune, dir_name, description)
MODELS = [
    ("M1-FT",  "m1",  True,  "m1_cnn_lstm_ft",          "CNN (fine-tuned) + LSTM"),
    ("M2-FT",  "m2",  True,  "m2_cnn_transformer_ft",   "CNN (fine-tuned) + Transformer"),
    ("M3-FT",  "m3",  True,  "m3_vit_transformer_ft",   "ViT (fine-tuned) + Transformer"),
    ("M5a",    "m5a", False, "m5a_cnn_gpt",             "CNN (frozen) + GePpeTto"),
    ("M5b",    "m5b", False, "m5b_cnnspatial_gpt",      "CNNSpatial (frozen) + GePpeTto"),
    ("M5c",    "m5c", False, "m5c_vit_gpt",             "ViT (frozen) + GePpeTto"),
    ("M5a-FT", "m5a", True,  "m5a_cnn_gpt_ft",          "CNN (fine-tuned) + GePpeTto"),
    ("M5b-FT", "m5b", True,  "m5b_cnnspatial_gpt_ft",   "CNNSpatial (fine-tuned) + GePpeTto"),
    ("M5c-FT", "m5c", True,  "m5c_vit_gpt_ft",          "ViT (fine-tuned) + GePpeTto"),
]


def parse_args():
    p = argparse.ArgumentParser(description="Train all 9 models on local RTX 4060")
    p.add_argument("--only", nargs="+", default=None,
                   help="Train only these (e.g. m1-ft m5a m5c-ft)")
    p.add_argument("--attributo", default=ATTRIBUTO)
    p.add_argument("--beam-size", type=int, default=3)
    return p.parse_args()


def fmt_time(seconds: float) -> str:
    m, s = divmod(int(seconds), 60)
    h, m = divmod(m, 60)
    return f"{h}h {m}m {s}s" if h else f"{m}m {s}s"


def check_gpu():
    """Verifica GPU e stampa info."""
    import torch
    if not torch.cuda.is_available():
        print("ERRORE: nessuna GPU CUDA disponibile!")
        sys.exit(1)

    name = torch.cuda.get_device_name(0)
    cap = torch.cuda.get_device_capability(0)
    vram = torch.cuda.get_device_properties(0).total_memory / 1024**3
    print(f"  GPU: {name}")
    print(f"  Compute: sm_{cap[0]}{cap[1]}")
    print(f"  VRAM: {vram:.1f} GB")
    print(f"  PyTorch: {torch.__version__}")

    # Quick CUDA test
    t = torch.tensor([1.0], device="cuda")
    _ = t + t
    print(f"  CUDA test: OK")
    return True


def load_metrics(model_dir: Path, attr: str) -> dict | None:
    """Carica metriche da metrics.json o log.csv + predictions.csv."""
    metrics_path = model_dir / attr / "metrics.json"
    if metrics_path.exists():
        with open(metrics_path) as f:
            return json.load(f)

    import csv
    result = {}

    log_path = model_dir / attr / "log.csv"
    if log_path.exists():
        with open(log_path) as f:
            rows = list(csv.DictReader(f))
        if rows:
            best = min(rows, key=lambda r: float(r["val_loss"]))
            result["best_epoch"] = int(best["epoch"])
            result["best_val_loss"] = float(best["val_loss"])
            result["total_epochs"] = len(rows)

    pred_path = model_dir / attr / "predictions.csv"
    if pred_path.exists():
        try:
            import pandas as pd
            import evaluate as hf_evaluate

            df = pd.read_csv(pred_path)
            preds = df["caption_pred"].tolist()
            refs = [[r] for r in df["caption_ref"].tolist()]

            bleu = hf_evaluate.load("bleu").compute(predictions=preds, references=refs)
            meteor = hf_evaluate.load("meteor").compute(predictions=preds, references=refs)
            rouge = hf_evaluate.load("rouge").compute(predictions=preds, references=refs)

            precisions = bleu.get("precisions", [0, 0, 0, 0])
            result["bleu1"] = round(precisions[0], 4) if precisions else 0.0
            result["bleu4"] = round(bleu.get("bleu", 0.0), 4)
            result["meteor"] = round(meteor.get("meteor", 0.0), 4)
            result["rouge_l"] = round(rouge.get("rougeL", 0.0), 4)
        except Exception as e:
            print(f"  WARN metriche test: {e}")

    return result if result else None


def run_training(model_flag: str, finetune: bool, attributo: str,
                 beam_size: int) -> tuple[bool, float]:
    """Lancia train.py come subprocess."""
    cmd = [
        sys.executable, str(REPO_ROOT / "train.py"),
        "--model", model_flag,
        "--attributo", attributo,
        "--beam-size", str(beam_size),
    ]
    if finetune:
        cmd.append("--finetune")

    env = os.environ.copy()
    env["PYTHONUNBUFFERED"] = "1"

    print(f"\n  Comando: {' '.join(cmd)}")
    t0 = time.time()

    try:
        proc = subprocess.run(
            cmd, cwd=str(REPO_ROOT), env=env,
            capture_output=False, text=True, timeout=14400,  # 4h max per model
        )
        elapsed = time.time() - t0
        return proc.returncode == 0, elapsed
    except subprocess.TimeoutExpired:
        elapsed = time.time() - t0
        print(f"  TIMEOUT dopo {fmt_time(elapsed)}")
        return False, elapsed
    except Exception as e:
        elapsed = time.time() - t0
        print(f"  ERRORE: {e}")
        return False, elapsed


def _all_metrics(results: list[dict]) -> dict[str, dict]:
    combined = {}
    for label, data in PRIOR_RESULTS.items():
        combined[label] = {k: data[k] for k in ("bleu1", "bleu4", "meteor", "rouge_l")}
    for r in results:
        if r["success"] and r.get("metrics") and "bleu4" in r["metrics"]:
            combined[r["label"]] = {
                k: r["metrics"][k] for k in ("bleu1", "bleu4", "meteor", "rouge_l")
            }
    return combined


def print_model_report(label: str, desc: str, metrics: dict | None,
                       elapsed: float, success: bool):
    status = "OK" if success else "ERRORE"
    print(f"\n--- {label}: {desc} ---")
    print(f"  Stato: {status} | Tempo: {fmt_time(elapsed)}")

    if metrics:
        if "best_epoch" in metrics:
            print(f"  Best epoch: {metrics['best_epoch']}/{metrics.get('total_epochs', '?')}"
                  f"  (val_loss: {metrics.get('best_val_loss', '?'):.4f})")
        if "bleu4" in metrics:
            print(f"  Test:  BLEU-1={metrics['bleu1']:.4f}  BLEU-4={metrics['bleu4']:.4f}"
                  f"  METEOR={metrics['meteor']:.4f}  ROUGE-L={metrics['rouge_l']:.4f}")

            # Confronto rapido con baseline
            retr = PRIOR_RESULTS["Baseline (retrieval)"]
            delta_b4 = metrics["bleu4"] - retr["bleu4"]
            delta_met = metrics["meteor"] - retr["meteor"]
            print(f"  vs Baseline: BLEU-4 {delta_b4:+.4f}  METEOR {delta_met:+.4f}"
                  f"  {'> baseline' if delta_b4 > 0 else '< baseline'}")


def print_summary_table(results: list[dict]):
    print(f"\n{'='*75}")
    print(f"{'Modello':<12} {'BLEU-1':>8} {'BLEU-4':>8} {'METEOR':>8} {'ROUGE-L':>8} {'Tempo':>10} {'OK':>4}")
    print(f"{'-'*75}")
    for r in results:
        m = r.get("metrics") or {}
        b1 = f"{m['bleu1']:.4f}" if "bleu1" in m else "  --  "
        b4 = f"{m['bleu4']:.4f}" if "bleu4" in m else "  --  "
        met = f"{m['meteor']:.4f}" if "meteor" in m else "  --  "
        rl = f"{m['rouge_l']:.4f}" if "rouge_l" in m else "  --  "
        ok = "Y" if r["success"] else "N"
        print(f"{r['label']:<12} {b1:>8} {b4:>8} {met:>8} {rl:>8} {fmt_time(r['elapsed']):>10} {ok:>4}")
    print(f"{'-'*75}")
    total = sum(r["elapsed"] for r in results)
    done = sum(1 for r in results if r["success"])
    print(f"Totale: {done}/{len(results)} completati in {fmt_time(total)}")


def save_report_md(results: list[dict], attributo: str):
    combined = _all_metrics(results)
    lines = [
        f"# Training Report - {attributo}",
        f"Data: {datetime.now().strftime('%Y-%m-%d %H:%M')}",
        f"GPU: NVIDIA RTX 4060 Laptop (8 GB VRAM)",
        "",
        "## Nuovi modelli",
        "",
        "| Modello | Descrizione | BLEU-1 | BLEU-4 | METEOR | ROUGE-L | Best Epoch | Tempo |",
        "|---|---|---|---|---|---|---|---|",
    ]
    for r in results:
        m = r.get("metrics") or {}
        b1 = f"{m['bleu1']:.4f}" if "bleu1" in m else "--"
        b4 = f"{m['bleu4']:.4f}" if "bleu4" in m else "--"
        met = f"{m['meteor']:.4f}" if "meteor" in m else "--"
        rl = f"{m['rouge_l']:.4f}" if "rouge_l" in m else "--"
        ep = str(m.get("best_epoch", "--"))
        err = " **ERRORE**" if not r["success"] else ""
        lines.append(
            f"| {r['label']}{err} | {r['desc']} | {b1} | {b4} | {met} | {rl} | {ep} | {fmt_time(r['elapsed'])} |"
        )

    lines.extend(["", f"**Totale:** {fmt_time(sum(r['elapsed'] for r in results))}", ""])

    # Tabella completa
    lines.extend([
        "## Confronto completo",
        "",
        "| Modello | BLEU-1 | BLEU-4 | METEOR | ROUGE-L |",
        "|---|---|---|---|---|",
    ])
    display_order = [
        "M1", "M2", "M3",
        "M1-FT", "M2-FT", "M3-FT",
        "M5a", "M5b", "M5c",
        "M5a-FT", "M5b-FT", "M5c-FT",
        "M4 BLIP",
        "Baseline (retrieval)", "Baseline (freq-weighted)",
    ]
    for lbl in display_order:
        if lbl in combined:
            cm = combined[lbl]
            lines.append(
                f"| {lbl} | {cm['bleu1']:.4f} | {cm['bleu4']:.4f} "
                f"| {cm['meteor']:.4f} | {cm['rouge_l']:.4f} |"
            )

    # Griglia 2x2
    lines.extend([
        "",
        "## Design fattoriale 2x2 (media BLEU-4)",
        "",
        "|  | Decoder from scratch | Decoder GePpeTto |",
        "|---|---|---|",
    ])
    for row_label, row_key in [("Encoder frozen", "frozen"), ("Encoder fine-tuned", "ft")]:
        s_models = FACTORIAL_GRID[f"{row_key}_scratch"]
        g_models = FACTORIAL_GRID[f"{row_key}_geppetto"]
        s_vals = [combined[m]["bleu4"] for m in s_models if m in combined]
        g_vals = [combined[m]["bleu4"] for m in g_models if m in combined]
        s_str = f"{sum(s_vals)/len(s_vals):.4f} (n={len(s_vals)})" if s_vals else "--"
        g_str = f"{sum(g_vals)/len(g_vals):.4f} (n={len(g_vals)})" if g_vals else "--"
        lines.append(f"| **{row_label}** | {s_str} | {g_str} |")

    lines.append("")

    REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
    REPORT_PATH.write_text("\n".join(lines), encoding="utf-8")
    print(f"\nReport salvato: {REPORT_PATH}")


def main():
    args = parse_args()

    print("=" * 70)
    print("  LOCAL TRAINING - Grana Trentino Image Captioning")
    print(f"  Attributo: {args.attributo}")
    print("=" * 70)

    # GPU check
    print("\nGPU check...")
    check_gpu()

    # VRAM check
    import torch
    vram_gb = torch.cuda.get_device_properties(0).total_memory / 1024**3
    if vram_gb < 6:
        print(f"\n  ATTENZIONE: solo {vram_gb:.1f} GB VRAM. M5c potrebbe avere problemi.")
        print(f"  Considera --only m1-ft m2-ft m3-ft m5a m5b m5a-ft m5b-ft")

    # Filter models
    models_to_train = MODELS
    if args.only:
        selected = {s.lower() for s in args.only}
        models_to_train = [m for m in MODELS if m[0].lower() in selected]
        if not models_to_train:
            print(f"Nessun modello trovato per: {args.only}")
            print(f"Disponibili: {[m[0].lower() for m in MODELS]}")
            sys.exit(1)

    print(f"\n  Modelli da trainare: {len(models_to_train)}")
    for label, _, ft, _, desc in models_to_train:
        print(f"    - {label}: {desc}")

    results = []

    for i, (label, model_flag, finetune, dir_name, desc) in enumerate(models_to_train, 1):
        print(f"\n{'#' * 70}")
        print(f"  [{i}/{len(models_to_train)}] {label} - {desc}")
        print(f"{'#' * 70}")

        # Clear VRAM before each model
        import torch
        torch.cuda.empty_cache()

        success, elapsed = run_training(
            model_flag, finetune, args.attributo, args.beam_size,
        )

        model_dir = MODELS_DIR / dir_name
        metrics = load_metrics(model_dir, args.attributo) if success else None

        print_model_report(label, desc, metrics, elapsed, success)

        results.append(dict(
            label=label, desc=desc, success=success,
            elapsed=elapsed, metrics=metrics,
        ))

        # Tabella progressiva dopo 2+ modelli
        if len(results) > 1:
            print_summary_table(results)

        save_report_md(results, args.attributo)

    # Report finale
    print(f"\n\n{'#' * 70}")
    print("  TRAINING COMPLETATO")
    print(f"{'#' * 70}")
    print_summary_table(results)
    save_report_md(results, args.attributo)


if __name__ == "__main__":
    main()
