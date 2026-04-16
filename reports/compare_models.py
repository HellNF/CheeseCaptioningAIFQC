# reports/compare_models.py
"""
Genera reports/training_results.md leggendo log.csv e predictions.csv da models/.

Uso:
  python reports/compare_models.py
"""
from __future__ import annotations
import csv
from pathlib import Path

import pandas as pd

PROJECT_ROOT = Path(__file__).parents[1]
MODELS_DIR = PROJECT_ROOT / "models"
OUT_PATH = PROJECT_ROOT / "reports" / "training_results.md"

MODEL_DIRS = {
    "M1 (CNN+LSTM)": "m1_cnn_lstm",
    "M2 (CNN+Transformer)": "m2_cnn_transformer",
    "M3 (ViT+Transformer)": "m3_vit_transformer",
    "M4 (BLIP fine-tuned)": "m4_blip",
    "M1-FT (CNN+LSTM)": "m1_cnn_lstm_ft",
    "M2-FT (CNN+Transformer)": "m2_cnn_transformer_ft",
    "M3-FT (ViT+Transformer)": "m3_vit_transformer_ft",
    "Baseline (random)": "baseline_random",
    "Baseline (most-frequent)": "baseline_most_frequent",
    "Baseline (freq-weighted)": "baseline_freq_weighted",
    "Baseline (retrieval)": "baseline_retrieval",
}
ATTRIBUTI = [
    "Aroma", "Profumo", "Sapore", "Texture",
    "Struttura_della_Pasta", "Colore_della_Pasta", "Spessore_della_Crosta",
    "global",
]
METRICS = ["bleu1", "bleu4", "meteor", "rouge_l"]


def _load_results(model_dir: Path, attr: str) -> dict | None:
    """Legge metriche da metrics.json (priorità) o le ricalcola da predictions.csv."""
    import json

    # Priorità 1: metrics.json pre-calcolato (prodotto dal notebook Kaggle per M4)
    metrics_path = model_dir / attr / "metrics.json"
    if metrics_path.exists():
        try:
            with open(metrics_path, encoding="utf-8") as f:
                data = json.load(f)
            # Il file può avere le metriche dirette oppure annidate in per_attributo
            if all(k in data for k in ("bleu1", "bleu4", "meteor", "rouge_l")):
                return {k: round(float(data[k]), 4) for k in ("bleu1", "bleu4", "meteor", "rouge_l")}
        except Exception as e:
            print(f"  WARN: {metrics_path}: {e}")

    # Priorità 2: ricalcola da predictions.csv
    pred_path = model_dir / attr / "predictions.csv"
    if not pred_path.exists():
        return None
    try:
        import evaluate as hf_evaluate
        df = pd.read_csv(pred_path)
        preds = df["caption_pred"].tolist()
        refs = [[r] for r in df["caption_ref"].tolist()]

        bleu = hf_evaluate.load("bleu", module_type="metric").compute(predictions=preds, references=refs)
        meteor = hf_evaluate.load("meteor", module_type="metric").compute(predictions=preds, references=refs)
        rouge = hf_evaluate.load("rouge", module_type="metric").compute(predictions=preds, references=refs)

        precisions = bleu.get("precisions", [0, 0, 0, 0])
        return {
            "bleu1": round(precisions[0], 4) if precisions else 0.0,
            "bleu4": round(bleu.get("bleu", 0.0), 4),
            "meteor": round(meteor.get("meteor", 0.0), 4),
            "rouge_l": round(rouge.get("rougeL", 0.0), 4),
        }
    except Exception as e:
        print(f"  WARN: {pred_path}: {e}")
        return None


def _best_epoch(model_dir: Path, attr: str) -> int | None:
    import json

    # Per M4: legge best_epoch da metrics.json
    metrics_path = model_dir / attr / "metrics.json"
    if metrics_path.exists():
        try:
            with open(metrics_path, encoding="utf-8") as f:
                data = json.load(f)
            if "best_epoch" in data:
                return int(data["best_epoch"])
        except Exception:
            pass

    log_path = model_dir / attr / "log.csv"
    if not log_path.exists():
        return None
    with open(log_path) as f:
        rows = list(csv.DictReader(f))
    if not rows:
        return None
    best = min(rows, key=lambda r: float(r["val_loss"]))
    return int(best["epoch"])


def main():
    lines = ["# Risultati Training — Grana Trentino Image Captioning", ""]
    lines.append("Dataset: `data/processed/dataset_captioning.csv` | Split: 70/15/15 per campione fisico")
    lines.append("")

    for model_label, model_dirname in MODEL_DIRS.items():
        model_dir = MODELS_DIR / model_dirname
        lines.append(f"## {model_label}")
        lines.append("")
        lines.append("| Attributo | Best Epoch | BLEU-1 | BLEU-4 | METEOR | ROUGE-L |")
        lines.append("|---|---|---|---|---|---|")

        for attr in ATTRIBUTI:
            metrics = _load_results(model_dir, attr)
            best_ep = _best_epoch(model_dir, attr)
            ep_str = str(best_ep) if best_ep else "—"
            if metrics:
                lines.append(
                    f"| {attr} | {ep_str} "
                    f"| {metrics['bleu1']:.4f} | {metrics['bleu4']:.4f} "
                    f"| {metrics['meteor']:.4f} | {metrics['rouge_l']:.4f} |"
                )
            else:
                lines.append(f"| {attr} | — | — | — | — | — |")

        lines.append("")

    # Tabella riassuntiva media per modello (escluso global)
    lines.append("## Confronto medie (per-attributo, escluso global)")
    lines.append("")
    lines.append("| Modello | BLEU-1 | BLEU-4 | METEOR | ROUGE-L |")
    lines.append("|---|---|---|---|---|")

    for model_label, model_dirname in MODEL_DIRS.items():
        model_dir = MODELS_DIR / model_dirname
        all_metrics = [
            _load_results(model_dir, a)
            for a in ATTRIBUTI if a != "global"
        ]
        valid = [m for m in all_metrics if m]
        if valid:
            avg = {k: round(sum(m[k] for m in valid) / len(valid), 4) for k in METRICS}
            lines.append(
                f"| {model_label} | {avg['bleu1']:.4f} | {avg['bleu4']:.4f} "
                f"| {avg['meteor']:.4f} | {avg['rouge_l']:.4f} |"
            )
        else:
            lines.append(f"| {model_label} | — | — | — | — |")

    lines.append("")
    md = "\n".join(lines)
    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUT_PATH.write_text(md, encoding="utf-8")
    print(f"Report salvato: {OUT_PATH}")
    print(md[:500])


if __name__ == "__main__":
    main()
