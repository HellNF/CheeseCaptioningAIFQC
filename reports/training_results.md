# Risultati Training — Grana Trentino Image Captioning

Dataset: `data/processed/dataset_captioning.csv` | Split: 70/15/15 per campione fisico

## M1 (CNN+LSTM)

| Attributo | Best Epoch | BLEU-1 | BLEU-4 | METEOR | ROUGE-L |
|---|---|---|---|---|---|
| Aroma | — | — | — | — | — |
| Profumo | — | — | — | — | — |
| Sapore | — | — | — | — | — |
| Texture | — | — | — | — | — |
| Struttura_della_Pasta | 50 | 0.3833 | 0.0472 | 0.2309 | 0.2566 |
| Colore_della_Pasta | — | — | — | — | — |
| Spessore_della_Crosta | — | — | — | — | — |
| global | — | — | — | — | — |

## M2 (CNN+Transformer)

| Attributo | Best Epoch | BLEU-1 | BLEU-4 | METEOR | ROUGE-L |
|---|---|---|---|---|---|
| Aroma | — | — | — | — | — |
| Profumo | — | — | — | — | — |
| Sapore | — | — | — | — | — |
| Texture | — | — | — | — | — |
| Struttura_della_Pasta | 7 | 0.3619 | 0.0420 | 0.2490 | 0.2242 |
| Colore_della_Pasta | — | — | — | — | — |
| Spessore_della_Crosta | — | — | — | — | — |
| global | — | — | — | — | — |

## M3 (ViT+Transformer)

| Attributo | Best Epoch | BLEU-1 | BLEU-4 | METEOR | ROUGE-L |
|---|---|---|---|---|---|
| Aroma | — | — | — | — | — |
| Profumo | — | — | — | — | — |
| Sapore | — | — | — | — | — |
| Texture | — | — | — | — | — |
| Struttura_della_Pasta | 9 | 0.3773 | 0.0435 | 0.2250 | 0.2417 |
| Colore_della_Pasta | — | — | — | — | — |
| Spessore_della_Crosta | — | — | — | — | — |
| global | — | — | — | — | — |

## M4 (BLIP fine-tuned)

| Attributo | Best Epoch | BLEU-1 | BLEU-4 | METEOR | ROUGE-L |
|---|---|---|---|---|---|
| Aroma | — | — | — | — | — |
| Profumo | — | — | — | — | — |
| Sapore | — | — | — | — | — |
| Texture | — | — | — | — | — |
| Struttura_della_Pasta | — | — | — | — | — |
| Colore_della_Pasta | — | — | — | — | — |
| Spessore_della_Crosta | — | — | — | — | — |
| global | — | — | — | — | — |

## M1-FT (CNN+LSTM)

| Attributo | Best Epoch | BLEU-1 | BLEU-4 | METEOR | ROUGE-L |
|---|---|---|---|---|---|
| Aroma | — | — | — | — | — |
| Profumo | — | — | — | — | — |
| Sapore | — | — | — | — | — |
| Texture | — | — | — | — | — |
| Struttura_della_Pasta | — | — | — | — | — |
| Colore_della_Pasta | — | — | — | — | — |
| Spessore_della_Crosta | — | — | — | — | — |
| global | — | — | — | — | — |

## M2-FT (CNN+Transformer)

| Attributo | Best Epoch | BLEU-1 | BLEU-4 | METEOR | ROUGE-L |
|---|---|---|---|---|---|
| Aroma | — | — | — | — | — |
| Profumo | — | — | — | — | — |
| Sapore | — | — | — | — | — |
| Texture | — | — | — | — | — |
| Struttura_della_Pasta | — | — | — | — | — |
| Colore_della_Pasta | — | — | — | — | — |
| Spessore_della_Crosta | — | — | — | — | — |
| global | — | — | — | — | — |

## M3-FT (ViT+Transformer)

| Attributo | Best Epoch | BLEU-1 | BLEU-4 | METEOR | ROUGE-L |
|---|---|---|---|---|---|
| Aroma | — | — | — | — | — |
| Profumo | — | — | — | — | — |
| Sapore | — | — | — | — | — |
| Texture | — | — | — | — | — |
| Struttura_della_Pasta | — | — | — | — | — |
| Colore_della_Pasta | — | — | — | — | — |
| Spessore_della_Crosta | — | — | — | — | — |
| global | — | — | — | — | — |

## Baseline (random)

| Attributo | Best Epoch | BLEU-1 | BLEU-4 | METEOR | ROUGE-L |
|---|---|---|---|---|---|
| Aroma | — | 0.2701 | 0.0527 | 0.2035 | 0.1653 |
| Profumo | — | 0.2746 | 0.0428 | 0.1812 | 0.1706 |
| Sapore | — | 0.2900 | 0.0644 | 0.2114 | 0.1736 |
| Texture | — | 0.3053 | 0.0396 | 0.2185 | 0.1750 |
| Struttura_della_Pasta | — | 0.2431 | 0.0110 | 0.1513 | 0.1303 |
| Colore_della_Pasta | — | 0.3070 | 0.0881 | 0.2378 | 0.2144 |
| Spessore_della_Crosta | — | 0.2642 | 0.1016 | 0.1709 | 0.1337 |
| global | — | — | — | — | — |

## Baseline (most-frequent)

| Attributo | Best Epoch | BLEU-1 | BLEU-4 | METEOR | ROUGE-L |
|---|---|---|---|---|---|
| Aroma | — | 0.4915 | 0.0000 | 0.1124 | 0.0602 |
| Profumo | — | 0.4516 | 0.0211 | 0.1647 | 0.1767 |
| Sapore | — | 0.4040 | 0.0000 | 0.1152 | 0.0835 |
| Texture | — | 0.4399 | 0.0712 | 0.2253 | 0.2527 |
| Struttura_della_Pasta | — | 0.1687 | 0.0000 | 0.0953 | 0.0644 |
| Colore_della_Pasta | — | 0.3506 | 0.0113 | 0.1378 | 0.1177 |
| Spessore_della_Crosta | — | 0.2626 | 0.0000 | 0.0997 | 0.0661 |
| global | — | — | — | — | — |

## Baseline (freq-weighted)

| Attributo | Best Epoch | BLEU-1 | BLEU-4 | METEOR | ROUGE-L |
|---|---|---|---|---|---|
| Aroma | — | 0.2319 | 0.0295 | 0.1688 | 0.1247 |
| Profumo | — | 0.2544 | 0.0267 | 0.1548 | 0.1465 |
| Sapore | — | 0.2942 | 0.0715 | 0.2265 | 0.1854 |
| Texture | — | 0.2999 | 0.0393 | 0.2243 | 0.1772 |
| Struttura_della_Pasta | — | 0.2637 | 0.0179 | 0.1689 | 0.1498 |
| Colore_della_Pasta | — | 0.2952 | 0.0665 | 0.2212 | 0.2047 |
| Spessore_della_Crosta | — | 0.2512 | 0.0950 | 0.1830 | 0.1539 |
| global | — | — | — | — | — |

## Baseline (retrieval)

| Attributo | Best Epoch | BLEU-1 | BLEU-4 | METEOR | ROUGE-L |
|---|---|---|---|---|---|
| Aroma | — | 0.2298 | 0.0442 | 0.2067 | 0.1672 |
| Profumo | — | 0.2526 | 0.0299 | 0.1641 | 0.1592 |
| Sapore | — | 0.2517 | 0.0441 | 0.2015 | 0.1719 |
| Texture | — | 0.3352 | 0.0370 | 0.2097 | 0.1825 |
| Struttura_della_Pasta | — | 0.2576 | 0.0236 | 0.1777 | 0.1678 |
| Colore_della_Pasta | — | 0.3040 | 0.0606 | 0.2065 | 0.1926 |
| Spessore_della_Crosta | — | 0.2203 | 0.0636 | 0.1758 | 0.1422 |
| global | — | — | — | — | — |

## Confronto medie (per-attributo, escluso global)

| Modello | BLEU-1 | BLEU-4 | METEOR | ROUGE-L |
|---|---|---|---|---|
| M1 (CNN+LSTM) | 0.3833 | 0.0472 | 0.2309 | 0.2566 |
| M2 (CNN+Transformer) | 0.3619 | 0.0420 | 0.2490 | 0.2242 |
| M3 (ViT+Transformer) | 0.3773 | 0.0435 | 0.2250 | 0.2417 |
| M4 (BLIP fine-tuned) | — | — | — | — |
| M1-FT (CNN+LSTM) | — | — | — | — |
| M2-FT (CNN+Transformer) | — | — | — | — |
| M3-FT (ViT+Transformer) | — | — | — | — |
| Baseline (random) | 0.2792 | 0.0572 | 0.1964 | 0.1661 |
| Baseline (most-frequent) | 0.3670 | 0.0148 | 0.1358 | 0.1173 |
| Baseline (freq-weighted) | 0.2701 | 0.0495 | 0.1925 | 0.1632 |
| Baseline (retrieval) | 0.2645 | 0.0433 | 0.1917 | 0.1691 |
