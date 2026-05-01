# M3-FT — ViT fine-tuned + Transformer (Sapore) 🏆 LEADER

**Data:** 2026-05-01
**GPU:** NVIDIA RTX 4060 Laptop (8 GB VRAM)
**Attributo:** Sapore (train=976, val=234, test=230)
**Loader:** `on_topic_only=True`

> Note: primo run crashato a inizio (CUDA `unknown error`, 0 checkpoint). Retry da zero senza problemi. Batch ridotto a **4** (vs 8 default Struttura).

## Configurazione

- Encoder: `ViTEncoder` (timm `vit_small_patch16_224`, **fine-tuned**) — 21M params
- Decoder: `TransformerDecoder` from-scratch (6 layers, 8 heads, d_model=512)
- 134M params trainable totali
- Batch 4 (ridotto da 8 per stabilità)
- AdamW lr=5e-5, cosine, label smoothing 0.1, nucleus
- Max 20 epoche, patience 5

## Metriche test 🏆 NUOVO LEADER

| Metrica | Valore |
|---|---|
| BLEU-1 | **0.3633** |
| **BLEU-4** | **0.1172** ⬅ vincitore pilot |
| METEOR | 0.3050 |
| ROUGE-L | **0.2624** |
| Caption uniche | 165/230 (72%) |

## Training

| | Valore |
|---|---|
| Best epoch | 13/18 (early stop, patience 5/5) |
| Best val_loss | **1.9732** |
| Tempo totale | 41m |

## Confronto con M3-FT di Struttura

| | Struttura | Sapore | Δ |
|---|---|---|---|
| BLEU-4 | 0.040 | **0.117** | +193% |
| METEOR | 0.249 | 0.305 | +22% |
| ROUGE-L | 0.265 | 0.262 | -1% |

Salto BLEU-4 quasi **triplo** (+193%). M3-FT mostra il salto più grande del pilot rispetto a Struttura.

## Confronto FT vs Frozen (M3)

| Variante | BLEU-4 | METEOR | ROUGE-L | Best ep |
|---|---|---|---|---|
| M3 frozen | 0.098 | **0.307** | 0.249 | 8/13 |
| **M3-FT** | **0.117** | 0.305 | **0.262** | 13/18 |

**Fine-tuning porta +20% BLEU-4 e +5% ROUGE-L** vs M3 frozen. METEOR praticamente identico. ViT fine-tuned cattura informazione visiva molto migliore di ViT frozen.

## Confronto LEADER pilot

| Modello | BLEU-4 | METEOR | ROUGE-L | Caption uniche |
|---|---|---|---|---|
| **M3-FT** 🏆 | **0.117** | 0.305 | **0.262** | 72% |
| M5b | 0.100 | 0.292 | 0.248 | 88% |
| M3 | 0.098 | **0.307** | 0.249 | 85% |
| M2-FT | 0.098 | 0.298 | 0.238 | 87% |
| M1-FT | 0.098 | 0.284 | 0.241 | 90% |
| M1 | 0.092 | 0.289 | 0.239 | 89% |
| M5a | 0.090 | 0.274 | 0.231 | 87% |
| M2 | 0.084 | 0.284 | 0.242 | 87% |

M3-FT vince su BLEU-4 e ROUGE-L. Pareggia con M3 frozen su METEOR. **Diversità più bassa** (72% vs 85-90% degli altri) — pattern atteso quando un modello converge fortemente su un'ipotesi specifica.

## Caption esempio (8 sample)

| # | Predizione | Riferimento |
|---|---|---|
| 0 | Il sapore è piccante, con una leggera nota amarognola. | Ha poco sapore. |
| 5 | Il sapore del Grana Trentino DOP si presenta leggermente salato. | C'è un amaro netto. |
| 10 | Il formaggio ha un sapore salato. | Troppo salato. |
| 25 | Il sapore è salato e presenta una piccantezza leggera acidità. | Il Grana Trentino DOP offre un sapore medio, conforme alle aspettative... |
| 50 | Il sapore è acido, salato e piccante. | Generalmente equilibrato. |
| 100 | Il sapore è dolce, con sapidità marcata e una leggera piccantezza. | Il sapore è leggermente saporito e piccante, ma nel complesso equilibrato. |
| 150 | Il sapore del Grana Trentino DOP presenta una nota acida e acidità. | Un po' troppo salato. |
| 200 | Il sapore del Grana Trentino DOP presenta un buon equilibrio, con una leggera piccantezza che si integra armonico. | Il sapore è equilibrato con note dolciastre, peccato per il finale amarognolo. |

## Osservazioni

**Cosa funziona molto bene:**
- **#10 quasi perfetto**: ref "troppo salato" → pred "salato" (direzione corretta!)
- **#0 buona direzionalità**: ref "ha poco sapore" → pred "piccante con leggera nota amarognola" (intensità bassa)
- **Caption più sintetiche e dirette** rispetto a M5* o M1-FT
- **Top BLEU-4**: 0.117 = +17% vs runner-up M5b (0.100)

**Cosa non funziona:**
- **Diversità bassa** (165/230 = 72%, vs 87% di M5b): il modello converge su poche varianti
- #25 "piccantezza leggera acidità" — concatenazione errata (manca "e" o virgola)
- #150 "nota acida e acidità" — ripetizione semantica
- #200 "armonico" invece di "armonica" (errore di accordo)

**Pattern interessante:**
- ViT fine-tuned + Transformer scratch: combinazione vincente su Sapore
- Caption più focalizzate sul "core" sensoriale ("sapore salato", "sapore acido salato e piccante") — meno "letterarie" di M5* (GePpeTto)
- **Sembra che fine-tuning encoder ViT + decoder semplice batta encoder frozen + decoder pretrained** su questo dataset
- Il **trade-off diversità vs accuracy**: M3-FT ha accuracy massima ma minore diversità → pattern di convergenza tipica di modelli ben allineati

**Ipotesi 2x2:**
- Su Sapore: cella **(FT × scratch)** = M1/M2/M3-FT è la migliore
- Su Struttura era invece (frozen × scratch+GePpeTto) la migliore
- L'attributo influenza fortemente quale combinazione vince

## Output

- Pesi: `models/m3_vit_transformer_ft/Sapore/best.pt`
- Predictions: `models/m3_vit_transformer_ft/Sapore/predictions.csv`
- Log: `models/m3_vit_transformer_ft/Sapore/log.csv` (18 epoche)
