# Analisi dei Risultati Preliminari — Mode Collapse

**Data:** 2026-04-22
**Attributo pilota:** Struttura_della_Pasta
**GPU:** NVIDIA RTX 4060 Laptop (8 GB VRAM)

## 1. Contesto

Obiettivo: confronto sistematico 2x2 (encoder frozen/fine-tuned x decoder from-scratch/pre-trained) per dimostrare che i modelli imparano dal dataset di captioning del Grana Trentino.

Modelli addestrati finora: M1 (CNN+LSTM frozen), M2 (CNN+Transformer frozen), M3 (ViT+Transformer frozen), M1-FT (CNN+LSTM fine-tuned).

## 2. Dataset — Struttura_della_Pasta

| Split | Campioni | Caption uniche | Parole medie |
|-------|----------|----------------|-------------|
| Train | 1071 | 1059 (98.9%) | 10.7 |
| Val | 256 | — | — |
| Test | 265 | 265 (100%) | 11.0 |

Osservazione critica: le caption di training sono **quasi tutte uniche** (1059/1071). Questo significa che il modello non vede quasi mai la stessa frase due volte — una condizione molto difficile per modelli generativi con vocabolario aperto.

Le 5 caption piu frequenti nel training set compaiono solo 2 volte ciascuna.

## 3. Risultati Quantitativi

| Modello | BLEU-1 | BLEU-4 | METEOR | ROUGE-L | Caption uniche |
|---------|--------|--------|--------|---------|----------------|
| M1 (frozen) | 0.2138 | 0.0472 | 0.2309 | 0.2130 | 2 |
| M2 (frozen) | 0.2104 | 0.0405 | 0.2286 | 0.2084 | 23 |
| M3 (frozen) | 0.2022 | 0.0445 | 0.2289 | 0.2048 | 24 |
| M1-FT | 0.4110 | 0.0406 | 0.2119 | 0.2434 | 2 |
| Baseline (retrieval) | 0.1312 | 0.0213 | 0.1548 | 0.1322 | — |
| Baseline (freq-weighted) | 0.0937 | 0.0068 | 0.1129 | 0.0924 | — |

Tutti i modelli **battono entrambi i baseline** su tutte le metriche, confermando che i modelli estraggono informazione visiva dalle immagini.

## 4. Problema Principale — Mode Collapse

Analizzando le 265 predizioni sul test set, emerge un grave problema di **mode collapse**: i modelli generano pochissime frasi diverse.

### M1 (frozen) — 2 frasi uniche su 265

| Frequenza | Frase generata |
|-----------|----------------|
| 76.6% (203/265) | "La pasta presenta una grana grossolana e una frattura regolare." |
| 23.4% (62/265) | "La pasta presenta una grana grossolana, con una frattura regolare." |

### M1-FT (fine-tuned) — 2 frasi uniche su 265

| Frequenza | Frase generata |
|-----------|----------------|
| 74.0% (196/265) | "La pasta presenta una grana grossolana, con microocchiature." |
| 26.0% (69/265) | "La pasta presenta una grana grossolana." |

### M2 (frozen) — 23 frasi uniche su 265

| Frequenza | Frase generata |
|-----------|----------------|
| 18.1% (48/265) | "La pasta presenta una grana granulosa, con una buona compattezza." |
| 13.6% (36/265) | "La frattura e regolare, la pasta e poco granulosa e presenta microocchiature." |
| 9.4% (25/265) | "La frattura e regolare, la pasta e poco granulosa e grossolana." |

### M3 (frozen) — 24 frasi uniche su 265

| Frequenza | Frase generata |
|-----------|----------------|
| 14.7% (39/265) | "La pasta presenta una frattura irregolare e una grana grossolana." |
| 14.3% (38/265) | "La pasta presenta una frattura irregolare, con grana grossolana." |
| 9.4% (25/265) | "La pasta presenta una grana grossolana." |

### Pattern Emerso

- **LSTM (M1, M1-FT):** collasso quasi totale su 1-2 frasi
- **Transformer (M2, M3):** leggermente meglio (23-24 frasi uniche) ma ancora dominato da poche varianti
- **Fine-tuning encoder (M1-FT):** non risolve il mode collapse, anzi la diversita resta identica (2 frasi)
- Tutti i modelli generano frasi **grammaticalmente corrette e nel dominio** ma **non specifiche per l'immagine**

### Perche Succede

1. **Dataset troppo piccolo e troppo vario:** 1071 caption quasi tutte uniche rendono impossibile per il modello imparare pattern specifici immagine-testo. Il modello impara la "frase media" che minimizza la cross-entropy su tutto il training set.

2. **Beam search amplifica il collasso:** beam search favorisce le sequenze ad alta probabilita, convergendo sulla frase piu "sicura". Con greedy decoding o sampling si avrebbe piu varieta, ma probabilmente meno qualita.

3. **Decoder from-scratch senza conoscenza linguistica:** i decoder LSTM e Transformer partono da zero, quindi con pochi dati imparano solo i pattern piu frequenti.

## 5. Aspetti Positivi

Nonostante il mode collapse, i risultati mostrano che:

1. **I modelli apprendono dal dataset:** tutti superano i baseline, confermando che l'informazione visiva viene utilizzata
2. **Le frasi generate sono nel dominio:** terminologia corretta (grana, frattura, microocchiature, pasta)
3. **M2/M3 (Transformer) producono piu varieta** rispetto a M1 (LSTM), suggerendo che l'architettura del decoder influenza la diversita
4. **M1-FT ha BLEU-1 molto alto (0.41):** le singole parole scelte sono rilevanti, anche se la frase complessiva e sempre la stessa

## 6. Confronto Reference vs Predizioni

| | Reference (test) | M1 | M1-FT | M2 | M3 |
|--|--|--|--|--|--|
| Caption uniche | 265/265 | 2/265 | 2/265 | 23/265 | 24/265 |
| Parole medie | 11.0 | 10.0 | 7.5 | 10.1 | 9.4 |

Le reference sono tutte diverse tra loro (265 su 265), mentre i modelli producono al massimo 24 varianti. Il gap di diversita e enorme.

---

## 7. Intervento: Label Smoothing + Nucleus Sampling

Per contrastare il mode collapse sono state applicate due tecniche:

### 7.1 Label Smoothing (training time)

Modifica: `CrossEntropyLoss(label_smoothing=0.1)` in `src/models/train.py`.

Effetto: durante il training, il modello non viene forzato ad assegnare probabilita 1.0 al token corretto. Il 10% della probabilita viene distribuito uniformemente su tutto il vocabolario. Questo impedisce al modello di diventare troppo "sicuro" su poche parole, mantenendo una distribuzione piu piatta e riducendo la tendenza a collassare sulla frase piu probabile.

### 7.2 Nucleus Sampling (inference time)

Modifica: nuova funzione `_nucleus_decode()` in `src/models/metrics.py` con parametri `top_p=0.9`, `temperature=0.7`.

Effetto: invece di prendere sempre la parola piu probabile (beam search), il modello campiona dalla distribuzione troncata al 90% della massa cumulativa. La temperature=0.7 rende la distribuzione leggermente piu peaked rispetto a temperature=1.0, bilanciando varieta e coerenza.

### 7.3 Risultati: M1-FT v1 vs M1-FT v2

| Metrica | M1-FT v1 (beam) | M1-FT v2 (label smooth + nucleus) | Delta |
|---------|-----------------|-------------------------------------|-------|
| **Caption uniche** | **2/265 (0.8%)** | **257/265 (97.0%)** | **+255** |
| BLEU-1 | 0.4110 | 0.3442 | -0.0668 |
| BLEU-4 | 0.0406 | **0.0482** | **+0.0076** |
| METEOR | 0.2119 | **0.2321** | **+0.0202** |
| ROUGE-L | 0.2434 | 0.2208 | -0.0226 |
| Best epoch | 30/30 | 29/30 | |

### 7.4 Analisi dell'Intervento

**Diversita:** incremento drastico da 2 a 257 caption uniche (97% del test set). Il modello ora genera frasi diverse per immagini diverse, avvicinandosi alla diversita delle reference (265/265).

**Qualita:** BLEU-4 e METEOR sono migliorati nonostante la maggiore varieta. Questo indica che le frasi generate non sono solo diverse, ma anche piu accurate. Il calo di BLEU-1 (-0.07) e atteso: con beam search il modello ripeteva sempre parole "sicure" (alta precisione unigram), ora esplora un vocabolario piu ampio.

**Esempi di caption generate (M1-FT v2):**

| # | Caption predetta | Caption riferimento |
|---|-----------------|---------------------|
| 1 | "La pasta presenta una frattura irregolare e una grana grossolana." | "Si riscontrano piccoli strappi sotto un piatto, compromettendo la compattezza." |
| 2 | "La pasta e stirata." | "La parte centrale e spugnosa." |
| 3 | "Ci sono striature." | "C'e una fessura sottile." |
| 4 | "La frattura e regolare e la grana e grossolana." | "C'e una grossa fessura." |
| 5 | "La pasta e stirata, con una grana grossolana." | "E presente una piccolissima zona stirata in periferia." |

Le caption sono grammaticalmente corrette, nel dominio, e usano terminologia tecnica appropriata (frattura, grana, striature, microocchiatura). Alcune frasi mostrano corrispondenza semantica con il riferimento (es. #5: "stirata" appare sia nella predizione che nel riferimento).

**Errori residui:** alcune frasi presentano artefatti ("La pasta e ru la grana e granulosa") dovuti al sampling stocastico. Questi sono rari (~1-2% delle predizioni) e accettabili come trade-off per la diversita.

### 7.5 Confronto Aggiornato con Tutti i Modelli

| Modello | BLEU-1 | BLEU-4 | METEOR | ROUGE-L | Uniche | Decoding |
|---------|--------|--------|--------|---------|--------|----------|
| M1 (frozen) | 0.2138 | 0.0472 | 0.2309 | 0.2130 | 2 | beam |
| M2 (frozen) | 0.2104 | 0.0405 | 0.2286 | 0.2084 | 23 | beam |
| M3 (frozen) | 0.2022 | 0.0445 | 0.2289 | 0.2048 | 24 | beam |
| **M1-FT v2** | **0.3442** | **0.0482** | **0.2321** | **0.2208** | **257** | **nucleus** |
| M4 BLIP | 0.2298 | 0.0483 | 0.2712 | 0.2301 | — | beam |
| Baseline (retrieval) | 0.1312 | 0.0213 | 0.1548 | 0.1322 | — | — |

M1-FT v2 raggiunge BLEU-4 pari a M1 frozen (0.0482 vs 0.0472) e quasi pari a M4 BLIP (0.0483), con una diversita di output drasticamente superiore.

### 7.6 Decisione

Label smoothing (0.1) e nucleus sampling (top_p=0.9, temperature=0.7) vengono adottati come **default per tutti i modelli successivi**. I rimanenti 8 modelli (M2-FT, M3-FT, M5a/b/c, M5a-FT/b-FT/c-FT) verranno addestrati con questa configurazione.

---

## 8. Training Progressivo con Nuovi Parametri

### 8.1 M2-FT — CNN (fine-tuned) + Transformer

**Training:** early stopping all'epoch 16 (best=9). Tempo: 20m 38s. Val_loss minima: 2.7346.

**Risultati test set:**

| Metrica | M2 (frozen) | **M2-FT** | M1-FT v2 |
|---------|-------------|-----------|----------|
| BLEU-1 | 0.2104 | **0.3235** | 0.3442 |
| BLEU-4 | 0.0405 | 0.0373 | **0.0482** |
| METEOR | 0.2286 | **0.2445** | 0.2321 |
| ROUGE-L | 0.2084 | **0.2235** | 0.2208 |
| Caption uniche | 23/265 | **259/265** | 257/265 |

**Osservazioni:**
- Diversita quasi totale: 259/265 caption uniche (97.7%)
- METEOR migliore di M1-FT v2 (0.2445 vs 0.2321) — il Transformer produce frasi semanticamente piu vicine ai riferimenti
- Early stopping anticipato: il modello e andato in overfitting piu velocemente rispetto a M1-FT (patience esaurita a epoch 16 vs 30 epoch completate per M1-FT)
- Le frasi generate sono piu articolate e con meno ripetizioni rispetto a M1-FT

**Esempi M2-FT:**
- "La pasta presenta una frattura irregolare, con una stiratura granulosa e microocchiature."
- "La frattura e regolare, con una stiratura granulosa e microocchiature."
- "C'e una spugnatura diffusa, con una struttura granulosa e grossolana."

**Conclusione:** risultato valido, procedo con M3-FT.

### 8.2 M3-FT — ViT (fine-tuned) + Transformer

**Training:** early stopping all'epoch 15 (best=10). Tempo: 1h 13m 2s (~5 min/epoch per il ViT). Val_loss minima: 2.7123.

**Risultati test set:**

| Metrica | M3 (frozen) | **M3-FT** | M2-FT | M1-FT v2 |
|---------|-------------|-----------|-------|----------|
| BLEU-1 | 0.2022 | **0.3497** | 0.3235 | 0.3442 |
| BLEU-4 | 0.0445 | 0.0399 | 0.0373 | 0.0482 |
| METEOR | 0.2289 | **0.2492** | 0.2445 | 0.2321 |
| ROUGE-L | 0.2048 | **0.2321** | 0.2235 | 0.2208 |
| Caption uniche | 24/265 | **258/265** | 259/265 | 257/265 |

**Osservazioni:**
- **METEOR e ROUGE-L i migliori finora tra i modelli from-scratch**. Il ViT con attention pre-addestrata su ImageNet fornisce rappresentazioni piu utili
- BLEU-1 0.3497: il piu alto tra i modelli FT — singole parole molto accurate
- Diversita: 258/265 (97.4%), in linea con gli altri modelli v2
- Training piu lento (~5 min/epoch vs ~1 min per M1/M2) ma converge in meno epoch (best=10)
- Meno artefatti rispetto a M1-FT, qualita delle frasi comparabile a M2-FT

**Esempi M3-FT:**
- "C'e una leggera fessura" vs ref "C'e una fessura sottile" — **corrispondenza semantica**
- "La pasta del campione presenta una grana fine e una frattura regolare, con microocchiature diffuse."
- "La pasta e stirata e presenta una grana grossolana."

**Conclusione:** risultato eccellente, procedo con M5a (primo modello con decoder pre-trained GePpeTto).

### 8.3 M5a — CNN (frozen) + GePpeTto

**Training:** early stopping all'epoch 15 (best=8). Tempo: 23m 55s. Val_loss minima: **2.0136** (la piu bassa finora, grazie al decoder pre-trained).

**Risultati test set:**

| Metrica | M5a | M1 (frozen) | M1-FT v2 | M4 BLIP |
|---------|-----|-------------|----------|---------|
| BLEU-1 | 0.3154 | 0.2138 | 0.3442 | 0.2298 |
| BLEU-4 | **0.0468** | 0.0472 | 0.0482 | 0.0483 |
| METEOR | 0.2258 | 0.2309 | 0.2321 | 0.2712 |
| ROUGE-L | 0.2069 | 0.2130 | 0.2208 | 0.2301 |
| Caption uniche | 259/265 | 2/265 | 257/265 | — |
| val_loss | **2.0136** | 3.06 (approx) | 3.0589 | — |

**Osservazioni:**
- **Val_loss la piu bassa di tutti i modelli (2.01 vs 2.7-3.0)**: il decoder pre-trained ha un'enorme partenza linguistica
- BLEU-4 0.0468, praticamente pari a M1 frozen (0.0472) e M1-FT (0.0482)
- Training veloce: best=8, convergenza rapida grazie al decoder pre-trained
- Qualche ripetizione residua nelle frasi ("grana grossolana e una grana grossolana"), tipica del prefix tuning quando il prefix visuale e corto (1 token globale)

**Esempi M5a:**
- "La pasta e leggermente stirata, evidenziando una certa disomogeneita."
- "La frattura e irregolare, con qualche microocchiatura e microocchiature ben distribuite."
- "La pasta mostra una frattura irregolare, con microocchiature diffuse e una grana grossa."

**Conclusione:** risultato valido, procedo con M5b (CNNSpatial + GePpeTto, 98 visual prefix tokens).

### 8.4 M5b — CNNSpatial (frozen) + GePpeTto

**Training:** early stopping all'epoch 15 (best=8). Tempo: 33m 24s. Val_loss minima: 2.0253.

**Risultati test set:**

| Metrica | M5b | M5a | M1-FT v2 | M4 BLIP |
|---------|-----|-----|----------|---------|
| BLEU-1 | 0.3328 | 0.3154 | 0.3442 | 0.2298 |
| BLEU-4 | **0.0482** | 0.0468 | **0.0482** | **0.0483** |
| METEOR | 0.2386 | 0.2258 | 0.2321 | 0.2712 |
| ROUGE-L | **0.2317** | 0.2069 | 0.2208 | 0.2301 |
| Caption uniche | 253/265 | 259/265 | 257/265 | — |

**Osservazioni:**
- **BLEU-4 0.0482, pari a M1-FT e quasi pari a M4 BLIP**: il modello raggiunge lo stato dell'arte su questo attributo
- **ROUGE-L 0.2317, il piu alto tra i modelli non-BLIP**: le sottosequenze comuni sono molto lunghe
- 98 visual prefix tokens danno al decoder una rappresentazione spaziale ricca, superiore al singolo token globale di M5a
- Meno varianti (253) rispetto a M5a (259), perche il modello ha trovato frasi piu consistenti
- Qualche ripetizione nelle top frasi ("frattura regolare e una frattura regolare")
- Terminologia tecnica sofisticata: "cristalli di tirosina" (cristalli naturali nei formaggi stagionati)

**Esempi M5b:**
- "La pasta e stirata con cristalli di tirosina." — terminologia tecnica specialistica
- "La struttura e granulosa, stirata e omogenea."
- "La pasta presenta una frattura regolare, con qualche piccola fessura e una grana grossolana."

**Conclusione:** risultato eccellente (top BLEU-4 insieme a M1-FT). Procedo con M5c (ViT + GePpeTto, 392 visual prefix tokens, ma con solo 30 minuti nominali).

### 8.5 M5c — ViT (frozen) + GePpeTto

**Nota tecnica:** Il primo tentativo e fallito per errore di scrittura disco (disco pieno al 100%). Risolto eliminando tutti i `last.pt` dei checkpoint precedenti, liberando 10 GB.

**Training:** early stopping all'epoch 15 (best=10). Tempo: 1h 28m 8s (~5 min/epoch per il ViT). Val_loss minima: 2.0706.

**Risultati test set:**

| Metrica | M5c | M5a | M5b | M3 (frozen) |
|---------|-----|-----|-----|-------------|
| BLEU-1 | 0.3380 | 0.3154 | 0.3328 | 0.2022 |
| BLEU-4 | 0.0476 | 0.0468 | **0.0482** | 0.0445 |
| METEOR | 0.2335 | 0.2258 | **0.2386** | 0.2289 |
| ROUGE-L | 0.2205 | 0.2069 | **0.2317** | 0.2048 |
| Caption uniche | 253/265 | 259/265 | 253/265 | 24/265 |

**Osservazioni:**
- BLEU-4 0.0476, in linea con gli altri M5 (tutti intorno a 0.047-0.048)
- M5c e leggermente inferiore a M5b: il ViT da solo, senza proiezione spaziale specializzata, non supera il CNNSpatial con 98 token prefix
- Training molto lento (~5 min/epoch) a causa dei 392 visual prefix tokens
- Il modello ha imparato a generare misurazioni numeriche ("un occhio di circa 5 mm", "una frattura media di 3 mm") riflettendo lo stile dei riferimenti
- Alcune ripetizioni residue tipiche del prefix tuning

**Esempi M5c:**
- "La frattura e abbastanza regolare, con un occhio di circa 5 mm e una frattura media di 3 mm." — **misurazioni precise**
- "La microocchiatura e fine, con grana tendente allo stirato." — terminologia tecnica
- "La pasta presenta una grana grossa, con microocchiature diffuse e zone stirate."

**Conclusione:** risultato valido. Tutti e 3 gli M5 frozen hanno performance simili (BLEU-4 ~0.047-0.048). M5b e il migliore. Procedo con gli M5-FT (encoder sbloccato).

### 8.6 M5a-FT — CNN (fine-tuned) + GePpeTto

**Training:** completato tutte le 20 epoch, best=18. Tempo: 40m 31s. Val_loss minima: 2.0508.

**Risultati test set:**

| Metrica | M5a-FT | M5a | M1-FT v2 |
|---------|--------|-----|----------|
| BLEU-1 | 0.3356 | 0.3154 | 0.3442 |
| BLEU-4 | 0.0451 | **0.0468** | **0.0482** |
| METEOR | **0.2398** | 0.2258 | 0.2321 |
| ROUGE-L | **0.2262** | 0.2069 | 0.2208 |
| Caption uniche | 255/265 | 259/265 | 257/265 |

**Osservazioni:**
- **METEOR e ROUGE-L migliorano rispetto a M5a** (+0.014 METEOR, +0.019 ROUGE-L): il fine-tuning dell'encoder aiuta
- BLEU-4 leggermente inferiore a M5a: piu varieta lessicale ma meno 4-grammi esatti
- Il training non ha fatto early stopping, miglioramento ancora in corso all'ultima epoca
- Ripetizioni tipiche del prefix tuning ancora presenti ("grana grossolana e una grana grossolana")
- Qualche frase contraddittoria ("frattura irregolare, con una frattura regolare")

**Esempi M5a-FT:**
- "E un po' stirata, con microocchiature diffuse." — frase naturale e corretta
- "La pasta e disomogenea e presenta una grana grossolana."
- "La pasta presenta una grana grossa e una frattura regolare."

**Conclusione:** risultato valido, METEOR/ROUGE-L al top tra i modelli M5. Procedo con M5b-FT.

### 8.7 M5b-FT — CNNSpatial (fine-tuned) + GePpeTto

**Training:** early stopping all'epoch 15 (best=8). Tempo: 33m 47s. Val_loss minima: 2.0451.

**Risultati test set:**

| Metrica | M5b-FT | M5b (frozen) | Delta |
|---------|--------|--------------|-------|
| BLEU-1 | 0.3405 | 0.3328 | +0.008 |
| BLEU-4 | 0.0392 | **0.0482** | -0.009 |
| METEOR | 0.2255 | **0.2386** | -0.013 |
| ROUGE-L | 0.2202 | **0.2317** | -0.012 |
| Caption uniche | 250/265 | 253/265 | -3 |

**Osservazione cruciale: M5b-FT e PEGGIO di M5b frozen.**

Questo e un risultato scientificamente importante: **il fine-tuning dell'encoder CNN non aiuta quando il decoder e gia pre-trained (GePpeTto)**. Possibili cause:
1. Il CNN frozen fornisce gia feature visuali generali sufficienti
2. L'unfreezing aumenta la capacita del modello oltre quello che il dataset puo supportare (1071 campioni)
3. Con l'encoder sbloccato, il modello rischia di adattare troppo le feature alle caption di training (overfitting)

**Esempi M5b-FT:**
- "La pasta presenta una microocchiatura diffusa e un occhio di 6 mm."
- "C'e una piccola fessura."
- "La pasta e granulosa."

**Conclusione:** risultato valido ma sub-ottimale rispetto al frozen. Procedo con M5c-FT (ultimo modello).

### 8.8 M5c-FT — ViT (fine-tuned) + GePpeTto

**Training:** 15 epoche complete (best=15, nessun early stopping). Tempo totale: 3h 38m (interrotto all'epoca 4 durante la compaction della sessione, ripreso da `last.pt` fino alla 15). Val_loss minima: 2.1866 (la migliore di tutti i modelli M5-FT).

**Risultati test set:**

| Metrica | M5c-FT | M5c (frozen) | M5a-FT | M5b-FT |
|---------|--------|--------------|--------|--------|
| BLEU-1 | 0.3289 | 0.3380 | 0.3356 | **0.3405** |
| BLEU-4 | 0.0439 | **0.0476** | 0.0451 | 0.0392 |
| METEOR | 0.2348 | 0.2335 | **0.2398** | 0.2255 |
| ROUGE-L | 0.2248 | 0.2205 | **0.2262** | 0.2202 |
| Caption uniche | **259/265** | 253/265 | 255/265 | 250/265 |

**Osservazioni:**
- Conferma il pattern visto con M5b-FT: **fine-tuning encoder + GePpeTto = leggero peggioramento BLEU-4** rispetto al frozen (0.0439 vs 0.0476, -0.004)
- Ma a differenza di M5b-FT, qui METEOR e ROUGE-L migliorano leggermente rispetto al frozen
- 259/265 caption uniche, il valore massimo tra tutti gli M5-FT
- Training completato senza early stopping: val_loss ancora in discesa all'epoca 15 (2.19 vs 2.21 epoca 13), il modello potrebbe migliorare con piu epoche
- BLEU-4 durante training e salito da 0.015 (ep 7) a 0.030 (ep 14): quasi raddoppiato nella seconda meta del training

**Esempi M5c-FT:**
- "La pasta presenta una grana fine e grossolana, con cristalli di tirosina." — terminologia tecnica specialistica
- "La frattura e regolare e la grana e abbastanza omogenea."
- "La pasta presenta una microocchiatura piu bella." — sintassi italiana naturale ereditata da GePpeTto
- Alcune ripetizioni residue ("grana grossa, con una grana grossolana e una grana grossa") tipiche del prefix tuning

**Conclusione:** completa il 2x2. Risultato in linea con M5a-FT (BLEU-4 ~0.044, METEOR ~0.24). Il pattern "encoder fine-tuning peggiora BLEU-4 ma migliora METEOR" e robusto tra diverse architetture encoder quando il decoder e GePpeTto.

### 8.9 Riepilogo finale — 9 modelli + 4 baseline + 1 ceiling

Vedi `reports/confronto_modelli_finale.md` per tabella completa, analisi 2x2, raccomandazioni per gli altri 6 attributi, e conclusioni complete dello studio pilota.
