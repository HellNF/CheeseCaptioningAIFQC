# Cumulativo 3 — Encoder fine-tuned × Decoder from-scratch (Sapore)

**Data:** 2026-05-01
**Modelli inclusi:** M1-FT, M2-FT, M3-FT (9/12 completati)
**Cella 2×2:** [Encoder fine-tuned, Decoder from-scratch]

## Tabella metriche

| Modello | Architettura | BLEU-1 | BLEU-4 | METEOR | ROUGE-L | Best ep | Tempo | Uniche |
|---|---|---|---|---|---|---|---|---|
| M1-FT | CNN(g) ft + LSTM | 0.339 | 0.098 | 0.284 | 0.241 | 30/30 | 24m | 90% |
| M2-FT | CNN(g) ft + Transformer | 0.309 | 0.098 | 0.298 | 0.238 | 9/16 | 17m | 87% |
| **M3-FT** | ViT ft + Transformer 🏆 | **0.363** | **0.117** | **0.305** | **0.262** | 13/18 | 41m | 72% |
| **Media** | — | **0.337** | **0.105** | **0.296** | **0.247** | — | — | 83% |

## Cella 2×2 vs Struttura

|  | Struttura (vecchio pilot) | Sapore (questo) | Δ |
|---|---|---|---|
| BLEU-4 medio | 0.042 | **0.105** | **+150%** |
| METEOR medio | 0.242 | 0.296 | +22% |
| ROUGE-L medio | 0.225 | 0.247 | +10% |

Il salto più grande tra le celle (vs +93% del frozen-scratch). La cella **FT × scratch è la migliore di Sapore**.

## Cumulativo 1 vs Cumulativo 3 — l'effetto fine-tuning

| | Frozen × scratch | FT × scratch | Δ |
|---|---|---|---|
| BLEU-4 medio | 0.091 | **0.105** | +15% |
| METEOR medio | 0.293 | 0.296 | +1% |
| ROUGE-L medio | 0.243 | 0.247 | +2% |

**Fine-tuning encoder porta +15% BLEU-4** ma quasi nessun guadagno su METEOR/ROUGE-L. Pattern opposto a Struttura, dove FT peggiorava BLEU-4 (-5%).

## Pattern osservati nel gruppo

### 1. M3-FT = vincitore assoluto
- Top BLEU-4 del pilot completo (0.117)
- Top BLEU-1 (0.363) e ROUGE-L (0.262)
- ViT fine-tuned + Transformer scratch è la combinazione vincente

### 2. M1-FT e M2-FT pareggiano (BLEU-4 = 0.098)
- LSTM e Transformer producono risultati equivalenti su BLEU-4
- M2-FT vince su METEOR (0.298 vs 0.284)
- M1-FT vince su BLEU-1 (0.339 vs 0.309)
- LSTM produce caption più diverse (90% uniche), Transformer più focalizzato

### 3. Diversità decrescente con FT
- Frozen-scratch: 87% caption uniche medie
- FT-scratch: 83% medie
- M3-FT: 72% (sotto la media — converge fortemente)
- Il fine-tuning riduce la varianza: il modello "sceglie" pattern più ricorrenti

### 4. Direzionalità migliorata
Esempi presi dai 3 report:
- M1-FT #5: ref "amaro netto" → "leggera nota amarognola" ✓
- M2-FT #100: ref "leggermente saporito" → "sapido" ✓
- M3-FT #10: ref "troppo salato" → "salato" ✓

I modelli FT azzeccano la **direzione** del giudizio meglio degli equivalenti frozen.

### 5. Errori grammaticali persistenti ma diversi
- M1-FT: rari (50/50 epoche, ottimo training)
- M2-FT: "umami marcata" (accordo), "risultando il palato" (frase tronca)
- M3-FT: "piccantezza leggera acidità" (concatenazione), "armonico" (accordo)

Pattern simile al gruppo frozen-scratch, ma in proporzione meno errori (mode collapse più pronunciato → meno output strani).

## Confronto con Struttura (cella per cella)

| | Frozen × scratch | FT × scratch | Frozen × GePpeTto | FT × GePpeTto |
|---|---|---|---|---|
| **Struttura** | 0.044 | 0.042 | 0.048 | 0.043 |
| **Sapore** | 0.091 | **0.105** | 0.097* | TBD |

*M5a (0.090) + M5b (0.100) = 0.095 medio (M5c skip).

**Pattern Sapore**: cella vincitrice = FT × scratch (0.105). Su Struttura era frozen × GePpeTto (0.048). **Inversione completa**.

## Implicazione: il pattern 2x2 dipende dall'attributo

- Su Struttura (rumoroso e visivamente complesso) il decoder pre-trained GePpeTto compensa la mancanza di fine-tuning encoder
- Su Sapore (pulito e con vocabolario più semplice) il fine-tuning encoder vince — non serve GePpeTto

Possibile spiegazione: le caption Sapore usano vocabolario più ridotto (~10 termini chiave: salato, dolce, amaro, acido, piccante, umami, equilibrato, sapido, marcato, leggero) mentre Struttura usa vocabolario più ricco e tecnico (microocchiatura, tirosina, friabile, frattura, ecc.). Per Sapore basta un decoder semplice; per Struttura serve la fluenza di GePpeTto.

## Stato pilot

Completati: 9/12 modelli + 1 skip (M5c).
Tempo totale finora: ~3h locali + retry.

Restanti: M5a-FT, M5b-FT, M5c-FT (cella FT × GePpeTto).

## Ipotesi per il prossimo gruppo (FT × GePpeTto, M5a-FT, M5b-FT, M5c-FT)

Domanda chiave: **GePpeTto + encoder fine-tuned è meglio di scratch + encoder fine-tuned?**

Su Struttura il pattern era: cumulare FT + GePpeTto NON migliorava (0.043 vs 0.042 FT-scratch e 0.048 frozen-GePpeTto). L'unione delle due tecniche era controproducente.

Su Sapore aspettativa: **probabilmente uguale o leggermente peggio di FT × scratch (0.105)**. GePpeTto produce caption più verbose e meno mirate; con encoder già fine-tuned non aggiunge valore.

Se confermato, conferma che **il fine-tuning encoder e il decoder pre-trained sono alternative, non complementari**.
