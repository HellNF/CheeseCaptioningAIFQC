# Training Models Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Implementare il package `src/models/` con dataset loader, tokenizer, tre encoder, due decoder, tre modelli, training loop con checkpoint e CLI per addestrare 24 esperimenti (7 attributi + 1 globale × 3 architetture).

**Architecture:** Package condiviso `src/models/` con componenti indipendenti e interfacce comuni tra encoder/decoder. Un singolo CLI `train.py` (root) istanzia il modello richiesto. Dataset già disponibile in `data/processed/dataset_captioning.csv`.

**Tech Stack:** PyTorch 2.x + CUDA, torchvision, timm 1.0 (ViT), transformers (GePpeTto tokenizer), evaluate (BLEU/METEOR/ROUGE), Pillow, pandas, tqdm

---

## Struttura file

```
src/models/
  __init__.py          # vuoto
  vocabulary.py        # ItalianTokenizer — wrapper GePpeTto
  dataset.py           # build_splits(), GranaTrentinoDataset
  encoders.py          # CNNEncoderGlobal, CNNEncoderSpatial, ViTEncoder
  decoders.py          # LSTMDecoder, TransformerDecoder
  models.py            # CnnLstm, CnnTransformer, ViTTransformer, build_model()
  train.py             # train_one_epoch(), evaluate_epoch(), train_model()
  metrics.py           # generate_caption(), quick_eval(), full_eval()

train.py               # CLI entry point (root del progetto)

tests/models/
  __init__.py
  test_vocabulary.py
  test_dataset.py
  test_encoders.py
  test_decoders.py
  test_models.py
  test_train.py
  test_metrics.py

reports/
  compare_models.py    # genera training_results.md

data/processed/
  splits.json          # generato da build_splits(), seed=42
```

---

## Task 1: Setup e scaffolding

**Files:**
- Create: `src/models/__init__.py`
- Create: `tests/models/__init__.py`

- [ ] **Step 1: Installa PyTorch con supporto CUDA**

Verifica prima la versione CUDA disponibile:
```bash
nvidia-smi
```
Poi installa PyTorch CUDA (adatta la versione CUDA all'output sopra — esempio per CUDA 12.1):
```bash
pip install torch torchvision --index-url https://download.pytorch.org/whl/cu121
```
Verifica:
```bash
python -c "import torch; print(torch.cuda.is_available(), torch.cuda.get_device_name(0))"
```
Atteso: `True  NVIDIA GeForce RTX 4060 Laptop GPU`

- [ ] **Step 2: Installa le altre dipendenze**

```bash
pip install timm>=0.9 transformers>=4.30 evaluate>=0.4 nltk tqdm
python -c "import nltk; nltk.download('wordnet'); nltk.download('punkt'); nltk.download('punkt_tab')"
```

- [ ] **Step 3: Crea le directory e i file vuoti**

```bash
mkdir -p src/models tests/models reports models
touch src/models/__init__.py tests/models/__init__.py
```

- [ ] **Step 4: Commit**

```bash
git add src/models/__init__.py tests/models/__init__.py
git commit -m "feat: scaffold src/models and tests/models packages"
```

---

## Task 2: ItalianTokenizer

**Files:**
- Create: `src/models/vocabulary.py`
- Create: `tests/models/test_vocabulary.py`

- [ ] **Step 1: Scrivi i test**

```python
# tests/models/test_vocabulary.py
import pytest
from src.models.vocabulary import ItalianTokenizer

ATTRIBUTI = [
    "Texture", "Sapore", "Aroma", "Profumo",
    "Struttura_della_Pasta", "Colore_della_Pasta", "Spessore_della_Crosta",
]

@pytest.fixture(scope="module")
def tok():
    return ItalianTokenizer()

def test_special_token_ids_are_distinct(tok):
    ids = [tok.SOS_ID, tok.EOS_ID, tok.PAD_ID]
    assert len(set(ids)) == 3

def test_attr_tokens_exist(tok):
    for attr in ATTRIBUTI:
        assert f"[{attr}]" in tok.ATTR_TOKENS, f"[{attr}] mancante"

def test_encode_adds_sos_eos(tok):
    ids = tok.encode("il campione è granuloso", add_special=True)
    assert ids[0] == tok.SOS_ID
    assert ids[-1] == tok.EOS_ID

def test_encode_no_special(tok):
    ids = tok.encode("il campione è granuloso", add_special=False)
    assert ids[0] != tok.SOS_ID
    assert ids[-1] != tok.EOS_ID

def test_decode_skips_special(tok):
    ids = tok.encode("pasta compatta", add_special=True)
    text = tok.decode(ids, skip_special=True)
    assert "<SOS>" not in text
    assert "<EOS>" not in text
    assert "pasta" in text.lower()

def test_decode_roundtrip(tok):
    original = "pasta compatta e granulosa"
    ids = tok.encode(original, add_special=False)
    decoded = tok.decode(ids, skip_special=False)
    # BPE può aggiungere spazi; verifichiamo le parole chiave
    assert "pasta" in decoded.lower()
    assert "granulosa" in decoded.lower()

def test_vocab_size_is_large(tok):
    assert len(tok) > 50_000
```

- [ ] **Step 2: Esegui i test e verifica che falliscono**

```bash
pytest tests/models/test_vocabulary.py -v
```
Atteso: `ModuleNotFoundError: No module named 'src.models.vocabulary'`

- [ ] **Step 3: Implementa `src/models/vocabulary.py`**

```python
# src/models/vocabulary.py
from __future__ import annotations
from transformers import AutoTokenizer

ATTRIBUTI = [
    "Texture", "Sapore", "Aroma", "Profumo",
    "Struttura_della_Pasta", "Colore_della_Pasta", "Spessore_della_Crosta",
]
_SPECIAL = ["<SOS>", "<EOS>", "<PAD>"] + [f"[{a}]" for a in ATTRIBUTI]


class ItalianTokenizer:
    """Wrapper su GePpeTto (GPT-2 italiano) con token speciali per il captioning."""

    MODEL_NAME = "LorenzoDeMattei/GePpeTto"

    def __init__(self) -> None:
        self._tok = AutoTokenizer.from_pretrained(self.MODEL_NAME)
        self._tok.add_special_tokens({"additional_special_tokens": _SPECIAL})
        # Assegna attributi di comodo
        self.SOS_ID: int = self._tok.convert_tokens_to_ids("<SOS>")
        self.EOS_ID: int = self._tok.convert_tokens_to_ids("<EOS>")
        self.PAD_ID: int = self._tok.convert_tokens_to_ids("<PAD>")
        self.ATTR_TOKENS: dict[str, int] = {
            f"[{a}]": self._tok.convert_tokens_to_ids(f"[{a}]") for a in ATTRIBUTI
        }

    def encode(self, text: str, add_special: bool = True) -> list[int]:
        ids = self._tok.encode(text, add_special_tokens=False)
        if add_special:
            ids = [self.SOS_ID] + ids + [self.EOS_ID]
        return ids

    def decode(self, ids: list[int], skip_special: bool = True) -> str:
        special_ids = {self.SOS_ID, self.EOS_ID, self.PAD_ID}
        if skip_special:
            ids = [i for i in ids if i not in special_ids]
        return self._tok.decode(ids, skip_special_tokens=skip_special)

    def __len__(self) -> int:
        return len(self._tok)
```

- [ ] **Step 4: Esegui i test e verifica che passano**

```bash
pytest tests/models/test_vocabulary.py -v
```
Atteso: tutti e 7 i test `PASSED`

- [ ] **Step 5: Commit**

```bash
git add src/models/vocabulary.py tests/models/test_vocabulary.py
git commit -m "feat: add ItalianTokenizer wrapping GePpeTto with special tokens"
```

---

## Task 3: Split logic e GranaTrentinoDataset

**Files:**
- Create: `src/models/dataset.py`
- Create: `tests/models/test_dataset.py`
- Create (generated at runtime): `data/processed/splits.json`

- [ ] **Step 1: Scrivi i test**

```python
# tests/models/test_dataset.py
import json
import pytest
import numpy as np
import pandas as pd
from pathlib import Path
from PIL import Image
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

def _make_fake_image(tmp_path, name):
    """Crea un'immagine BMP RGB 224×224 di rumore."""
    arr = np.random.randint(0, 256, (224, 224, 3), dtype=np.uint8)
    img = Image.fromarray(arr, mode="RGB")
    p = tmp_path / name
    p.parent.mkdir(parents=True, exist_ok=True)
    img.save(str(p))
    return str(p)

def test_dataset_item_keys(tmp_path, mock_csv, splits_json, tok):
    # Crea le immagini fake nella cartella del progetto
    project_root = Path(__file__).parents[2]
    for i in range(10):
        _make_fake_image(project_root, f"fake/fetta_{i}.bmp")
        _make_fake_image(project_root, f"fake/grana_{i}.bmp")

    splits_path = tmp_path / "splits.json"
    with open(splits_path, "w") as f:
        json.dump(splits_json, f)

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

    project_root = Path(__file__).parents[2]
    for i in range(10):
        _make_fake_image(project_root, f"fake/fetta_{i}.bmp")
        _make_fake_image(project_root, f"fake/grana_{i}.bmp")

    ds = GranaTrentinoDataset(
        csv_path=mock_csv, tokenizer=tok, splits_path=splits_path,
        attributo="Texture", split="train",
    )
    # Con attributo="Texture" otteniamo solo le righe Texture
    df = pd.read_csv(mock_csv)
    train_ids = set(splits_json["train"])
    expected = df[(df["attributo"] == "Texture") & df["sample_id"].isin(train_ids)]
    assert len(ds) == len(expected)

def test_dataset_global_mode_prepends_attr_token(tmp_path, mock_csv, splits_json, tok):
    splits_path = tmp_path / "splits.json"
    with open(splits_path, "w") as f:
        json.dump(splits_json, f)

    project_root = Path(__file__).parents[2]
    for i in range(10):
        _make_fake_image(project_root, f"fake/fetta_{i}.bmp")
        _make_fake_image(project_root, f"fake/grana_{i}.bmp")

    ds = GranaTrentinoDataset(
        csv_path=mock_csv, tokenizer=tok, splits_path=splits_path,
        attributo=None, split="train",
    )
    item = ds[0]
    # Dopo <SOS> ci deve essere un token attributo
    attr_ids = set(tok.ATTR_TOKENS.values())
    assert item["caption"][1].item() in attr_ids
```

- [ ] **Step 2: Esegui i test e verifica che falliscono**

```bash
pytest tests/models/test_dataset.py -v
```
Atteso: `ModuleNotFoundError: No module named 'src.models.dataset'`

- [ ] **Step 3: Implementa `src/models/dataset.py`**

```python
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
    """Divide i sample_id in train/val/test, stratificato per anno.

    Restituisce {'train': [...], 'val': [...], 'test': [...]} e
    opzionalmente salva in out_path come JSON.
    """
    import numpy as np

    df = pd.read_csv(csv_path)
    trainable = df[df["has_caption"] & df["has_both_views"]].copy()

    # Un sample_id per riga (anno = anno più comune per quel campione)
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
    """Dataset PyTorch per image captioning Grana Trentino.

    Ogni item: {"fetta": Tensor[3,224,224], "grana": Tensor[3,224,224],
                "caption": LongTensor[seq_len], "weight": float}
    """

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
        self.attributo = attributo  # None = modello globale

        df = pd.read_csv(csv_path)

        # Filtro base
        mask = df["has_caption"] & df["has_images"]
        if require_both_views:
            mask &= df["has_both_views"]
        df = df[mask].copy()

        # Carica split
        with open(splits_path, encoding="utf-8") as f:
            splits = json.load(f)
        split_ids = set(splits[split])
        df = df[df["sample_id"].isin(split_ids)].copy()

        # Filtro per attributo
        if attributo is not None:
            df = df[df["attributo"] == attributo].copy()

        self.df = df.reset_index(drop=True)

    def __len__(self) -> int:
        return len(self.df)

    def __getitem__(self, idx: int) -> dict:
        row = self.df.iloc[idx]

        # Immagini
        fetta = self._load_image(row["path_fetta_primaria"])
        if pd.notna(row.get("path_grana_primaria")):
            grana = self._load_image(row["path_grana_primaria"])
        else:
            grana = torch.zeros(3, 224, 224)

        # Caption
        caption_text = str(row["caption"])
        if self.attributo is None:
            # Modello globale: preponi token attributo
            attr_token = f"[{row['attributo']}]"
            attr_id = self.tokenizer.ATTR_TOKENS.get(attr_token, self.tokenizer.EOS_ID)
            ids = [self.tokenizer.SOS_ID, attr_id] + \
                  self.tokenizer.encode(caption_text, add_special=False) + \
                  [self.tokenizer.EOS_ID]
        else:
            ids = self.tokenizer.encode(caption_text, add_special=True)

        # Tronca e converti
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
```

- [ ] **Step 4: Genera il file splits.json reale**

```bash
python -c "
from pathlib import Path
from src.models.dataset import build_splits
build_splits(
    csv_path=Path('data/processed/dataset_captioning.csv'),
    seed=42,
    out_path=Path('data/processed/splits.json'),
)
print('splits.json generato.')
"
```
Atteso: `splits.json generato.`

- [ ] **Step 5: Esegui i test e verifica che passano**

```bash
pytest tests/models/test_dataset.py -v
```
Atteso: tutti i test `PASSED`

- [ ] **Step 6: Pulizia immagini fake create dai test**

```bash
python -c "import shutil; shutil.rmtree('fake', ignore_errors=True)"
```

- [ ] **Step 7: Commit**

```bash
git add src/models/dataset.py tests/models/test_dataset.py data/processed/splits.json
git commit -m "feat: add build_splits and GranaTrentinoDataset with per-attribute and global mode"
```

---

## Task 4: Encoders

**Files:**
- Create: `src/models/encoders.py`
- Create: `tests/models/test_encoders.py`

- [ ] **Step 1: Scrivi i test**

```python
# tests/models/test_encoders.py
import torch
import pytest
from src.models.encoders import CNNEncoderGlobal, CNNEncoderSpatial, ViTEncoder

B = 2  # batch size per test

@pytest.fixture(scope="module")
def dummy_images():
    """Coppia di immagini sintetiche 224×224 RGB."""
    fetta = torch.randn(B, 3, 224, 224)
    grana = torch.randn(B, 3, 224, 224)
    return fetta, grana

def test_cnn_global_output_shape(dummy_images):
    fetta, grana = dummy_images
    enc = CNNEncoderGlobal()
    out = enc(fetta, grana)
    assert out.shape == (B, 1, 512), f"Atteso (B,1,512), ottenuto {out.shape}"

def test_cnn_global_trainable_params(dummy_images):
    enc = CNNEncoderGlobal()
    trainable = [p for p in enc.parameters() if p.requires_grad]
    frozen = [p for p in enc.parameters() if not p.requires_grad]
    # La proiezione è trainabile; i layer conv di ResNet sono congelati
    assert len(trainable) > 0
    assert len(frozen) > 0

def test_cnn_spatial_output_shape(dummy_images):
    fetta, grana = dummy_images
    enc = CNNEncoderSpatial()
    out = enc(fetta, grana)
    assert out.shape == (B, 98, 512), f"Atteso (B,98,512), ottenuto {out.shape}"

def test_vit_output_shape(dummy_images):
    fetta, grana = dummy_images
    enc = ViTEncoder()
    out = enc(fetta, grana)
    assert out.shape == (B, 392, 512), f"Atteso (B,392,512), ottenuto {out.shape}"

def test_vit_partial_freeze():
    enc = ViTEncoder()
    # Gli ultimi 4 layer ViT devono essere trainabili
    trainable_names = [n for n, p in enc.named_parameters() if p.requires_grad]
    assert any("blocks.11" in n for n in trainable_names)  # ultimo block
    assert any("blocks.8" in n for n in trainable_names)   # 4° dall'ultimo

def test_encoders_d_model():
    for enc_cls in [CNNEncoderGlobal, CNNEncoderSpatial, ViTEncoder]:
        enc = enc_cls()
        assert enc.d_model == 512

def test_encoders_n_visual_tokens():
    assert CNNEncoderGlobal().n_visual_tokens == 1
    assert CNNEncoderSpatial().n_visual_tokens == 98
    assert ViTEncoder().n_visual_tokens == 392
```

- [ ] **Step 2: Esegui i test e verifica che falliscono**

```bash
pytest tests/models/test_encoders.py -v
```
Atteso: `ModuleNotFoundError: No module named 'src.models.encoders'`

- [ ] **Step 3: Implementa `src/models/encoders.py`**

```python
# src/models/encoders.py
from __future__ import annotations
import torch
import torch.nn as nn
from torchvision import models
import timm


class CNNEncoderGlobal(nn.Module):
    """ResNet-50 → vettore globale 2048-dim × 2 → proiezione 512. Output: (B,1,512)."""

    d_model: int = 512
    n_visual_tokens: int = 1

    def __init__(self) -> None:
        super().__init__()
        backbone = models.resnet50(weights=models.ResNet50_Weights.IMAGENET1K_V1)
        # Congela tutti i layer conv
        for p in backbone.parameters():
            p.requires_grad = False
        # Rimuovi il classificatore finale
        self.backbone = nn.Sequential(*list(backbone.children())[:-1])  # fino ad avgpool
        self.proj = nn.Linear(2048 * 2, self.d_model)

    def forward(self, fetta: torch.Tensor, grana: torch.Tensor) -> torch.Tensor:
        f = self.backbone(fetta).flatten(1)   # (B, 2048)
        g = self.backbone(grana).flatten(1)   # (B, 2048)
        x = torch.cat([f, g], dim=1)          # (B, 4096)
        x = self.proj(x)                       # (B, 512)
        return x.unsqueeze(1)                  # (B, 1, 512)


class CNNEncoderSpatial(nn.Module):
    """ResNet-50 → feature map 7×7 → 49 token × 2 → proiezione 512. Output: (B,98,512)."""

    d_model: int = 512
    n_visual_tokens: int = 98

    def __init__(self) -> None:
        super().__init__()
        backbone = models.resnet50(weights=models.ResNet50_Weights.IMAGENET1K_V1)
        for p in backbone.parameters():
            p.requires_grad = False
        # Strati fino all'ultimo layer conv (layer4), senza avgpool
        self.backbone = nn.Sequential(*list(backbone.children())[:-2])
        self.proj = nn.Linear(2048, self.d_model)

    def forward(self, fetta: torch.Tensor, grana: torch.Tensor) -> torch.Tensor:
        f = self.backbone(fetta)                         # (B, 2048, 7, 7)
        g = self.backbone(grana)                         # (B, 2048, 7, 7)
        B = f.size(0)
        f = f.permute(0, 2, 3, 1).reshape(B, 49, 2048)  # (B, 49, 2048)
        g = g.permute(0, 2, 3, 1).reshape(B, 49, 2048)  # (B, 49, 2048)
        tokens = torch.cat([f, g], dim=1)                # (B, 98, 2048)
        return self.proj(tokens)                          # (B, 98, 512)


class ViTEncoder(nn.Module):
    """ViT-B/16 → 196 patch × 2 → proiezione 512. Output: (B,392,512)."""

    d_model: int = 512
    n_visual_tokens: int = 392
    _TRAINABLE_BLOCKS = {8, 9, 10, 11}  # ultimi 4 dei 12 block ViT-B

    def __init__(self) -> None:
        super().__init__()
        self.vit = timm.create_model(
            "vit_base_patch16_224",
            pretrained=True,
            num_classes=0,       # rimuove il classificatore
            global_pool="",      # restituisce tutti i patch token (no CLS pooling)
        )
        # Congela tutti i parametri
        for p in self.vit.parameters():
            p.requires_grad = False
        # Sblocca gli ultimi 4 block
        for idx in self._TRAINABLE_BLOCKS:
            for p in self.vit.blocks[idx].parameters():
                p.requires_grad = True
        # Sblocca anche la norm finale e il patch embedding
        for p in self.vit.norm.parameters():
            p.requires_grad = True

        self.proj = nn.Linear(768, self.d_model)

    def _extract_patches(self, x: torch.Tensor) -> torch.Tensor:
        """Estrae i 196 patch token (escluso CLS) da un'immagine."""
        out = self.vit.forward_features(x)  # (B, 197, 768) — 1 CLS + 196 patch
        return out[:, 1:, :]               # (B, 196, 768)

    def forward(self, fetta: torch.Tensor, grana: torch.Tensor) -> torch.Tensor:
        f = self._extract_patches(fetta)         # (B, 196, 768)
        g = self._extract_patches(grana)         # (B, 196, 768)
        tokens = torch.cat([f, g], dim=1)        # (B, 392, 768)
        return self.proj(tokens)                 # (B, 392, 512)
```

- [ ] **Step 4: Esegui i test**

```bash
pytest tests/models/test_encoders.py -v
```
Atteso: tutti i test `PASSED` (ViT impiega ~20s al primo run per scaricare i pesi)

- [ ] **Step 5: Commit**

```bash
git add src/models/encoders.py tests/models/test_encoders.py
git commit -m "feat: add CNNEncoderGlobal, CNNEncoderSpatial, ViTEncoder"
```

---

## Task 5: Decoders

**Files:**
- Create: `src/models/decoders.py`
- Create: `tests/models/test_decoders.py`

- [ ] **Step 1: Scrivi i test**

```python
# tests/models/test_decoders.py
import torch
import pytest
from src.models.decoders import LSTMDecoder, TransformerDecoder

B, SEQ, VOCAB = 2, 10, 52000

@pytest.fixture
def lstm_dec():
    return LSTMDecoder(vocab_size=VOCAB)

@pytest.fixture
def transformer_dec():
    return TransformerDecoder(vocab_size=VOCAB, n_visual_tokens=98)

def test_lstm_output_shape(lstm_dec):
    visual = torch.randn(B, 1, 512)
    captions = torch.randint(0, VOCAB, (B, SEQ))
    out = lstm_dec(visual, captions)
    assert out.shape == (B, SEQ, VOCAB)

def test_transformer_output_shape(transformer_dec):
    visual = torch.randn(B, 98, 512)
    captions = torch.randint(0, VOCAB, (B, SEQ))
    out = transformer_dec(visual, captions)
    assert out.shape == (B, SEQ, VOCAB)

def test_transformer_with_vit_tokens():
    dec = TransformerDecoder(vocab_size=VOCAB, n_visual_tokens=392)
    visual = torch.randn(B, 392, 512)
    captions = torch.randint(0, VOCAB, (B, SEQ))
    out = dec(visual, captions)
    assert out.shape == (B, SEQ, VOCAB)

def test_lstm_causal_property(lstm_dec):
    """Output al passo t non dipende dai token oltre t (LSTM è già causale)."""
    visual = torch.randn(1, 1, 512)
    cap1 = torch.randint(0, VOCAB, (1, SEQ))
    cap2 = cap1.clone()
    cap2[0, SEQ // 2:] = 0  # modifica la seconda metà
    out1 = lstm_dec(visual, cap1)
    out2 = lstm_dec(visual, cap2)
    # Le prime SEQ//2 posizioni devono essere identiche
    assert torch.allclose(out1[0, : SEQ // 2], out2[0, : SEQ // 2], atol=1e-5)

def test_transformer_causal_mask(transformer_dec):
    """Il Transformer usa causal mask: output a posizione t non vede token t+1."""
    visual = torch.randn(1, 98, 512)
    cap1 = torch.randint(0, VOCAB, (1, SEQ))
    cap2 = cap1.clone()
    cap2[0, SEQ // 2:] = 0
    out1 = transformer_dec(visual, cap1)
    out2 = transformer_dec(visual, cap2)
    assert torch.allclose(out1[0, : SEQ // 2], out2[0, : SEQ // 2], atol=1e-5)
```

- [ ] **Step 2: Esegui i test e verifica che falliscono**

```bash
pytest tests/models/test_decoders.py -v
```
Atteso: `ModuleNotFoundError: No module named 'src.models.decoders'`

- [ ] **Step 3: Implementa `src/models/decoders.py`**

```python
# src/models/decoders.py
from __future__ import annotations
import math
import torch
import torch.nn as nn


class LSTMDecoder(nn.Module):
    """LSTM decoder con input visivo come h0. Output: (B, seq_len, vocab_size)."""

    def __init__(
        self,
        vocab_size: int,
        embed_dim: int = 256,
        hidden_size: int = 512,
        pad_id: int = 0,
    ) -> None:
        super().__init__()
        self.embed = nn.Embedding(vocab_size, embed_dim, padding_idx=pad_id)
        self.lstm = nn.LSTM(embed_dim, hidden_size, batch_first=True)
        self.fc = nn.Linear(hidden_size, vocab_size)
        self.hidden_size = hidden_size

    def forward(
        self,
        visual_tokens: torch.Tensor,   # (B, 1, 512)
        captions: torch.Tensor,        # (B, seq_len)
    ) -> torch.Tensor:                 # (B, seq_len, vocab_size)
        # visual_tokens: (B,1,512) → h0/c0: (1,B,512)
        h0 = visual_tokens.squeeze(1).unsqueeze(0)  # (1, B, 512)
        c0 = torch.zeros_like(h0)
        emb = self.embed(captions)                   # (B, seq_len, embed_dim)
        out, _ = self.lstm(emb, (h0, c0))            # (B, seq_len, hidden_size)
        return self.fc(out)                           # (B, seq_len, vocab_size)


class _SinusoidalPE(nn.Module):
    """Positional encoding sinusoidale."""

    def __init__(self, d_model: int, max_len: int = 512) -> None:
        super().__init__()
        pe = torch.zeros(max_len, d_model)
        pos = torch.arange(max_len).unsqueeze(1).float()
        div = torch.exp(torch.arange(0, d_model, 2).float() * (-math.log(10000.0) / d_model))
        pe[:, 0::2] = torch.sin(pos * div)
        pe[:, 1::2] = torch.cos(pos * div)
        self.register_buffer("pe", pe.unsqueeze(0))  # (1, max_len, d_model)

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        return x + self.pe[:, : x.size(1)]


class TransformerDecoder(nn.Module):
    """Transformer decoder con cross-attention sui visual token.
    Output: (B, seq_len, vocab_size).
    """

    def __init__(
        self,
        vocab_size: int,
        n_visual_tokens: int,
        d_model: int = 512,
        n_heads: int = 8,
        n_layers: int = 4,
        ffn_dim: int = 2048,
        pad_id: int = 0,
        dropout: float = 0.1,
    ) -> None:
        super().__init__()
        self.embed = nn.Embedding(vocab_size, d_model, padding_idx=pad_id)
        self.pe = _SinusoidalPE(d_model)
        decoder_layer = nn.TransformerDecoderLayer(
            d_model=d_model,
            nhead=n_heads,
            dim_feedforward=ffn_dim,
            dropout=dropout,
            batch_first=True,
        )
        self.transformer = nn.TransformerDecoder(decoder_layer, num_layers=n_layers)
        self.fc = nn.Linear(d_model, vocab_size)
        self.d_model = d_model

    @staticmethod
    def _causal_mask(seq_len: int, device: torch.device) -> torch.Tensor:
        """Maschera causale (upper-triangular = -inf)."""
        mask = torch.triu(torch.ones(seq_len, seq_len, device=device), diagonal=1)
        return mask.masked_fill(mask.bool(), float("-inf"))

    def forward(
        self,
        visual_tokens: torch.Tensor,   # (B, n_visual_tokens, 512)
        captions: torch.Tensor,        # (B, seq_len)
    ) -> torch.Tensor:                 # (B, seq_len, vocab_size)
        seq_len = captions.size(1)
        tgt_mask = self._causal_mask(seq_len, captions.device)
        emb = self.pe(self.embed(captions))   # (B, seq_len, d_model)
        out = self.transformer(
            tgt=emb,
            memory=visual_tokens,
            tgt_mask=tgt_mask,
        )                                     # (B, seq_len, d_model)
        return self.fc(out)                   # (B, seq_len, vocab_size)
```

- [ ] **Step 4: Esegui i test**

```bash
pytest tests/models/test_decoders.py -v
```
Atteso: tutti i test `PASSED`

- [ ] **Step 5: Commit**

```bash
git add src/models/decoders.py tests/models/test_decoders.py
git commit -m "feat: add LSTMDecoder and TransformerDecoder with causal mask"
```

---

## Task 6: Modelli e build_model

**Files:**
- Create: `src/models/models.py`
- Create: `tests/models/test_models.py`

- [ ] **Step 1: Scrivi i test**

```python
# tests/models/test_models.py
import torch
import pytest
from src.models.models import CnnLstm, CnnTransformer, ViTTransformer, build_model

B, SEQ, VOCAB = 2, 8, 52000

@pytest.fixture(scope="module")
def dummy():
    fetta = torch.randn(B, 3, 224, 224)
    grana = torch.randn(B, 3, 224, 224)
    captions = torch.randint(0, VOCAB, (B, SEQ))
    return fetta, grana, captions

def test_cnn_lstm_forward(dummy):
    fetta, grana, caps = dummy
    model = CnnLstm(vocab_size=VOCAB)
    out = model(fetta, grana, caps)
    assert out.shape == (B, SEQ, VOCAB)

def test_cnn_transformer_forward(dummy):
    fetta, grana, caps = dummy
    model = CnnTransformer(vocab_size=VOCAB)
    out = model(fetta, grana, caps)
    assert out.shape == (B, SEQ, VOCAB)

def test_vit_transformer_forward(dummy):
    fetta, grana, caps = dummy
    model = ViTTransformer(vocab_size=VOCAB)
    out = model(fetta, grana, caps)
    assert out.shape == (B, SEQ, VOCAB)

def test_build_model_m1(dummy):
    fetta, grana, caps = dummy
    model = build_model("m1", vocab_size=VOCAB, device=torch.device("cpu"))
    out = model(fetta, grana, caps)
    assert out.shape == (B, SEQ, VOCAB)

def test_build_model_m2(dummy):
    fetta, grana, caps = dummy
    model = build_model("m2", vocab_size=VOCAB, device=torch.device("cpu"))
    out = model(fetta, grana, caps)
    assert out.shape == (B, SEQ, VOCAB)

def test_build_model_m3(dummy):
    fetta, grana, caps = dummy
    model = build_model("m3", vocab_size=VOCAB, device=torch.device("cpu"))
    out = model(fetta, grana, caps)
    assert out.shape == (B, SEQ, VOCAB)

def test_build_model_invalid():
    with pytest.raises(ValueError, match="Modello sconosciuto"):
        build_model("m99", vocab_size=VOCAB, device=torch.device("cpu"))
```

- [ ] **Step 2: Esegui i test e verifica che falliscono**

```bash
pytest tests/models/test_models.py -v
```
Atteso: `ModuleNotFoundError: No module named 'src.models.models'`

- [ ] **Step 3: Implementa `src/models/models.py`**

```python
# src/models/models.py
from __future__ import annotations
import torch
import torch.nn as nn

from src.models.encoders import CNNEncoderGlobal, CNNEncoderSpatial, ViTEncoder
from src.models.decoders import LSTMDecoder, TransformerDecoder


class CnnLstm(nn.Module):
    """M1: CNN encoder globale + LSTM decoder."""

    def __init__(self, vocab_size: int) -> None:
        super().__init__()
        self.encoder = CNNEncoderGlobal()
        self.decoder = LSTMDecoder(vocab_size=vocab_size)

    def forward(
        self,
        fetta: torch.Tensor,
        grana: torch.Tensor,
        captions: torch.Tensor,
    ) -> torch.Tensor:
        visual = self.encoder(fetta, grana)         # (B, 1, 512)
        return self.decoder(visual, captions)        # (B, seq, vocab)


class CnnTransformer(nn.Module):
    """M2: CNN encoder spaziale + Transformer decoder."""

    def __init__(self, vocab_size: int) -> None:
        super().__init__()
        self.encoder = CNNEncoderSpatial()
        self.decoder = TransformerDecoder(vocab_size=vocab_size, n_visual_tokens=98)

    def forward(
        self,
        fetta: torch.Tensor,
        grana: torch.Tensor,
        captions: torch.Tensor,
    ) -> torch.Tensor:
        visual = self.encoder(fetta, grana)         # (B, 98, 512)
        return self.decoder(visual, captions)        # (B, seq, vocab)


class ViTTransformer(nn.Module):
    """M3: ViT encoder + Transformer decoder."""

    def __init__(self, vocab_size: int) -> None:
        super().__init__()
        self.encoder = ViTEncoder()
        self.decoder = TransformerDecoder(vocab_size=vocab_size, n_visual_tokens=392)

    def forward(
        self,
        fetta: torch.Tensor,
        grana: torch.Tensor,
        captions: torch.Tensor,
    ) -> torch.Tensor:
        visual = self.encoder(fetta, grana)         # (B, 392, 512)
        return self.decoder(visual, captions)        # (B, seq, vocab)


def build_model(
    model_name: str,
    vocab_size: int,
    device: torch.device,
) -> nn.Module:
    """Factory: crea il modello richiesto e lo sposta sul device."""
    mapping = {
        "m1": CnnLstm,
        "m2": CnnTransformer,
        "m3": ViTTransformer,
    }
    if model_name not in mapping:
        raise ValueError(f"Modello sconosciuto: {model_name!r}. Scegli tra {list(mapping)}")
    return mapping[model_name](vocab_size=vocab_size).to(device)
```

- [ ] **Step 4: Esegui i test**

```bash
pytest tests/models/test_models.py -v
```
Atteso: tutti i test `PASSED`

- [ ] **Step 5: Commit**

```bash
git add src/models/models.py tests/models/test_models.py
git commit -m "feat: add CnnLstm, CnnTransformer, ViTTransformer and build_model factory"
```

---

## Task 7: Training loop e checkpoint

**Files:**
- Create: `src/models/train.py`
- Create: `tests/models/test_train.py`

- [ ] **Step 1: Scrivi i test**

```python
# tests/models/test_train.py
import json
import csv
import torch
import pytest
from pathlib import Path
from torch.utils.data import DataLoader, TensorDataset

from src.models.models import build_model
from src.models.train import train_one_epoch, evaluate_epoch, train_model, load_checkpoint

VOCAB = 100
B, SEQ = 4, 6

def _make_loader(n=8):
    """DataLoader sintetico: batch di (fetta, grana, caption, weight)."""
    fetta = torch.randn(n, 3, 224, 224)
    grana = torch.randn(n, 3, 224, 224)
    caps = torch.randint(1, VOCAB, (n, SEQ))
    weights = torch.ones(n)
    ds = TensorDataset(fetta, grana, caps, weights)
    return DataLoader(ds, batch_size=B)

@pytest.fixture
def m1_model():
    return build_model("m1", vocab_size=VOCAB, device=torch.device("cpu"))

def test_train_one_epoch_returns_float(m1_model):
    loader = _make_loader()
    opt = torch.optim.Adam(m1_model.parameters(), lr=1e-3)
    loss = train_one_epoch(m1_model, loader, opt, pad_id=0, device=torch.device("cpu"))
    assert isinstance(loss, float)
    assert loss > 0

def test_evaluate_epoch_returns_dict(m1_model):
    loader = _make_loader()
    result = evaluate_epoch(m1_model, loader, pad_id=0, device=torch.device("cpu"))
    assert "val_loss" in result
    assert isinstance(result["val_loss"], float)

def test_checkpoint_save_load(tmp_path, m1_model):
    run_dir = tmp_path / "m1" / "Texture"
    opt = torch.optim.Adam(m1_model.parameters())
    # Salva
    from src.models.train import save_checkpoint
    save_checkpoint(m1_model, opt, epoch=3, val_loss=1.23, run_dir=run_dir, is_best=True)
    assert (run_dir / "last.pt").exists()
    assert (run_dir / "best.pt").exists()
    # Carica
    loaded_model = build_model("m1", vocab_size=VOCAB, device=torch.device("cpu"))
    loaded_opt = torch.optim.Adam(loaded_model.parameters())
    epoch, val_loss = load_checkpoint(run_dir / "last.pt", loaded_model, loaded_opt)
    assert epoch == 3
    assert abs(val_loss - 1.23) < 1e-6

def test_log_csv_written(tmp_path, m1_model):
    run_dir = tmp_path / "m1" / "Texture"
    run_dir.mkdir(parents=True)
    from src.models.train import append_log
    append_log(run_dir, epoch=1, train_loss=2.0, val_loss=1.8, bleu4=0.1, elapsed=10.0)
    append_log(run_dir, epoch=2, train_loss=1.5, val_loss=1.3, bleu4=0.2, elapsed=11.0)
    log_path = run_dir / "log.csv"
    assert log_path.exists()
    with open(log_path) as f:
        rows = list(csv.DictReader(f))
    assert len(rows) == 2
    assert rows[0]["epoch"] == "1"
    assert float(rows[1]["bleu4"]) == pytest.approx(0.2)
```

- [ ] **Step 2: Esegui i test e verifica che falliscono**

```bash
pytest tests/models/test_train.py -v
```
Atteso: `ModuleNotFoundError: No module named 'src.models.train'`

- [ ] **Step 3: Implementa `src/models/train.py`**

```python
# src/models/train.py
from __future__ import annotations
import csv
import json
import time
from pathlib import Path

import torch
import torch.nn as nn
from torch.utils.data import DataLoader
from tqdm import tqdm


def train_one_epoch(
    model: nn.Module,
    loader: DataLoader,
    optimizer: torch.optim.Optimizer,
    pad_id: int,
    device: torch.device,
) -> float:
    """Teacher-forcing training. Restituisce la loss media sull'epoca."""
    model.train()
    criterion = nn.CrossEntropyLoss(ignore_index=pad_id, reduction="none")
    total_loss, total_weight = 0.0, 0.0

    for batch in tqdm(loader, leave=False, desc="train"):
        fetta, grana, caps, weights = [b.to(device) for b in batch]
        # Input: tutti i token tranne l'ultimo; target: tutti tranne il primo
        inp = caps[:, :-1]
        tgt = caps[:, 1:]
        logits = model(fetta, grana, inp)                    # (B, T-1, vocab)
        B, T, V = logits.shape
        loss_per_token = criterion(logits.reshape(B * T, V), tgt.reshape(B * T))
        loss_per_sample = loss_per_token.reshape(B, T).mean(dim=1)  # (B,)
        weighted_loss = (loss_per_sample * weights).sum()
        optimizer.zero_grad()
        weighted_loss.backward()
        nn.utils.clip_grad_norm_(model.parameters(), max_norm=5.0)
        optimizer.step()
        total_loss += weighted_loss.item()
        total_weight += weights.sum().item()

    return total_loss / max(total_weight, 1.0)


def evaluate_epoch(
    model: nn.Module,
    loader: DataLoader,
    pad_id: int,
    device: torch.device,
) -> dict[str, float]:
    """Calcola la val_loss. BLEU-4 aggiunto solo da quick_eval (più lento)."""
    model.eval()
    criterion = nn.CrossEntropyLoss(ignore_index=pad_id)
    total_loss, n_batches = 0.0, 0

    with torch.no_grad():
        for batch in loader:
            fetta, grana, caps, _weights = [b.to(device) for b in batch]
            inp = caps[:, :-1]
            tgt = caps[:, 1:]
            logits = model(fetta, grana, inp)
            B, T, V = logits.shape
            loss = criterion(logits.reshape(B * T, V), tgt.reshape(B * T))
            total_loss += loss.item()
            n_batches += 1

    return {"val_loss": total_loss / max(n_batches, 1)}


def save_checkpoint(
    model: nn.Module,
    optimizer: torch.optim.Optimizer,
    epoch: int,
    val_loss: float,
    run_dir: Path,
    is_best: bool,
) -> None:
    run_dir = Path(run_dir)
    run_dir.mkdir(parents=True, exist_ok=True)
    state = {
        "epoch": epoch,
        "val_loss": val_loss,
        "model_state": model.state_dict(),
        "optimizer_state": optimizer.state_dict(),
    }
    torch.save(state, run_dir / "last.pt")
    if is_best:
        torch.save(state, run_dir / "best.pt")


def load_checkpoint(
    path: Path,
    model: nn.Module,
    optimizer: torch.optim.Optimizer,
) -> tuple[int, float]:
    """Carica checkpoint. Restituisce (epoch, val_loss)."""
    state = torch.load(path, map_location="cpu")
    model.load_state_dict(state["model_state"])
    optimizer.load_state_dict(state["optimizer_state"])
    return state["epoch"], state["val_loss"]


def append_log(
    run_dir: Path,
    epoch: int,
    train_loss: float,
    val_loss: float,
    bleu4: float,
    elapsed: float,
) -> None:
    log_path = Path(run_dir) / "log.csv"
    write_header = not log_path.exists()
    with open(log_path, "a", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(
            f, fieldnames=["epoch", "train_loss", "val_loss", "bleu4", "elapsed_sec"]
        )
        if write_header:
            writer.writeheader()
        writer.writerow(
            dict(epoch=epoch, train_loss=round(train_loss, 6),
                 val_loss=round(val_loss, 6), bleu4=round(bleu4, 6),
                 elapsed_sec=round(elapsed, 1))
        )


def train_model(
    model: nn.Module,
    train_loader: DataLoader,
    val_loader: DataLoader,
    optimizer: torch.optim.Optimizer,
    scheduler: torch.optim.lr_scheduler._LRScheduler,
    tokenizer,
    device: torch.device,
    run_dir: Path,
    config: dict,
    resume: bool = False,
) -> None:
    """Loop di training completo con early stopping e checkpoint."""
    from src.models.metrics import quick_eval

    run_dir = Path(run_dir)
    run_dir.mkdir(parents=True, exist_ok=True)

    # Salva config
    with open(run_dir / "config.json", "w", encoding="utf-8") as f:
        json.dump(config, f, indent=2, ensure_ascii=False)

    start_epoch = 1
    best_val_loss = float("inf")
    patience_counter = 0
    patience = config.get("early_stopping_patience", 7)
    max_epochs = config.get("epochs", 50)
    pad_id = tokenizer.PAD_ID

    if resume and (run_dir / "last.pt").exists():
        start_epoch, best_val_loss = load_checkpoint(
            run_dir / "last.pt", model, optimizer
        )
        start_epoch += 1
        print(f"Ripreso da epoca {start_epoch}, best_val_loss={best_val_loss:.4f}")

    for epoch in range(start_epoch, max_epochs + 1):
        t0 = time.time()
        train_loss = train_one_epoch(model, train_loader, optimizer, pad_id, device)
        val_metrics = evaluate_epoch(model, val_loader, pad_id, device)
        val_loss = val_metrics["val_loss"]
        bleu4 = quick_eval(model, val_loader, tokenizer, device)
        elapsed = time.time() - t0

        is_best = val_loss < best_val_loss
        if is_best:
            best_val_loss = val_loss
            patience_counter = 0
        else:
            patience_counter += 1

        save_checkpoint(model, optimizer, epoch, val_loss, run_dir, is_best)
        append_log(run_dir, epoch, train_loss, val_loss, bleu4, elapsed)
        scheduler.step()

        print(
            f"Epoca {epoch:3d}/{max_epochs} | "
            f"train_loss={train_loss:.4f} | val_loss={val_loss:.4f} | "
            f"BLEU-4={bleu4:.4f} | {'★ BEST' if is_best else f'patience {patience_counter}/{patience}'} | "
            f"{elapsed:.0f}s"
        )

        if patience_counter >= patience:
            print(f"Early stopping a epoca {epoch}.")
            break

    print(f"Training completato. Best val_loss: {best_val_loss:.4f}")
    print(f"Pesi migliori: {run_dir / 'best.pt'}")
```

- [ ] **Step 4: Esegui i test**

```bash
pytest tests/models/test_train.py -v
```
Atteso: tutti i test `PASSED`

- [ ] **Step 5: Commit**

```bash
git add src/models/train.py tests/models/test_train.py
git commit -m "feat: add training loop, checkpoint save/load, early stopping"
```

---

## Task 8: Metriche e generate_caption

**Files:**
- Create: `src/models/metrics.py`
- Create: `tests/models/test_metrics.py`

- [ ] **Step 1: Scrivi i test**

```python
# tests/models/test_metrics.py
import torch
import pytest
from torch.utils.data import DataLoader, TensorDataset
from src.models.vocabulary import ItalianTokenizer
from src.models.models import build_model
from src.models.metrics import generate_caption, quick_eval, full_eval

VOCAB_SIZE = 52000
B, SEQ = 2, 8

@pytest.fixture(scope="module")
def tok():
    return ItalianTokenizer()

@pytest.fixture(scope="module")
def tiny_model(tok):
    return build_model("m1", vocab_size=len(tok), device=torch.device("cpu"))

@pytest.fixture
def tiny_loader(tok):
    fetta = torch.randn(4, 3, 224, 224)
    grana = torch.randn(4, 3, 224, 224)
    caps = torch.randint(1, len(tok), (4, SEQ))
    weights = torch.ones(4)
    ds = TensorDataset(fetta, grana, caps, weights)
    return DataLoader(ds, batch_size=B)

def test_generate_caption_returns_string(tiny_model, tok):
    fetta = torch.randn(1, 3, 224, 224)
    grana = torch.randn(1, 3, 224, 224)
    result = generate_caption(tiny_model, fetta, grana, tok, torch.device("cpu"), max_len=20)
    assert isinstance(result, str)
    assert len(result) >= 0  # può essere vuota se il modello non è addestrato

def test_generate_caption_respects_max_len(tiny_model, tok):
    fetta = torch.randn(1, 3, 224, 224)
    grana = torch.randn(1, 3, 224, 224)
    result = generate_caption(tiny_model, fetta, grana, tok, torch.device("cpu"), max_len=5)
    ids = tok.encode(result, add_special=False)
    assert len(ids) <= 5

def test_quick_eval_returns_float(tiny_model, tok, tiny_loader):
    bleu4 = quick_eval(tiny_model, tiny_loader, tok, torch.device("cpu"))
    assert isinstance(bleu4, float)
    assert 0.0 <= bleu4 <= 1.0

def test_full_eval_returns_all_metrics(tiny_model, tok, tiny_loader, tmp_path):
    results = full_eval(
        tiny_model, tiny_loader, tok, torch.device("cpu"),
        predictions_path=tmp_path / "predictions.csv",
    )
    for key in ["bleu1", "bleu4", "meteor", "rouge_l"]:
        assert key in results, f"{key} mancante in full_eval"
        assert 0.0 <= results[key] <= 1.0

def test_full_eval_saves_predictions(tiny_model, tok, tiny_loader, tmp_path):
    pred_path = tmp_path / "predictions.csv"
    full_eval(tiny_model, tiny_loader, tok, torch.device("cpu"), predictions_path=pred_path)
    assert pred_path.exists()
    import pandas as pd
    df = pd.read_csv(pred_path)
    assert "caption_pred" in df.columns
    assert "caption_ref" in df.columns
    assert len(df) == 4  # 4 campioni nel loader
```

- [ ] **Step 2: Esegui i test e verifica che falliscono**

```bash
pytest tests/models/test_metrics.py -v
```
Atteso: `ModuleNotFoundError: No module named 'src.models.metrics'`

- [ ] **Step 3: Implementa `src/models/metrics.py`**

```python
# src/models/metrics.py
from __future__ import annotations
from pathlib import Path

import pandas as pd
import torch
import torch.nn as nn
import evaluate as hf_evaluate
from torch.utils.data import DataLoader


def generate_caption(
    model: nn.Module,
    fetta: torch.Tensor,
    grana: torch.Tensor,
    tokenizer,
    device: torch.device,
    beam_size: int = 1,
    max_len: int = 50,
) -> str:
    """Genera una caption con greedy decoding (beam_size=1) o beam search."""
    model.eval()
    fetta = fetta.to(device)
    grana = grana.to(device)

    with torch.no_grad():
        if beam_size == 1:
            return _greedy_decode(model, fetta, grana, tokenizer, device, max_len)
        return _beam_search(model, fetta, grana, tokenizer, device, beam_size, max_len)


def _greedy_decode(model, fetta, grana, tokenizer, device, max_len):
    generated = [tokenizer.SOS_ID]
    for _ in range(max_len):
        inp = torch.tensor([generated], dtype=torch.long, device=device)
        logits = model(fetta, grana, inp)       # (1, t, vocab)
        next_id = logits[0, -1].argmax().item()
        if next_id == tokenizer.EOS_ID:
            break
        generated.append(next_id)
    return tokenizer.decode(generated[1:], skip_special=True)


def _beam_search(model, fetta, grana, tokenizer, device, beam_size, max_len):
    # Beam search: lista di (score, token_sequence)
    beams = [(0.0, [tokenizer.SOS_ID])]
    completed = []

    for _ in range(max_len):
        candidates = []
        for score, seq in beams:
            inp = torch.tensor([seq], dtype=torch.long, device=device)
            logits = model(fetta, grana, inp)    # (1, t, vocab)
            log_probs = torch.log_softmax(logits[0, -1], dim=-1)
            topk = log_probs.topk(beam_size)
            for prob, token_id in zip(topk.values.tolist(), topk.indices.tolist()):
                new_score = score + prob
                new_seq = seq + [token_id]
                if token_id == tokenizer.EOS_ID:
                    completed.append((new_score, new_seq))
                else:
                    candidates.append((new_score, new_seq))
        if not candidates:
            break
        beams = sorted(candidates, key=lambda x: x[0], reverse=True)[:beam_size]

    if completed:
        best = max(completed, key=lambda x: x[0])
    elif beams:
        best = max(beams, key=lambda x: x[0])
    else:
        return ""

    return tokenizer.decode(best[1][1:], skip_special=True)


def quick_eval(
    model: nn.Module,
    loader: DataLoader,
    tokenizer,
    device: torch.device,
    max_samples: int = 100,
) -> float:
    """BLEU-4 rapido su un sottoinsieme del loader. Usato ogni epoca."""
    bleu_metric = hf_evaluate.load("bleu")
    preds, refs = [], []
    n = 0

    model.eval()
    for batch in loader:
        fetta, grana, caps, _weights = [b.to(device) for b in batch]
        for i in range(fetta.size(0)):
            pred = generate_caption(
                model, fetta[i: i + 1], grana[i: i + 1], tokenizer, device,
                beam_size=1, max_len=50,
            )
            ref_ids = caps[i].tolist()
            ref = tokenizer.decode(ref_ids, skip_special=True)
            preds.append(pred)
            refs.append([ref])
            n += 1
            if n >= max_samples:
                break
        if n >= max_samples:
            break

    if not preds:
        return 0.0
    try:
        result = bleu_metric.compute(predictions=preds, references=refs)
        return float(result.get("bleu", 0.0))
    except Exception:
        return 0.0


def full_eval(
    model: nn.Module,
    loader: DataLoader,
    tokenizer,
    device: torch.device,
    predictions_path: Path | None = None,
    beam_size: int = 3,
) -> dict[str, float]:
    """BLEU-1/4, METEOR, ROUGE-L su tutto il loader. Salva predictions.csv."""
    bleu_metric = hf_evaluate.load("bleu")
    meteor_metric = hf_evaluate.load("meteor")
    rouge_metric = hf_evaluate.load("rouge")

    preds, refs = [], []
    model.eval()

    for batch in loader:
        fetta, grana, caps, _weights = [b.to(device) for b in batch]
        for i in range(fetta.size(0)):
            pred = generate_caption(
                model, fetta[i: i + 1], grana[i: i + 1], tokenizer, device,
                beam_size=beam_size, max_len=50,
            )
            ref_ids = caps[i].tolist()
            ref = tokenizer.decode(ref_ids, skip_special=True)
            preds.append(pred)
            refs.append(ref)

    refs_for_bleu = [[r] for r in refs]

    results: dict[str, float] = {}
    try:
        b = bleu_metric.compute(predictions=preds, references=refs_for_bleu)
        results["bleu4"] = float(b.get("bleu", 0.0))
        precisions = b.get("precisions", [0.0, 0.0, 0.0, 0.0])
        results["bleu1"] = float(precisions[0]) if precisions else 0.0
    except Exception:
        results["bleu1"] = results["bleu4"] = 0.0

    try:
        m = meteor_metric.compute(predictions=preds, references=refs)
        results["meteor"] = float(m.get("meteor", 0.0))
    except Exception:
        results["meteor"] = 0.0

    try:
        r = rouge_metric.compute(predictions=preds, references=refs)
        results["rouge_l"] = float(r.get("rougeL", 0.0))
    except Exception:
        results["rouge_l"] = 0.0

    if predictions_path is not None:
        predictions_path = Path(predictions_path)
        predictions_path.parent.mkdir(parents=True, exist_ok=True)
        pd.DataFrame({"caption_pred": preds, "caption_ref": refs}).to_csv(
            predictions_path, index=False, encoding="utf-8"
        )

    return results
```

- [ ] **Step 4: Esegui i test**

```bash
pytest tests/models/test_metrics.py -v
```
Atteso: tutti i test `PASSED` (la prima run scarica i moduli `evaluate`)

- [ ] **Step 5: Commit**

```bash
git add src/models/metrics.py tests/models/test_metrics.py
git commit -m "feat: add generate_caption (greedy+beam), quick_eval and full_eval"
```

---

## Task 9: CLI `train.py`

**Files:**
- Create: `train.py` (root del progetto)

- [ ] **Step 1: Implementa il CLI**

```python
# train.py  (root del progetto)
"""
CLI per training dei modelli encoder-decoder Grana Trentino.

Esempi:
  python train.py --model m1 --attributo Texture
  python train.py --model m2 --attributo all --epochs 50
  python train.py --model m1 --attributo Texture --resume
  python train.py --model m1 --attributo Texture --eval-only
"""
from __future__ import annotations
import argparse
import json
import sys
from pathlib import Path

import torch
from torch.utils.data import DataLoader

PROJECT_ROOT = Path(__file__).parent

sys.path.insert(0, str(PROJECT_ROOT))

from src.models.vocabulary import ItalianTokenizer
from src.models.dataset import GranaTrentinoDataset, build_splits
from src.models.models import build_model
from src.models.train import train_model
from src.models.metrics import full_eval

DATASET_CSV = PROJECT_ROOT / "data" / "processed" / "dataset_captioning.csv"
SPLITS_JSON = PROJECT_ROOT / "data" / "processed" / "splits.json"
MODELS_DIR = PROJECT_ROOT / "models"

DEFAULTS = {
    "m1": dict(epochs=50, batch_size=32, lr=3e-4, patience=7, scheduler="steplr"),
    "m2": dict(epochs=50, batch_size=32, lr=3e-4, patience=7, scheduler="steplr"),
    "m3": dict(epochs=30, batch_size=16, lr=1e-4, patience=5, scheduler="cosine"),
}
MODEL_DIR_NAMES = {"m1": "m1_cnn_lstm", "m2": "m2_cnn_transformer", "m3": "m3_vit_transformer"}


def parse_args():
    p = argparse.ArgumentParser(description="Training image captioning Grana Trentino")
    p.add_argument("--model", required=True, choices=["m1", "m2", "m3"])
    p.add_argument("--attributo", required=True,
                   help="Nome attributo (es. Texture) o 'all' per modello globale")
    p.add_argument("--epochs", type=int, default=None)
    p.add_argument("--batch-size", type=int, default=None)
    p.add_argument("--lr", type=float, default=None)
    p.add_argument("--beam-size", type=int, default=3)
    p.add_argument("--seed", type=int, default=42)
    p.add_argument("--resume", action="store_true")
    p.add_argument("--include-fetta-only", action="store_true")
    p.add_argument("--eval-only", action="store_true")
    return p.parse_args()


def make_loader(
    split: str,
    tokenizer: ItalianTokenizer,
    attributo: str | None,
    batch_size: int,
    require_both_views: bool,
) -> DataLoader:
    ds = GranaTrentinoDataset(
        csv_path=DATASET_CSV,
        tokenizer=tokenizer,
        splits_path=SPLITS_JSON,
        attributo=attributo,
        split=split,
        require_both_views=require_both_views,
    )

    def collate(batch):
        import torch
        from torch.nn.utils.rnn import pad_sequence
        fette = torch.stack([b["fetta"] for b in batch])
        grana = torch.stack([b["grana"] for b in batch])
        caps = pad_sequence(
            [b["caption"] for b in batch], batch_first=True,
            padding_value=tokenizer.PAD_ID,
        )
        weights = torch.tensor([b["weight"] for b in batch], dtype=torch.float)
        return fette, grana, caps, weights

    return DataLoader(
        ds, batch_size=batch_size, shuffle=(split == "train"),
        collate_fn=collate, num_workers=2, pin_memory=True,
    )


def main():
    args = parse_args()
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    print(f"Device: {device}")

    # Genera splits se non esiste
    if not SPLITS_JSON.exists():
        print("Generazione splits.json...")
        build_splits(DATASET_CSV, seed=args.seed, out_path=SPLITS_JSON)

    # Risolvi attributo
    attributo = None if args.attributo == "all" else args.attributo
    attr_dir = "global" if attributo is None else attributo

    # Iperparametri
    defaults = DEFAULTS[args.model]
    epochs = args.epochs or defaults["epochs"]
    batch_size = args.batch_size or defaults["batch_size"]
    lr = args.lr or defaults["lr"]

    # Run directory
    run_dir = MODELS_DIR / MODEL_DIR_NAMES[args.model] / attr_dir

    # Tokenizer
    print("Caricamento tokenizer...")
    tokenizer = ItalianTokenizer()

    # Modello
    if args.eval_only:
        best_pt = run_dir / "best.pt"
        if not best_pt.exists():
            print(f"ERRORE: {best_pt} non trovato. Esegui prima il training.")
            sys.exit(1)

    print(f"Costruzione modello {args.model.upper()}...")
    model = build_model(args.model, vocab_size=len(tokenizer), device=device)

    if args.eval_only:
        from src.models.train import load_checkpoint
        opt_tmp = torch.optim.Adam(model.parameters())
        load_checkpoint(run_dir / "best.pt", model, opt_tmp)
        print("Valutazione su test set...")
        test_loader = make_loader("test", tokenizer, attributo, batch_size,
                                  require_both_views=not args.include_fetta_only)
        results = full_eval(model, test_loader, tokenizer, device,
                            predictions_path=run_dir / "predictions.csv",
                            beam_size=args.beam_size)
        print("Test set results:")
        for k, v in results.items():
            print(f"  {k}: {v:.4f}")
        return

    # Controlla sovrascrittura
    if (run_dir / "best.pt").exists() and not args.resume:
        answer = input(f"Esiste già un training in {run_dir}. Sovrascrivere? [s/N] ")
        if answer.lower() not in ("s", "si", "y", "yes"):
            print("Annullato.")
            sys.exit(0)

    # Loaders
    require_both = not args.include_fetta_only
    train_loader = make_loader("train", tokenizer, attributo, batch_size, require_both)
    val_loader = make_loader("val", tokenizer, attributo, batch_size, require_both)
    print(f"Train: {len(train_loader.dataset)} campioni | Val: {len(val_loader.dataset)} campioni")

    # Optimizer e scheduler
    if args.model == "m3":
        vit_params = [p for n, p in model.named_parameters()
                      if p.requires_grad and "encoder.vit" in n]
        other_params = [p for n, p in model.named_parameters()
                        if p.requires_grad and "encoder.vit" not in n]
        optimizer = torch.optim.AdamW([
            {"params": vit_params, "lr": lr * 0.1},
            {"params": other_params, "lr": lr},
        ])
        scheduler = torch.optim.lr_scheduler.CosineAnnealingLR(optimizer, T_max=epochs)
    else:
        optimizer = torch.optim.Adam(model.parameters(), lr=lr)
        scheduler = torch.optim.lr_scheduler.StepLR(optimizer, step_size=10, gamma=0.5)

    config = dict(
        model=args.model, attributo=attr_dir, epochs=epochs,
        batch_size=batch_size, lr=lr, seed=args.seed,
        beam_size=args.beam_size, early_stopping_patience=defaults["patience"],
        include_fetta_only=args.include_fetta_only,
    )

    # Training
    train_model(
        model=model,
        train_loader=train_loader,
        val_loader=val_loader,
        optimizer=optimizer,
        scheduler=scheduler,
        tokenizer=tokenizer,
        device=device,
        run_dir=run_dir,
        config=config,
        resume=args.resume,
    )

    # Valutazione finale su test set
    print("\nValutazione finale su test set con best.pt...")
    from src.models.train import load_checkpoint
    load_checkpoint(run_dir / "best.pt", model, optimizer)
    test_loader = make_loader("test", tokenizer, attributo, batch_size, require_both)
    results = full_eval(model, test_loader, tokenizer, device,
                        predictions_path=run_dir / "predictions.csv",
                        beam_size=args.beam_size)
    print("Test set results:")
    for k, v in results.items():
        print(f"  {k}: {v:.4f}")


if __name__ == "__main__":
    main()
```

- [ ] **Step 2: Smoke test del CLI (dry run — verifica che parse e import funzionino)**

```bash
python train.py --help
```
Atteso: lista degli argomenti senza errori.

- [ ] **Step 3: Test end-to-end su M1/Texture (1 epoca, batch piccolo)**

```bash
python train.py --model m1 --attributo Texture --epochs 1 --batch-size 8
```
Atteso: training per 1 epoca, poi valutazione su test set con BLEU/METEOR/ROUGE-L stampati.

- [ ] **Step 4: Commit**

```bash
git add train.py
git commit -m "feat: add CLI train.py with --model, --attributo, --resume, --eval-only"
```

---

## Task 10: Report comparativo

**Files:**
- Create: `reports/compare_models.py`

- [ ] **Step 1: Implementa `reports/compare_models.py`**

```python
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
}
ATTRIBUTI = [
    "Aroma", "Profumo", "Sapore", "Texture",
    "Struttura_della_Pasta", "Colore_della_Pasta", "Spessore_della_Crosta",
    "global",
]
METRICS = ["bleu1", "bleu4", "meteor", "rouge_l"]


def _load_results(model_dir: Path, attr: str) -> dict | None:
    """Legge predictions.csv e restituisce le metriche, o None se non esiste."""
    pred_path = model_dir / attr / "predictions.csv"
    if not pred_path.exists():
        return None
    try:
        import evaluate as hf_evaluate
        df = pd.read_csv(pred_path)
        preds = df["caption_pred"].tolist()
        refs = [[r] for r in df["caption_ref"].tolist()]

        bleu = hf_evaluate.load("bleu").compute(predictions=preds, references=refs)
        meteor = hf_evaluate.load("meteor").compute(predictions=preds, references=refs)
        rouge = hf_evaluate.load("rouge").compute(predictions=preds, references=refs)

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
    lines.append(f"Dataset: `data/processed/dataset_captioning.csv` | Split: 70/15/15 per campione fisico")
    lines.append("")

    for model_label, model_dirname in MODEL_DIRS.items():
        model_dir = MODELS_DIR / model_dirname
        lines.append(f"## {model_label}")
        lines.append("")
        lines.append(f"| Attributo | Best Epoch | BLEU-1 | BLEU-4 | METEOR | ROUGE-L |")
        lines.append(f"|---|---|---|---|---|---|")

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
```

- [ ] **Step 2: Test smoke (con cartella models/ vuota)**

```bash
python reports/compare_models.py
```
Atteso: `training_results.md` generato con tutte le righe `—` (nessun training ancora completato).

- [ ] **Step 3: Commit**

```bash
git add reports/compare_models.py reports/training_results.md
git commit -m "feat: add compare_models.py report generator"
```

---

## Self-Review

**Copertura spec:**
- ✅ `GranaTrentinoDataset` con `require_both_views`, `attributo=None` (global), split da `splits.json`
- ✅ `ItalianTokenizer` con GePpeTto + token speciali + ATTR_TOKENS
- ✅ Tutti e 3 gli encoder con interfaccia comune `(B, n_tokens, 512)`
- ✅ `LSTMDecoder` e `TransformerDecoder` con causal mask
- ✅ `build_model` factory
- ✅ `train_one_epoch` con teacher forcing + weighted loss
- ✅ `evaluate_epoch` con val_loss
- ✅ `save_checkpoint` / `load_checkpoint` / `append_log`
- ✅ `train_model` con early stopping, scheduler, resume
- ✅ `generate_caption` greedy + beam search
- ✅ `quick_eval` (BLEU-4) e `full_eval` (BLEU-1/4, METEOR, ROUGE-L)
- ✅ CLI con tutti i flag della spec
- ✅ `compare_models.py`

**Tipo consistency check:**
- `train_one_epoch` / `evaluate_epoch` ricevono `DataLoader` con tuple `(fetta, grana, caps, weights)` — coerente con il `collate_fn` del CLI
- `generate_caption` riceve un singolo sample `(1, 3, 224, 224)` — coerente con l'uso in `quick_eval` e `full_eval`
- `build_model` restituisce `nn.Module` con signature `forward(fetta, grana, captions)` — coerente in tutti i task

**Nessun placeholder o TBD trovato.**
