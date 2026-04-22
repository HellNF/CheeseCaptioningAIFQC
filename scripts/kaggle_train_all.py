"""
Kaggle notebook script: train all 9 new models on Struttura_della_Pasta.

Usage — paste in a Kaggle notebook cell after cloning the repo:
  !python scripts/kaggle_train_all.py

Oppure lancia singoli modelli:
  !python scripts/kaggle_train_all.py --only m1-ft m5a

Il dataset Kaggle deve contenere le immagini BMP originali e il CSV processato.
Adatta KAGGLE_DATA_ROOT se necessario.
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

# ── Paths ────────────────────────────────────────────────────────────────
# Adatta questi path alla struttura del tuo dataset Kaggle
KAGGLE_DATA_ROOT = Path("/kaggle/input/grana-trentino-captioning")
REPO_ROOT = Path("/kaggle/working/CheeseCaptioningAIFQC")

# Se il repo è già la working directory (es. notebook inline)
if Path("train.py").exists():
    REPO_ROOT = Path(".")
elif Path("/kaggle/working/train.py").exists():
    REPO_ROOT = Path("/kaggle/working")

MODELS_DIR = REPO_ROOT / "models"
REPORT_PATH = REPO_ROOT / "reports" / "kaggle_training_report.md"

# ── Risultati precedenti (M1/M2/M3 from-scratch + M4 BLIP + baseline) ──
# Metriche test set su Struttura_della_Pasta (già addestrati)
PRIOR_RESULTS = {
    "M1":       {"bleu1": 0.2138, "bleu4": 0.0472, "meteor": 0.2309, "rouge_l": 0.2130, "desc": "CNN (frozen) + LSTM"},
    "M2":       {"bleu1": 0.2104, "bleu4": 0.0405, "meteor": 0.2286, "rouge_l": 0.2084, "desc": "CNN (frozen) + Transformer"},
    "M3":       {"bleu1": 0.2022, "bleu4": 0.0445, "meteor": 0.2289, "rouge_l": 0.2048, "desc": "ViT (frozen) + Transformer"},
    "M4 BLIP":  {"bleu1": 0.2298, "bleu4": 0.0483, "meteor": 0.2712, "rouge_l": 0.2301, "desc": "BLIP fully pre-trained"},
    "Baseline (retrieval)": {"bleu1": 0.1312, "bleu4": 0.0213, "meteor": 0.1548, "rouge_l": 0.1322, "desc": "ResNet-50 cosine similarity"},
    "Baseline (freq-weighted)": {"bleu1": 0.0937, "bleu4": 0.0068, "meteor": 0.1129, "rouge_l": 0.0924, "desc": "Weighted random sampling"},
}

# Mapping per analisi fattoriale 2×2
FACTORIAL_GRID = {
    "frozen_scratch":  ["M1", "M2", "M3"],
    "frozen_geppetto": ["M5a", "M5b", "M5c"],
    "ft_scratch":      ["M1-FT", "M2-FT", "M3-FT"],
    "ft_geppetto":     ["M5a-FT", "M5b-FT", "M5c-FT"],
}

# ── Configurazione modelli ───────────────────────────────────────────────
ATTRIBUTO = "Struttura_della_Pasta"

MODELS = [
    # (label, model_flag, finetune, dir_name, description)
    ("M1-FT", "m1", True, "m1_cnn_lstm_ft",
     "CNN encoder (fine-tuned) + LSTM decoder"),
    ("M2-FT", "m2", True, "m2_cnn_transformer_ft",
     "CNN encoder (fine-tuned) + Transformer decoder"),
    ("M3-FT", "m3", True, "m3_vit_transformer_ft",
     "ViT encoder (fine-tuned) + Transformer decoder"),
    ("M5a", "m5a", False, "m5a_cnn_gpt",
     "CNN encoder (frozen) + GePpeTto decoder"),
    ("M5b", "m5b", False, "m5b_cnnspatial_gpt",
     "CNNSpatial encoder (frozen) + GePpeTto decoder"),
    ("M5c", "m5c", False, "m5c_vit_gpt",
     "ViT encoder (frozen) + GePpeTto decoder"),
    ("M5a-FT", "m5a", True, "m5a_cnn_gpt_ft",
     "CNN encoder (fine-tuned) + GePpeTto decoder"),
    ("M5b-FT", "m5b", True, "m5b_cnnspatial_gpt_ft",
     "CNNSpatial encoder (fine-tuned) + GePpeTto decoder"),
    ("M5c-FT", "m5c", True, "m5c_vit_gpt_ft",
     "ViT encoder (fine-tuned) + GePpeTto decoder"),
]


def parse_args():
    p = argparse.ArgumentParser()
    p.add_argument(
        "--only", nargs="+", default=None,
        help="Train only these models (e.g. m1-ft m5a m5c-ft). "
             "Use lowercase with dash: m1-ft, m2-ft, m3-ft, m5a, m5b, m5c, "
             "m5a-ft, m5b-ft, m5c-ft",
    )
    p.add_argument("--attributo", default=ATTRIBUTO)
    p.add_argument("--beam-size", type=int, default=3)
    p.add_argument("--skip-eval", action="store_true",
                   help="Skip test-set evaluation (faster for debugging)")
    return p.parse_args()


def fmt_time(seconds: float) -> str:
    m, s = divmod(int(seconds), 60)
    h, m = divmod(m, 60)
    if h:
        return f"{h}h {m}m {s}s"
    return f"{m}m {s}s"


def load_metrics(model_dir: Path, attr: str) -> dict | None:
    metrics_path = model_dir / attr / "metrics.json"
    if metrics_path.exists():
        with open(metrics_path) as f:
            return json.load(f)

    import csv
    log_path = model_dir / attr / "log.csv"
    pred_path = model_dir / attr / "predictions.csv"
    result = {}

    if log_path.exists():
        with open(log_path) as f:
            rows = list(csv.DictReader(f))
        if rows:
            best = min(rows, key=lambda r: float(r["val_loss"]))
            result["best_epoch"] = int(best["epoch"])
            result["best_val_loss"] = float(best["val_loss"])
            result["best_bleu4_val"] = float(best.get("bleu4", 0))
            result["total_epochs"] = len(rows)

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


def print_report_header():
    print("\n" + "=" * 70)
    print("  REPORT TRAINING — Grana Trentino Image Captioning")
    print(f"  Attributo: {ATTRIBUTO}")
    print(f"  Data: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    print("=" * 70)


def print_model_report(label: str, desc: str, metrics: dict | None,
                       elapsed: float, success: bool):
    print(f"\n{'─' * 60}")
    print(f"  {label}: {desc}")
    print(f"  Stato: {'✓ Completato' if success else '✗ ERRORE'}")
    print(f"  Tempo: {fmt_time(elapsed)}")

    if metrics:
        if "best_epoch" in metrics:
            print(f"  Best epoch: {metrics['best_epoch']}/{metrics.get('total_epochs', '?')}"
                  f"  (val_loss: {metrics.get('best_val_loss', '?'):.4f})")
        if "bleu4" in metrics:
            print(f"  Test set:")
            print(f"    BLEU-1:  {metrics['bleu1']:.4f}")
            print(f"    BLEU-4:  {metrics['bleu4']:.4f}")
            print(f"    METEOR:  {metrics['meteor']:.4f}")
            print(f"    ROUGE-L: {metrics['rouge_l']:.4f}")
    print(f"{'─' * 60}")


def print_summary_table(results: list[dict]):
    print("\n" + "=" * 70)
    print("  RIEPILOGO COMPLETO")
    print("=" * 70)
    print(f"\n{'Modello':<12} {'BLEU-1':>8} {'BLEU-4':>8} {'METEOR':>8} {'ROUGE-L':>8} {'Tempo':>10} {'Stato':>8}")
    print("─" * 70)
    for r in results:
        m = r.get("metrics") or {}
        status = "✓" if r["success"] else "✗"
        b1 = f"{m['bleu1']:.4f}" if "bleu1" in m else "—"
        b4 = f"{m['bleu4']:.4f}" if "bleu4" in m else "—"
        met = f"{m['meteor']:.4f}" if "meteor" in m else "—"
        rl = f"{m['rouge_l']:.4f}" if "rouge_l" in m else "—"
        print(f"{r['label']:<12} {b1:>8} {b4:>8} {met:>8} {rl:>8} {fmt_time(r['elapsed']):>10} {status:>8}")
    print("─" * 70)

    total_time = sum(r["elapsed"] for r in results)
    completed = sum(1 for r in results if r["success"])
    print(f"\nTotale: {completed}/{len(results)} completati in {fmt_time(total_time)}")


def _all_metrics(results: list[dict]) -> dict[str, dict]:
    """Unisce risultati nuovi + precedenti in un unico dict label→metrics."""
    combined = {}
    for label, data in PRIOR_RESULTS.items():
        combined[label] = {k: data[k] for k in ("bleu1", "bleu4", "meteor", "rouge_l")}
    for r in results:
        if r["success"] and r.get("metrics") and "bleu4" in r["metrics"]:
            combined[r["label"]] = {
                k: r["metrics"][k] for k in ("bleu1", "bleu4", "meteor", "rouge_l")
            }
    return combined


def print_analysis(results: list[dict], latest: dict):
    """Stampa analisi dettagliata dopo ogni modello completato."""
    label = latest["label"]
    m = latest.get("metrics")
    if not m or "bleu4" not in m:
        return

    print(f"\n{'╔' + '═' * 68 + '╗'}")
    print(f"{'║'} {'ANALISI — ' + label:^68} {'║'}")
    print(f"{'╚' + '═' * 68 + '╝'}")

    # 1. Confronto con baseline
    retr = PRIOR_RESULTS["Baseline (retrieval)"]
    print(f"\n  vs Baseline (retrieval):")
    for metric in ("bleu1", "bleu4", "meteor", "rouge_l"):
        val = m[metric]
        base = retr[metric]
        delta = val - base
        ratio = val / base if base > 0 else float("inf")
        arrow = "▲" if delta > 0 else "▼"
        print(f"    {metric:>8}: {val:.4f}  {arrow} {delta:+.4f}  ({ratio:.1f}x baseline)")

    beats_baseline = m["bleu4"] > retr["bleu4"]
    print(f"\n  {'✓ Batte il baseline' if beats_baseline else '✗ NON batte il baseline'}"
          f" → il modello {'usa' if beats_baseline else 'non usa'} informazione visiva")

    # 2. Confronto con controparte frozen/unfrozen
    counterpart = None
    if label.endswith("-FT"):
        base_label = label.replace("-FT", "")
        combined = _all_metrics(results)
        if base_label in combined:
            counterpart = (base_label, combined[base_label])
    elif not label.endswith("-FT"):
        ft_label = label + "-FT"
        combined = _all_metrics(results)
        if ft_label in combined:
            counterpart = (ft_label, combined[ft_label])

    if counterpart:
        c_label, c_m = counterpart
        print(f"\n  vs {c_label} (effetto fine-tuning encoder):")
        for metric in ("bleu4", "meteor", "rouge_l"):
            delta = m[metric] - c_m[metric]
            arrow = "▲" if delta > 0 else "▼"
            print(f"    {metric:>8}: {m[metric]:.4f} vs {c_m[metric]:.4f}  {arrow} {delta:+.4f}")

    # 3. Confronto con controparte decoder (scratch vs GePpeTto)
    decoder_map = {
        "M1-FT": "M5a-FT", "M5a-FT": "M1-FT",
        "M2-FT": "M5b-FT", "M5b-FT": "M2-FT",
        "M3-FT": "M5c-FT", "M5c-FT": "M3-FT",
        "M1": "M5a", "M5a": "M1",
        "M2": "M5b", "M5b": "M2",
        "M3": "M5c", "M5c": "M3",
    }
    combined = _all_metrics(results)
    dec_counterpart_label = decoder_map.get(label)
    if dec_counterpart_label and dec_counterpart_label in combined:
        dec_m = combined[dec_counterpart_label]
        geppetto_label = label if label.startswith("M5") else dec_counterpart_label
        scratch_label = dec_counterpart_label if label.startswith("M5") else label
        print(f"\n  Effetto decoder pre-trained ({scratch_label} vs {geppetto_label}):")
        for metric in ("bleu4", "meteor", "rouge_l"):
            s_val = combined.get(scratch_label, {}).get(metric)
            g_val = combined.get(geppetto_label, {}).get(metric)
            if s_val is not None and g_val is not None:
                delta = g_val - s_val
                arrow = "▲" if delta > 0 else "▼"
                print(f"    {metric:>8}: scratch={s_val:.4f}  geppetto={g_val:.4f}  {arrow} {delta:+.4f}")

    # 4. Confronto con M4 BLIP
    m4 = PRIOR_RESULTS["M4 BLIP"]
    print(f"\n  vs M4 BLIP (fully pre-trained, 129M image-text pairs):")
    for metric in ("bleu4", "meteor", "rouge_l"):
        delta = m[metric] - m4[metric]
        pct = (delta / m4[metric] * 100) if m4[metric] > 0 else 0
        arrow = "▲" if delta > 0 else "▼"
        print(f"    {metric:>8}: {m[metric]:.4f} vs {m4[metric]:.4f}  {arrow} {pct:+.1f}%")

    # 5. Stato griglia 2×2
    combined = _all_metrics(results)
    print(f"\n  Griglia fattoriale 2×2 (BLEU-4):")
    print(f"  {'':>20} {'Decoder scratch':>18} {'Decoder GePpeTto':>18}")
    for row_label, row_key in [("Encoder frozen", "frozen"), ("Encoder fine-tuned", "ft")]:
        scratch_models = FACTORIAL_GRID[f"{row_key}_scratch"]
        geppetto_models = FACTORIAL_GRID[f"{row_key}_geppetto"]
        s_vals = [combined[m_l]["bleu4"] for m_l in scratch_models if m_l in combined]
        g_vals = [combined[m_l]["bleu4"] for m_l in geppetto_models if m_l in combined]
        s_avg = f"{sum(s_vals)/len(s_vals):.4f}" if s_vals else "..."
        g_avg = f"{sum(g_vals)/len(g_vals):.4f}" if g_vals else "..."
        s_n = f"(n={len(s_vals)}/3)"
        g_n = f"(n={len(g_vals)}/3)"
        print(f"  {row_label:>20} {s_avg:>10} {s_n:<8} {g_avg:>10} {g_n:<8}")

    print()


def save_report_md(results: list[dict], attributo: str):
    lines = [
        f"# Report Training Kaggle — {attributo}",
        f"Data: {datetime.now().strftime('%Y-%m-%d %H:%M')}",
        "",
        "## Nuovi modelli",
        "",
        "| Modello | Descrizione | BLEU-1 | BLEU-4 | METEOR | ROUGE-L | Best Epoch | Tempo |",
        "|---|---|---|---|---|---|---|---|",
    ]
    for r in results:
        m = r.get("metrics") or {}
        b1 = f"{m['bleu1']:.4f}" if "bleu1" in m else "—"
        b4 = f"{m['bleu4']:.4f}" if "bleu4" in m else "—"
        met = f"{m['meteor']:.4f}" if "meteor" in m else "—"
        rl = f"{m['rouge_l']:.4f}" if "rouge_l" in m else "—"
        ep = str(m.get("best_epoch", "—"))
        status = "" if r["success"] else " **ERRORE**"
        lines.append(
            f"| {r['label']}{status} | {r['desc']} | {b1} | {b4} | {met} | {rl} | {ep} | {fmt_time(r['elapsed'])} |"
        )

    lines.append("")
    total_time = sum(r["elapsed"] for r in results)
    lines.append(f"**Totale:** {fmt_time(total_time)}")

    # Tabella completa con tutti i modelli
    combined = _all_metrics(results)
    lines.extend([
        "",
        "## Confronto completo (tutti i modelli)",
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

    # Griglia 2×2
    lines.extend([
        "",
        "## Design fattoriale 2x2 (media BLEU-4)",
        "",
        "|  | Decoder from scratch | Decoder GePpeTto |",
        "|---|---|---|",
    ])
    for row_label, row_key in [("Encoder frozen", "frozen"), ("Encoder fine-tuned", "ft")]:
        scratch_models = FACTORIAL_GRID[f"{row_key}_scratch"]
        geppetto_models = FACTORIAL_GRID[f"{row_key}_geppetto"]
        s_vals = [combined[m_l]["bleu4"] for m_l in scratch_models if m_l in combined]
        g_vals = [combined[m_l]["bleu4"] for m_l in geppetto_models if m_l in combined]
        s_str = f"{sum(s_vals)/len(s_vals):.4f} (n={len(s_vals)})" if s_vals else "—"
        g_str = f"{sum(g_vals)/len(g_vals):.4f} (n={len(g_vals)})" if g_vals else "—"
        lines.append(f"| **{row_label}** | {s_str} | {g_str} |")

    lines.append("")

    REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
    REPORT_PATH.write_text("\n".join(lines), encoding="utf-8")
    print(f"\nReport salvato: {REPORT_PATH}")


def run_training(model_flag: str, finetune: bool, attributo: str,
                 beam_size: int, skip_eval: bool) -> tuple[bool, float]:
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
            capture_output=False, text=True, timeout=7200,
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


def main():
    args = parse_args()
    attributo = args.attributo

    # Filtra modelli se --only
    models_to_train = MODELS
    if args.only:
        selected = {s.lower() for s in args.only}
        models_to_train = [
            m for m in MODELS
            if m[0].lower().replace("-", "-") in selected
        ]
        if not models_to_train:
            print(f"Nessun modello trovato per: {args.only}")
            print(f"Disponibili: {[m[0].lower() for m in MODELS]}")
            sys.exit(1)

    print_report_header()
    print(f"\n  Modelli da trainare: {len(models_to_train)}")
    for label, _, ft, _, desc in models_to_train:
        print(f"    • {label}: {desc}")

    results = []

    for i, (label, model_flag, finetune, dir_name, desc) in enumerate(models_to_train, 1):
        print(f"\n{'█' * 70}")
        print(f"  [{i}/{len(models_to_train)}] Training {label}")
        print(f"  {desc}")
        print(f"{'█' * 70}")

        success, elapsed = run_training(
            model_flag, finetune, attributo, args.beam_size, args.skip_eval,
        )

        model_dir = MODELS_DIR / dir_name
        metrics = load_metrics(model_dir, attributo) if success else None

        print_model_report(label, desc, metrics, elapsed, success)

        result_entry = dict(
            label=label, desc=desc, success=success,
            elapsed=elapsed, metrics=metrics,
        )
        results.append(result_entry)

        # Analisi dettagliata dopo ogni modello
        if success and metrics:
            print_analysis(results, result_entry)

        # Tabella progressiva dopo 2+ modelli
        if len(results) > 1:
            print_summary_table(results)

        save_report_md(results, attributo)

    # Report finale
    print("\n\n")
    print("█" * 70)
    print("  TRAINING COMPLETATO")
    print("█" * 70)
    print_summary_table(results)
    save_report_md(results, attributo)


if __name__ == "__main__":
    main()
