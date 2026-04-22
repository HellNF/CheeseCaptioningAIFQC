"""
Prepara un dataset Kaggle con tutte le immagini (fetta + grana separate)
convertite da BMP a JPG, il CSV processato e splits.json.

Uso:
  python scripts/prepare_kaggle_dataset_full.py

Crea la directory kaggle_dataset_full/ pronta per upload con:
  kaggle datasets create -p kaggle_dataset_full/
"""
from __future__ import annotations
import json
import shutil
from pathlib import Path

import pandas as pd
from PIL import Image

PROJECT_ROOT = Path(__file__).parents[1]
CSV_PATH = PROJECT_ROOT / "data" / "processed" / "dataset_captioning.csv"
SPLITS_PATH = PROJECT_ROOT / "data" / "processed" / "splits.json"
OUT_DIR = PROJECT_ROOT / "kaggle_dataset_full"
IMAGES_DIR = OUT_DIR / "images"

JPG_QUALITY = 85  # bilanciamento qualita/dimensione


def main():
    print("Caricamento CSV...")
    df = pd.read_csv(CSV_PATH)

    # Raccogli tutti i path immagine unici
    fetta_paths = df["path_fetta_primaria"].dropna().unique().tolist()
    grana_paths = df["path_grana_primaria"].dropna().unique().tolist()
    all_paths = list(set(fetta_paths + grana_paths))
    print(f"Immagini uniche: {len(all_paths)}")

    # Crea directory output
    IMAGES_DIR.mkdir(parents=True, exist_ok=True)

    # Converti BMP → JPG mantenendo la struttura come filename flat
    # Mappa: path_originale → path_kaggle_relativo
    path_map = {}
    converted = 0
    skipped = 0

    for rel_path in all_paths:
        src = PROJECT_ROOT / rel_path
        if not src.exists():
            print(f"  SKIP (non trovato): {rel_path}")
            skipped += 1
            continue

        # Crea nome flat: sostituisci / con __ e cambia estensione
        flat_name = rel_path.replace("/", "__").replace("\\", "__")
        flat_name = Path(flat_name).with_suffix(".jpg").name
        dst = IMAGES_DIR / flat_name
        kaggle_rel = f"images/{flat_name}"

        if not dst.exists():
            img = Image.open(src).convert("RGB")
            img.save(dst, "JPEG", quality=JPG_QUALITY)
            converted += 1
        else:
            converted += 1  # gia convertito

        path_map[rel_path] = kaggle_rel

    print(f"Convertite: {converted}, Skipped: {skipped}")

    # Aggiorna il CSV con i nuovi path
    df_out = df.copy()
    df_out["path_fetta_primaria"] = df_out["path_fetta_primaria"].map(
        lambda p: path_map.get(p, p) if pd.notna(p) else p
    )
    df_out["path_grana_primaria"] = df_out["path_grana_primaria"].map(
        lambda p: path_map.get(p, p) if pd.notna(p) else p
    )

    # Salva CSV e splits
    data_dir = OUT_DIR / "data" / "processed"
    data_dir.mkdir(parents=True, exist_ok=True)
    df_out.to_csv(data_dir / "dataset_captioning.csv", index=False)
    print(f"CSV salvato: {data_dir / 'dataset_captioning.csv'}")

    if SPLITS_PATH.exists():
        shutil.copy2(SPLITS_PATH, data_dir / "splits.json")
        print(f"Splits copiato: {data_dir / 'splits.json'}")
    else:
        print("WARN: splits.json non trovato, verra generato al primo training")

    # Metadata per Kaggle dataset API
    metadata = {
        "title": "Grana Trentino Full Dataset",
        "id": "marcopanciera/grana-trentino-full",
        "licenses": [{"name": "CC0-1.0"}],
    }
    with open(OUT_DIR / "dataset-metadata.json", "w") as f:
        json.dump(metadata, f, indent=2)

    # Calcola dimensione
    total_size = sum(f.stat().st_size for f in OUT_DIR.rglob("*") if f.is_file())
    print(f"\nDimensione totale: {total_size / 1e6:.1f} MB")
    print(f"Directory: {OUT_DIR}")
    print(f"\nPer uploadare su Kaggle:")
    print(f"  kaggle datasets create -p {OUT_DIR}")


if __name__ == "__main__":
    main()
