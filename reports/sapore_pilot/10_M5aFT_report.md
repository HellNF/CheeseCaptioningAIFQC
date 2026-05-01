# M5a-FT — CNN fine-tuned + GePpeTto (Sapore)

**Data:** 2026-05-01
**GPU:** NVIDIA RTX 4060 Laptop (8 GB VRAM)
**Attributo:** Sapore (train=976, val=234, test=230)
**Loader:** `on_topic_only=True`

## Configurazione

- Encoder: `CNNEncoderGlobal` (ResNet-50, **fine-tuned**)
- Decoder: `GePpeTtoDecoder` (Italian GPT-2, fine-tuned)
- 135M params trainable
- Batch 8 (ridotto da 16)
- AdamW lr=5e-5, cosine, label smoothing 0.1, nucleus
- Max 20 epoche, patience 7

## Metriche test

| Metrica | Valore |
|---|---|
| BLEU-1 | 0.3226 |
| **BLEU-4** | **0.0924** |
| METEOR | 0.2960 |
| ROUGE-L | 0.2449 |
| Caption uniche | 207/230 (90%) |

## Training

| | Valore |
|---|---|
| Best epoch | 9/16 (early stop, patience 7/7) |
| Best val_loss | **1.5526** |
| Tempo totale | 22m |

Val_loss molto bassa (1.55), come M5a frozen (1.54). Convergenza rapida.

## Confronto con M5a-FT di Struttura

| | Struttura | Sapore | Δ |
|---|---|---|---|
| BLEU-4 | 0.045 | **0.092** | +106% |
| METEOR | 0.240 | 0.296 | +23% |

## Confronto FT vs Frozen (M5a)

| Variante | BLEU-4 | METEOR | ROUGE-L | Best ep |
|---|---|---|---|---|
| M5a frozen | 0.090 | 0.274 | 0.231 | 9/16 |
| **M5a-FT** | 0.092 | **0.296** | 0.245 | 9/16 |

**Fine-tuning con GePpeTto: +2% BLEU-4, +8% METEOR**. Differenza piccola, GePpeTto frozen sembra avere più valore quando l'encoder è anche fine-tuned ma il guadagno è modesto.

## Posizionamento

| Modello | BLEU-4 | METEOR |
|---|---|---|
| M3-FT 🏆 | 0.117 | 0.305 |
| M5b | 0.100 | 0.292 |
| M3 | 0.098 | 0.307 |
| M2-FT | 0.098 | 0.298 |
| M1-FT | 0.098 | 0.284 |
| **M5a-FT** | 0.092 | 0.296 |
| M1 | 0.092 | 0.289 |
| M5a | 0.090 | 0.274 |
| M2 | 0.084 | 0.284 |

M5a-FT è **6° su BLEU-4**, ma **3° su METEOR** (0.296). GePpeTto fine-tuned eccelle nella qualità lessicale (sinonimi naturali) anche se non vince su 4-gram exact match.

## Caption esempio (8 sample)

| # | Predizione | Riferimento |
|---|---|---|
| 0 | Il sapore del Grana Trentino DOP si presenta leggermente salato e piccante. | Ha poco sapore. |
| 5 | Il sapore è equilibrato, con una sapidità contenuta e una sapidità marcata. | C'è un amaro netto. |
| 10 | Il sapore è caratterizzato da una leggera amarezza. | Troppo salato. |
| 25 | Il sapore presenta una leggera acidità. | Il Grana Trentino DOP offre un sapore medio... |
| 50 | Il sapore è dolce e sapido, con una sapidità marcata. | Generalmente equilibrato. |
| 100 | Il sapore del Grana Trentino DOP si presenta con un amaro finale, con una leggera piccantezza. | Il sapore è leggermente saporito e piccante, ma nel complesso equilibrato. |
| 150 | Il sapore è caratterizzato da una sapidità e una piccantezza non percepibili. | Un po' troppo salato. |
| 200 | Il sapore è leggermente piccante, con una leggera piccantezza. | Il sapore è equilibrato con note dolciastre, peccato per il finale amarognolo. |

## Osservazioni

**Cosa funziona:**
- **#100 sofisticato**: ref "saporito e piccante" → pred "amaro finale con leggera piccantezza" (semantica vicina)
- **#150 interessante**: ref "troppo salato" → pred "non percepibili" (modello incerto, ma non strafalcione)
- METEOR alto (0.296) — GePpeTto fine-tuned aggiunge sinonimi naturali

**Errori grammaticali persistono:**
- #5 "una sapidità contenuta e una sapidità marcata" — contraddizione semantica (contenuta + marcata)
- #200 "leggermente piccante, con una leggera piccantezza" — ripetizione semantica

**Pattern problematico:**
- Caption più lunghe e meno mirate di M3-FT (vincitore)
- Direzionalità simile agli altri FT, niente di particolarmente migliore o peggiore

## Output

- Pesi: `models/m5a_cnn_gpt_ft/Sapore/best.pt`
- Predictions: `models/m5a_cnn_gpt_ft/Sapore/predictions.csv`
- Log: `models/m5a_cnn_gpt_ft/Sapore/log.csv` (16 epoche)
