# tests/models/test_dataset.py
import json
import pytest
import pandas as pd
from unittest.mock import patch
import torch

from src.models.vocabulary import ItalianTokenizer
from src.models.dataset import build_splits, GranaTrentinoDataset

ATTRIBUTI = [
    "Texture", "Sapore", "Aroma", "Profumo",
    "Struttura_della_Pasta", "Colore_della_Pasta", "Spessore_della_Crosta",
]

@pytest.fixture(scope="module")
def tok():
    return ItalianTokenizer()

@pytest.fixture
def mock_csv(tmp_path):
    """CSV minimale con 10 campioni fisici, 2 attributi, entrambe le viste."""
    rows = []
    for i in range(10):
        sample_id = f"TN30{i}_2019-09-0{i+1}"
        for attr in ["Texture", "Sapore"]:
            rows.append({
                "attributo": attr,
                "sample_id": sample_id,
                "caption": f"Caption di test {i}",
                "classe": "OK",
                "has_caption": True,
                "has_images": True,
                "has_fetta": True,
                "has_grana": True,
                "has_both_views": True,
                "path_fetta_primaria": f"fake/fetta_{i}.bmp",
                "path_grana_primaria": f"fake/grana_{i}.bmp",
                "anno": 2019.0,
                "peso": 1.0,
            })
    df = pd.DataFrame(rows)
    p = tmp_path / "dataset_captioning.csv"
    df.to_csv(p, index=False)
    return p

@pytest.fixture
def splits_json(tmp_path, mock_csv):
    return build_splits(mock_csv, seed=42, out_path=tmp_path / "splits.json")

def test_splits_disjoint(splits_json):
    train = set(splits_json["train"])
    val = set(splits_json["val"])
    test = set(splits_json["test"])
    assert train & val == set()
    assert train & test == set()
    assert val & test == set()

def test_splits_cover_all_samples(splits_json, mock_csv):
    df = pd.read_csv(mock_csv)
    all_ids = set(df["sample_id"].unique())
    covered = set(splits_json["train"]) | set(splits_json["val"]) | set(splits_json["test"])
    assert covered == all_ids

def test_splits_approximate_ratio(splits_json):
    n_train = len(splits_json["train"])
    n_total = n_train + len(splits_json["val"]) + len(splits_json["test"])
    ratio = n_train / n_total
    assert 0.60 <= ratio <= 0.80  # ~70%

def test_dataset_item_keys(tmp_path, mock_csv, splits_json, tok):
    splits_path = tmp_path / "splits.json"
    with open(splits_path, "w") as f:
        json.dump(splits_json, f)

    fake_img = torch.zeros(3, 224, 224)
    with patch.object(GranaTrentinoDataset, "_load_image", return_value=fake_img):
        ds = GranaTrentinoDataset(
            csv_path=mock_csv,
            tokenizer=tok,
            splits_path=splits_path,
            attributo="Texture",
            split="train",
        )
        assert len(ds) > 0
        item = ds[0]
        assert set(item.keys()) == {"fetta", "grana", "caption", "weight"}
        assert item["fetta"].shape == (3, 224, 224)
        assert item["grana"].shape == (3, 224, 224)
        assert isinstance(item["caption"], torch.Tensor)
        assert item["caption"][0].item() == tok.SOS_ID
        assert item["weight"] == 1.0

def test_dataset_filters_attributo(tmp_path, mock_csv, splits_json, tok):
    splits_path = tmp_path / "splits.json"
    with open(splits_path, "w") as f:
        json.dump(splits_json, f)

    fake_img = torch.zeros(3, 224, 224)
    with patch.object(GranaTrentinoDataset, "_load_image", return_value=fake_img):
        ds = GranaTrentinoDataset(
            csv_path=mock_csv, tokenizer=tok, splits_path=splits_path,
            attributo="Texture", split="train",
        )
        df = pd.read_csv(mock_csv)
        train_ids = set(splits_json["train"])
        expected = df[(df["attributo"] == "Texture") & df["sample_id"].isin(train_ids)]
        assert len(ds) == len(expected)

def test_dataset_global_mode_prepends_attr_token(tmp_path, mock_csv, splits_json, tok):
    splits_path = tmp_path / "splits.json"
    with open(splits_path, "w") as f:
        json.dump(splits_json, f)

    fake_img = torch.zeros(3, 224, 224)
    with patch.object(GranaTrentinoDataset, "_load_image", return_value=fake_img):
        ds = GranaTrentinoDataset(
            csv_path=mock_csv, tokenizer=tok, splits_path=splits_path,
            attributo=None, split="train",
        )
        item = ds[0]
        # Dopo <SOS> ci deve essere un token attributo
        attr_ids = set(tok.ATTR_TOKENS.values())
        assert item["caption"][1].item() in attr_ids
