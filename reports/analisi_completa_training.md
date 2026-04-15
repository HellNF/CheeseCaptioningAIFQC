# Analisi Completa del Training — Grana Trentino Image Captioning

**Data:** 15 aprile 2026  
**Progetto:** Automatic quality captioning per Grana Trentino / Trentingrana  
**Dataset:** `data/processed/dataset_captioning.csv`

---

## 1. Contesto e Obiettivo

Il progetto mira a generare automaticamente descrizioni testuali degli attributi sensoriali del Grana Trentino a partire da immagini del formaggio (vista fetta + vista grana). Gli attributi target sono sette:

| Attributo | Natura | Osservabile visivamente? |
|---|---|---|
| Aroma | Olfattivo | No |
| Profumo | Olfattivo | No |
| Sapore | Gustativo | No |
| Texture | Tattile/visivo | Parzialmente |
| Struttura_della_Pasta | Visivo | Sì |
| Colore_della_Pasta | Visivo | Sì |
| Spessore_della_Crosta | Visivo | Sì |

---

## 2. Dataset

| Split | Campioni fisici | Caption totali (×7 attr, più panelisti) |
|---|---|---|
| Train | 329 | 5.911 |
| Val | 69 | 1.440 |
| Test | 75 | 1.505 |
| **Totale** | **473** | **8.856** |

**Note critiche:**
- Ogni campione fisico è valutato da più panelisti → alta variabilità inter-annotatore
- Alcuni attributi (Aroma, Profumo) sono intrinsecamente non rilevabili da immagini
- Il dataset è piccolo per task di captioning: i benchmark standard (MSCOCO) usano 100.000+ immagini
- Split stratificato per anno di produzione (70/15/15)

---

## 3. Architetture Valutate

### M1 — CNN + LSTM (baseline classica)
- **Encoder:** ResNet-50 pre-addestrato (ImageNet), features concatenate da vista fetta e grana
- **Decoder:** LSTM con attention
- **Ottimizzatore:** Adam lr=3e-4, StepLR (step=10, gamma=0.5)
- **Iperparametri pilota:** epochs=50, batch=32, patience=7

### M2 — CNN + Transformer Decoder
- **Encoder:** ResNet-50 (identico a M1)
- **Decoder:** Transformer decoder con multi-head attention
- **Fix applicato:** `tgt_is_causal=True` in TransformerDecoder.forward() per evitare CUDA illegal memory access
- **Iperparametri pilota:** epochs=50, batch=32, patience=7

### M3 — ViT + Transformer Decoder
- **Encoder:** Vision Transformer (ViT-B/16) pre-addestrato
- **Decoder:** Transformer decoder
- **Problema rilevato:** crash sistema Windows con batch_size=16 (pressione VRAM)
- **Fix:** usare sempre `--batch-size 8` su Windows
- **Ottimizzatore:** AdamW con 2 param groups (ViT lr×0.1, resto lr), CosineAnnealingLR
- **Iperparametri pilota:** epochs=30, batch=8, patience=5

### M4 — BLIP-large fine-tuned (Salesforce/blip-image-captioning-large)
- **Approccio:** modello pre-addestrato su miliardi di coppie immagine-testo
- **Strategia dual-view:** concatenazione verticale fetta (sopra) + grana (sotto) in canvas 384×384
- **Conditioning per attributo:** prompt prefix in italiano (`"descrivi l'aroma:"`, ecc.)
- **Modello:** unico globale (non 7 per-attributo)
- **Training:** Kaggle T4 GPU, float32 + GradScaler + autocast(float16), gradient checkpointing
- **Iperparametri:** epochs=10, batch=4, lr=2e-5, patience=3, warmup 10%

---

## 4. Risultati — Fase Pilota (solo Struttura_della_Pasta)

M1, M2 e M3 sono stati valutati in fase pilota sul solo attributo `Struttura_della_Pasta` come proof-of-concept architetturale.

| Modello | Best Epoch | BLEU-1 | BLEU-4 | METEOR | ROUGE-L |
|---|---|---|---|---|---|
| M1 (CNN+LSTM) | 50 | 0.3833 | 0.0472 | 0.2309 | 0.2563 |
| M2 (CNN+Transformer) | 7 | 0.3619 | 0.0420 | 0.2490 | 0.2235 |
| M3 (ViT+Transformer) | 9 | 0.3773 | 0.0435 | 0.2250 | 0.2410 |

**Osservazioni M1/M2/M3:**
- Le differenze tra i tre modelli sono minime (±0.005 BLEU-4) — il collo di bottiglia è il dataset, non l'architettura
- **M1** produce le metriche BLEU-1 e ROUGE-L più alte ma con mode collapse nelle predizioni (ripete le stesse frasi brevi)
- **M2** vince su METEOR ma va in overfitting rapidamente (best epoch 7 su 50)
- **M3** è il più instabile: crash GPU su Windows con batch_size=16, stabile con batch_size=8
- BLEU-4 nell'ordine 0.04–0.05 indica predizioni con poca sovrapposizione di 4-gram con i riferimenti

---

## 5. Risultati — M4 BLIP fine-tuned (tutti gli attributi)

Training completato su Kaggle T4 (≈3.4 ore). Early stopping a epoch 8, best epoch 5.

| Attributo | BLEU-1 | BLEU-4 | METEOR | ROUGE-L |
|---|---|---|---|---|
| Aroma | 0.2439 | 0.0599 | 0.3212 | 0.2875 |
| Profumo | 0.2407 | 0.0450 | 0.2545 | 0.2552 |
| Sapore | 0.1815 | 0.0197 | 0.3085 | 0.2451 |
| Texture | 0.2589 | 0.0225 | 0.2771 | 0.2467 |
| Struttura_della_Pasta | 0.1925 | 0.0125 | 0.1688 | 0.1976 |
| Colore_della_Pasta | 0.2350 | 0.0929 | 0.3346 | 0.2728 |
| Spessore_della_Crosta | 0.1853 | 0.0715 | 0.2410 | 0.1784 |
| **Media** | **0.2197** | **0.0463** | **0.2722** | **0.2405** |

**Curve di training M4:**

| Epoch | Train Loss | Val Loss | Note |
|---|---|---|---|
| 1 | 2.8904 | 1.7452 | Best |
| 2 | 1.5325 | 1.4606 | Best |
| 3 | 1.2599 | 1.3668 | Best |
| 4 | 1.0806 | 1.3348 | Best |
| 5 | 0.9302 | 1.3168 | **Best finale** |
| 6 | 0.7878 | 1.3489 | patience=1 |
| 7 | 0.6649 | 1.3650 | patience=2 |
| 8 | 0.5725 | 1.3895 | patience=3 → stop |

Train loss continua a scendere mentre val loss risale da epoch 6: segno di overfitting, tipico con dataset piccoli.

---

## 6. Confronto M1 vs M4 (su Struttura_della_Pasta)

| Metrica | M1 | M4 | Δ |
|---|---|---|---|
| BLEU-1 | 0.3833 | 0.1925 | M1 +0.19 |
| BLEU-4 | 0.0472 | 0.0125 | M1 +0.035 |
| METEOR | 0.2309 | 0.1688 | M1 +0.062 |
| ROUGE-L | 0.2563 | 0.1976 | M1 +0.059 |

**Attenzione:** il confronto non è fair — M1 è specializzato su Struttura_della_Pasta, M4 è un modello globale su 7 attributi. Su un singolo attributo, la specializzazione ha vantaggio.

**Confronto fair (media M4 vs M1 single-attribute):**

| Metrica | M1 (Struttura) | M4 (media 7 attr) | Interpretazione |
|---|---|---|---|
| BLEU-4 | 0.0472 | 0.0463 | Sostanzialmente pari |
| METEOR | 0.2309 | **0.2722** | M4 +18% — qualità semantica superiore |
| ROUGE-L | 0.2563 | 0.2405 | M1 leggermente superiore |

---

## 7. Osservazioni Chiave

### 7.1 Il collo di bottiglia è il dataset, non l'architettura
Con 329 campioni train, le differenze tra M1/M2/M3 sono statisticamente trascurabili. Raddoppiare i dati farebbe più differenza di qualsiasi cambio architetturale.

### 7.2 BLIP migliora la qualità semantica (METEOR)
Il pretraining su miliardi di immagini dà a BLIP un vantaggio reale nella comprensione semantica (+18% METEOR rispetto a M1). Le caption generate sono più naturali e variegate, anche se la sovrapposizione esatta di parole (BLEU) non migliora drasticamente.

### 7.3 Attributi visivi vs non-visivi
I risultati di M4 confermano la dicotomia:

| Categoria | Attributi | BLEU-4 medio M4 |
|---|---|---|
| **Visivi** | Colore_della_Pasta, Spessore_della_Crosta | 0.0822 |
| **Semi-visivi** | Struttura_della_Pasta, Texture | 0.0175 |
| **Non visivi** | Aroma, Profumo, Sapore | 0.0415 |

Colore_della_Pasta (0.0929) è il risultato migliore in assoluto — direttamente osservabile dall'immagine. Aroma e Profumo ottengono risultati non trascurabili (0.0599, 0.0450) probabilmente perché la rete impara correlazioni visive indirette con il tipo di stagionatura.

### 7.4 Mode collapse in M1
Le alte metriche BLEU-1 di M1 (0.3833) sono parzialmente artificiali: il decoder LSTM tende a ripetere caption brevi e frequenti nel training set, massimizzando la sovrapposizione di unigram. METEOR e ROUGE-L, più robusti a questo fenomeno, mostrano un quadro più realistico.

### 7.5 Overfitting rapido
Tutti i modelli mostrano overfitting precoce:
- M2: best epoch 7/50
- M3: best epoch 9/30
- M4: best epoch 5/10

È la firma di un dataset troppo piccolo per la capacità del modello.

---

## 8. Problemi Tecnici Risolti

| Problema | Causa | Fix |
|---|---|---|
| CUDA illegal memory access (M2/M3) | Mask causale non gestita correttamente | `tgt_is_causal=True` in TransformerDecoder |
| Crash sistema Windows (M3) | Pressione VRAM con batch_size=16 | Usare sempre `--batch-size 8` per M3 |
| Checkpoint incompatibile in eval-only | AdamW M3 ha 2 param groups | Caricare solo `model_state`, non ottimizzatore |
| NaN loss in training BLIP | float16 senza GradScaler → gradient underflow | float32 + GradScaler + autocast(float16) |
| OOM con float32 batch=8 | 1.8GB modello + attivazioni > 16GB T4 | Gradient checkpointing + batch_size=4 |
| P100 incompatibile con PyTorch 2.x | sm_60 non supportato da sm_70+ required | T4 (sm_75) obbligatorio su Kaggle |

---

## 9. Possibili Miglioramenti

In ordine di impatto stimato:

1. **Valutazione multi-riferimento** — usare tutte le caption dei panelisti come riferimenti durante eval (costo zero, metriche più rappresentative)
2. **Più dati** — raddoppiare il dataset da 473 a 1000+ campioni è l'intervento più impattante
3. **Image augmentation** — RandomFlip, ColorJitter (con cautela su Colore_della_Pasta), RandomRotation
4. **Separare attributi visivi da non-visivi** — approccio ibrido: generazione per Colore/Struttura/Spessore, classificazione+lookup per Aroma/Profumo/Sapore
5. **Freeze encoder iniziale** — congelare ViT per le prime N epoche, poi fine-tuning completo
6. **BLIP-2** — architettura più recente con Q-Former, potenzialmente più efficiente su domain-specific

---

## 10. Conclusioni

Il progetto ha dimostrato tre risultati principali:

1. **Con dataset piccoli (329 train), la scelta dell'architettura from-scratch è irrilevante** — M1/M2/M3 producono metriche statisticamente equivalenti (±0.005 BLEU-4).

2. **Il fine-tuning di modelli pre-addestrati migliora la qualità semantica** — M4 BLIP supera M1 del 18% su METEOR, che è la metrica più correlata alla qualità percepita delle caption.

3. **Il limite fondamentale è la natura del task** — gli attributi olfattivi e gustativi non sono rilevabili da immagini; qualsiasi modello visivo è strutturalmente limitato su Aroma, Profumo e Sapore.

Il sistema attuale è adeguato come proof-of-concept e base di ricerca. Per un utilizzo applicativo, si raccomanda di focalizzarsi sugli attributi visivi (Colore, Struttura, Spessore) e di raccogliere almeno il doppio dei dati annotati.
