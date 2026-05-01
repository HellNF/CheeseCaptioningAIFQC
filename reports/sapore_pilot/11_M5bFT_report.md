# M5b-FT — CNNSpatial fine-tuned + GePpeTto (Sapore)

**Data:** 2026-05-01
**GPU:** NVIDIA RTX 4060 Laptop (8 GB VRAM)
**Attributo:** Sapore (train=976, val=234, test=230)

## Configurazione

- Encoder: `CNNEncoderSpatial` (ResNet-50, **fine-tuned**, 98 token spaziali)
- Decoder: `GePpeTtoDecoder` (Italian GPT-2, fine-tuned)
- 135M+ params trainable
- Batch 4 (ridotto da 8 per stabilità)
- AdamW lr=5e-5, cosine, label smoothing 0.1, nucleus

## Metriche test

| Metrica | Valore |
|---|---|
| BLEU-1 | 0.3493 |
| **BLEU-4** | **0.1001** |
| METEOR | 0.2945 |
| ROUGE-L | 0.2444 |
| Caption uniche | 199/230 (87%) |

## Training

| | Valore |
|---|---|
| Best epoch | 7/14 (early stop, patience 7/7) |
| Best val_loss | **1.5647** |
| Tempo totale | 22m |

## Confronto con M5b-FT di Struttura

| | Struttura | Sapore | Δ |
|---|---|---|---|
| BLEU-4 | 0.039 | **0.100** | +156% |
| METEOR | 0.226 | 0.294 | +30% |

## Confronto FT vs Frozen (M5b)

| Variante | BLEU-4 | METEOR | ROUGE-L | Best ep |
|---|---|---|---|---|
| M5b frozen | **0.100** | 0.292 | 0.248 | 8/15 |
| **M5b-FT** | 0.100 | **0.294** | 0.244 | 7/14 |

**Praticamente identici**. M5b-FT non aggiunge valore vs M5b frozen — anomalia nel pattern Sapore (per tutti gli altri modelli FT > frozen).

## Posizionamento

| Modello | BLEU-4 | METEOR |
|---|---|---|
| M3-FT 🏆 | 0.117 | 0.305 |
| **M5b-FT** | 0.100 | 0.294 |
| M5b | 0.100 | 0.292 |
| M3 | 0.098 | 0.307 |
| M2-FT | 0.098 | 0.298 |
| M1-FT | 0.098 | 0.284 |
| M5a-FT | 0.092 | 0.296 |
| M1 | 0.092 | 0.289 |
| M5a | 0.090 | 0.274 |
| M2 | 0.084 | 0.284 |

M5b-FT secondo posto BLEU-4 (pareggio con M5b frozen) ma sotto M3-FT.

## Caption esempio (8 sample)

| # | Predizione | Riferimento |
|---|---|---|
| 0 | Il sapore del Grana Trentino DOP si presenta leggermente acido. | Ha poco sapore. |
| 5 | Il sapore è piccante, con una leggera piccantezza e una leggera nota amara. | C'è un amaro netto. |
| 10 | Il sapore è equilibrato, con una leggera nota amarognola. | Troppo salato. |
| 25 | Il sapore è salato e piccante. | Il Grana Trentino DOP offre un sapore medio... |
| 50 | Il sapore è amaro e piccante. | Generalmente equilibrato. |
| 100 | Il sapore del Grana Trentino DOP è piccante, con una leggera piccantezza. | Il sapore è leggermente saporito e piccante, ma nel complesso equilibrato. |
| 150 | Il sapore è leggermente salato e dolce. | Un po' troppo salato. |
| 200 | Il sapore è equilibrato, con una leggera piccantezza. | Il sapore è equilibrato con note dolciastre, peccato per il finale amarognolo. |

## Osservazioni

**Cosa funziona:**
- **#5 buona direzionalità**: ref "amaro netto" → pred "leggera nota amara" ✓
- **#25 corretto**: ref "medio" → pred "salato e piccante" (ragionevole)
- **#150 parziale**: ref "troppo salato" → pred "salato e dolce" (cattura "salato")
- **#200 quasi perfetto**: ref "equilibrato" → pred "equilibrato con leggera piccantezza" ✓

**Errori grammaticali:**
- #5 "piccantezza e una leggera piccantezza" — ripetizione (stesso bug di M5a)
- #100 "piccante con una leggera piccantezza" — ripetizione

**Pattern interessante:**
- M5b-FT pareggia M5b frozen — fine-tuning encoder con prefix spaziale + GePpeTto = stesso risultato del solo encoder frozen
- Suggerisce che l'ottimo per CNNSpatial+GePpeTto è già raggiunto quando l'encoder è frozen
- L'aggiunta del fine-tuning non aiuta perché GePpeTto è già ben allineato ai token spaziali
- METEOR leggermente sopra (+0.002) = differenza trascurabile

## Output

- Pesi: `models/m5b_cnnspatial_gpt_ft/Sapore/best.pt`
- Predictions: `models/m5b_cnnspatial_gpt_ft/Sapore/predictions.csv`
- Log: `models/m5b_cnnspatial_gpt_ft/Sapore/log.csv` (14 epoche)
