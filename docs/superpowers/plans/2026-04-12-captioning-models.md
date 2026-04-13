# Captioning Models Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Implementare e confrontare tre metodi encoder-decoder (CNN+LSTM, CNN+Transformer, ViT+Transformer) per generare caption testuali in italiano a partire da coppie di immagini FETTA+GRANA di Grana Trentino.

**Architecture:** Dataset builder che unisce caption per-attributo con path immagini → modulo PyTorch condiviso (vocabulary, dataset, training loop, evaluation) → tre model class separati che condividono l'infrastruttura comune. Ogni modello viene addestrato e valutato con le stesse metriche (BLEU/METEOR/CIDEr/ROUGE-L).

**Tech Stack:** Python 3.8+, PyTorch 2.0, torchvision, timm (ViT), transformers (GePpeTto tokenizer), pycocoevalcap, pandas, Pillow, tqdm

---

## Struttura file

```
src/models/
  __init__.py                  # vuoto
  dataset.py                   # build_caption_index(), GranaTrentinoDataset
  vocabulary.py                # ItalianTokenizer (wrapper GePpeTto)
  encoders.py                  # CNNEncoderGlobal, CNNEncoderSpatial, ViTEncoder
  decoders.py                  # LSTMDecoder, TransformerDecoder
  models.py                    # CnnLstm, CnnTransformer, ViTTransformer
  train.py                     # train_one_epoch(), evaluate_epoch(), train_model()
  metrics.py                   # compute_nlg_metrics(), generate_caption()

src/data/
  14_prepare_training_data.py  # CLI: crea data/processed/dataset_captioning.csv

tests/models/
  __init__.py
  test_dataset.py
  test_vocabulary.py
  test_encoders.py
  test_decoders.py
  test_models.py
  test_metrics.py

data/processed/
  dataset_captioning.csv       # OUTPUT di Task 1: (fetta_path, grana_path, attributo, caption)

models/
  m1_cnn_lstm/                 # checkpoint salvati durante training
  m2_cnn_transformer/
  m3_vit_transformer/

reports/
  training_results.md          # OUTPUT di Task 8
```

---

## Task 1: Build dataset index

**Scopo:** creare `data/processed/dataset_captioning.csv` unendo le caption per-attributo con i path immagini da `campioni_completi.csv`. La caption CSV ha `prodotto` (codice anonimato, es. "C0N") e `anno`; `campioni_completi.csv` ha `codice_caseificio` (es. "TN323") e `anno`. Il join avviene tramite `codifica caseifici.xlsx`.

**Files:**
- Create: `src/data/14_prepare_training_data.py`
- Create: `tests/models/test_dataset.py` (sezione build_caption_index)

- [ ] **Step 1: Scrivi il test per build_caption_index**

```python
# tests/models/test_dataset.py
import pandas as pd
import pytest
from pathlib import Path
from src.models.dataset import build_caption_index

@pytest.fixture
def tmp_data(tmp_path):
    # Caption CSV per-attributo (formato reale)
    cap = pd.DataFrame([
        {"id": 1, "classe": "OK",             "caption": "Il campione è granuloso.",  "anno": "2019", "prodotto": "C0A"},
        {"id": 2, "classe": "FUORI_ATTRIBUTO","caption": None,                        "anno": "2019", "prodotto": "C0A"},
        {"id": 3, "classe": "OK",             "caption": "Pasta compatta.",           "anno": "2019", "prodotto": "C0B"},
    ])
    cap_dir = tmp_path / "caption_per_attributo"
    cap_dir.mkdir()
    cap.to_csv(cap_dir / "Texture_captions.csv", index=False)

    # campioni_completi
    camp = pd.DataFrame([
        {"sample_id": "TN302_2019-09-11", "codice_caseificio": "TN302", "anno": "2019",
         "path_fetta_primaria": "img/fetta1.bmp", "path_grana_primaria": "img/grana1.bmp"},
        {"sample_id": "TN305_2019-09-11", "codice_caseificio": "TN305", "anno": "2019",
         "path_fetta_primaria": "img/fetta2.bmp", "path_grana_primaria": "img/grana2.bmp"},
    ])
    camp.to_csv(tmp_path / "campioni_completi.csv", index=False)

    # codifica: C0A → TN302, C0B → TN305
    cod = pd.DataFrame([
        {"prodotto": "C0A", "codice_caseificio": "TN302"},
        {"prodotto": "C0B", "codice_caseificio": "TN305"},
    ])
    cod.to_csv(tmp_path / "codifica_caseifici.csv", index=False)

    return tmp_path

def test_build_caption_index_columns(tmp_data):
    df = build_caption_index(
        captions_dir=tmp_data / "caption_per_attributo",
        campioni_csv=tmp_data / "campioni_completi.csv",
        codifica_csv=tmp_data / "codifica_caseifici.csv",
    )
    assert set(["fetta_path", "grana_path", "attributo", "caption"]).issubset(df.columns)

def test_build_caption_index_filters_non_ok(tmp_data):
    df = build_caption_index(
        captions_dir=tmp_data / "caption_per_attributo",
        campioni_csv=tmp_data / "campioni_completi.csv",
        codifica_csv=tmp_data / "codifica_caseifici.csv",
    )
    # FUORI_ATTRIBUTO (caption=None) deve essere escluso
    assert len(df) == 2
    assert df["caption"].notna().all()

def test_build_caption_index_has_image_paths(tmp_data):
    df = build_caption_index(
        captions_dir=tmp_data / "caption_per_attributo",
        campioni_csv=tmp_data / "campioni_completi.csv",
        codifica_csv=tmp_data / "codifica_caseifici.csv",
    )
    assert (df["fetta_path"] != "").all()
    assert (df["grana_path"] != "").all()
```

- [ ] **Step 2: Esegui il test per verificare che fallisce**

```
pytest tests/models/test_dataset.py::test_build_caption_index_columns -v
```
Atteso: `ModuleNotFoundError: No module named 'src.models.dataset'`

- [ ] **Step 3: Crea `src/models/__init__.py` vuoto e `src/models/dataset.py` con `build_caption_index`**

```python
# src/models/__init__.py
# (file vuoto)
```

```python
# src/models/dataset.py
import pandas as pd
from pathlib import Path


def build_caption_index(
    captions_dir: Path,
    campioni_csv: Path,
    codifica_csv: Path,
) -> pd.DataFrame:
    """
    Unisce i CSV caption per-attributo con i path immagini.

    Restituisce DataFrame con colonne:
      fetta_path, grana_path, attributo, caption, sample_id, anno
    Esclude righe con caption=None (classe FUORI_ATTRIBUTO / ILLEGGIBILE).
    """
    captions_dir = Path(captions_dir)
    campioni = pd.read_csv(campioni_csv, dtype=str)
    codifica = pd.read_csv(codifica_csv, dtype=str)

    # join codifica: prodotto → codice_caseificio
    # campioni ha già codice_caseificio; uniamo tramite codifica
    records = []
    for csv_path in sorted(captions_dir.glob("*_captions.csv")):
        attributo = csv_path.stem.replace("_captions", "")
        cap_df = pd.read_csv(csv_path, dtype=str)

        # filtra solo righe con caption non nulla
        cap_df = cap_df[cap_df["caption"].notna() & (cap_df["caption"] != "")].copy()

        # mappa prodotto → codice_caseificio
        cap_df = cap_df.merge(codifica, on="prodotto", how="left")

        # join con campioni su (codice_caseificio, anno)
        # se più date per stesso anno/caseificio → prendi la prima
        campioni_dedup = (
            campioni
            .sort_values("data_seduta")
            .drop_duplicates(subset=["codice_caseificio", "anno"])
        )
        cap_df = cap_df.merge(
            campioni_dedup[["codice_caseificio", "anno", "sample_id",
                             "path_fetta_primaria", "path_grana_primaria"]],
            on=["codice_caseificio", "anno"],
            how="left",
        )

        # rinomina colonne
        cap_df = cap_df.rename(columns={
            "path_fetta_primaria": "fetta_path",
            "path_grana_primaria": "grana_path",
        })
        cap_df["attributo"] = attributo

        records.append(cap_df[["fetta_path", "grana_path", "attributo", "caption", "sample_id", "anno"]])

    result = pd.concat(records, ignore_index=True)
    # rimuovi righe senza immagine trovata
    result = result[result["fetta_path"].notna() & result["grana_path"].notna()].reset_index(drop=True)
    return result
```

- [ ] **Step 4: Esegui i test per verificare che passano**

```
pytest tests/models/test_dataset.py -v
```
Atteso: 3 PASSED

- [ ] **Step 5: Crea `src/data/14_prepare_training_data.py`**

```python
# src/data/14_prepare_training_data.py
"""
Script CLI per costruire data/processed/dataset_captioning.csv.

Uso:
  python src/data/14_prepare_training_data.py

Output:
  data/processed/dataset_captioning.csv  — (fetta_path, grana_path, attributo, caption)
  reports/14_prepare_training_data.md    — statistiche
"""
import argparse
from pathlib import Path
import pandas as pd
from src.models.dataset import build_caption_index


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--captions-dir", default="data/processed/caption_per_attributo")
    parser.add_argument("--campioni-csv", default="data/processed/campioni_completi.csv")
    parser.add_argument("--codifica-csv",
                        default="07_captioning risultati grana Trentino/GT commenti liberi/codifiche/codifica_caseifici.csv")
    parser.add_argument("--out", default="data/processed/dataset_captioning.csv")
    args = parser.parse_args()

    print("Costruendo dataset index...")
    df = build_caption_index(
        captions_dir=Path(args.captions_dir),
        campioni_csv=Path(args.campioni_csv),
        codifica_csv=Path(args.codifica_csv),
    )

    Path(args.out).parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(args.out, index=False)

    # report
    report_lines = [
        "# Report: dataset_captioning.csv\n",
        f"- Righe totali: {len(df)}",
        f"- Campioni unici: {df['sample_id'].nunique()}",
        "",
        "## Per attributo",
        df.groupby("attributo").size().to_string(),
    ]
    Path("reports/14_prepare_training_data.md").write_text(
        "\n".join(report_lines), encoding="utf-8"
    )
    print(f"Salvato in {args.out}")
    print(f"Totale righe: {len(df)}")


if __name__ == "__main__":
    main()
```

- [ ] **Step 6: Esegui lo script** (richiede `codifica_caseifici.csv` — se il file è xlsx, esportalo prima come CSV)

```
python src/data/14_prepare_training_data.py
cat reports/14_prepare_training_data.md
```
Atteso: file `data/processed/dataset_captioning.csv` con ~7000–9000 righe, distribuzione per attributo.

- [ ] **Step 7: Commit**

```bash
git add src/models/__init__.py src/models/dataset.py src/data/14_prepare_training_data.py tests/models/__init__.py tests/models/test_dataset.py
git commit -m "feat: add dataset builder — build_caption_index joins captions + image paths"
```

---

## Task 2: GranaTrentinoDataset (PyTorch)

**Files:**
- Modify: `src/models/dataset.py` (aggiungi classe Dataset)
- Modify: `tests/models/test_dataset.py` (aggiungi test Dataset)

- [ ] **Step 1: Scrivi il test per GranaTrentinoDataset**

Aggiungi in fondo a `tests/models/test_dataset.py`:

```python
import torch
from PIL import Image
from src.models.dataset import GranaTrentinoDataset

def test_dataset_len(tmp_path):
    # crea immagini BMP fittizie
    for name in ["fetta.bmp", "grana.bmp"]:
        img = Image.new("RGB", (224, 224), color=(128, 64, 32))
        img.save(tmp_path / name)

    df = pd.DataFrame([
        {"fetta_path": str(tmp_path / "fetta.bmp"),
         "grana_path":  str(tmp_path / "grana.bmp"),
         "attributo": "Texture",
         "caption": "Il campione è granuloso."},
        {"fetta_path": str(tmp_path / "fetta.bmp"),
         "grana_path":  str(tmp_path / "grana.bmp"),
         "attributo": "Texture",
         "caption": "Pasta molto solubile."},
    ])
    ds = GranaTrentinoDataset(df, transform=None, tokenizer=None)
    assert len(ds) == 2

def test_dataset_getitem_returns_tensors(tmp_path):
    import torchvision.transforms as T
    for name in ["fetta.bmp", "grana.bmp"]:
        img = Image.new("RGB", (224, 224))
        img.save(tmp_path / name)

    df = pd.DataFrame([{
        "fetta_path": str(tmp_path / "fetta.bmp"),
        "grana_path":  str(tmp_path / "grana.bmp"),
        "attributo": "Texture",
        "caption": "Il campione è granuloso.",
    }])
    transform = T.Compose([T.Resize((224, 224)), T.ToTensor()])
    ds = GranaTrentinoDataset(df, transform=transform, tokenizer=None)
    fetta, grana, caption = ds[0]
    assert fetta.shape == (3, 224, 224)
    assert grana.shape == (3, 224, 224)
    assert isinstance(caption, str)
```

- [ ] **Step 2: Esegui i test per verificare che falliscono**

```
pytest tests/models/test_dataset.py::test_dataset_len -v
```
Atteso: `ImportError: cannot import name 'GranaTrentinoDataset'`

- [ ] **Step 3: Aggiungi `GranaTrentinoDataset` a `src/models/dataset.py`**

Aggiungi in fondo al file esistente:

```python
import torch
from torch.utils.data import Dataset
from PIL import Image
import torchvision.transforms as T


class GranaTrentinoDataset(Dataset):
    """
    Dataset PyTorch per image captioning Grana Trentino.

    Ogni item restituisce:
      (fetta_tensor, grana_tensor, caption_str)
    Il tokenizer (se fornito) viene applicato fuori dal Dataset,
    nel collate_fn del DataLoader.
    """

    DEFAULT_TRANSFORM = T.Compose([
        T.Resize((224, 224)),
        T.ToTensor(),
        T.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225]),
    ])

    def __init__(self, dataframe, transform=None, tokenizer=None):
        """
        Args:
            dataframe: pd.DataFrame con colonne fetta_path, grana_path, caption
            transform: torchvision transform da applicare alle immagini
            tokenizer: non usato internamente, disponibile per collate_fn esterna
        """
        self.df = dataframe.reset_index(drop=True)
        self.transform = transform if transform is not None else self.DEFAULT_TRANSFORM
        self.tokenizer = tokenizer

    def __len__(self):
        return len(self.df)

    def __getitem__(self, idx):
        row = self.df.iloc[idx]
        fetta = Image.open(row["fetta_path"]).convert("RGB")
        grana = Image.open(row["grana_path"]).convert("RGB")
        if self.transform:
            fetta = self.transform(fetta)
            grana = self.transform(grana)
        caption = str(row["caption"])
        return fetta, grana, caption
```

- [ ] **Step 4: Esegui i test**

```
pytest tests/models/test_dataset.py -v
```
Atteso: 5 PASSED (3 di Task 1 + 2 nuovi)

- [ ] **Step 5: Commit**

```bash
git add src/models/dataset.py tests/models/test_dataset.py
git commit -m "feat: add GranaTrentinoDataset PyTorch class"
```

---

## Task 3: ItalianTokenizer

**Scopo:** wrapper attorno al tokenizer di GePpeTto (`LorenzoDeMattei/GePpeTto`) che espone `encode`, `decode`, `vocab_size`, e i token speciali `<SOS>`, `<EOS>`, `<PAD>`.

**Files:**
- Create: `src/models/vocabulary.py`
- Create: `tests/models/test_vocabulary.py`

- [ ] **Step 1: Installa il pacchetto (se non già presente)**

```
pip install transformers
```

- [ ] **Step 2: Scrivi il test**

```python
# tests/models/test_vocabulary.py
import pytest
from src.models.vocabulary import ItalianTokenizer

@pytest.fixture(scope="module")
def tok():
    return ItalianTokenizer()

def test_vocab_size(tok):
    assert tok.vocab_size > 10_000

def test_encode_decode_roundtrip(tok):
    text = "Il campione è granuloso."
    ids = tok.encode(text)
    assert isinstance(ids, list)
    assert all(isinstance(i, int) for i in ids)
    decoded = tok.decode(ids)
    # la decodifica deve contenere le parole chiave
    assert "granuloso" in decoded.lower()

def test_special_tokens_exist(tok):
    assert tok.pad_id is not None
    assert tok.eos_id is not None
    assert tok.bos_id is not None

def test_encode_adds_bos_eos(tok):
    ids = tok.encode("ciao", add_special_tokens=True)
    assert ids[0] == tok.bos_id
    assert ids[-1] == tok.eos_id
```

- [ ] **Step 3: Esegui il test per verificare che fallisce**

```
pytest tests/models/test_vocabulary.py -v
```
Atteso: `ModuleNotFoundError: No module named 'src.models.vocabulary'`

- [ ] **Step 4: Implementa `src/models/vocabulary.py`**

```python
# src/models/vocabulary.py
"""
ItalianTokenizer: wrapper attorno al tokenizer GPT-2 di GePpeTto.

Usa il tokenizer pre-addestrato su italiano per avere un vocabolario
italiano consolidato. I pesi del decoder vengono comunque inizializzati
da zero (il tokenizer è solo per la tokenizzazione, non per i pesi).
"""
from transformers import AutoTokenizer


class ItalianTokenizer:
    """
    Tokenizer italiano basato su GePpeTto (GPT-2 addestrato su italiano).
    HuggingFace model: LorenzoDeMattei/GePpeTto
    """

    MODEL_NAME = "LorenzoDeMattei/GePpeTto"

    def __init__(self, model_name: str = None):
        name = model_name or self.MODEL_NAME
        self._tok = AutoTokenizer.from_pretrained(name)

        # GePpeTto non ha pad token di default: usiamo eos come pad
        if self._tok.pad_token is None:
            self._tok.add_special_tokens({"pad_token": "<PAD>"})
        if self._tok.bos_token is None:
            self._tok.add_special_tokens({"bos_token": "<SOS>"})
        if self._tok.eos_token is None:
            self._tok.add_special_tokens({"eos_token": "<EOS>"})

    @property
    def vocab_size(self) -> int:
        return len(self._tok)

    @property
    def pad_id(self) -> int:
        return self._tok.pad_token_id

    @property
    def bos_id(self) -> int:
        return self._tok.bos_token_id

    @property
    def eos_id(self) -> int:
        return self._tok.eos_token_id

    def encode(self, text: str, add_special_tokens: bool = False) -> list[int]:
        ids = self._tok.encode(text, add_special_tokens=False)
        if add_special_tokens:
            ids = [self.bos_id] + ids + [self.eos_id]
        return ids

    def decode(self, ids: list[int], skip_special_tokens: bool = True) -> str:
        return self._tok.decode(ids, skip_special_tokens=skip_special_tokens)

    def batch_encode(
        self, texts: list[str], max_length: int = 64, padding: bool = True
    ):
        """
        Tokenizza un batch di testi con padding e troncamento.
        Restituisce dict con 'input_ids' e 'attention_mask' come tensori.
        """
        return self._tok(
            texts,
            max_length=max_length,
            padding="max_length" if padding else False,
            truncation=True,
            return_tensors="pt",
        )
```

- [ ] **Step 5: Esegui i test**

```
pytest tests/models/test_vocabulary.py -v
```
Atteso: 4 PASSED (richiede download ~500MB del modello GePpeTto al primo run)

- [ ] **Step 6: Commit**

```bash
git add src/models/vocabulary.py tests/models/test_vocabulary.py
git commit -m "feat: add ItalianTokenizer wrapper around GePpeTto"
```

---

## Task 4: Encoders (CNN globale, CNN spaziale, ViT)

**Files:**
- Create: `src/models/encoders.py`
- Create: `tests/models/test_encoders.py`

- [ ] **Step 1: Scrivi i test**

```python
# tests/models/test_encoders.py
import torch
import pytest
from src.models.encoders import CNNEncoderGlobal, CNNEncoderSpatial, ViTEncoder

B = 2  # batch size
IMG = torch.randn(B, 3, 224, 224)  # due immagini fittizie

def test_cnn_global_output_shape():
    enc = CNNEncoderGlobal(embed_dim=512, frozen=True)
    out = enc(IMG)
    # output: (B, embed_dim)
    assert out.shape == (B, 512)

def test_cnn_spatial_output_shape():
    enc = CNNEncoderSpatial(embed_dim=512, frozen=True)
    out = enc(IMG)
    # output: (B, n_regions, embed_dim) dove n_regions = 49
    assert out.shape == (B, 49, 512)

def test_vit_output_shape():
    enc = ViTEncoder(embed_dim=512, frozen=True)
    out = enc(IMG)
    # output: (B, n_patches, embed_dim) dove n_patches = 196
    assert out.shape == (B, 196, 512)
```

- [ ] **Step 2: Esegui il test per verificare che fallisce**

```
pytest tests/models/test_encoders.py -v
```
Atteso: `ModuleNotFoundError: No module named 'src.models.encoders'`

- [ ] **Step 3: Implementa `src/models/encoders.py`**

```python
# src/models/encoders.py
import torch
import torch.nn as nn
import torchvision.models as tvm
import timm


class CNNEncoderGlobal(nn.Module):
    """
    Encoder CNN che produce un singolo vettore globale per immagine.
    Usato da M1 (CNN+LSTM).

    Architettura: ResNet-50 pre-trained → global avg pool → Linear(2048, embed_dim)
    """

    def __init__(self, embed_dim: int = 512, frozen: bool = True):
        super().__init__()
        resnet = tvm.resnet50(weights=tvm.ResNet50_Weights.IMAGENET1K_V2)
        # rimuovi l'ultimo layer di classificazione
        self.backbone = nn.Sequential(*list(resnet.children())[:-1])  # → (B, 2048, 1, 1)
        self.proj = nn.Linear(2048, embed_dim)

        if frozen:
            for p in self.backbone.parameters():
                p.requires_grad = False

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        """
        Args:
            x: (B, 3, 224, 224)
        Returns:
            (B, embed_dim)
        """
        feat = self.backbone(x)          # (B, 2048, 1, 1)
        feat = feat.flatten(1)           # (B, 2048)
        return self.proj(feat)           # (B, embed_dim)


class CNNEncoderSpatial(nn.Module):
    """
    Encoder CNN che produce una griglia spaziale di feature.
    Usato da M2 (CNN+Transformer decoder).

    Architettura: ResNet-50 → layer4 output → flatten → Linear(2048, embed_dim)
    Output: 49 vettori (griglia 7×7) per immagine.
    """

    def __init__(self, embed_dim: int = 512, frozen: bool = True):
        super().__init__()
        resnet = tvm.resnet50(weights=tvm.ResNet50_Weights.IMAGENET1K_V2)
        # prendi fino a layer4 (esclusi avgpool e fc)
        self.backbone = nn.Sequential(*list(resnet.children())[:-2])  # → (B, 2048, 7, 7)
        self.proj = nn.Linear(2048, embed_dim)

        if frozen:
            for p in self.backbone.parameters():
                p.requires_grad = False

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        """
        Args:
            x: (B, 3, 224, 224)
        Returns:
            (B, 49, embed_dim)
        """
        feat = self.backbone(x)               # (B, 2048, 7, 7)
        B, C, H, W = feat.shape
        feat = feat.permute(0, 2, 3, 1)       # (B, 7, 7, 2048)
        feat = feat.reshape(B, H * W, C)      # (B, 49, 2048)
        return self.proj(feat)                # (B, 49, embed_dim)


class ViTEncoder(nn.Module):
    """
    Encoder Vision Transformer che produce una sequenza di patch tokens.
    Usato da M3 (ViT+Transformer decoder).

    Architettura: ViT-B/16 pre-trained (ImageNet-21k) → 196 patch tokens
    I primi (frozen_layers) layer sono congelati, gli ultimi sono trainabili.
    """

    def __init__(self, embed_dim: int = 512, frozen: bool = True, trainable_layers: int = 4):
        super().__init__()
        self.vit = timm.create_model(
            "vit_base_patch16_224",
            pretrained=True,
            num_classes=0,   # rimuovi classification head
        )
        self.proj = nn.Linear(768, embed_dim)  # ViT-B/16 → dim 768

        if frozen:
            # congela tutto il ViT
            for p in self.vit.parameters():
                p.requires_grad = False
            # scongela gli ultimi trainable_layers blocchi
            n_blocks = len(self.vit.blocks)
            for block in self.vit.blocks[n_blocks - trainable_layers:]:
                for p in block.parameters():
                    p.requires_grad = True
            # scongela sempre la norm finale
            for p in self.vit.norm.parameters():
                p.requires_grad = True

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        """
        Args:
            x: (B, 3, 224, 224)
        Returns:
            (B, 196, embed_dim)  — patch tokens, CLS token escluso
        """
        # forward_features restituisce (B, n_tokens, 768)
        # il primo token è il CLS token → lo escludiamo
        feats = self.vit.forward_features(x)  # (B, 197, 768)
        patch_feats = feats[:, 1:, :]          # (B, 196, 768) — escludi CLS
        return self.proj(patch_feats)          # (B, 196, embed_dim)
```

- [ ] **Step 4: Installa timm**

```
pip install timm
```

- [ ] **Step 5: Esegui i test**

```
pytest tests/models/test_encoders.py -v
```
Atteso: 3 PASSED (richiede download modelli al primo run)

- [ ] **Step 6: Commit**

```bash
git add src/models/encoders.py tests/models/test_encoders.py
git commit -m "feat: add CNN and ViT encoders (global, spatial, patch)"
```

---

## Task 5: Decoders (LSTM e Transformer)

**Files:**
- Create: `src/models/decoders.py`
- Create: `tests/models/test_decoders.py`

- [ ] **Step 1: Scrivi i test**

```python
# tests/models/test_decoders.py
import torch
import pytest
from src.models.decoders import LSTMDecoder, TransformerDecoder

VOCAB_SIZE = 1000
EMBED_DIM = 512
B = 2
SEQ_LEN = 10

def test_lstm_decoder_output_shape():
    dec = LSTMDecoder(vocab_size=VOCAB_SIZE, embed_dim=256, hidden_dim=EMBED_DIM)
    visual_feat = torch.randn(B, EMBED_DIM)   # feature globale da CNN (M1)
    captions = torch.randint(0, VOCAB_SIZE, (B, SEQ_LEN))
    logits = dec(visual_feat, captions)
    # output: (B, SEQ_LEN, VOCAB_SIZE)
    assert logits.shape == (B, SEQ_LEN, VOCAB_SIZE)

def test_transformer_decoder_output_shape():
    dec = TransformerDecoder(vocab_size=VOCAB_SIZE, embed_dim=EMBED_DIM,
                              n_heads=8, n_layers=4, ffn_dim=2048)
    visual_tokens = torch.randn(B, 49, EMBED_DIM)   # feature spaziali da CNN (M2)
    captions = torch.randint(0, VOCAB_SIZE, (B, SEQ_LEN))
    logits = dec(visual_tokens, captions)
    # output: (B, SEQ_LEN, VOCAB_SIZE)
    assert logits.shape == (B, SEQ_LEN, VOCAB_SIZE)

def test_transformer_decoder_with_vit_tokens():
    dec = TransformerDecoder(vocab_size=VOCAB_SIZE, embed_dim=EMBED_DIM,
                              n_heads=8, n_layers=4, ffn_dim=2048)
    visual_tokens = torch.randn(B, 196, EMBED_DIM)   # patch tokens da ViT (M3)
    captions = torch.randint(0, VOCAB_SIZE, (B, SEQ_LEN))
    logits = dec(visual_tokens, captions)
    assert logits.shape == (B, SEQ_LEN, VOCAB_SIZE)
```

- [ ] **Step 2: Esegui il test per verificare che fallisce**

```
pytest tests/models/test_decoders.py -v
```
Atteso: `ModuleNotFoundError: No module named 'src.models.decoders'`

- [ ] **Step 3: Implementa `src/models/decoders.py`**

```python
# src/models/decoders.py
import math
import torch
import torch.nn as nn


class LSTMDecoder(nn.Module):
    """
    Decoder LSTM per M1 (CNN+LSTM, nessuna attention).

    L'immagine viene iniettata come hidden state iniziale dell'LSTM.
    Ad ogni step riceve l'embedding della parola precedente.
    """

    def __init__(self, vocab_size: int, embed_dim: int = 256, hidden_dim: int = 512):
        super().__init__()
        self.embedding = nn.Embedding(vocab_size, embed_dim)
        self.lstm = nn.LSTM(embed_dim, hidden_dim, batch_first=True)
        self.fc_out = nn.Linear(hidden_dim, vocab_size)
        # proiezione: feature visiva → hidden state iniziale LSTM
        self.visual_to_hidden = nn.Linear(hidden_dim, hidden_dim)
        self.visual_to_cell = nn.Linear(hidden_dim, hidden_dim)

    def forward(
        self,
        visual_feat: torch.Tensor,
        captions: torch.Tensor,
    ) -> torch.Tensor:
        """
        Args:
            visual_feat: (B, hidden_dim) — vettore globale dalla CNN
            captions:    (B, seq_len) — indici parole (teacher forcing)
        Returns:
            logits: (B, seq_len, vocab_size)
        """
        h0 = self.visual_to_hidden(visual_feat).unsqueeze(0)   # (1, B, H)
        c0 = self.visual_to_cell(visual_feat).unsqueeze(0)     # (1, B, H)
        embeds = self.embedding(captions)                       # (B, seq_len, E)
        out, _ = self.lstm(embeds, (h0, c0))                   # (B, seq_len, H)
        return self.fc_out(out)                                 # (B, seq_len, V)


class TransformerDecoder(nn.Module):
    """
    Decoder Transformer per M2 (CNN+Transformer) e M3 (ViT+Transformer).

    Usa nn.TransformerDecoder di PyTorch: self-attention sulle parole +
    cross-attention sui visual tokens. Funziona con qualsiasi numero di
    visual tokens (49 per CNN spaziale, 196/392 per ViT).
    """

    def __init__(
        self,
        vocab_size: int,
        embed_dim: int = 512,
        n_heads: int = 8,
        n_layers: int = 4,
        ffn_dim: int = 2048,
        max_len: int = 128,
        dropout: float = 0.1,
    ):
        super().__init__()
        self.embed_dim = embed_dim
        self.embedding = nn.Embedding(vocab_size, embed_dim)
        self.pos_encoding = _PositionalEncoding(embed_dim, max_len, dropout)

        decoder_layer = nn.TransformerDecoderLayer(
            d_model=embed_dim,
            nhead=n_heads,
            dim_feedforward=ffn_dim,
            dropout=dropout,
            batch_first=True,
        )
        self.transformer_decoder = nn.TransformerDecoder(decoder_layer, num_layers=n_layers)
        self.fc_out = nn.Linear(embed_dim, vocab_size)

    def forward(
        self,
        visual_tokens: torch.Tensor,
        captions: torch.Tensor,
    ) -> torch.Tensor:
        """
        Args:
            visual_tokens: (B, n_visual, embed_dim) — da CNN spaziale o ViT
            captions:      (B, seq_len) — indici parole (teacher forcing)
        Returns:
            logits: (B, seq_len, vocab_size)
        """
        seq_len = captions.size(1)
        # causal mask: impedisce di vedere parole future
        causal_mask = nn.Transformer.generate_square_subsequent_mask(
            seq_len, device=captions.device
        )
        embeds = self.pos_encoding(
            self.embedding(captions) * math.sqrt(self.embed_dim)
        )  # (B, seq_len, embed_dim)

        out = self.transformer_decoder(
            tgt=embeds,
            memory=visual_tokens,
            tgt_mask=causal_mask,
        )  # (B, seq_len, embed_dim)
        return self.fc_out(out)  # (B, seq_len, vocab_size)


class _PositionalEncoding(nn.Module):
    def __init__(self, embed_dim: int, max_len: int, dropout: float):
        super().__init__()
        self.dropout = nn.Dropout(dropout)
        pe = torch.zeros(max_len, embed_dim)
        pos = torch.arange(max_len).unsqueeze(1)
        div = torch.exp(torch.arange(0, embed_dim, 2) * (-math.log(10000.0) / embed_dim))
        pe[:, 0::2] = torch.sin(pos * div)
        pe[:, 1::2] = torch.cos(pos * div)
        self.register_buffer("pe", pe.unsqueeze(0))  # (1, max_len, embed_dim)

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        x = x + self.pe[:, : x.size(1)]
        return self.dropout(x)
```

- [ ] **Step 4: Esegui i test**

```
pytest tests/models/test_decoders.py -v
```
Atteso: 3 PASSED

- [ ] **Step 5: Commit**

```bash
git add src/models/decoders.py tests/models/test_decoders.py
git commit -m "feat: add LSTMDecoder and TransformerDecoder"
```

---

## Task 6: Tre model assemblies

**Files:**
- Create: `src/models/models.py`
- Create: `tests/models/test_models.py`

- [ ] **Step 1: Scrivi i test**

```python
# tests/models/test_models.py
import torch
import pytest
from src.models.models import CnnLstm, CnnTransformer, ViTTransformer

B, SEQ_LEN, VOCAB_SIZE = 2, 10, 1000
FETTA = torch.randn(B, 3, 224, 224)
GRANA = torch.randn(B, 3, 224, 224)
CAPTIONS = torch.randint(0, VOCAB_SIZE, (B, SEQ_LEN))


def test_cnn_lstm_forward():
    model = CnnLstm(vocab_size=VOCAB_SIZE, embed_dim=256, hidden_dim=512, frozen_encoder=True)
    logits = model(FETTA, GRANA, CAPTIONS)
    assert logits.shape == (B, SEQ_LEN, VOCAB_SIZE)


def test_cnn_transformer_forward():
    model = CnnTransformer(vocab_size=VOCAB_SIZE, embed_dim=512, frozen_encoder=True)
    logits = model(FETTA, GRANA, CAPTIONS)
    assert logits.shape == (B, SEQ_LEN, VOCAB_SIZE)


def test_vit_transformer_forward():
    model = ViTTransformer(vocab_size=VOCAB_SIZE, embed_dim=512, frozen_encoder=True)
    logits = model(FETTA, GRANA, CAPTIONS)
    assert logits.shape == (B, SEQ_LEN, VOCAB_SIZE)
```

- [ ] **Step 2: Esegui il test per verificare che fallisce**

```
pytest tests/models/test_models.py -v
```
Atteso: `ModuleNotFoundError: No module named 'src.models.models'`

- [ ] **Step 3: Implementa `src/models/models.py`**

```python
# src/models/models.py
import torch
import torch.nn as nn
from src.models.encoders import CNNEncoderGlobal, CNNEncoderSpatial, ViTEncoder
from src.models.decoders import LSTMDecoder, TransformerDecoder


class CnnLstm(nn.Module):
    """
    M1 — CNN + LSTM (Show and Tell).
    Encoder: ResNet-50 globale (una feature per immagine).
    Fusione FETTA+GRANA: concatenazione → proiezione lineare.
    Decoder: LSTM, feature visiva come hidden state iniziale.
    """

    def __init__(
        self,
        vocab_size: int,
        embed_dim: int = 256,
        hidden_dim: int = 512,
        frozen_encoder: bool = True,
    ):
        super().__init__()
        self.encoder = CNNEncoderGlobal(embed_dim=hidden_dim, frozen=frozen_encoder)
        # fusione: concat(fetta, grana) → proiezione a hidden_dim
        self.fusion = nn.Linear(hidden_dim * 2, hidden_dim)
        self.decoder = LSTMDecoder(vocab_size=vocab_size, embed_dim=embed_dim, hidden_dim=hidden_dim)

    def forward(
        self,
        fetta: torch.Tensor,
        grana: torch.Tensor,
        captions: torch.Tensor,
    ) -> torch.Tensor:
        """
        Args:
            fetta, grana: (B, 3, 224, 224)
            captions: (B, seq_len)
        Returns:
            logits: (B, seq_len, vocab_size)
        """
        f_feat = self.encoder(fetta)                         # (B, hidden_dim)
        g_feat = self.encoder(grana)                         # (B, hidden_dim)
        visual = self.fusion(torch.cat([f_feat, g_feat], dim=1))  # (B, hidden_dim)
        return self.decoder(visual, captions)


class CnnTransformer(nn.Module):
    """
    M2 — CNN + Transformer Decoder.
    Encoder: ResNet-50 spaziale (49 visual tokens per immagine).
    Fusione FETTA+GRANA: concatenazione → 98 visual tokens.
    Decoder: Transformer con cross-attention sui 98 tokens.
    """

    def __init__(
        self,
        vocab_size: int,
        embed_dim: int = 512,
        n_heads: int = 8,
        n_layers: int = 4,
        frozen_encoder: bool = True,
    ):
        super().__init__()
        self.encoder = CNNEncoderSpatial(embed_dim=embed_dim, frozen=frozen_encoder)
        self.decoder = TransformerDecoder(
            vocab_size=vocab_size,
            embed_dim=embed_dim,
            n_heads=n_heads,
            n_layers=n_layers,
        )

    def forward(
        self,
        fetta: torch.Tensor,
        grana: torch.Tensor,
        captions: torch.Tensor,
    ) -> torch.Tensor:
        f_tokens = self.encoder(fetta)                                  # (B, 49, D)
        g_tokens = self.encoder(grana)                                  # (B, 49, D)
        visual_tokens = torch.cat([f_tokens, g_tokens], dim=1)         # (B, 98, D)
        return self.decoder(visual_tokens, captions)


class ViTTransformer(nn.Module):
    """
    M3 — ViT + Transformer Decoder (CPTR-like).
    Encoder: ViT-B/16 (196 patch tokens per immagine).
    Fusione FETTA+GRANA: concatenazione → 392 visual tokens.
    Decoder: Transformer con cross-attention sui 392 patch tokens.
    """

    def __init__(
        self,
        vocab_size: int,
        embed_dim: int = 512,
        n_heads: int = 8,
        n_layers: int = 4,
        frozen_encoder: bool = True,
        trainable_vit_layers: int = 4,
    ):
        super().__init__()
        self.encoder = ViTEncoder(
            embed_dim=embed_dim,
            frozen=frozen_encoder,
            trainable_layers=trainable_vit_layers,
        )
        self.decoder = TransformerDecoder(
            vocab_size=vocab_size,
            embed_dim=embed_dim,
            n_heads=n_heads,
            n_layers=n_layers,
        )

    def forward(
        self,
        fetta: torch.Tensor,
        grana: torch.Tensor,
        captions: torch.Tensor,
    ) -> torch.Tensor:
        f_tokens = self.encoder(fetta)                                  # (B, 196, D)
        g_tokens = self.encoder(grana)                                  # (B, 196, D)
        visual_tokens = torch.cat([f_tokens, g_tokens], dim=1)         # (B, 392, D)
        return self.decoder(visual_tokens, captions)
```

- [ ] **Step 4: Esegui i test**

```
pytest tests/models/test_models.py -v
```
Atteso: 3 PASSED

- [ ] **Step 5: Commit**

```bash
git add src/models/models.py tests/models/test_models.py
git commit -m "feat: add CnnLstm, CnnTransformer, ViTTransformer model classes"
```

---

## Task 7: Training loop

**Files:**
- Create: `src/models/train.py`
- Create: `tests/models/test_train.py`

- [ ] **Step 1: Scrivi il test (integrazione leggera con dati fittizi)**

```python
# tests/models/test_train.py
import torch
import pytest
import pandas as pd
from PIL import Image
from src.models.train import train_model
from src.models.models import CnnLstm
from src.models.vocabulary import ItalianTokenizer

@pytest.fixture(scope="module")
def tok():
    return ItalianTokenizer()

def test_train_model_runs_without_error(tmp_path, tok):
    # crea 4 immagini fittizie
    for name in ["f1.bmp", "g1.bmp", "f2.bmp", "g2.bmp"]:
        Image.new("RGB", (224, 224)).save(tmp_path / name)

    df = pd.DataFrame([
        {"fetta_path": str(tmp_path / "f1.bmp"), "grana_path": str(tmp_path / "g1.bmp"),
         "attributo": "Texture", "caption": "Il campione è granuloso."},
        {"fetta_path": str(tmp_path / "f2.bmp"), "grana_path": str(tmp_path / "g2.bmp"),
         "attributo": "Texture", "caption": "Pasta compatta e solubile."},
    ])

    model = CnnLstm(vocab_size=tok.vocab_size, embed_dim=64, hidden_dim=128, frozen_encoder=True)
    history = train_model(
        model=model,
        train_df=df,
        val_df=df,
        tokenizer=tok,
        epochs=1,
        batch_size=2,
        lr=1e-3,
        device="cpu",
        checkpoint_dir=tmp_path / "checkpoints",
        max_caption_len=20,
    )
    assert "train_loss" in history
    assert len(history["train_loss"]) == 1
```

- [ ] **Step 2: Esegui il test per verificare che fallisce**

```
pytest tests/models/test_train.py -v
```
Atteso: `ModuleNotFoundError: No module named 'src.models.train'`

- [ ] **Step 3: Implementa `src/models/train.py`**

```python
# src/models/train.py
import torch
import torch.nn as nn
from torch.utils.data import DataLoader
from pathlib import Path
import pandas as pd
from tqdm import tqdm
from src.models.dataset import GranaTrentinoDataset
from src.models.vocabulary import ItalianTokenizer


def _collate_fn(batch, tokenizer: ItalianTokenizer, max_caption_len: int):
    """
    Collate function per il DataLoader.
    Tokenizza le caption e crea i tensori input/target con teacher forcing.
    """
    fettas, granas, captions = zip(*batch)
    fettas = torch.stack(fettas)
    granas = torch.stack(granas)

    # tokenizza con BOS/EOS + padding
    encoded = tokenizer.batch_encode(
        list(captions),
        max_length=max_caption_len + 1,
        padding=True,
    )
    ids = encoded["input_ids"]  # (B, max_len+1)

    # teacher forcing: input = ids[:, :-1], target = ids[:, 1:]
    caption_input = ids[:, :-1]   # (B, max_len)
    caption_target = ids[:, 1:]   # (B, max_len)

    return fettas, granas, caption_input, caption_target


def train_one_epoch(model, loader, optimizer, criterion, device):
    model.train()
    total_loss = 0.0
    for fetta, grana, cap_in, cap_tgt in loader:
        fetta, grana = fetta.to(device), grana.to(device)
        cap_in, cap_tgt = cap_in.to(device), cap_tgt.to(device)

        optimizer.zero_grad()
        logits = model(fetta, grana, cap_in)        # (B, seq_len, vocab_size)
        B, S, V = logits.shape
        loss = criterion(logits.reshape(B * S, V), cap_tgt.reshape(B * S))
        loss.backward()
        torch.nn.utils.clip_grad_norm_(model.parameters(), max_norm=1.0)
        optimizer.step()
        total_loss += loss.item()
    return total_loss / len(loader)


def evaluate_epoch(model, loader, criterion, device):
    model.eval()
    total_loss = 0.0
    with torch.no_grad():
        for fetta, grana, cap_in, cap_tgt in loader:
            fetta, grana = fetta.to(device), grana.to(device)
            cap_in, cap_tgt = cap_in.to(device), cap_tgt.to(device)
            logits = model(fetta, grana, cap_in)
            B, S, V = logits.shape
            loss = criterion(logits.reshape(B * S, V), cap_tgt.reshape(B * S))
            total_loss += loss.item()
    return total_loss / len(loader)


def train_model(
    model: nn.Module,
    train_df: pd.DataFrame,
    val_df: pd.DataFrame,
    tokenizer: ItalianTokenizer,
    epochs: int = 20,
    batch_size: int = 32,
    lr: float = 1e-4,
    device: str = "cuda",
    checkpoint_dir: Path = Path("models/checkpoints"),
    max_caption_len: int = 64,
) -> dict:
    """
    Addestra il modello e salva il checkpoint migliore (val loss).

    Restituisce dict con history: {'train_loss': [...], 'val_loss': [...]}
    """
    checkpoint_dir = Path(checkpoint_dir)
    checkpoint_dir.mkdir(parents=True, exist_ok=True)
    device = torch.device(device if torch.cuda.is_available() else "cpu")
    model = model.to(device)

    collate = lambda b: _collate_fn(b, tokenizer, max_caption_len)
    train_ds = GranaTrentinoDataset(train_df)
    val_ds = GranaTrentinoDataset(val_df)
    train_loader = DataLoader(train_ds, batch_size=batch_size, shuffle=True,
                              collate_fn=collate, num_workers=2, pin_memory=True)
    val_loader = DataLoader(val_ds, batch_size=batch_size, shuffle=False,
                            collate_fn=collate, num_workers=2, pin_memory=True)

    optimizer = torch.optim.Adam(
        filter(lambda p: p.requires_grad, model.parameters()), lr=lr
    )
    scheduler = torch.optim.lr_scheduler.ReduceLROnPlateau(optimizer, patience=3, factor=0.5)
    criterion = nn.CrossEntropyLoss(ignore_index=tokenizer.pad_id)

    history = {"train_loss": [], "val_loss": []}
    best_val_loss = float("inf")

    for epoch in range(1, epochs + 1):
        train_loss = train_one_epoch(model, train_loader, optimizer, criterion, device)
        val_loss = evaluate_epoch(model, val_loader, criterion, device)
        scheduler.step(val_loss)

        history["train_loss"].append(train_loss)
        history["val_loss"].append(val_loss)
        print(f"Epoch {epoch:03d} | train_loss={train_loss:.4f} | val_loss={val_loss:.4f}")

        if val_loss < best_val_loss:
            best_val_loss = val_loss
            torch.save(model.state_dict(), checkpoint_dir / "best_model.pt")

    return history
```

- [ ] **Step 4: Esegui il test**

```
pytest tests/models/test_train.py -v
```
Atteso: 1 PASSED

- [ ] **Step 5: Commit**

```bash
git add src/models/train.py tests/models/test_train.py
git commit -m "feat: add training loop with teacher forcing, checkpointing, lr scheduler"
```

---

## Task 8: Metriche di valutazione

**Files:**
- Create: `src/models/metrics.py`
- Create: `tests/models/test_metrics.py`

- [ ] **Step 1: Installa la libreria metriche**

```
pip install evaluate rouge-score
```

_(pycocoevalcap può avere problemi su Windows; usiamo `evaluate` di HuggingFace come alternativa più stabile)_

- [ ] **Step 2: Scrivi il test**

```python
# tests/models/test_metrics.py
import pytest
from src.models.metrics import compute_nlg_metrics

def test_perfect_prediction():
    refs = ["Il campione è granuloso e solubile."]
    hyps = ["Il campione è granuloso e solubile."]
    scores = compute_nlg_metrics(hypotheses=hyps, references=refs)
    assert scores["bleu"] > 0.99
    assert scores["rouge_l"] > 0.99

def test_empty_overlap():
    refs = ["Il campione è granuloso."]
    hyps = ["Pasta molto compatta e friabile."]
    scores = compute_nlg_metrics(hypotheses=hyps, references=refs)
    assert scores["bleu"] < 0.3

def test_returns_all_metrics(tmp_path):
    refs = ["Testo di riferimento per il test."]
    hyps = ["Testo di test per riferimento."]
    scores = compute_nlg_metrics(hypotheses=hyps, references=refs)
    assert set(["bleu", "meteor", "rouge_l"]).issubset(scores.keys())
```

- [ ] **Step 3: Esegui il test per verificare che fallisce**

```
pytest tests/models/test_metrics.py -v
```
Atteso: `ModuleNotFoundError: No module named 'src.models.metrics'`

- [ ] **Step 4: Implementa `src/models/metrics.py`**

```python
# src/models/metrics.py
"""
Metriche NLG per valutare le caption generate.
Usa la libreria `evaluate` di HuggingFace (più stabile su Windows di pycocoevalcap).

Metriche calcolate:
  - BLEU (corpus-level, sacrebleu)
  - METEOR
  - ROUGE-L
"""
import evaluate as hf_evaluate
import torch
from torch.utils.data import DataLoader

# lazy loading per evitare download al import
_BLEU = None
_METEOR = None
_ROUGE = None


def _get_metrics():
    global _BLEU, _METEOR, _ROUGE
    if _BLEU is None:
        _BLEU   = hf_evaluate.load("sacrebleu")
        _METEOR = hf_evaluate.load("meteor")
        _ROUGE  = hf_evaluate.load("rouge")
    return _BLEU, _METEOR, _ROUGE


def compute_nlg_metrics(
    hypotheses: list[str],
    references: list[str],
) -> dict[str, float]:
    """
    Calcola BLEU, METEOR e ROUGE-L tra ipotesi e riferimenti.

    Args:
        hypotheses: lista di caption generate dal modello
        references:  lista di caption di riferimento (ground truth)
    Returns:
        dict con chiavi 'bleu', 'meteor', 'rouge_l'
    """
    bleu_m, meteor_m, rouge_m = _get_metrics()

    # sacrebleu vuole references come lista di liste
    bleu_score = bleu_m.compute(
        predictions=hypotheses,
        references=[[r] for r in references],
    )["score"] / 100.0  # normalizza da 0-100 a 0-1

    meteor_score = meteor_m.compute(
        predictions=hypotheses,
        references=references,
    )["meteor"]

    rouge_score = rouge_m.compute(
        predictions=hypotheses,
        references=references,
    )["rougeL"]

    return {
        "bleu":    round(bleu_score, 4),
        "meteor":  round(meteor_score, 4),
        "rouge_l": round(rouge_score, 4),
    }


def generate_caption(
    model,
    fetta: torch.Tensor,
    grana: torch.Tensor,
    tokenizer,
    max_len: int = 64,
    device: str = "cpu",
) -> str:
    """
    Genera una caption per una coppia di immagini usando greedy decoding.

    Args:
        model: CnnLstm / CnnTransformer / ViTTransformer
        fetta, grana: tensori (1, 3, 224, 224) già normalizzati
        tokenizer: ItalianTokenizer
        max_len: lunghezza massima caption generata
        device: 'cpu' o 'cuda'
    Returns:
        stringa caption generata
    """
    model.eval()
    device = torch.device(device)
    model = model.to(device)
    fetta = fetta.to(device)
    grana = grana.to(device)

    generated = [tokenizer.bos_id]

    with torch.no_grad():
        for _ in range(max_len):
            cap_tensor = torch.tensor([generated], device=device)   # (1, t)
            logits = model(fetta, grana, cap_tensor)                 # (1, t, V)
            next_id = logits[0, -1].argmax().item()
            generated.append(next_id)
            if next_id == tokenizer.eos_id:
                break

    return tokenizer.decode(generated[1:])  # escludi BOS
```

- [ ] **Step 5: Esegui i test**

```
pytest tests/models/test_metrics.py -v
```
Atteso: 3 PASSED

- [ ] **Step 6: Commit**

```bash
git add src/models/metrics.py tests/models/test_metrics.py
git commit -m "feat: add NLG evaluation metrics (BLEU, METEOR, ROUGE-L)"
```

---

## Task 9: Script training + run M1 (pilota su Texture)

**Scopo:** script CLI unificato per addestrare un modello su un attributo specifico. Prima esecuzione reale con M1 su Texture (dataset più grande, ~945 caption).

**Files:**
- Create: `src/data/15_train_captioning_model.py`

- [ ] **Step 1: Crea lo script CLI**

```python
# src/data/15_train_captioning_model.py
"""
Script per addestrare un modello di image captioning.

Uso:
  python src/data/15_train_captioning_model.py \\
      --model m1 \\
      --attributo Texture \\
      --epochs 20 \\
      --batch-size 16 \\
      --lr 1e-4 \\
      --device cuda

Modelli disponibili: m1 (CNN+LSTM), m2 (CNN+Transformer), m3 (ViT+Transformer)
"""
import argparse
import json
from pathlib import Path
import pandas as pd
import torch
from sklearn.model_selection import train_test_split

from src.models.vocabulary import ItalianTokenizer
from src.models.models import CnnLstm, CnnTransformer, ViTTransformer
from src.models.train import train_model
from src.models.metrics import compute_nlg_metrics, generate_caption
from src.models.dataset import GranaTrentinoDataset
import torchvision.transforms as T


MODEL_CLASSES = {
    "m1": CnnLstm,
    "m2": CnnTransformer,
    "m3": ViTTransformer,
}

AUGMENT_TRANSFORM = T.Compose([
    T.RandomResizedCrop(224, scale=(0.8, 1.0)),
    T.RandomHorizontalFlip(),
    T.ColorJitter(brightness=0.2, contrast=0.2, saturation=0.1),
    T.ToTensor(),
    T.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225]),
])


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--model",     choices=["m1", "m2", "m3"], required=True)
    parser.add_argument("--attributo", default="Texture")
    parser.add_argument("--dataset-csv", default="data/processed/dataset_captioning.csv")
    parser.add_argument("--epochs",    type=int, default=20)
    parser.add_argument("--batch-size",type=int, default=16)
    parser.add_argument("--lr",        type=float, default=1e-4)
    parser.add_argument("--device",    default="cuda")
    parser.add_argument("--max-len",   type=int, default=64)
    args = parser.parse_args()

    print(f"Caricamento dataset: {args.dataset_csv}")
    df = pd.read_csv(args.dataset_csv)
    df = df[df["attributo"] == args.attributo].reset_index(drop=True)
    print(f"Righe per {args.attributo}: {len(df)}")

    # split stratificato per sample_id (nessun campione in train E val)
    sample_ids = df["sample_id"].unique()
    train_ids, val_ids = train_test_split(sample_ids, test_size=0.15, random_state=42)
    test_ids = val_ids[:len(val_ids)//2]
    val_ids  = val_ids[len(val_ids)//2:]

    train_df = df[df["sample_id"].isin(train_ids)].reset_index(drop=True)
    val_df   = df[df["sample_id"].isin(val_ids)].reset_index(drop=True)
    test_df  = df[df["sample_id"].isin(test_ids)].reset_index(drop=True)
    print(f"Train: {len(train_df)} | Val: {len(val_df)} | Test: {len(test_df)}")

    tokenizer = ItalianTokenizer()
    print(f"Vocabolario: {tokenizer.vocab_size} token")

    ModelClass = MODEL_CLASSES[args.model]
    model = ModelClass(vocab_size=tokenizer.vocab_size, frozen_encoder=True)

    checkpoint_dir = Path(f"models/{args.model}_{args.attributo}")
    history = train_model(
        model=model,
        train_df=train_df,
        val_df=val_df,
        tokenizer=tokenizer,
        epochs=args.epochs,
        batch_size=args.batch_size,
        lr=args.lr,
        device=args.device,
        checkpoint_dir=checkpoint_dir,
        max_caption_len=args.max_len,
    )

    # salva history
    with open(checkpoint_dir / "history.json", "w") as f:
        json.dump(history, f, indent=2)

    print(f"\nTraining completato. Checkpoint in: {checkpoint_dir}")
    print(f"Best val_loss: {min(history['val_loss']):.4f}")


if __name__ == "__main__":
    main()
```

- [ ] **Step 2: Esegui il dataset builder se non già fatto**

```
python src/data/14_prepare_training_data.py
```

- [ ] **Step 3: Esegui il training M1 su Texture (pilota)**

```
python src/data/15_train_captioning_model.py --model m1 --attributo Texture --epochs 20 --batch-size 16 --device cpu
```
Su GPU:
```
python src/data/15_train_captioning_model.py --model m1 --attributo Texture --epochs 20 --batch-size 32 --device cuda
```
Atteso: training loss scende nel corso delle epoche; file `models/m1_Texture/best_model.pt` creato.

- [ ] **Step 4: Commit**

```bash
git add src/data/15_train_captioning_model.py
git commit -m "feat: add training CLI script, run M1 pilot on Texture attribute"
```

---

## Task 10: Run M2 e M3 + script di confronto

**Files:**
- Create: `src/data/16_evaluate_and_compare.py`

- [ ] **Step 1: Addestra M2**

```
python src/data/15_train_captioning_model.py --model m2 --attributo Texture --epochs 20 --batch-size 16 --device cuda
```

- [ ] **Step 2: Addestra M3** (consigliato su Colab per VRAM)

```
python src/data/15_train_captioning_model.py --model m3 --attributo Texture --epochs 20 --batch-size 8 --device cuda
```

- [ ] **Step 3: Crea lo script di confronto**

```python
# src/data/16_evaluate_and_compare.py
"""
Carica i tre modelli addestrati e genera il report di confronto.

Uso:
  python src/data/16_evaluate_and_compare.py --attributo Texture
"""
import argparse
import json
from pathlib import Path
import pandas as pd
import torch
from sklearn.model_selection import train_test_split
import torchvision.transforms as T
from PIL import Image

from src.models.vocabulary import ItalianTokenizer
from src.models.models import CnnLstm, CnnTransformer, ViTTransformer
from src.models.metrics import compute_nlg_metrics, generate_caption


EVAL_TRANSFORM = T.Compose([
    T.Resize((224, 224)),
    T.ToTensor(),
    T.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225]),
])

MODEL_CLASSES = {"m1": CnnLstm, "m2": CnnTransformer, "m3": ViTTransformer}


def load_model(model_key: str, attributo: str, tokenizer: ItalianTokenizer, device):
    ModelClass = MODEL_CLASSES[model_key]
    model = ModelClass(vocab_size=tokenizer.vocab_size, frozen_encoder=False)
    ckpt = Path(f"models/{model_key}_{attributo}/best_model.pt")
    model.load_state_dict(torch.load(ckpt, map_location=device))
    model = model.to(device)
    model.eval()
    return model


def evaluate_model(model, test_df: pd.DataFrame, tokenizer, device) -> dict:
    hyps, refs = [], []
    for _, row in test_df.iterrows():
        fetta = EVAL_TRANSFORM(Image.open(row["fetta_path"]).convert("RGB")).unsqueeze(0)
        grana = EVAL_TRANSFORM(Image.open(row["grana_path"]).convert("RGB")).unsqueeze(0)
        caption = generate_caption(model, fetta, grana, tokenizer, device=str(device))
        hyps.append(caption)
        refs.append(str(row["caption"]))
    return compute_nlg_metrics(hypotheses=hyps, references=refs)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--attributo", default="Texture")
    parser.add_argument("--dataset-csv", default="data/processed/dataset_captioning.csv")
    parser.add_argument("--device", default="cpu")
    args = parser.parse_args()

    device = torch.device(args.device if torch.cuda.is_available() else "cpu")
    df = pd.read_csv(args.dataset_csv)
    df = df[df["attributo"] == args.attributo].reset_index(drop=True)

    sample_ids = df["sample_id"].unique()
    _, test_ids = train_test_split(sample_ids, test_size=0.15, random_state=42)
    test_ids = test_ids[:len(test_ids)//2]
    test_df = df[df["sample_id"].isin(test_ids)].reset_index(drop=True)

    tokenizer = ItalianTokenizer()
    results = {}
    for key in ["m1", "m2", "m3"]:
        ckpt = Path(f"models/{key}_{args.attributo}/best_model.pt")
        if not ckpt.exists():
            print(f"Checkpoint non trovato per {key}, skip.")
            continue
        print(f"Valutazione {key}...")
        model = load_model(key, args.attributo, tokenizer, device)
        scores = evaluate_model(model, test_df, tokenizer, device)
        results[key] = scores
        print(f"  {key}: {scores}")

    # genera report
    lines = [
        f"# Report Valutazione Modelli — {args.attributo}\n",
        "| Modello | BLEU | METEOR | ROUGE-L |",
        "|---|---|---|---|",
    ]
    model_names = {"m1": "CNN+LSTM", "m2": "CNN+Transformer", "m3": "ViT+Transformer"}
    for key, scores in results.items():
        lines.append(
            f"| {model_names[key]} | {scores['bleu']:.4f} | {scores['meteor']:.4f} | {scores['rouge_l']:.4f} |"
        )

    report = "\n".join(lines)
    out_path = Path("reports/training_results.md")
    out_path.write_text(report, encoding="utf-8")
    print(f"\nReport salvato in {out_path}")
    print(report)


if __name__ == "__main__":
    main()
```

- [ ] **Step 4: Esegui il confronto**

```
python src/data/16_evaluate_and_compare.py --attributo Texture
cat reports/training_results.md
```
Atteso: tabella con BLEU/METEOR/ROUGE-L per M1, M2, M3.

- [ ] **Step 5: Commit finale**

```bash
git add src/data/16_evaluate_and_compare.py reports/training_results.md
git commit -m "feat: add evaluation and comparison script, generate training_results.md"
```

---

## Note operative

**Ordine di esecuzione:**
1. Task 1 → Task 2 → Task 3 (prerequisiti condivisi, nessun GPU richiesto)
2. Task 4 → Task 5 → Task 6 → Task 7 → Task 8 (componenti modello, nessun GPU richiesto)
3. Task 9 → Task 10 (training reale, richiede GPU o Colab)

**Per il training su Google Colab:**
- Carica il repo su Drive o clona da GitHub
- Installa le dipendenze con `pip install torch torchvision timm transformers evaluate rouge-score`
- Esegui i Task 9 e 10 con `--device cuda`
- Scarica i checkpoint (`models/`) al termine

**Dipendenze da installare:**
```
pip install torch>=2.0 torchvision>=0.15 timm transformers evaluate rouge-score tqdm scikit-learn Pillow pandas
```
