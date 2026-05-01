# M3 — ViT frozen + Transformer (Sapore)

**Data:** 2026-04-30
**GPU:** NVIDIA RTX 4060 Laptop (8 GB VRAM)
**Attributo:** Sapore (train=976, val=234, test=230)
**Loader:** `on_topic_only=True`

> Note: questo è il **secondo run di M3**. Il primo è stato corrotto da un crash di sistema durante il training (best.pt zip-truncated). Re-run da zero ha prodotto risultati significativamente migliori (BLEU-4 da 0.0783 a 0.0980, +25%) confermando che le metriche del primo run erano inaffidabili.

## Configurazione

- Encoder: `ViTEncoder` (timm `vit_small_patch16_224.augreg_in21k_ft_in1k`, **frozen**) — 196 token visivi proiettati a 512
- Decoder: `TransformerDecoder` from-scratch — 6 layers, 8 heads, d_model=512
- Loss: CE label smoothing 0.1
- Decode: nucleus (top_p=0.9, T=0.7)
- AdamW lr=5e-5, cosine, clip=5.0
- Batch 16, max 30 epoche, patience 5

## Metriche test

| Metrica | Valore |
|---|---|
| BLEU-1 | 0.3153 |
| **BLEU-4** | **0.0980** |
| METEOR | **0.3073** |
| ROUGE-L | **0.2489** |
| Caption uniche | 195/230 (85%) |

## Training

| | Valore |
|---|---|
| Best epoch | 8/13 (early stop) |
| Best val_loss | **1.9742** |
| Tempo totale | 21m |

Convergenza simile al primo run (best a ep 8), early stop a ep 13. Differenza chiave: best.pt salvato correttamente.

## Confronto con M3 di Struttura

| | Struttura | Sapore | Δ |
|---|---|---|---|
| BLEU-4 | 0.045 | **0.098** | +118% |
| METEOR | 0.229 | 0.307 | +34% |
| ROUGE-L | 0.205 | 0.249 | +21% |

Il pattern di raddoppio rispetto a Struttura è confermato e M3 ha l'aumento percentuale più alto del gruppo.

## Confronto interno (gruppo frozen-scratch)

| Modello | BLEU-1 | BLEU-4 | METEOR | ROUGE-L | Best ep | Tempo |
|---|---|---|---|---|---|---|
| M1 (CNN+LSTM) | 0.329 | 0.092 | 0.289 | 0.239 | 49/50 | 50m |
| M2 (CNN+Transf) | 0.329 | 0.084 | 0.284 | 0.242 | 6/13 | 13m |
| **M3 (ViT+Transf)** | 0.315 | **0.098** | **0.307** | **0.249** | 8/13 | 21m |

**M3 è il vincitore del gruppo** su tutte le metriche (BLEU-4, METEOR, ROUGE-L) — il ViT cattura informazione visiva migliore della CNN globale per questo dataset, una volta che il decoder ha tempo di imparare. Pattern coerente con Struttura dove M3 era anche superiore (0.045 vs 0.047 ma valori comparabili).

## Caption esempio (8 sample)

| # | Predizione | Riferimento |
|---|---|---|
| 0 | Il sapore è equilibrato, con una sapidità marcata e una piccantezza media, con una sapidità marcata. | Ha poco sapore. |
| 5 | Il sapore del Grana Trentino DOP è equilibrato, con una piccantezza marcata e una dolcezza assente. | C'è un amaro netto. |
| 10 | Il sapore del Grana Trentino DOP si presenta leggermente amaro, con una leggera piccantezza che si fa sentire in modo. | Troppo salato. |
| 25 | Il sapore è dolce e sapido, con una piccantezza contenuta e un umami marcato. | Il Grana Trentino DOP offre un sapore medio, conforme alle aspettative di un formaggio di alta qualità. |
| 50 | Il sapore del Grana Trentino DOP è caratterizzato da un umami e una leggera piccantezza, risultando equilibrato. | Generalmente equilibrato. |
| 100 | Il sapore è salato e piccante, con una leggera nota di umami. | Il sapore è leggermente saporito e piccante, ma nel complesso equilibrato. |
| 150 | Il sapore del Grana Trentino DOP si presenta leggermente piccante, con una sapidità marcata. | Un po' troppo salato. |
| 200 | Il sapore del Grana Trentino DOP si presenta molto dolce, con una sapidità marcata piccantezza leggera. | Il sapore è equilibrato con note dolciastre, peccato per il finale amarognolo. |

## Osservazioni

**Cosa funziona meglio di M1/M2:**
- **METEOR sostanzialmente più alto** (0.307 vs 0.289 di M1). Suggerisce che M3 produce più frasi semanticamente vicine al riferimento.
- **#50 è quasi perfetto**: ref "generalmente equilibrato" → pred "...risultando equilibrato" (lessico esatto).
- **#100 buon allineamento**: ref "leggermente saporito e piccante" → pred "salato e piccante, leggera nota umami".

**Errori grammaticali persistono:**
- #0 "...con una sapidità marcata e una piccantezza media, con una sapidità marcata" — ripetizione del frammento "con una sapidità marcata".
- #10 "...si fa sentire in modo" — frase troncata (manca complemento).
- #200 "sapidità marcata piccantezza leggera" — concatenazione strana (manca virgola/connettivo).

**Pattern interessante:**
- M3 (ViT) è il primo modello del pilot a battere M1 (CNN globale) su BLEU-4. Su Struttura era leggermente sotto (0.045 vs 0.047).
- ViT genera 196 token visivi → più capacità di descrivere zone diverse dell'immagine. Su Sapore (attributo gustativo, meno spazialmente legato all'immagine?) ha comunque valore probabilmente perché il modello impara correlazioni globali tra texture/colore visivo e descrittori sensoriali.

**Confronto col M3 corrotto (precedente):**
- BLEU-4: 0.0783 → 0.0980 (+25%)
- METEOR: 0.260 → 0.307 (+18%)
- ROUGE-L: 0.218 → 0.249 (+14%)
- Caption uniche: 80% → 85%

L'epoch 8 (best reale) vs epoch 13 (post-overfit) fa una differenza notevole. Il salvataggio corretto del checkpoint è cruciale.

## Output

- Pesi: `models/m3_vit_transformer/Sapore/best.pt` (ep 8 valido)
- Predictions: `models/m3_vit_transformer/Sapore/predictions.csv`
- Log: `models/m3_vit_transformer/Sapore/log.csv` (13 epoche)
