# M5b — CNNSpatial frozen + GePpeTto (Sapore)

**Data:** 2026-04-30
**GPU:** NVIDIA RTX 4060 Laptop (8 GB VRAM)
**Attributo:** Sapore (train=976, val=234, test=230)
**Loader:** `on_topic_only=True`

## Configurazione

- Encoder: `CNNEncoderSpatial` (ResNet-50 ImageNet, **frozen**, output spaziale 7×7=49 token + 49 da view secondaria = ~98) — 98 token visivi proiettati a 768
- Decoder: `GePpeTtoDecoder` — Italian GPT-2 (LorenzoDeMattei/GePpeTto, **frozen** transformer + LM head, MLP projection 512→768 trainable)
- Loss: CE label smoothing 0.1
- Decode: nucleus (top_p=0.9, T=0.7)
- AdamW lr=1e-4 (proj only)
- Batch 16, max 30 epoche, patience 7

## Metriche test

| Metrica | Valore |
|---|---|
| BLEU-1 | 0.3293 |
| **BLEU-4** | **0.1004** |
| METEOR | 0.2923 |
| ROUGE-L | 0.2481 |
| Caption uniche | 203/230 (88%) |

## Training

| | Valore |
|---|---|
| Best epoch | 8/15 (early stop, patience 7/7) |
| Best val_loss | **1.5493** |
| Tempo totale | 23m |

## Confronto con M5b di Struttura

| | Struttura | Sapore | Δ |
|---|---|---|---|
| BLEU-4 | 0.048 | **0.100** | +109% |
| METEOR | 0.239 | 0.292 | +22% |
| ROUGE-L | 0.232 | 0.248 | +7% |

Pattern di +100% confermato anche per M5b.

## Confronto interno (4 modelli completati)

| Modello | BLEU-1 | BLEU-4 | METEOR | ROUGE-L | Val_loss | Best ep | Tempo |
|---|---|---|---|---|---|---|---|
| M1 (CNN+LSTM) | 0.329 | 0.092 | 0.289 | 0.239 | 1.959 | 49/50 | 50m |
| M2 (CNN+Transf) | 0.329 | 0.084 | 0.284 | 0.242 | 1.933 | 6/13 | 13m |
| M3 (ViT+Transf) | 0.315 | 0.098 | **0.307** | 0.249 | 1.974 | 8/13 | 21m |
| M5a (CNN+GePpeTto) | 0.308 | 0.090 | 0.274 | 0.231 | 1.542 | 9/16 | 21m |
| **M5b (CNNSpatial+GePpeTto)** | **0.329** | **0.100** | 0.292 | 0.248 | **1.549** | 8/15 | 23m |

**M5b è il leader del pilot finora** per BLEU-4 (0.100), supera M3 (0.098) e M5a (0.090). Su METEOR/ROUGE-L è praticamente alla pari di M3.

## Caption esempio (8 sample)

| # | Predizione | Riferimento |
|---|---|---|
| 0 | Il sapore del Grana Trentino DOP presenta una dolcezza marcata. | Ha poco sapore. |
| 5 | Il sapore del Grana Trentino DOP è piccante, con una leggera piccantezza. | C'è un amaro netto. |
| 10 | Il sapore del Grana Trentino DOP presenta una leggera acidità, che si integra bene con le altre note gustative. | Troppo salato. |
| 25 | Il sapore è caratterizzato da una piccantezza marcata, con una nota acida che pizzica nel finale. | Il Grana Trentino DOP offre un sapore medio, conforme alle aspettative di un formaggio di alta qualità. |
| 50 | Il sapore è acido e amaro, con una leggera piccantezza. | Generalmente equilibrato. |
| 100 | Il sapore è dolce, con una sapidità marcata e una leggera amarezza. | Il sapore è leggermente saporito e piccante, ma nel complesso equilibrato. |
| 150 | Il sapore è acido, salato e piccante. | Un po' troppo salato. |
| 200 | Il sapore del Grana Trentino DOP presenta un sapore salato che arricchisce l'esperienza gustativa. | Il sapore è equilibrato con note dolciastre, peccato per il finale amarognolo. |

## Osservazioni

**Cosa funziona meglio rispetto a M5a:**
- Il prefix spaziale (98 token) anziché globale (1 token) dà al decoder GePpeTto più informazione visiva strutturata. **Risultato concreto: +0.010 BLEU-4 vs M5a**.
- Caption più ricche e meno ripetitive: #25 "una piccantezza marcata, con una nota acida che pizzica nel finale" — costruzione idiomatica sofisticata.
- Errori grammaticali ridotti rispetto a M5a (no più "una nota amara e una nota amara").

**Cosa funziona meglio rispetto a M3:**
- BLEU-4 marginalmente superiore (0.100 vs 0.098)
- Caption uniche 88% (vs 85% di M3)
- Italiano più naturale ("che pizzica nel finale", "arricchisce l'esperienza gustativa")

**Persiste:**
- **Errore #5**: "piccante, con una leggera piccantezza" — stessa ripetizione semantica di M1. Sorprendente che GePpeTto non la blocchi.
- **Direzionalità incerta**: 
  - Ref "ha poco sapore" → "una dolcezza marcata" (semanticamente opposto)
  - Ref "troppo salato" → "leggera acidità" (sbagliato)
  - Ref "un po' troppo salato" → "acido, salato e piccante" (parzialmente corretto, salato c'è)
- Hallucination "Grana Trentino DOP" presente in molte caption come template.

**Pattern visione-spaziale:**
- M5b sfrutta i 98 token spaziali per descrivere meglio. Esempio #25 e #100: caption arricchite con dettagli ("nota acida che pizzica", "leggera amarezza") che M5a non produrrebbe.
- Però il vantaggio non si traduce in **fedeltà** ai riferimenti: la direzionalità semantica resta debole come negli altri modelli.

## Output

- Pesi: `models/m5b_cnnspatial_gpt/Sapore/best.pt`
- Predictions: `models/m5b_cnnspatial_gpt/Sapore/predictions.csv`
- Log: `models/m5b_cnnspatial_gpt/Sapore/log.csv` (15 epoche)
