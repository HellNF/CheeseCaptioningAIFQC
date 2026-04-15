"""
Prepara il dataset per il fine-tuning BLIP su Kaggle.

Operazioni:
1. Legge dataset_captioning.csv e splits.json
2. Per ogni sample_id: carica fetta + grana (BMP), resize+pad a 384×192 ciascuna,
   concatena verticalmente → 384×384, salva come JPEG q92
3. Genera kaggle_dataset/images/ (flat) + kaggle_dataset/metadata.csv

Uso:
  python scripts/prepare_kaggle_dataset.py
  python scripts/prepare_kaggle_dataset.py --data-root /path/to/images
"""
from __future__ import annotations
import argparse
import json
import sys
from pathlib import Path

import pandas as pd
from PIL import Image

PROJECT_ROOT = Path(__file__).parents[1]
DATASET_CSV = PROJECT_ROOT / "data" / "processed" / "dataset_captioning.csv"
SPLITS_JSON = PROJECT_ROOT / "data" / "processed" / "splits.json"
OUT_DIR = PROJECT_ROOT / "kaggle_dataset"
IMAGES_DIR = OUT_DIR / "images"

TARGET_W = 384
HALF_H = 192  # altezza di ciascuna vista (fetta o grana) prima della concatenazione

ATTR_PROMPTS: dict[str, str] = {
    "Aroma": "l'aroma",
    "Profumo": "il profumo",
    "Sapore": "il sapore",
    "Texture": "la texture",
    "Struttura_della_Pasta": "la struttura della pasta",
    "Colore_della_Pasta": "il colore della pasta",
    "Spessore_della_Crosta": "lo spessore della crosta",
}


def _resize_pad(img: Image.Image, w: int, h: int) -> Image.Image:
    """Ridimensiona mantenendo l'aspect ratio e aggiunge padding bianco."""
    img = img.convert("RGB")
    img.thumbnail((w, h), Image.LANCZOS)
    canvas = Image.new("RGB", (w, h), (255, 255, 255))
    x = (w - img.width) // 2
    y = (h - img.height) // 2
    canvas.paste(img, (x, y))
    return canvas


def _make_combined(fetta_path: Path, grana_path: Path | None) -> Image.Image:
    """Concatena fetta (sopra) e grana (sotto) in un canvas TARGET_W × (2*HALF_H)."""
    fetta = _resize_pad(Image.open(fetta_path), TARGET_W, HALF_H)
    if grana_path and grana_path.exists():
        grana = _resize_pad(Image.open(grana_path), TARGET_W, HALF_H)
    else:
        grana = Image.new("RGB", (TARGET_W, HALF_H), (255, 255, 255))
    canvas = Image.new("RGB", (TARGET_W, HALF_H * 2))
    canvas.paste(fetta, (0, 0))
    canvas.paste(grana, (0, HALF_H))
    return canvas


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Prepara dataset Kaggle per BLIP fine-tuning")
    p.add_argument("--data-root", type=Path, default=PROJECT_ROOT,
                   help="Root da cui risolvere i path relativi delle immagini (default: project root)")
    p.add_argument("--out-dir", type=Path, default=OUT_DIR,
                   help="Directory di output (default: kaggle_dataset/)")
    p.add_argument("--quality", type=int, default=92,
                   help="Qualità JPEG (default: 92)")
    return p.parse_args()


def main() -> None:
    args = parse_args()
    data_root: Path = args.data_root
    out_dir: Path = args.out_dir
    images_dir = out_dir / "images"
    images_dir.mkdir(parents=True, exist_ok=True)

    # Carica CSV
    print("Caricamento dataset_captioning.csv...")
    df = pd.read_csv(DATASET_CSV)
    df = df[df["has_caption"] & df["has_both_views"]].copy()

    # Carica splits
    print("Caricamento splits.json...")
    with open(SPLITS_JSON, encoding="utf-8") as f:
        splits = json.load(f)
    id_to_split = {sid: sname for sname, ids in splits.items() for sid in ids}

    # Filtra solo i sample con split noto (quelli in splits.json)
    df = df[df["sample_id"].isin(id_to_split)].copy()
    df["split"] = df["sample_id"].map(id_to_split)

    # Genera immagini combinate (una per sample_id)
    print("Generazione immagini combinate...")
    sample_ids_done: set[str] = set()
    skipped = 0
    for _, row in df.drop_duplicates("sample_id").iterrows():
        sample_id = row["sample_id"]
        fetta_path = data_root / row["path_fetta_primaria"]
        grana_path = data_root / row["path_grana_primaria"] if pd.notna(row.get("path_grana_primaria")) else None

        if not fetta_path.exists():
            print(f"  WARN: fetta non trovata: {fetta_path}", file=sys.stderr)
            skipped += 1
            continue

        out_path = images_dir / f"{sample_id}__combined.jpg"
        if not out_path.exists():
            combined = _make_combined(fetta_path, grana_path)
            combined.save(out_path, "JPEG", quality=args.quality)
        sample_ids_done.add(sample_id)

    print(f"  Immagini salvate: {len(sample_ids_done)} | skippate: {skipped}")

    # Genera metadata.csv con una riga per (sample_id, attributo)
    print("Generazione metadata.csv...")
    records = []
    for _, row in df.iterrows():
        sample_id = row["sample_id"]
        if sample_id not in sample_ids_done:
            continue
        attributo = row["attributo"]
        if attributo not in ATTR_PROMPTS:
            continue
        prompt = f"descrivi {ATTR_PROMPTS[attributo]}:"
        records.append({
            "sample_id": sample_id,
            "split": row["split"],
            "attributo": attributo,
            "image_file": f"{sample_id}__combined.jpg",
            "caption": str(row["caption"]),
            "prompt": prompt,
            "peso": float(row.get("peso", 1.0)),
        })

    meta_df = pd.DataFrame(records)
    meta_path = out_dir / "metadata.csv"
    meta_df.to_csv(meta_path, index=False, encoding="utf-8")

    # Summary
    print("\n=== Summary ===")
    for split_name in ("train", "val", "test"):
        subset = meta_df[meta_df["split"] == split_name]
        n_samples = subset["sample_id"].nunique()
        n_rows = len(subset)
        print(f"  {split_name:6s}: {n_samples:3d} campioni fisici × {n_rows // max(n_samples,1):.1f} attr = {n_rows} righe")
    print(f"  Totale righe metadata: {len(meta_df)}")

    # Dimensione immagini
    total_bytes = sum(p.stat().st_size for p in images_dir.glob("*.jpg"))
    print(f"  Dimensione immagini: {total_bytes / 1e6:.1f} MB")
    print(f"\nOutput: {out_dir}")
    print("Pronto per l'upload su Kaggle.")


if __name__ == "__main__":
    main()
