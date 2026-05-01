# M5c-FT — ViT fine-tuned + GePpeTto (Sapore)

**Data:** 2026-05-01
**GPU:** NVIDIA RTX 4060 Laptop (8 GB VRAM)
**Attributo:** Sapore (train=976, val=234, test=230)

## Configurazione

- Encoder: `ViTEncoder` (timm vit_small_patch16_224, **fine-tuned**)
- Decoder: `GePpeTtoDecoder` (Italian GPT-2, fine-tuned)
- 196M+ params trainable totali (modello più grande del pilot)
- Batch 4 (ridotto da 8)
- AdamW lr=2e-5, cosine, label smoothing 0.1, nucleus

## Metriche test

| Metrica | Valore |
|---|---|
| BLEU-1 | 0.3274 |
| **BLEU-4** | **0.0981** |
| METEOR | 0.2945 |
| ROUGE-L | 0.2459 |
| Caption uniche | 208/230 (90%) |

## Training

| | Valore |
|---|---|
| Best epoch | 13/15 (no early stop) |
| Best val_loss | **1.6344** |
| Tempo totale | 70m (~5min/epoca) |

Modello più grande e più lento del pilot. Val_loss in calo monotono fino a ep 13 — avrebbe potuto migliorare oltre 15 epoche.

## Confronto con M5c-FT di Struttura

| | Struttura | Sapore | Δ |
|---|---|---|---|
| BLEU-4 | 0.044 | **0.098** | +123% |
| METEOR | 0.235 | 0.294 | +25% |

## Confronto FT vs Frozen (M5c)

| Variante | BLEU-4 | METEOR | ROUGE-L | Best ep |
|---|---|---|---|---|
| M5c frozen | ✗ skipped | — | — | — |
| **M5c-FT** | 0.098 | 0.294 | 0.246 | 13/15 |

M5c frozen non è disponibile (skip per crash). M5c-FT in linea con altri FT GePpeTto.

## Caption esempio (8 sample)

| # | Predizione | Riferimento |
|---|---|---|
| 0 | Il sapore è equilibrato, con una leggera piccantezza. | Ha poco sapore. |
| 5 | Il sapore è equilibrato, con una sapidità marcata e una piccantezza marcata. | C'è un amaro netto. |
| 10 | Il sapore è leggermente acido. | Troppo salato. |
| 25 | Il sapore è poco sapido, con una dolcezza che si fa sentire nel complesso. | Il Grana Trentino DOP offre un sapore medio... |
| 50 | Il sapore del Grana Trentino DOP si presenta con una sapidità marcata, con una sapidità marcata, una sapidità medio alta. | Generalmente equilibrato. |
| 100 | Il sapore del Grana Trentino DOP è leggermente piccante, ma si distingue per una dolcezza evidente, con una leggera piccantezza. | Il sapore è leggermente saporito e piccante, ma nel complesso equilibrato. |
| 150 | Il sapore è abbastanza saporito, con una leggera piccantezza e una leggera acidità. | Un po' troppo salato. |
| 200 | Il formaggio è piccante e amaro. | Il sapore è equilibrato con note dolciastre, peccato per il finale amarognolo. |

## Osservazioni

**Cosa funziona:**
- **#10 corretto direzionalità**: ref "salato" → pred "leggermente acido" (sbagliato sapore ma cattura intensità)
- **#25 sofisticato**: pred "dolcezza che si fa sentire nel complesso" — costruzione idiomatica
- **Diversità alta** (90% uniche, vincitore tra i FT)

**Errori grammaticali pronunciati:**
- **#50 disastro**: "sapidità marcata, con una sapidità marcata, una sapidità medio alta" — 3 ripetizioni!
- **#100 ridondante**: "leggermente piccante, [...] una leggera piccantezza" — riformulazione duplicata
- **#5 contraddittorio**: "sapidità marcata E piccantezza marcata" mentre ref è "amaro"

**Il modello più pesante non è il migliore:**
- 196M params, 70 min training
- BLEU-4 = 0.098 (sotto M5b 0.100, M3-FT 0.117)
- ViT fine-tuned + GePpeTto fine-tuned su solo 976 samples → overfitting probabile sul vocabolario fisso del dataset

**Pattern interessante:**
- Caption più lunghe e elaborate degli altri FT (vedi #25, #100)
- Costruzioni idiomatiche italiane più sofisticate, ma non sempre sensate
- Il fine-tuning di entrambi encoder e decoder produce caption "letterarie" ma poco precise

## Output

- Pesi: `models/m5c_vit_gpt_ft/Sapore/best.pt`
- Predictions: `models/m5c_vit_gpt_ft/Sapore/predictions.csv`
- Log: `models/m5c_vit_gpt_ft/Sapore/log.csv` (15 epoche)
