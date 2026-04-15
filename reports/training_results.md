# Risultati Training — Grana Trentino Image Captioning

Dataset: `data/processed/dataset_captioning.csv` | Split: 70/15/15 per campione fisico

## M1 (CNN+LSTM)

| Attributo | Best Epoch | BLEU-1 | BLEU-4 | METEOR | ROUGE-L |
|---|---|---|---|---|---|
| Aroma | — | — | — | — | — |
| Profumo | — | — | — | — | — |
| Sapore | — | — | — | — | — |
| Texture | — | — | — | — | — |
| Struttura_della_Pasta | 50 | 0.3833 | 0.0472 | 0.2309 | 0.2567 |
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
| Struttura_della_Pasta | 7 | 0.3619 | 0.0420 | 0.2490 | 0.2244 |
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
| Struttura_della_Pasta | 9 | 0.3773 | 0.0435 | 0.2250 | 0.2416 |
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

## Confronto medie (per-attributo, escluso global)

| Modello | BLEU-1 | BLEU-4 | METEOR | ROUGE-L |
|---|---|---|---|---|
| M1 (CNN+LSTM) | 0.3833 | 0.0472 | 0.2309 | 0.2567 |
| M2 (CNN+Transformer) | 0.3619 | 0.0420 | 0.2490 | 0.2244 |
| M3 (ViT+Transformer) | 0.3773 | 0.0435 | 0.2250 | 0.2416 |
| M4 (BLIP fine-tuned) | — | — | — | — |
