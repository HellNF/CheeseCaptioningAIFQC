# src/models/dataset.py
from __future__ import annotations
import json
from pathlib import Path

import pandas as pd
import torch
from PIL import Image
from torch.utils.data import Dataset
from torchvision import transforms

from src.models.vocabulary import ItalianTokenizer

PROJECT_ROOT = Path(__file__).parents[2]

IMAGENET_TRANSFORM = transforms.Compose([
    transforms.Resize((224, 224)),
    transforms.ToTensor(),
    transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225]),
])


def build_splits(
    csv_path: Path,
    seed: int = 42,
    out_path: Path | None = None,
    train_ratio: float = 0.70,
    val_ratio: float = 0.15,
) -> dict[str, list[str]]:
    """Divide i sample_id in train/val/test, stratificato per anno."""
    import numpy as np

    df = pd.read_csv(csv_path)
    trainable = df[df["has_caption"] & df["has_both_views"]].copy()

    samples = (
        trainable.groupby("sample_id")["anno"]
        .agg(lambda x: x.mode()[0])
        .reset_index()
        .rename(columns={"anno": "anno_mode"})
    )
    samples["anno_bin"] = samples["anno_mode"].fillna(0).astype(int).astype(str)

    rng = np.random.default_rng(seed)
    train_ids, val_ids, test_ids = [], [], []

    for _, grp in samples.groupby("anno_bin"):
        ids = grp["sample_id"].tolist()
        rng.shuffle(ids)
        n = len(ids)
        n_train = max(1, int(n * train_ratio))
        n_val = max(1, int(n * val_ratio))
        train_ids.extend(ids[:n_train])
        val_ids.extend(ids[n_train: n_train + n_val])
        test_ids.extend(ids[n_train + n_val:])

    splits = {"train": train_ids, "val": val_ids, "test": test_ids}

    if out_path is not None:
        out_path = Path(out_path)
        out_path.parent.mkdir(parents=True, exist_ok=True)
        with open(out_path, "w", encoding="utf-8") as f:
            json.dump(splits, f, ensure_ascii=False, indent=2)

    return splits


class GranaTrentinoDataset(Dataset):
    def __init__(
        self,
        csv_path: Path,
        tokenizer: ItalianTokenizer,
        splits_path: Path,
        attributo: str | None = None,
        split: str = "train",
        require_both_views: bool = True,
        max_caption_len: int = 50,
        transform: transforms.Compose | None = None,
    ) -> None:
        self.tokenizer = tokenizer
        self.max_caption_len = max_caption_len
        self.transform = transform or IMAGENET_TRANSFORM
        self.attributo = attributo

        df = pd.read_csv(csv_path)

        mask = df["has_caption"] & df["has_images"]
        if require_both_views:
            mask &= df["has_both_views"]
        df = df[mask].copy()

        with open(splits_path, encoding="utf-8") as f:
            splits = json.load(f)
        split_ids = set(splits[split])
        df = df[df["sample_id"].isin(split_ids)].copy()

        if attributo is not None:
            df = df[df["attributo"] == attributo].copy()

        self.df = df.reset_index(drop=True)

    def __len__(self) -> int:
        return len(self.df)

    def __getitem__(self, idx: int) -> dict:
        row = self.df.iloc[idx]

        fetta = self._load_image(row["path_fetta_primaria"])
        if pd.notna(row.get("path_grana_primaria")):
            grana = self._load_image(row["path_grana_primaria"])
        else:
            grana = torch.zeros(3, 224, 224)

        caption_text = str(row["caption"])
        if self.attributo is None:
            # Modello globale: usa encode() con attribute= per preporre il token
            ids = self.tokenizer.encode(
                caption_text,
                add_special=True,
                attribute=row["attributo"],
            )
        else:
            ids = self.tokenizer.encode(caption_text, add_special=True)

        ids = ids[: self.max_caption_len]
        caption_tensor = torch.tensor(ids, dtype=torch.long)

        return {
            "fetta": fetta,
            "grana": grana,
            "caption": caption_tensor,
            "weight": float(row.get("peso", 1.0)),
        }

    def _load_image(self, rel_path: str) -> torch.Tensor:
        full_path = PROJECT_ROOT / rel_path
        img = Image.open(full_path).convert("RGB")
        return self.transform(img)
