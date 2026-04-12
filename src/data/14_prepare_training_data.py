"""14_prepare_training_data.py — Build the captioning dataset index.

Usage
-----
python src/data/14_prepare_training_data.py \\
    --captions-dir data/processed/caption_per_attributo \\
    --campioni-csv data/processed/campioni_completi.csv \\
    --codifica-csv "07_captioning risultati grana Trentino/GT commenti liberi/codifiche/codifica caseifici.xlsx" \\
    --out data/processed/dataset_captioning.csv
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

import pandas as pd

# Allow running as a script from the repo root (adds project root to sys.path)
_ROOT = Path(__file__).resolve().parents[2]
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

from src.models.dataset import build_caption_index  # noqa: E402


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Join captions with image paths from campioni_completi."
    )
    parser.add_argument(
        "--captions-dir",
        type=Path,
        default=Path("data/processed/caption_per_attributo"),
        help="Directory with *_captions.csv files",
    )
    parser.add_argument(
        "--campioni-csv",
        type=Path,
        default=Path("data/processed/campioni_completi.csv"),
        help="Path to campioni_completi.csv",
    )
    parser.add_argument(
        "--codifica-csv",
        type=Path,
        default=Path(
            "07_captioning risultati grana Trentino/"
            "GT commenti liberi/codifiche/codifica caseifici.xlsx"
        ),
        help="Path to codifica caseifici (.xlsx or .csv)",
    )
    parser.add_argument(
        "--out",
        type=Path,
        default=Path("data/processed/dataset_captioning.csv"),
        help="Output CSV path",
    )
    parser.add_argument(
        "--reports-dir",
        type=Path,
        default=Path("reports"),
        help="Directory for the markdown statistics report",
    )
    return parser.parse_args()


def _write_report(df: pd.DataFrame, reports_dir: Path, out_path: Path) -> None:
    """Write a markdown statistics report to reports_dir."""
    reports_dir.mkdir(parents=True, exist_ok=True)
    report_path = reports_dir / "14_prepare_training_data.md"

    n_rows = len(df)
    n_samples = df["sample_id"].nunique()
    n_anni = df["anno"].nunique()

    per_attributo = (
        df.groupby("attributo")
        .size()
        .reset_index(name="n_captions")
        .sort_values("n_captions", ascending=False)
    )

    lines = [
        "# Report: 14_prepare_training_data",
        "",
        f"Output file: `{out_path}`",
        "",
        "## Statistiche generali",
        "",
        f"| Metrica | Valore |",
        f"|---------|--------|",
        f"| Righe totali | {n_rows:,} |",
        f"| Campioni unici (sample_id) | {n_samples:,} |",
        f"| Anni presenti | {n_anni} |",
        "",
        "## Distribuzione per attributo",
        "",
        "| Attributo | N caption |",
        "|-----------|-----------|",
    ]
    for _, row in per_attributo.iterrows():
        lines.append(f"| {row['attributo']} | {row['n_captions']:,} |")

    lines.append("")

    report_path.write_text("\n".join(lines), encoding="utf-8")
    print(f"Report scritto in: {report_path}")


def main() -> None:
    args = _parse_args()

    print(f"Captions dir : {args.captions_dir}")
    print(f"Campioni CSV : {args.campioni_csv}")
    print(f"Codifica CSV : {args.codifica_csv}")
    print(f"Output       : {args.out}")

    result = build_caption_index(
        captions_dir=args.captions_dir,
        campioni_csv=args.campioni_csv,
        codifica_csv=args.codifica_csv,
    )

    print(f"\nDataset costruito: {len(result):,} righe, {result['sample_id'].nunique():,} campioni unici")
    print("\nDistribuzione per attributo:")
    print(result.groupby("attributo").size().to_string())

    args.out.parent.mkdir(parents=True, exist_ok=True)
    result.to_csv(args.out, index=False)
    print(f"\nSalvato in: {args.out}")

    _write_report(result, args.reports_dir, args.out)


if __name__ == "__main__":
    main()
