# Training Report - Struttura_della_Pasta
Data: 2026-04-23 00:14
GPU: NVIDIA RTX 4060 Laptop (8 GB VRAM)

## Nuovi modelli

| Modello | Descrizione | BLEU-1 | BLEU-4 | METEOR | ROUGE-L | Best Epoch | Tempo |
|---|---|---|---|---|---|---|---|
| M5b-FT | CNNSpatial (fine-tuned) + GePpeTto | 0.3405 | 0.0392 | 0.2255 | 0.2209 | 8 | 33m 47s |

**Totale:** 33m 47s

## Confronto completo

| Modello | BLEU-1 | BLEU-4 | METEOR | ROUGE-L |
|---|---|---|---|---|
| M1 | 0.2138 | 0.0472 | 0.2309 | 0.2130 |
| M2 | 0.2104 | 0.0405 | 0.2286 | 0.2084 |
| M3 | 0.2022 | 0.0445 | 0.2289 | 0.2048 |
| M5b-FT | 0.3405 | 0.0392 | 0.2255 | 0.2209 |
| M4 BLIP | 0.2298 | 0.0483 | 0.2712 | 0.2301 |
| Baseline (retrieval) | 0.1312 | 0.0213 | 0.1548 | 0.1322 |
| Baseline (freq-weighted) | 0.0937 | 0.0068 | 0.1129 | 0.0924 |

## Design fattoriale 2x2 (media BLEU-4)

|  | Decoder from scratch | Decoder GePpeTto |
|---|---|---|
| **Encoder frozen** | 0.0441 (n=3) | -- |
| **Encoder fine-tuned** | -- | 0.0392 (n=1) |
