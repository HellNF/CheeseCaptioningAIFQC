"""Dataset builder for Grana Trentino captioning project.

Joins normalised per-attribute captions with image paths from campioni_completi.
"""
from __future__ import annotations

from pathlib import Path

import pandas as pd
from PIL import Image
import torch
from torch.utils.data import Dataset
from torchvision import transforms


def _load_codifica(codifica_path: Path) -> pd.DataFrame:
    """Load the caseificio mapping file (xlsx or csv, no header).

    Returns a DataFrame with columns: prodotto (C0A…), codice_caseificio (TN302…).
    The source file encodes TN codes with underscore (TN_302); we normalise to
    the format used in campioni_completi (TN302).
    """
    path = Path(codifica_path)
    if path.suffix.lower() == ".xlsx":
        df = pd.read_excel(path, header=None, engine="openpyxl")
    else:
        df = pd.read_csv(path, header=None)

    # Drop rows where either of the first two columns is NaN
    df = df.dropna(subset=[0, 1])

    # col 0 → codice TN (TN_302 → TN302), col 1 → prodotto (C0A)
    df = df[[0, 1]].copy()
    df.columns = ["codice_caseificio", "prodotto"]
    df["codice_caseificio"] = df["codice_caseificio"].str.replace("_", "", regex=False)
    return df


def build_caption_index(
    captions_dir: Path,
    campioni_csv: Path,
    codifica_csv: Path,
) -> pd.DataFrame:
    """Build a flat DataFrame joining captions with image paths.

    Parameters
    ----------
    captions_dir:
        Directory containing ``*_captions.csv`` files (one per attribute).
    campioni_csv:
        Path to ``campioni_completi.csv``.
    codifica_csv:
        Path to the caseificio mapping file (.xlsx or .csv, no header).

    Returns
    -------
    pd.DataFrame with columns:
        fetta_path, grana_path, attributo, caption, sample_id, anno
    Rows without a matching image path are dropped.
    """
    captions_dir = Path(captions_dir)
    campioni_csv = Path(campioni_csv)
    codifica_csv = Path(codifica_csv)

    if not campioni_csv.exists():
        raise FileNotFoundError(f"campioni_csv not found: {campioni_csv}")
    if not codifica_csv.exists():
        raise FileNotFoundError(f"codifica_csv not found: {codifica_csv}")
    if not captions_dir.is_dir():
        raise NotADirectoryError(f"captions_dir not found: {captions_dir}")

    # ------------------------------------------------------------------
    # 1. Load all *_captions.csv files and tag with attributo name
    # ------------------------------------------------------------------
    caption_frames: list[pd.DataFrame] = []
    for csv_file in sorted(captions_dir.glob("*_captions.csv")):
        attributo = csv_file.stem.replace("_captions", "")
        cap_df = pd.read_csv(csv_file)
        required_cols = {"caption", "prodotto", "anno"}
        missing = required_cols - set(cap_df.columns)
        if missing:
            raise ValueError(f"Colonne mancanti in {csv_file.name}: {missing}")
        cap_df["attributo"] = attributo
        caption_frames.append(cap_df)

    if not caption_frames:
        return pd.DataFrame(
            columns=["fetta_path", "grana_path", "attributo", "caption", "sample_id", "anno"]
        )

    captions = pd.concat(caption_frames, ignore_index=True)

    # ------------------------------------------------------------------
    # 2. Filter: keep only rows with non-null, non-empty caption
    # ------------------------------------------------------------------
    captions = captions[captions["caption"].notna()]
    captions = captions[captions["caption"].str.strip() != ""]

    # ------------------------------------------------------------------
    # 3. Map prodotto → codice_caseificio via codifica file
    # ------------------------------------------------------------------
    codifica = _load_codifica(codifica_csv)
    # prodotto column in captions is the anonymous code (C0A)
    captions = captions.merge(
        codifica[["prodotto", "codice_caseificio"]],
        on="prodotto",
        how="left",
    )

    # ------------------------------------------------------------------
    # 4. Load campioni_completi; keep one row per (codice_caseificio, anno)
    #    by taking the earliest data_seduta
    # ------------------------------------------------------------------
    campioni = pd.read_csv(campioni_csv, parse_dates=["data_seduta"])
    campioni_sorted = campioni.sort_values("data_seduta")
    campioni_dedup = campioni_sorted.drop_duplicates(
        subset=["codice_caseificio", "anno"], keep="first"
    )

    # ------------------------------------------------------------------
    # 5. Join captions with campioni on (codice_caseificio, anno)
    # ------------------------------------------------------------------
    merged = captions.merge(
        campioni_dedup[["sample_id", "codice_caseificio", "anno",
                         "path_fetta_primaria", "path_grana_primaria"]],
        on=["codice_caseificio", "anno"],
        how="left",
    )

    # ------------------------------------------------------------------
    # 6. Drop rows without image paths; rename and select output columns
    # ------------------------------------------------------------------
    merged = merged[merged["path_fetta_primaria"].notna()]
    merged = merged[merged["path_grana_primaria"].notna()]

    result = merged.rename(
        columns={
            "path_fetta_primaria": "fetta_path",
            "path_grana_primaria": "grana_path",
        }
    )[["fetta_path", "grana_path", "attributo", "caption", "sample_id", "anno"]].reset_index(
        drop=True
    )

    return result


# ---------------------------------------------------------------------------
# Default transform (ImageNet normalisation, 224×224)
# ---------------------------------------------------------------------------
DEFAULT_TRANSFORM = transforms.Compose(
    [
        transforms.Resize((224, 224)),
        transforms.ToTensor(),
        transforms.Normalize(
            mean=[0.485, 0.456, 0.406],
            std=[0.229, 0.224, 0.225],
        ),
    ]
)


class GranaTrentinoDataset(Dataset):
    """PyTorch Dataset for the Grana Trentino image-captioning task.

    Parameters
    ----------
    dataframe:
        pd.DataFrame with columns ``fetta_path``, ``grana_path``, ``caption``.
    transform:
        torchvision transform applied to both images.  Defaults to
        ``DEFAULT_TRANSFORM`` (Resize 224×224 + ToTensor + ImageNet normalise).
    tokenizer:
        Optional tokenizer stored as an attribute; not used internally.
        Intended for use in a custom ``collate_fn``.
    """

    def __init__(
        self,
        dataframe: pd.DataFrame,
        transform=None,
        tokenizer=None,
    ) -> None:
        self.df = dataframe.reset_index(drop=True)
        self.transform = transform if transform is not None else DEFAULT_TRANSFORM
        self.tokenizer = tokenizer

    # ------------------------------------------------------------------
    def __len__(self) -> int:
        return len(self.df)

    # ------------------------------------------------------------------
    def __getitem__(self, idx: int):
        row = self.df.iloc[idx]

        fetta_img = Image.open(row["fetta_path"]).convert("RGB")
        grana_img = Image.open(row["grana_path"]).convert("RGB")

        fetta_tensor: torch.Tensor = self.transform(fetta_img)
        grana_tensor: torch.Tensor = self.transform(grana_img)

        caption_str: str = str(row["caption"])

        return fetta_tensor, grana_tensor, caption_str
