# Design: Tre Metodi Encoder-Decoder per Image Captioning
**Data:** 2026-04-12  
**Progetto:** Grana Trentino Image Captioning FQC  
**Stato:** Validato — approvato per implementazione

---

## Contesto

Il dataset è composto da ~2.745 immagini BMP di fette di Grana Trentino DOP, organizzate in coppie (FETTA + GRANA) per ogni campione fisico. Le caption sono state prodotte dalla Fase 4 (normalizzazione LLM dei commenti del panel sensoriale) e sono **per-attributo**: ogni campione ha fino a 7 caption separate (Texture, Struttura della Pasta, Colore della Pasta, Spessore della Crosta, Profumo, Sapore, Aroma).

**Input del modello:** coppia di immagini [FETTA, GRANA] dello stesso campione  
**Output del modello:** caption testuale in italiano che descrive un attributo sensoriale  
**Backbone:** pre-trained su ImageNet (transfer learning)  
**Framework:** PyTorch  
**Risorse:** CPU / GPU consumer (6-8 GB VRAM) / Google Colab

---

## Relazione con il corso AI4FQC

Il corso (Capitoli 3-7) tratta image captioning con un approccio encoder-decoder classico: **CNN encoder + catena di SVM** che predicono le parole una alla volta. Questo rappresenta il "grado zero" del captioning moderno.

I tre metodi proposti si collocano come naturale evoluzione rispetto a quel baseline, giustificata dalla teoria del corso stesso:

| Livello | Encoder | Decoder | Fonte |
|---|---|---|---|
| **Baseline corso** | CNN (feature globale) | Catena di SVM | Capitolo 6 |
| **M1 (nostro)** | CNN (feature globale) | LSTM | Estensione del corso |
| **M2 (nostro)** | CNN (feature spaziali) | Transformer | Oltre il corso |
| **M3 (nostro)** | ViT (patch tokens) | Transformer | Oltre il corso |

Il corso fornisce tre argomenti teorici che giustificano il passaggio dai decoder SVM a quelli neurali (Capitolo 6):
1. **Maggiore potere rappresentazionale** delle reti profonde rispetto ai modelli shallow
2. **Apprendimento end-to-end**: encoder e decoder si ottimizzano congiuntamente
3. **Scalabilità**: le SVM soffrono con vocabolari di migliaia di classi (matrice di Gram ingestibile); i layer Softmax neurali non hanno questo problema

Il concetto di **transfer learning** da ImageNet (ResNet, VGG come feature extractor) è esplicitamente trattato nel Capitolo 6 e direttamente applicato in tutti e tre i metodi.

---

## Principio di selezione dei metodi

La consegna richiede tre metodi "concettualmente il più diversi possibile". I tre metodi scelti differiscono lungo **due assi indipendenti**:

| | Encoder visuale | Decoder | Ricorrenza | Meccanismo di attenzione |
|---|---|---|---|---|
| **M1** | CNN (feature globale) | LSTM | Sì | Nessuna |
| **M2** | CNN (feature spaziali) | Transformer | No | Cross-attention |
| **M3** | ViT (patch tokens) | Transformer | No | Self-attention + Cross-attention |

Progressione concettuale:
- **M1 → M2**: stesso encoder CNN, ma il decoder passa da ricorrente (LSTM) ad attention-based (Transformer)
- **M2 → M3**: stesso decoder Transformer, ma l'encoder passa da CNN a Vision Transformer (nessuna convoluzione)
- **M1 → M3**: cambio completo di encoder e decoder — paradigmi opposti

---

## Metodo 1 — CNN + LSTM
**Paradigma:** ricorrente, feature globale, nessuna attention  
**Paper di riferimento:** Vinyals et al., *Show and Tell* (CVPR 2015)

### Architettura

```
[FETTA] → ResNet-50 → avgpool → vettore 2048-dim ──┐
                                                    ├─→ concat → Linear(4096→512) → hidden_0
[GRANA] → ResNet-50 → avgpool → vettore 2048-dim ──┘
                                                    
hidden_0 → LSTM → word_1 → LSTM → word_2 → ... → <EOS>
              ↑               ↑
          Embedding(w_{t-1}) Embedding(w_{t-1})
```

### Dettagli chiave

- **Encoder:** ResNet-50 pre-trained (ImageNet), strati convoluzionali congelati, solo il layer finale di proiezione è trainabile
- **Fusione FETTA+GRANA:** concatenazione dei due vettori globali (4096-dim) → proiezione lineare a 512-dim → usato come `h_0` dell'LSTM
- **Decoder:** LSTM a 1 layer, hidden size 512; input = embedding della parola precedente (dim 256)
- **Vocabolario:** costruito dalle caption normalizzate; token speciali `<SOS>`, `<EOS>`, `<PAD>`, `<UNK>`. In alternativa, si può riutilizzare il tokenizer di un modello italiano pre-trained (es. `LorenzoDeMattei/GePpeTto` o `GroNLP/gpt2-small-italian`) per avere un vocabolario italiano già consolidato — ma i pesi LSTM rimangono inizializzati da zero
- **Generazione:** greedy decoding o beam search (k=3) a inference time

### Perché è concettualmente distinto

L'immagine viene compressa in un unico vettore e usata **una sola volta** per inizializzare il decoder. Durante la generazione, il modello non ha più accesso alla rappresentazione visiva — genera il testo "dalla memoria". Questo è il paradigma più semplice e la baseline naturale.

---

## Metodo 2 — CNN + Transformer Decoder
**Paradigma:** attention-based decoder, feature spaziali CNN, nessuna ricorrenza  
**Ispirazione:** CPTR (Liu et al., 2021) — variante con encoder CNN invece di ViT

### Architettura

```
[FETTA] → ResNet-50 → feature map 7×7×2048 → flatten → 49 vettori ──┐
                                                                       ├─→ concat → 98 visual tokens (dim 2048→512)
[GRANA] → ResNet-50 → feature map 7×7×2048 → flatten → 49 vettori ──┘

98 visual tokens
      ↓
Transformer Decoder (N=4 layer, h=8 heads, d=512)
  - Self-attention sulle parole generate finora
  - Cross-attention sui 98 visual tokens
      ↓
Linear → Softmax → distribuzione sul vocabolario
```

### Dettagli chiave

- **Encoder:** ResNet-50 pre-trained, estratta la feature map dall'ultimo layer conv (prima del global avg pooling) → shape `(B, 2048, 7, 7)` → reshape in `(B, 49, 2048)` → proiezione lineare a 512
- **Fusione FETTA+GRANA:** concatenazione delle due feature map spaziali → `(B, 98, 512)` — mantiene la struttura spaziale di entrambe le viste
- **Decoder:** Transformer decoder PyTorch standard (`nn.TransformerDecoder`), 4 layer, 8 teste, dim 512, FFN 2048
- **Positional encoding:** sinusoidale sulle sequenze testuali; per le visual features si usa positional encoding 2D apprendibile (o nessuno, dato che sono già ordinate spazialmente)
- **Generazione:** autoregressive con causal mask; beam search a inference

### Perché è concettualmente distinto

Rispetto a M1, il decoder non ha ricorrenza: ogni parola viene generata guardando **tutte le parole precedenti contemporaneamente** (self-attention) e **tutte le 98 regioni visive** (cross-attention). Il training è parallelizzabile. Rispetto a M3, l'encoder rimane una CNN — la struttura a griglia spaziale è ancora imposta dall'architettura.

---

## Metodo 3 — Vision Transformer + Transformer Decoder
**Paradigma:** full-attention, patch-based, nessuna CNN né RNN  
**Ispirazione:** ViT (Dosovitskiy et al., 2021) + decoder Transformer standard

### Architettura

```
[FETTA] → ViT-B/16 → 196 patch tokens (dim 768) ──┐
                                                    ├─→ concat → 392 visual tokens → Linear(768→512)
[GRANA] → ViT-B/16 → 196 patch tokens (dim 768) ──┘

392 visual tokens (dim 512)
      ↓
Transformer Decoder (N=4 layer, h=8 heads, d=512)
  - Self-attention sulle parole generate
  - Cross-attention sui 392 patch tokens
      ↓
Linear → Softmax → distribuzione sul vocabolario
```

### Dettagli chiave

- **Encoder:** `vit_base_patch16_224` da `timm`, pre-trained su ImageNet-21k; le immagini vengono ridimensionate a 224×224; ogni immagine produce 196 patch tokens di dim 768 (escluso il CLS token, che non viene usato)
- **Fusione FETTA+GRANA:** concatenazione delle due sequenze di patch → `(B, 392, 768)` → proiezione lineare a 512
- **Strategia fine-tuning ViT:** i primi N layer del ViT sono congelati, gli ultimi 4 sono trainabili con learning rate ridotto (1/10 rispetto al decoder) — come raccomandato dal corso (Cap. 6, sezione Transfer Learning) e dalla letteratura specifica su ViT con dataset piccoli (Gani et al., BMVC 2022)
- **Data augmentation obbligatoria per M3:** con ~1300 campioni, il ViT tende all'overfitting; applicare random crop, flip orizzontale, color jitter, e random rotation durante il training
- **Decoder:** identico a M2 (Transformer decoder PyTorch, 4 layer, 8 teste, dim 512)
- **Memoria GPU:** ViT-B/16 ≈ 86M parametri — raccomandato training su Colab con GPU A100 o T4 con batch size ridotto (8-16)

### Perché è concettualmente distinto

Nessuna convoluzione nell'encoder: l'immagine viene trattata come una **sequenza di patch** (simile a parole in un testo). Il ViT impara dipendenze globali tra patch lontane già nell'encoder, senza induzione di bias località (come nelle CNN). Combinato con il decoder Transformer, l'intera pipeline è basata su self-attention e cross-attention — zero ricorrenza, zero convoluzione.

---

## Gestione del dataset per il training

### Struttura campioni

Ogni campione è identificato da `(codice_caseificio, data_seduta)`. Per ogni campione:
- 2 immagini: `FETTA.bmp`, `GRANA.bmp`
- Fino a 7 caption (una per attributo)

### Dataset PyTorch

```python
# Ogni record nel dataset è:
{
    "fetta_path": "path/to/FETTA.bmp",
    "grana_path": "path/to/GRANA.bmp",
    "attributo": "Texture",          # opzionale: per training condizionato
    "caption": "Il campione è granuloso e solubile..."
}
```

Un campione con K attributi disponibili genera K record indipendenti. Il modello non è condizionato sull'attributo (ciascun attributo usa il proprio modello separato, oppure si addestra un modello unico con conditioning token).

### Split train/val/test

Split a livello di **campione fisico** (non di immagine), per evitare data leakage:
- Train: 70%
- Validation: 15%
- Test: 15%

Stratificazione per anno (2018-2021) raccomandata.

---

## Metriche di valutazione

Tutti e tre i modelli vengono valutati con le stesse metriche standard NLG:

| Metrica | Cosa misura |
|---|---|
| **BLEU-1/4** | Sovrapposizione n-gram con riferimento |
| **METEOR** | Matching lessicale + sinonimi |
| **CIDEr** | Consenso tra caption di riferimento (TF-IDF pesato) |
| **ROUGE-L** | Sottosequenza comune più lunga |

Libreria: `pycocoevalcap` o `evaluate` (HuggingFace).

---

## Ordine di implementazione consigliato

1. **M1 (CNN+LSTM)** — baseline veloce, verifica pipeline dati e metriche
2. **M2 (CNN+Transformer)** — stesso encoder di M1, cambio decoder; valida il Transformer decoder
3. **M3 (ViT+Transformer)** — stesso decoder di M2, cambio encoder; richiede più risorse

Ogni metodo riusa i componenti comuni (dataset loader, tokenizer, loop di training, evaluation) da un modulo condiviso.

---

## Dipendenze Python

```
torch>=2.0
torchvision>=0.15
timm>=0.9          # per ViT-B/16
Pillow
nltk
pycocoevalcap      # metriche BLEU/METEOR/CIDEr/ROUGE
tqdm
```

---

## Riferimenti bibliografici

- Vinyals et al., *Show and Tell: A Neural Image Caption Generator*, CVPR 2015 — [arXiv:1411.4555](https://arxiv.org/pdf/1411.4555)
- Liu et al., *CPTR: Full Transformer Network for Image Captioning*, 2021 — [arXiv:2101.10804](https://arxiv.org/abs/2101.10804)
- Dosovitskiy et al., *An Image is Worth 16×16 Words: Transformers for Image Recognition at Scale (ViT)*, ICLR 2021
- Gani et al., *How to Train Vision Transformer on Small-scale Datasets?*, BMVC 2022 — [PDF](https://bmvc2022.mpi-inf.mpg.de/0731.pdf)
- Kumar et al., *Comparative Study of Transformer and LSTM Network with Attention Mechanism on Image Captioning*, 2023 — [arXiv:2303.02648](https://arxiv.org/abs/2303.02648)
