# M2-FT — CNN fine-tuned + Transformer (Sapore)

**Data:** 2026-05-01
**GPU:** NVIDIA RTX 4060 Laptop (8 GB VRAM)
**Attributo:** Sapore (train=976, val=234, test=230)
**Loader:** `on_topic_only=True`

## Configurazione

- Encoder: `CNNEncoderGlobal` (ResNet-50 ImageNet, **fine-tuned**)
- Decoder: `TransformerDecoder` from-scratch (6 layers, 8 heads, d_model=512)
- 72M params trainable
- Batch 8 (ridotto da 16 per stabilità)
- AdamW lr=1e-4, cosine, label smoothing 0.1, nucleus (top_p=0.9, T=0.7)
- Max 30 epoche, patience 7

## Metriche test

| Metrica | Valore |
|---|---|
| BLEU-1 | 0.3093 |
| **BLEU-4** | **0.0983** |
| METEOR | 0.2976 |
| ROUGE-L | 0.2379 |
| Caption uniche | 201/230 (87%) |

## Training

| | Valore |
|---|---|
| Best epoch | 9/16 (early stop, patience 7/7) |
| Best val_loss | **1.9465** |
| Tempo totale | 17m |

Convergenza rapida (best ep 9), poi overfitting. Pattern simile a M2 frozen che era best ep 6/13.

## Confronto con M2-FT di Struttura

| | Struttura | Sapore | Δ |
|---|---|---|---|
| BLEU-4 | 0.037 | **0.098** | +166% |
| METEOR | 0.244 | 0.298 | +22% |

Il salto BLEU-4 più grande del pilot finora (+166%).

## Confronto FT vs Frozen (M2)

| Variante | BLEU-4 | METEOR | ROUGE-L | Best ep | Tempo |
|---|---|---|---|---|---|
| M2 frozen | 0.084 | 0.284 | 0.242 | 6/13 | 13m |
| **M2-FT** | **0.098** | **0.298** | 0.238 | 9/16 | 17m |

**Fine-tuning porta +17% BLEU-4 e +5% METEOR** vs M2 frozen. Su Sapore l'encoder fine-tuned aiuta significativamente. Pattern coerente con M1 (FT > frozen) e opposto a Struttura (FT < frozen).

## Caption esempio (8 sample)

| # | Predizione | Riferimento |
|---|---|---|
| 0 | Il sapore è equilibrato, ma presenta una dolcezza ben definita. | Ha poco sapore. |
| 5 | Il sapore è acido, con una sapidità prevalente, un umami marcata. | C'è un amaro netto. |
| 10 | C'è un leggero sapore amaro. | Troppo salato. |
| 25 | Il sapore è salato, con una leggera piccantezza. | Il Grana Trentino DOP offre un sapore medio, conforme alle aspettative di un formaggio di alta qualità. |
| 50 | Il sapore è leggermente piccante, ma presenta un finale amarognolo che emerge in gola. | Generalmente equilibrato. |
| 100 | Il sapore è sapido, con note di umami e una leggera piccantezza. | Il sapore è leggermente saporito e piccante, ma nel complesso equilibrato. |
| 150 | Il sapore è piccante, ma non persiste, risultando il palato. | Un po' troppo salato. |
| 200 | Il sapore è salato, con una leggera piccantezza. | Il sapore è equilibrato con note dolciastre, peccato per il finale amarognolo. |

## Osservazioni

**Cosa funziona:**
- **METEOR migliore di M1-FT** (0.298 vs 0.284). M2-FT produce caption più semanticamente vicine ai riferimenti.
- **#100 quasi perfetto**: ref "leggermente saporito e piccante" → pred "sapido con leggera piccantezza" — coincidenza lessicale alta.
- **Caption ricche**: #50 "presenta un finale amarognolo che emerge in gola" — costruzione idiomatica sofisticata.

**Errori grammaticali persistono:**
- #5 "umami marcata" — accordo aggettivo errato (umami è maschile/invariabile)
- #150 "ma non persiste, risultando il palato" — frase troncata/strana

**Direzionalità:**
- #10: ref "troppo salato" → pred "leggero sapore amaro" — sbagliato
- #200: ref "dolciastre... amarognolo" → pred "salato con piccantezza" — sbagliato
- Pattern stesso degli altri modelli.

**Confronto con altri FT:**
- M1-FT: BLEU-4=0.098, METEOR=0.284
- **M2-FT: BLEU-4=0.098, METEOR=0.298** (più alto METEOR del gruppo FT-scratch finora)
- Su Sapore il Transformer batte LSTM su METEOR ma sono praticamente equivalenti su BLEU-4

## Output

- Pesi: `models/m2_cnn_transformer_ft/Sapore/best.pt`
- Predictions: `models/m2_cnn_transformer_ft/Sapore/predictions.csv`
- Log: `models/m2_cnn_transformer_ft/Sapore/log.csv` (16 epoche)
