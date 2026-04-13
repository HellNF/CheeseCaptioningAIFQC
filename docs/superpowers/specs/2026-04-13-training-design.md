# Design: Training Pipeline — Tre Modelli Encoder-Decoder
**Data:** 2026-04-13  
**Progetto:** Grana Trentino Image Captioning FQC  
**Stato:** Approvato — pronto per implementazione

---

## Contesto

Il dataset di training è già disponibile in `data/processed/dataset_captioning.csv` (9.209 righe trainable, 34 colonne). Ogni riga lega una coppia di immagini BMP (fetta + grana) a una caption italiana generata via GPT-4o-mini e normalizzata attraverso una pipeline LLM a 4 passi.

**Obiettivo:** implementare e confrontare tre architetture encoder-decoder per image captioning:
- **M1** — CNN (feature globale) + LSTM
- **M2** — CNN (feature spaziali) + Transformer Decoder  
- **M3** — ViT (patch tokens) + Transformer Decoder

**Strategia di training:** un modello per attributo (7 run per architettura) + un modello globale con conditioning token (1 run per architettura) = **24 esperimenti totali**.

**Hardware target:** NVIDIA RTX 4060 laptop (8 GB VRAM). VM come fallback.

---

## Struttura file

```
src/models/
  __init__.py
  dataset.py        # GranaTrentinoDataset, split logic
  vocabulary.py     # ItalianTokenizer (wrapper GePpeTto)
  encoders.py       # CNNEncoderGlobal, CNNEncoderSpatial, ViTEncoder
  decoders.py       # LSTMDecoder, TransformerDecoder
  models.py         # CnnLstm, CnnTransformer, ViTTransformer
  train.py          # train_one_epoch(), evaluate_epoch(), train_model()
  metrics.py        # quick_eval(), full_eval(), generate_caption()

train.py            # CLI entry point (root del progetto)

models/
  m1_cnn_lstm/
    Texture/
      best.pt           # pesi con miglior val_loss
      last.pt           # pesi ultima epoca (per resume)
      config.json       # iperparametri usati
      log.csv           # epoca, train_loss, val_loss, bleu4
      predictions.csv   # caption_pred, caption_ref (test set)
    Sapore/...
    ...
    global/...          # modello condizionato su tutti gli attributi
  m2_cnn_transformer/...
  m3_vit_transformer/...

reports/
  compare_models.py     # genera tabella comparativa da log.csv + predictions.csv
  training_results.md   # output del confronto finale

tests/models/
  __init__.py
  test_dataset.py
  test_vocabulary.py
  test_encoders.py
  test_decoders.py
  test_models.py
  test_metrics.py
```

---

## Dataset Loader (`src/models/dataset.py`)

### Input

Legge `data/processed/dataset_captioning.csv`. Filtra su:
- `has_caption == True`
- `has_images == True`
- Per default: `has_both_views == True` (fetta-only escluse)

### Parametri

```python
GranaTrentinoDataset(
    csv_path: Path,
    tokenizer: ItalianTokenizer,
    transform: transforms.Compose,
    attributo: str | None = None,   # None = modello globale
    split: str = "train",           # "train" | "val" | "test"
    require_both_views: bool = True, # False = includi fetta-only con grana=zeros
    max_caption_len: int = 50,
)
```

### Output per item

```python
{
    "fetta":   Tensor[3, 224, 224],    # immagine normalizzata
    "grana":   Tensor[3, 224, 224],    # zeros se fetta-only e require_both_views=False
    "caption": LongTensor[seq_len],    # token ids con <SOS> e <EOS>
    "weight":  float,                  # colonna peso (0.5 per pattern ripetuti)
}
```

Per il modello globale (`attributo=None`): il token `[Texture]`, `[Sapore]`, ecc. viene preposto alla caption: `<SOS> [Texture] Il campione è ... <EOS>`.

### Split

Divisione a livello di **campione fisico** (`sample_id = codice_caseificio + data_seduta`), stratificata per anno (2018-2021):
- Train: 70%
- Validation: 15%
- Test: 15%

Tutte le caption (fino a 7) dello stesso campione fisico stanno nello stesso split. Split salvato come `data/processed/splits.json` per riproducibilità.

---

## Vocabulary / Tokenizer (`src/models/vocabulary.py`)

Wrapper su `LorenzoDeMattei/GePpeTto` (GPT-2 italiano, ~50.000 token BPE).

```python
class ItalianTokenizer:
    SOS_ID: int
    EOS_ID: int
    PAD_ID: int
    ATTR_TOKENS: dict[str, int]  # {"[Texture]": id, ...}

    def encode(self, text: str, add_special: bool = True) -> list[int]
    def decode(self, ids: list[int], skip_special: bool = True) -> str
    def __len__(self) -> int
```

Token speciali aggiunti al vocabolario GePpeTto:
- `<SOS>`, `<EOS>`, `<PAD>`
- `[Texture]`, `[Sapore]`, `[Aroma]`, `[Profumo]`, `[Struttura_della_Pasta]`, `[Colore_della_Pasta]`, `[Spessore_della_Crosta]`

---

## Encoders (`src/models/encoders.py`)

Interfaccia comune per tutti gli encoder:

```python
class BaseEncoder(nn.Module):
    d_model: int = 512
    n_visual_tokens: int           # 1 | 98 | 392

    def forward(self, fetta: Tensor, grana: Tensor) -> Tensor:
        # output: (B, n_visual_tokens, d_model)
        ...
```

### CNNEncoderGlobal (M1)

- Backbone: ResNet-50 pre-trained (ImageNet), layer conv congelati
- Estrazione: dopo `avgpool` → vettore 2048-dim per immagine
- Fusione: `concat(fetta_vec, grana_vec)` → 4096-dim → `Linear(4096, 512)`
- Output: `(B, 1, 512)` — singolo token usato come `h0` dell'LSTM

### CNNEncoderSpatial (M2)

- Backbone: ResNet-50 pre-trained, estratto prima del global avgpool
- Feature map: `(B, 2048, 7, 7)` → reshape `(B, 49, 2048)` → `Linear(2048, 512)`
- Fusione: `concat(fetta_tokens, grana_tokens)` → `(B, 98, 512)`
- Output: `(B, 98, 512)`

### ViTEncoder (M3)

- Backbone: `vit_base_patch16_224` da `timm`, pre-trained su ImageNet-21k
- Immagini ridimensionate a 224×224; output: 196 patch token da 768-dim (escluso CLS)
- Fusione: `concat(fetta_patches, grana_patches)` → `(B, 392, 768)` → `Linear(768, 512)`
- Fine-tuning: ultimi 4 layer ViT trainabili con `lr × 0.1`; primi layer congelati
- Output: `(B, 392, 512)`

---

## Decoders (`src/models/decoders.py`)

Interfaccia comune:

```python
class BaseDecoder(nn.Module):
    def forward(
        self,
        visual_tokens: Tensor,   # (B, n_tokens, 512) — da qualsiasi encoder
        captions: LongTensor,    # (B, seq_len) — con <SOS>, senza <EOS>
    ) -> Tensor:                 # (B, seq_len, vocab_size) — logit
        ...
```

### LSTMDecoder (M1)

- LSTM 1 layer, hidden size 512
- `h0` = visual_tokens squeezed `(B, 512)` (solo per M1 che ha 1 token)
- Input per step: embedding della parola precedente, dim 256
- Output: `Linear(512, vocab_size)`
- Generazione: greedy decoding o beam search `k=3`

### TransformerDecoder (M2 e M3)

- `nn.TransformerDecoder`: 4 layer, 8 teste, `d_model=512`, FFN 2048
- Self-attention causale sulle parole generate finora
- Cross-attention sui visual token (`n_tokens` = 98 per M2, 392 per M3)
- Positional encoding sinusoidale sulle sequenze testuali
- Pesi inizializzati da `GroNLP/gpt2-small-italian` (layer self-attention); cross-attention inizializzato da zero
- Generazione: autoregressive con causal mask, beam search `k=3`

M2 e M3 condividono lo **stesso** `TransformerDecoder` — cambia solo l'encoder.

---

## Modelli (`src/models/models.py`)

```python
class CnnLstm(nn.Module):
    encoder: CNNEncoderGlobal
    decoder: LSTMDecoder

class CnnTransformer(nn.Module):
    encoder: CNNEncoderSpatial
    decoder: TransformerDecoder

class ViTTransformer(nn.Module):
    encoder: ViTEncoder
    decoder: TransformerDecoder
```

Factory function:

```python
def build_model(
    model_name: str,          # "m1" | "m2" | "m3"
    vocab_size: int,
    device: torch.device,
) -> nn.Module
```

---

## Training Loop (`src/models/train.py`)

### Teacher forcing

A ogni step il decoder riceve la parola target corretta (non quella predetta). Loss: `CrossEntropyLoss` con `ignore_index=PAD_ID`. Campioni con `peso=0.5` applicano weighted loss.

### Loop per epoca

```
train_one_epoch(model, loader, optimizer, device) → float (loss media)
evaluate_epoch(model, loader, tokenizer, device)  → dict {val_loss, bleu4}
```

### Iperparametri di default

| Parametro | M1 | M2 | M3 |
|---|---|---|---|
| Batch size | 32 | 32 | 16 |
| Learning rate | 3e-4 | 3e-4 | 1e-4 |
| Epoche max | 50 | 50 | 30 |
| Early stopping patience | 7 | 7 | 5 |
| Optimizer | Adam | Adam | AdamW |
| LR scheduler | StepLR(step=10, γ=0.5) | StepLR(step=10, γ=0.5) | CosineAnnealing |

Per M3: ViT usa `lr × 0.1` (param group separato).

### Checkpoint

Ogni run salva in `models/{model_name}/{attributo}/`:

```
best.pt        ← state_dict con miglior val_loss
last.pt        ← state_dict ultima epoca
config.json    ← tutti gli iperparametri + split seed + vocab_size
log.csv        ← epoca, train_loss, val_loss, bleu4, elapsed_sec
```

`--resume`: carica `last.pt` + `log.csv`, riparte dall'epoca successiva.  
Se `best.pt` esiste e `--resume` non è specificato: il CLI avvisa e chiede conferma prima di sovrascrivere.

---

## Metriche (`src/models/metrics.py`)

Libreria: `evaluate` (HuggingFace).

```python
def quick_eval(model, loader, tokenizer, device) -> float
# Solo BLEU-4, usato durante training ogni epoca per velocità

def full_eval(model, loader, tokenizer, device) -> dict
# BLEU-1, BLEU-4, METEOR, ROUGE-L
# Salva predictions.csv con caption_pred e caption_ref

def generate_caption(
    model, fetta, grana, tokenizer, device,
    beam_size: int = 3,
    max_len: int = 50,
) -> str
```

**CIDEr escluso:** richiede riferimenti multipli per campione; ogni campione ha una sola caption ground truth.

---

## CLI (`train.py`)

```bash
# Training per-attributo
python train.py --model m1 --attributo Texture
python train.py --model m2 --attributo Sapore --epochs 60 --batch-size 16

# Modello globale (tutti gli attributi con conditioning token)
python train.py --model m1 --attributo all

# Resume da checkpoint
python train.py --model m1 --attributo Texture --resume

# Includi righe fetta-only (grana = zeros)
python train.py --model m1 --attributo Texture --include-fetta-only

# Evaluazione su test set con modello già addestrato
python train.py --model m1 --attributo Texture --eval-only
```

Argomenti completi:

| Flag | Default | Descrizione |
|---|---|---|
| `--model` | obbligatorio | `m1` / `m2` / `m3` |
| `--attributo` | obbligatorio | nome attributo o `all` |
| `--epochs` | 50 (30 per M3) | epoche massime |
| `--batch-size` | 32 (16 per M3) | dimensione batch |
| `--lr` | vedi tabella | learning rate |
| `--beam-size` | 3 | beam search width |
| `--resume` | False | riprendi da last.pt |
| `--include-fetta-only` | False | includi campioni senza grana |
| `--eval-only` | False | solo test set, no training |
| `--seed` | 42 | seed per riproducibilità |

---

## Report comparativo (`reports/compare_models.py`)

Legge tutti i `log.csv` e `predictions.csv` da `models/`. Produce `reports/training_results.md` con:
- Tabella BLEU-1/4, METEOR, ROUGE-L per ogni run (modello × attributo)
- Confronto per-attributo tra M1, M2, M3
- Confronto per-modello vs. modello globale

---

## Dipendenze Python

```
torch>=2.0
torchvision>=0.15
timm>=0.9              # ViT-B/16
transformers>=4.30     # GePpeTto tokenizer
evaluate>=0.4          # BLEU, METEOR, ROUGE-L
Pillow
pandas
tqdm
```

---

## Ordine di implementazione

1. `dataset.py` + `vocabulary.py` — fondamenta, testabili senza GPU
2. `encoders.py` — uno alla volta, test con input sintetico
3. `decoders.py` — uno alla volta, test con input sintetico
4. `models.py` + forward pass end-to-end
5. `train.py` — loop, checkpoint, early stopping
6. `metrics.py` — quick_eval e full_eval
7. `train.py` CLI — entry point completo
8. `reports/compare_models.py` — report finale
