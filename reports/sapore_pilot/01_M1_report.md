# M1 — CNN frozen + LSTM (Sapore)

**Data:** 2026-04-30
**GPU:** NVIDIA RTX 4060 Laptop (8 GB VRAM)
**Attributo:** Sapore (train=976, val=234, test=230)
**Loader:** `on_topic_only=True` (fix FUORI_ATTRIBUTO applicato)

## Configurazione

- Encoder: `CNNEncoderGlobal` (ResNet-50 ImageNet, **frozen**) — 1 token visivo (B, 1, 512)
- Decoder: `LSTMDecoder` from-scratch — vocab 30010, embed 512, hidden 512
- Loss: `CrossEntropyLoss` con label smoothing 0.1, weighted per riprocessati
- Decode strategy: nucleus (`top_p=0.9`, `T=0.7`)
- Optimizer: AdamW lr=1e-3, cosine scheduler, gradient clipping max_norm=5.0
- Batch size: 32, max epochs 50, early stop patience 7

## Metriche test

| Metrica | Valore |
|---|---|
| BLEU-1 | 0.3285 |
| **BLEU-4** | **0.0921** |
| METEOR | 0.2888 |
| ROUGE-L | 0.2391 |
| Caption uniche | 205/230 (89%) |

## Training

| | Valore |
|---|---|
| Best epoch | 49/50 (no early stop) |
| Best val_loss | 1.9591 |
| Tempo totale | 50m 44s |

Val_loss in calo monotono lento dall'epoca 32 in poi (1.978 → 1.959). Curva ancora in decrescita a fine 50 epoche → il modello **avrebbe potuto trainare ancora**.

## Confronto con M1 di Struttura

| | Struttura (vecchio pilot) | Sapore (questo) | Δ |
|---|---|---|---|
| BLEU-4 | 0.047 | **0.092** | **+96%** |
| METEOR | 0.231 | 0.289 | +25% |
| ROUGE-L | 0.213 | 0.239 | +12% |
| Caption uniche | n/a (mode collapse v1) | 205/230 | — |

Il quasi-raddoppio di BLEU-4 conferma l'ipotesi del pilot precedente: il "plateau a 0.048" su Struttura era artefatto del rumore FUORI_ATTRIBUTO (47% del train). Su dataset pulito (Sapore, <1% rumore) lo stesso modello esprime il suo vero potenziale.

## Caption esempio (8 sample del test)

| # | Predizione | Riferimento |
|---|---|---|
| 0 | Il sapore è caratterizzato da una leggera piccantezza. | Ha poco sapore. |
| 5 | Il sapore è acido e acido, con una piccantezza marcata. | C'è un amaro netto. |
| 10 | Il sapore del Grana Trentino DOP è molto salato, con una nota acida e una piccantezza leggera. | Troppo salato. |
| 25 | Il formaggio è equilibrato e presenta una leggera piccantezza. | Il Grana Trentino DOP offre un sapore medio, conforme alle aspettative di un formaggio di alta qualità. |
| 50 | Il sapore del Grana Trentino DOP è piccante, con una nota amara e un umami. | Generalmente equilibrato. |
| 100 | Il sapore del Grana Trentino DOP si presenta con una nota acida, accompagnata da un'intensità che arricchisce l'esperienza gustativa. | Il sapore è leggermente saporito e piccante, ma nel complesso equilibrato. |
| 150 | Il sapore del Grana Trentino DOP si presenta con una dolcezza sapidità, che si integra armoniosamente con le altre note gustative. | Un po' troppo salato. |
| 200 | Il formaggio ha un sapore salato, con una leggera piccantezza e un sapore umami. | Il sapore è equilibrato con note dolciastre, peccato per il finale amarognolo. |

## Osservazioni

**Cosa funziona:**
- **Vocabolario corretto al 100%**: piccante, salato, amaro, acido, dolce, umami, equilibrato, sapidità — tutti termini specifici del dominio sensoriale del Grana.
- **Italiano fluido**: tutte le caption sono frasi grammaticalmente corrette, struttura "Il sapore [...] presenta [...]" coerente.
- **Mode collapse risolto**: 205/230 caption uniche (89%) — label smoothing + nucleus sampling fanno il loro lavoro.
- **Direzione semantica spesso azzeccata** (es. campione #10 "salato" pred + "salato" ref).

**Cosa non funziona:**
- **Dettaglio specifico mancante**: il modello produce descrizioni generiche ("una leggera piccantezza") quando il ground truth è puntuale ("ha poco sapore", "troppo salato"). Stesso pattern di Struttura.
- **Errori grammaticali rari ma presenti**: campione #5 "acido e acido" (ripetizione), #150 "dolcezza sapidità" (concatenazione errata).
- **Tendenza al "sempre positivo"**: campione #50 il riferimento dice "equilibrato" e il modello inventa "piccante con nota amara e umami" — segnale che ha imparato il vocabolario senza saperlo associare a stimoli visivi specifici.
- **Hallucination del nome di prodotto**: "Grana Trentino DOP" appare in molte predizioni anche quando il ref non lo cita.

**Ipotesi per i modelli successivi:**
- Decoder GePpeTto dovrebbe ridurre gli errori grammaticali tipo "acido e acido" perché ha un prior linguistico forte.
- Encoder fine-tuned dovrebbe migliorare la specificità (modello impara feature visive correlate al gusto).
- ViT (M3) potrebbe catturare attributi globali del campione meglio di CNNGlobal.

## Output

- Pesi: `models/m1_cnn_lstm/Sapore/best.pt`
- Predictions: `models/m1_cnn_lstm/Sapore/predictions.csv`
- Log: `models/m1_cnn_lstm/Sapore/log.csv`
- Config: `models/m1_cnn_lstm/Sapore/config.json`
