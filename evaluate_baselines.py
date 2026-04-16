"""
CLI per la valutazione dei baseline per il captioning Grana Trentino.

Esempi:
  python evaluate_baselines.py --attributo Struttura_della_Pasta
  python evaluate_baselines.py --attributo all
  python evaluate_baselines.py --attributo all --skip-gpu
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent
sys.path.insert(0, str(PROJECT_ROOT))

import pandas as pd
import torch

from src.models.vocabulary import ItalianTokenizer, ATTRIBUTI
from src.models.baselines import (
    random_baseline,
    most_frequent_baseline,
    frequency_weighted_baseline,
    retrieval_baseline,
    compute_baseline_metrics,
)

DATASET_CSV = PROJECT_ROOT / "data" / "processed" / "dataset_captioning.csv"
SPLITS_JSON = PROJECT_ROOT / "data" / "processed" / "splits.json"
MODELS_DIR = PROJECT_ROOT / "models"

BASELINES = {
    "baseline_random": "random",
    "baseline_most_frequent": "most_frequent",
    "baseline_freq_weighted": "freq_weighted",
    "baseline_retrieval": "retrieval",
}


def parse_args():
    p = argparse.ArgumentParser(description="Valuta baseline per image captioning Grana Trentino")
    p.add_argument(
        "--attributo", required=True,
        help="Nome attributo (es. Struttura_della_Pasta) o 'all' per tutti e 7",
    )
    p.add_argument(
        "--skip-gpu", action="store_true",
        help="Salta il retrieval baseline (richiede GPU/CPU per ResNet-50)",
    )
    p.add_argument("--seed", type=int, default=42)
    return p.parse_args()


def load_split_df(df: pd.DataFrame, splits: dict, split_name: str) -> pd.DataFrame:
    """Filtra df per split, stessa logica di GranaTrentinoDataset."""
    ids = set(splits[split_name])
    mask = df["has_caption"] & df["has_images"] & df["has_both_views"]
    return df[mask & df["sample_id"].isin(ids)].copy()


def run_baselines_for_attribute(
    attributo: str | None,
    train_df: pd.DataFrame,
    test_df: pd.DataFrame,
    tokenizer: ItalianTokenizer,
    device: torch.device,
    skip_gpu: bool,
    seed: int,
) -> None:
    attr_dir = attributo if attributo is not None else "global"
    print(f"\n{'='*60}")
    print(f"Attributo: {attr_dir}")
    print(f"  Train rows: {len(train_df[train_df['attributo'] == attributo]) if attributo else len(train_df)}")
    print(f"  Test rows:  {len(test_df[test_df['attributo'] == attributo]) if attributo else len(test_df)}")

    baseline_fns = [
        ("baseline_random", lambda: random_baseline(train_df, test_df, attributo, tokenizer, seed)),
        ("baseline_most_frequent", lambda: most_frequent_baseline(train_df, test_df, attributo, tokenizer)),
        ("baseline_freq_weighted", lambda: frequency_weighted_baseline(train_df, test_df, attributo, tokenizer, seed)),
    ]
    if not skip_gpu:
        baseline_fns.append((
            "baseline_retrieval",
            lambda: retrieval_baseline(train_df, test_df, attributo, tokenizer, device),
        ))

    for dir_name, fn in baseline_fns:
        print(f"\n  [{dir_name}]")
        try:
            preds, refs = fn()
            if not preds:
                print("  WARN: nessuna predizione generata, skip.")
                continue

            out_dir = MODELS_DIR / dir_name / attr_dir
            out_dir.mkdir(parents=True, exist_ok=True)

            metrics = compute_baseline_metrics(
                preds, refs,
                predictions_path=out_dir / "predictions.csv",
            )
            with open(out_dir / "metrics.json", "w", encoding="utf-8") as f:
                json.dump(metrics, f, indent=2, ensure_ascii=False)

            print(f"  BLEU-1: {metrics['bleu1']:.4f} | BLEU-4: {metrics['bleu4']:.4f} "
                  f"| METEOR: {metrics['meteor']:.4f} | ROUGE-L: {metrics['rouge_l']:.4f}")
            print(f"  Salvato in: {out_dir}")
        except Exception as e:
            print(f"  ERRORE: {e}")


def main():
    args = parse_args()
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    print(f"Device: {device}")

    print("Caricamento tokenizer...")
    tokenizer = ItalianTokenizer()

    print("Caricamento dataset...")
    df = pd.read_csv(DATASET_CSV)
    with open(SPLITS_JSON, encoding="utf-8") as f:
        splits = json.load(f)

    train_df = load_split_df(df, splits, "train")
    test_df = load_split_df(df, splits, "test")

    if args.attributo == "all":
        attributi = ATTRIBUTI
    else:
        if args.attributo not in ATTRIBUTI:
            print(f"ERRORE: attributo '{args.attributo}' non riconosciuto. Scegli tra: {ATTRIBUTI}")
            sys.exit(1)
        attributi = [args.attributo]

    for attributo in attributi:
        run_baselines_for_attribute(
            attributo=attributo,
            train_df=train_df,
            test_df=test_df,
            tokenizer=tokenizer,
            device=device,
            skip_gpu=args.skip_gpu,
            seed=args.seed,
        )

    print("\nDone. Esegui `python reports/compare_models.py` per aggiornare il report.")


if __name__ == "__main__":
    main()
