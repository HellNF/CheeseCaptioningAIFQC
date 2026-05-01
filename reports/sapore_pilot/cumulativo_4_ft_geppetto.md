# Cumulativo 4 — Encoder fine-tuned × Decoder GePpeTto (Sapore)

**Data:** 2026-05-01
**Modelli inclusi:** M5a-FT, M5b-FT, M5c-FT (12/12 modelli pilot completati)
**Cella 2×2:** [Encoder fine-tuned, Decoder GePpeTto]

## Tabella metriche

| Modello | Architettura | BLEU-1 | BLEU-4 | METEOR | ROUGE-L | Best ep | Tempo | Uniche |
|---|---|---|---|---|---|---|---|---|
| M5a-FT | CNN(g) ft + GePpeTto | 0.323 | 0.092 | **0.296** | 0.245 | 9/16 | 22m | 90% |
| **M5b-FT** | CNNSpatial ft + GePpeTto | **0.349** | **0.100** | 0.294 | 0.244 | 7/14 | 22m | 87% |
| M5c-FT | ViT ft + GePpeTto | 0.327 | 0.098 | 0.294 | 0.246 | 13/15 | 70m | 90% |
| **Media** | — | **0.333** | **0.097** | **0.295** | **0.245** | — | — | 89% |

## Cella 2×2 vs Struttura

|  | Struttura (vecchio pilot) | Sapore (questo) | Δ |
|---|---|---|---|
| BLEU-4 medio | 0.043 | **0.097** | **+126%** |
| METEOR medio | 0.232 | 0.295 | +27% |
| ROUGE-L medio | 0.222 | 0.245 | +10% |

Salto medio +126% su BLEU-4. Pattern coerente con tutte le altre celle.

## Pattern osservati

### Risultati molto omogenei
- BLEU-4 di M5a-FT, M5b-FT, M5c-FT in range stretto: 0.092 - 0.100 - 0.098
- METEOR praticamente identico: 0.296 - 0.294 - 0.294
- ROUGE-L: 0.245 - 0.244 - 0.246

**L'architettura encoder (CNN globale, CNNSpatial, ViT) cambia poco** quando entrambi encoder e decoder sono fine-tuned con GePpeTto pre-trained. Il decoder GePpeTto fine-tuned **livella** le differenze tra encoder.

### Differenza chiave da cumulativo_3 (FT × scratch)

| | FT × scratch | FT × GePpeTto |
|---|---|---|
| BLEU-4 medio | **0.105** | 0.097 |
| METEOR medio | 0.296 | 0.295 |
| Range BLEU-4 | 0.098-0.117 | 0.092-0.100 |

Il decoder scratch produce **outlier vincente** (M3-FT 0.117) mentre GePpeTto produce risultati uniformi ma sotto. Questo è l'opposto del pattern Struttura.

### Errori grammaticali persistenti
- M5a-FT #5: "una sapidità contenuta e una sapidità marcata"
- M5b-FT #5: "piccantezza e una leggera piccantezza"
- M5c-FT #50: "sapidità marcata, con una sapidità marcata, una sapidità medio alta" (3 ripetizioni!)

GePpeTto non risolve il problema delle ripetizioni semantiche. Anzi, M5c-FT (modello più grande) ha il caso peggiore — più capacità non implica meglio quando il dataset è piccolo.

### Diversità alta
- M5a-FT 90%, M5b-FT 87%, M5c-FT 90%
- vs M3-FT 72% (vincitore con scratch)
- I modelli FT × GePpeTto producono caption più diversificate ma meno accurate

## Confronto 2x2 finale (medie BLEU-4)

|  | Decoder scratch | Decoder GePpeTto | Effetto decoder |
|---|---|---|---|
| Encoder frozen | 0.091 | 0.095 | **+0.004** |
| Encoder fine-tuned | **0.105** | 0.097 | **-0.008** |
| Effetto encoder | **+0.014** | **+0.002** | |

### Effetto principale 1: Encoder fine-tuning
- Decoder scratch: +0.014 BLEU-4 (+15%)
- Decoder GePpeTto: +0.002 BLEU-4 (+2%)
- **Encoder fine-tuning aiuta solo con decoder scratch.** Con GePpeTto il guadagno si annulla.

### Effetto principale 2: Decoder GePpeTto
- Encoder frozen: +0.004 BLEU-4 (+4%)
- Encoder fine-tuned: -0.008 BLEU-4 (-7%)
- **GePpeTto aiuta solo con encoder frozen.** Con encoder ft peggiora.

### Interazione negativa
Le due tecniche (FT encoder + GePpeTto) **non sono additive**: si "rubano" il guadagno a vicenda. Coerente con Struttura ma con magnitudo diversa.

## Conclusione cumulativo 4

La cella **FT × GePpeTto è la peggiore di Sapore** (BLEU-4 medio 0.097). Combinare le due tecniche di "potenziamento" (encoder fine-tuning + decoder pre-trained) **non funziona** su questo dataset piccolo (976 train).

**Vincitore Sapore confermato**: M3-FT (FT × scratch, BLEU-4 = 0.117).

Per il report finale del pilot vedi `confronto_modelli_finale_sapore.md`.
