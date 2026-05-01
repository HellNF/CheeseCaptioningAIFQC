# M5a — CNN frozen + GePpeTto (Sapore)

**Data:** 2026-04-30
**GPU:** NVIDIA RTX 4060 Laptop (8 GB VRAM)
**Attributo:** Sapore (train=976, val=234, test=230)
**Loader:** `on_topic_only=True`

## Configurazione

- Encoder: `CNNEncoderGlobal` (ResNet-50 ImageNet, **frozen**) — 1 token visivo (B, 1, 512)
- Decoder: `GePpeTtoDecoder` — Italian GPT-2 (LorenzoDeMattei/GePpeTto, **frozen** transformer + LM head, MLP projection 512→768 trainable)
- Loss: CE label smoothing 0.1
- Decode: nucleus (top_p=0.9, T=0.7)
- AdamW lr=1e-4 (proj only, GePpeTto frozen)
- Batch 16, max 30 epoche, patience 7

## Metriche test

| Metrica | Valore |
|---|---|
| BLEU-1 | 0.3082 |
| **BLEU-4** | **0.0903** |
| METEOR | 0.2744 |
| ROUGE-L | 0.2311 |
| Caption uniche | 200/230 (87%) |

## Training

| | Valore |
|---|---|
| Best epoch | 9/16 (early stop ep 16, patience 7/7) |
| Best val_loss | **1.5419** |
| Tempo totale | 21m |

**Val_loss notevolmente più bassa** rispetto ai modelli scratch del gruppo precedente (1.54 vs 1.96-2.00). Questo conferma che il decoder pre-trained GePpeTto fornisce un prior linguistico molto migliore della baseline. Il test BLEU-4 (0.0903) però è simile a M1 (0.092) — la migliore val_loss non si traduce in test pari (overfit residuo o limite del dataset).

## Confronto con M5a di Struttura

| | Struttura | Sapore | Δ |
|---|---|---|---|
| BLEU-4 | 0.047 | **0.090** | +91% |
| METEOR | 0.226 | 0.274 | +21% |
| ROUGE-L | 0.207 | 0.231 | +12% |

Pattern coerente con i frozen-scratch: dataset pulito raddoppia BLEU-4.

## Confronto interno (M5a vs M1, M2, M3)

| Modello | BLEU-4 | METEOR | ROUGE-L | Best val_loss |
|---|---|---|---|---|
| M1 (CNN+LSTM) | **0.092** | **0.289** | 0.239 | 1.959 |
| M2 (CNN+Transf) | 0.084 | 0.284 | **0.242** | 1.933 |
| M3 (ViT+Transf)* | 0.078 | 0.260 | 0.218 | 1.998 |
| **M5a (CNN+GePpeTto)** | **0.090** | 0.274 | 0.231 | **1.542** |

*M3 con disclaimer (best.pt corrotto, ep 13 invece di ep 8 — verrà rifatto).

**Risultato sorprendente**: M5a non batte M1 per BLEU-4 nonostante val_loss molto più bassa. Spiegazioni possibili:
- Train set 976 è troppo piccolo per sfruttare GePpeTto da 124M params anche con prefix-tuning
- Il prior linguistico di GePpeTto produce caption "troppo letterarie" che si scostano dallo stile sintetico del dataset (vedi #25 "Il sapore presenta una leggera sapidità...")
- M1 con LSTM piccola fitta meglio al "dialetto" specifico delle caption del Grana

## Caption esempio (8 sample)

| # | Predizione | Riferimento |
|---|---|---|
| 0 | Il sapore è caratterizzato da un amaro predominante, con una leggera acidità che si fa sentire in modo marcato. | Ha poco sapore. |
| 5 | Il sapore del Grana Trentino DOP è caratterizzato da una nota amara e una nota amara. | C'è un amaro netto. |
| 10 | Il sapore è dolce, con una leggera piccantezza. | Troppo salato. |
| 25 | Il sapore presenta una leggera sapidità e una leggera piccantezza. | Il Grana Trentino DOP offre un sapore medio, conforme alle aspettative di un formaggio di alta qualità. |
| 50 | Il sapore è caratterizzato da una nota amarognola e una leggera piccantezza. | Generalmente equilibrato. |
| 100 | Il sapore del Grana Trentino DOP è caratterizzato da una piccantezza marcata. | Il sapore è leggermente saporito e piccante, ma nel complesso equilibrato. |
| 150 | Il sapore è equilibrato, con una sapidità marcata. | Un po' troppo salato. |
| 200 | Il sapore è leggermente salato e dolce. | Il sapore è equilibrato con note dolciastre, peccato per il finale amarognolo. |

## Osservazioni

**Cosa migliora rispetto al gruppo scratch:**
- **Italiano più naturale e fluido**. Frasi come "Il sapore è caratterizzato da un amaro predominante, con una leggera acidità che si fa sentire in modo marcato" hanno costruzioni complesse (subordinate relative) che M1/M2/M3 non producono mai.
- Vocabolario più ricco: "amarognola" (forma diminutiva), "predominante", "in modo marcato" — espressioni naturalmente italiane non comuni nel training set.

**Errori grammaticali persistono:**
- #5 "una nota amara e una nota amara" — la stessa ripetizione di M1 ("acido e acido"). **Sorprendente**: un modello LM da 124M params dovrebbe evitare questo tipo di errore. Probabile causa: il prior linguistico è dominato dal training task (next-token-prediction con MLE) e non vede ripetizioni simili nei dati di training Sapore.

**Direzionalità ancora incerta:**
- #0: ref "ha poco sapore" → pred "amaro predominante, leggera acidità marcata" (semanticamente opposto)
- #10: ref "troppo salato" → pred "dolce, leggera piccantezza" (opposto)
- Il problema visione→giudizio non è risolto da GePpeTto. Il decoder è linguisticamente migliore, ma l'allineamento immagine-caption resta debole.

**Hallucination "Grana Trentino DOP":**
- Compare in #5, #100. Stessa hallucination di M1/M2 — la frase "Grana Trentino DOP" è frequente nel training quindi tutti i modelli la incorporano come stilema generico.

**Pattern delicato:**
- Val_loss 1.54 vs 1.96 dei scratch: GePpeTto **modella molto meglio la distribuzione dei token italiani** (la val_loss è log-perplexity).
- Ma BLEU-4 è quasi identico a M1: **fluency ≠ accuracy semantica**.
- METEOR è leggermente sotto M1 (0.274 vs 0.289). METEOR penalizza traduzioni "stilisticamente diverse anche se semanticamente vicine" — M5a parafrasea di più, M1 ricalca lo stile del training.

## Output

- Pesi: `models/m5a_cnn_gpt/Sapore/best.pt`
- Predictions: `models/m5a_cnn_gpt/Sapore/predictions.csv`
- Log: `models/m5a_cnn_gpt/Sapore/log.csv` (16 epoche)
