# Cumulativo 2 — Encoder frozen × Decoder GePpeTto (Sapore)

**Data:** 2026-05-01 (aggiornato con M5c)
**Modelli inclusi:** M5a, M5b, M5c (12/12 completati)
**Cella 2×2:** [Encoder frozen, Decoder GePpeTto]

## Tabella metriche

| Modello | Architettura | BLEU-1 | BLEU-4 | METEOR | ROUGE-L | Best ep | Tempo | Uniche |
|---|---|---|---|---|---|---|---|---|
| M5a | CNN(g) frozen + GePpeTto | 0.308 | 0.090 | 0.274 | 0.231 | 9/16 | 21m | 87% |
| M5b | CNNSpatial frozen + GePpeTto | 0.327 | 0.100 | 0.292 | 0.248 | 8/15 | 23m | 88% |
| **M5c** | ViT frozen + GePpeTto 🥈 | 0.316 | **0.112** | **0.320** ⬅ TOP | **0.261** | 8 | ~47m | 90% |
| **Media (n=3)** | — | **0.317** | **0.101** | **0.295** | **0.247** | — | — | 88% |

## Cella 2×2 vs Struttura

|  | Struttura (vecchio pilot) | Sapore (questo) | Δ |
|---|---|---|---|
| BLEU-4 medio | 0.048 | **0.101** | **+110%** |
| METEOR medio | 0.227 | 0.295 | +30% |
| ROUGE-L medio | 0.220 | 0.247 | +12% |

## Pattern osservati

### M5c > M5b > M5a (BLEU-4)
- M5a (CNNGlobal, 1 token): 0.090
- M5b (CNNSpatial, 98 token): 0.100
- M5c (ViT, 196 token): 0.112

**Più token visivi = miglior BLEU-4.** GePpeTto sa sfruttare prefix multi-token strutturati.

### METEOR top per M5c
M5c (0.320) > M5b (0.292) > M5a (0.274). ViT genera caption più sinonimicamente vicine ai riferimenti.

### Caption uniche alte (87-90%)
GePpeTto frozen produce caption più diversificate del decoder scratch (in particolare di M3-FT che aveva 72%).

### Val_loss molto bassa
- M5a: 1.542
- M5b: 1.549
- M5c: 1.578
- vs ~1.96 del frozen-scratch

GePpeTto modella meglio la distribuzione token italiani.

## Confronto cumulativo_1 vs cumulativo_2

| | Frozen × scratch | Frozen × GePpeTto | Δ |
|---|---|---|---|
| BLEU-4 medio | 0.091 | **0.101** | +11% |
| METEOR medio | 0.293 | 0.295 | +1% |
| ROUGE-L medio | 0.243 | 0.247 | +2% |

**GePpeTto frozen aiuta su BLEU-4** (+11%) ma marginalmente su METEOR/ROUGE-L. Il guadagno è guidato principalmente da M5c.

## Conclusioni

**M5c è la combinazione vincente di questa cella** e secondo classificato del pilot completo (BLEU-4=0.112, METEOR=0.320). Conferma che ViT cattura informazione visiva di qualità superiore a CNN, e che GePpeTto frozen amplifica questo vantaggio mantenendo un prior linguistico forte.

Vedi `confronto_modelli_finale_sapore.md` per la sintesi completa del pilot.
