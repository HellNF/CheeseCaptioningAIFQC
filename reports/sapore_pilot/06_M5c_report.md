# M5c — ViT frozen + GePpeTto (Sapore) 🥈 2° classificato

**Data:** 2026-05-01
**GPU:** NVIDIA RTX 4060 Laptop (8 GB VRAM)
**Attributo:** Sapore (train=976, val=234, test=230)

> Note: 3 crash CUDA precedenti (illegal memory access, CUBLAS) durante prima epoca, recovered dopo riavvio del PC. Last successful run completato prima dell'ennesimo reset (ep 11/20 patience 3/5). Best.pt ep 8 (val_loss 1.578) recuperato e valutato con `--eval-only`.

## Configurazione

- Encoder: `ViTEncoder` (timm vit_small_patch16_224, **frozen**)
- Decoder: `GePpeTtoDecoder` (Italian GPT-2, **frozen** transformer + LM head, MLP projection)
- ~211M params totali, ~10M trainable (solo proj)
- Batch 8, AdamW lr=5e-5, cosine, label smoothing 0.1, nucleus

## Metriche test 🥈

| Metrica | Valore |
|---|---|
| BLEU-1 | 0.3163 |
| **BLEU-4** | **0.1118** ⬅ 2° del pilot |
| **METEOR** | **0.3196** ⬅ 🏆 TOP del pilot |
| ROUGE-L | 0.2612 |
| Caption uniche | 208/230 (90%) |

## Training

| | Valore |
|---|---|
| Best epoch | 8 (val_loss 1.578) |
| Tempo cumulativo | ~47m (con interruzioni) |

## Confronto con M5c di Struttura

| | Struttura | Sapore | Δ |
|---|---|---|---|
| BLEU-4 | 0.048 | **0.112** | +133% |
| METEOR | 0.234 | 0.320 | +37% |

Tra i salti più grandi del pilot rispetto a Struttura.

## Confronto con altri modelli del pilot

| Modello | BLEU-4 | METEOR | ROUGE-L |
|---|---|---|---|
| M3-FT 🏆 | 0.117 | 0.305 | 0.262 |
| **M5c** 🥈 | **0.112** | **0.320** ⬅ TOP | 0.261 |
| M5b | 0.100 | 0.292 | 0.248 |
| M5b-FT | 0.100 | 0.294 | 0.244 |
| M3 | 0.098 | 0.307 | 0.249 |
| M2-FT | 0.098 | 0.298 | 0.238 |
| M1-FT | 0.098 | 0.284 | 0.241 |
| M5c-FT | 0.098 | 0.294 | 0.246 |
| M1 | 0.092 | 0.289 | 0.239 |
| M5a-FT | 0.092 | 0.296 | 0.245 |
| M5a | 0.090 | 0.274 | 0.231 |
| M2 | 0.084 | 0.284 | 0.242 |

**M5c è 2° su BLEU-4 e 1° su METEOR.** Combinazione vincente: ViT + GePpeTto con entrambi frozen.

## Caption esempio

| # | Predizione | Riferimento |
|---|---|---|
| 0 | Il sapore del Grana Trentino DOP è abbastanza equilibrato, con una leggera piccantezza. | Ha poco sapore. |
| 5 | Il sapore del Grana Trentino DOP è amaro, con una leggera piccantezza. | C'è un amaro netto. |
| 10 | Il sapore è caratterizzato da una dolcezza marcata. | Troppo salato. |
| 25 | Il sapore è salato, con una leggera piccantezza. | Il Grana Trentino DOP offre un sapore medio... |
| 50 | Il sapore del Grana Trentino DOP si presenta con una dolcezza marcata, che contribuisce a un profilo gustativo. | Generalmente equilibrato. |
| 100 | Il sapore del Grana Trentino DOP si presenta con una leggera acidità e una piccantezza marcata. | Il sapore è leggermente saporito e piccante, ma nel complesso equilibrato. |
| 150 | Il sapore del Grana Trentino DOP è leggermente acido e piccante, ma presenta una piccantezza ben definita. | Un po' troppo salato. |
| 200 | Il sapore è equilibrato, con una piccantezza marcata. | Il sapore è equilibrato con note dolciastre, peccato per il finale amarognolo. |

## Osservazioni

**Cosa funziona molto bene:**
- **#5 quasi perfetto**: ref "amaro netto" → pred "amaro con leggera piccantezza" ✓
- **METEOR top del pilot (0.320)**: GePpeTto frozen produce sinonimi naturali italiani, METEOR premia
- Caption uniche 90%, alta diversità
- **Niente errori grammaticali evidenti** in 8 sample mostrati (a differenza di M5c-FT che aveva ripetizioni)

**Cosa non funziona:**
- #10: ref "salato" → pred "dolce" (direzione opposta)
- #50, #100, #200: caption più verbose dei riferimenti
- Hallucination "Grana Trentino DOP" come template

**Pattern key:**
- **Frozen GePpeTto > FT GePpeTto** su Sapore: M5c frozen (0.112) vince M5c-FT (0.098)
- Coerente con cumulativo_2 vs cumulativo_4 (frozen-GePpeTto migliore di FT-GePpeTto)
- ViT cattura informazione visiva ricca + GePpeTto frozen mantiene il prior linguistico forte = combinazione vincente

## Output

- Pesi: `models/m5c_vit_gpt/Sapore/best.pt`
- Predictions: `models/m5c_vit_gpt/Sapore/predictions.csv`
