# M1-FT — CNN fine-tuned + LSTM (Sapore)

**Data:** 2026-04-30 / 2026-05-01 (resumed)
**GPU:** NVIDIA RTX 4060 Laptop (8 GB VRAM)
**Attributo:** Sapore (train=976, val=234, test=230)
**Loader:** `on_topic_only=True`

> Nota: training crashato a ep 11 con CUDA `illegal memory access`, ripreso da `last.pt` (ep 11) con `--resume` dopo riavvio del PC. Run continuata 12-30 senza ulteriori crash. Batch ridotto a **8** (vs 16 del pilot Struttura) per stabilità.

## Configurazione

- Encoder: `CNNEncoderGlobal` (ResNet-50 ImageNet, **fine-tuned**) — 25M params encoder + LSTM ≈ 50M trainable
- Decoder: `LSTMDecoder` from-scratch
- Loss: CE label smoothing 0.1
- Decode: nucleus (top_p=0.9, T=0.7)
- AdamW lr=1e-4, cosine, clip=5.0
- **Batch 8** (ridotto da 16 per stabilità GPU laptop)
- Max 30 epoche, patience 7

## Metriche test

| Metrica | Valore |
|---|---|
| BLEU-1 | 0.3390 |
| **BLEU-4** | **0.0980** |
| METEOR | 0.2836 |
| ROUGE-L | 0.2409 |
| Caption uniche | 206/230 (90%) |

## Training

| | Valore |
|---|---|
| Best epoch | 30/30 (no early stop) |
| Best val_loss | **2.0380** |
| Tempo totale | 24m |

Val_loss in calo costante 2.30 → 2.04 — il modello stava ancora migliorando, **avrebbe potuto trainare oltre 30 epoche**. Niente overfitting.

## Confronto con M1-FT di Struttura

| | Struttura | Sapore | Δ |
|---|---|---|---|
| BLEU-4 | 0.048 | **0.098** | +103% |
| METEOR | 0.232 | 0.284 | +22% |
| ROUGE-L | 0.221 | 0.241 | +9% |

Pattern coerente con frozen-scratch: dataset pulito raddoppia BLEU-4.

## Confronto FT vs Frozen (M1)

| Variante | BLEU-4 | METEOR | ROUGE-L | Best ep |
|---|---|---|---|---|
| M1 frozen | 0.092 | 0.289 | 0.239 | 49/50 |
| **M1-FT** | 0.098 | 0.284 | 0.241 | 30/30 |

**Fine-tuning encoder porta +6% BLEU-4** ma -2% METEOR. Il pattern di Struttura ("FT peggiora BLEU-4") **non si manifesta su Sapore**. Possibile spiegazione:
- Su Struttura il rumore FUORI_ATTRIBUTO confondeva il fine-tuning (encoder imparava feature non discriminanti)
- Su Sapore (dati puliti) l'encoder può specializzarsi sui veri segnali visivi correlati al gusto

## Caption esempio (8 sample)

| # | Predizione | Riferimento |
|---|---|---|
| 0 | Il sapore è leggermente salato e piccante. | Ha poco sapore. |
| 5 | Il sapore è caratterizzato da una leggera nota amarognola. | C'è un amaro netto. |
| 10 | Il sapore presenta un buon equilibrio, ma non è dolce, con una leggera piccantezza. | Troppo salato. |
| 25 | Il sapore presenta una nota amara. | Il Grana Trentino DOP offre un sapore medio, conforme alle aspettative di un formaggio di alta qualità. |
| 50 | Il sapore è leggermente salato e presenta una piccantezza. | Generalmente equilibrato. |
| 100 | Il sapore del Grana Trentino DOP è caratterizzato da una leggera acidità. | Il sapore è leggermente saporito e piccante, ma nel complesso equilibrato. |
| 150 | Il sapore è equilibrato, con una leggera piccantezza. | Un po' troppo salato. |
| 200 | Il sapore è caratterizzato da una sapidità marcata. | Il sapore è equilibrato con note dolciastre, peccato per il finale amarognolo. |

## Osservazioni

**Cosa migliora rispetto a M1 frozen:**
- **Caption più sintetiche** (vedi #25 "una nota amara" vs M1 frozen "il sapore presenta una grana grossolana e una grana grossolana")
- **Diversità più alta** (90% uniche vs 89% di M1 frozen)
- **Direzionalità leggermente migliore**:
  - #5: ref "amaro netto" → pred "leggera nota amarognola" (correttamente in direzione amaro)
  - #10: ref "troppo salato" → pred "non è dolce, con leggera piccantezza" (almeno non dolce, ma manca salato)

**Persiste:**
- Errori grammaticali rari ma presenti (nessuno nei sample mostrati)
- Hallucination "Grana Trentino DOP" (#100) come template
- Direzionalità ancora incerta: #0 "ha poco sapore" → "salato e piccante" (sbagliato), #50 "equilibrato" → "salato con piccantezza" (parziale)

**Pattern key:**
- M1-FT è il **secondo migliore BLEU-4 del pilot dopo M5b** (0.098 vs 0.100). 
- Su 7 modelli completati, l'ordine è: M5b (0.100) > M3 ≈ M1-FT (0.098) > M1 (0.092) > M5a (0.090) > M2 (0.084) > M2 (0.084)
- L'encoder fine-tuning aiuta su Sapore (a differenza di Struttura) — primo segnale che il pattern del 2x2 Sapore potrebbe essere diverso da quello di Struttura.

## Output

- Pesi: `models/m1_cnn_lstm_ft/Sapore/best.pt`
- Predictions: `models/m1_cnn_lstm_ft/Sapore/predictions.csv`
- Log: `models/m1_cnn_lstm_ft/Sapore/log.csv` (30 epoche)
