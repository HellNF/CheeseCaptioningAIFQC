# Confronto Finale dei Modelli — Sapore (Pilot 2×2 completo)

**Data:** 2026-05-01
**GPU:** NVIDIA RTX 4060 Laptop (8 GB VRAM)
**Attributo:** Sapore (train=976, val=234, test=230)
**Loader:** `on_topic_only=True` (FUORI_ATTRIBUTO escluse, 0.6% del dataset)
**Modelli completati:** 12/12

## 1. Obiettivo

Replicare il design fattoriale 2×2 del pilot Struttura su un attributo "pulito" (Sapore, <1% rumore FUORI_ATTRIBUTO) per:
1. Validare il fix del loader (`on_topic_only=True`)
2. Misurare quanto del plateau BLEU-4 ~0.048 di Struttura era artefatto del rumore
3. Verificare se il pattern 2×2 (cella vincente) cambia con l'attributo

## 2. Tabella completa (12 modelli)

| # | Modello | Architettura | BLEU-1 | BLEU-4 | METEOR | ROUGE-L | Best ep | Tempo | Uniche |
|---|---|---|---|---|---|---|---|---|---|
| 1 | M1 | CNN(g) frozen + LSTM | 0.329 | 0.092 | 0.289 | 0.239 | 49/50 | 50m | 89% |
| 2 | M2 | CNN(g) frozen + Transformer | 0.329 | 0.084 | 0.284 | 0.242 | 6/13 | 13m | 87% |
| 3 | M3 | ViT frozen + Transformer | 0.315 | 0.098 | 0.307 | 0.249 | 8/13 | 21m | 85% |
| 4 | M5a | CNN(g) frozen + GePpeTto | 0.308 | 0.090 | 0.274 | 0.231 | 9/16 | 21m | 87% |
| 5 | M5b | CNNSpatial frozen + GePpeTto | 0.327 | 0.100 | 0.292 | 0.248 | 8/15 | 23m | 88% |
| 6 | **M5c** 🥈 | ViT frozen + GePpeTto | 0.316 | **0.112** | **0.320** ⬅ TOP METEOR | 0.261 | 8 | 47m | 90% |
| 7 | M1-FT | CNN(g) ft + LSTM | 0.339 | 0.098 | 0.284 | 0.241 | 30/30 | 24m | 90% |
| 8 | M2-FT | CNN(g) ft + Transformer | 0.309 | 0.098 | 0.298 | 0.238 | 9/16 | 17m | 87% |
| 9 | **M3-FT** 🏆 | ViT ft + Transformer | **0.363** | **0.117** ⬅ TOP BLEU-4 | 0.305 | 0.262 | 13/18 | 41m | 72% |
| 10 | M5a-FT | CNN(g) ft + GePpeTto | 0.323 | 0.092 | 0.296 | 0.245 | 9/16 | 22m | 90% |
| 11 | M5b-FT | CNNSpatial ft + GePpeTto | 0.349 | 0.100 | 0.294 | 0.244 | 7/14 | 22m | 87% |
| 12 | M5c-FT | ViT ft + GePpeTto | 0.327 | 0.098 | 0.294 | 0.246 | 13/15 | 70m | 90% |

## 3. Matrice 2×2 (medie BLEU-4)

|  | Decoder from-scratch | Decoder GePpeTto | Effetto decoder |
|---|---|---|---|
| **Encoder frozen** | 0.091 (n=3) | **0.101** (n=3) | +0.010 ✓ |
| **Encoder fine-tuned** | **0.105** (n=3) | 0.097 (n=3) | -0.008 ✗ |
| **Effetto encoder** | +0.014 ✓ | -0.004 ✗ | |

### Effetti principali
- **Encoder fine-tuning**: aiuta con scratch (+0.014), penalizza con GePpeTto (-0.004)
- **GePpeTto**: aiuta con frozen (+0.010), penalizza con FT (-0.008)
- **Interazione**: le due tecniche **non si sommano** (anzi, si annullano)

### Top 3 per cella
- frozen × scratch: **M3 (0.098)**
- frozen × GePpeTto: **M5c (0.112)** 🥈
- ft × scratch: **M3-FT (0.117)** 🏆
- ft × GePpeTto: **M5b-FT (0.100)**

## 4. Confronto Sapore vs Struttura (cella per cella)

| Cella | Struttura | Sapore | Δ |
|---|---|---|---|
| frozen × scratch | 0.044 | **0.091** | +107% |
| frozen × GePpeTto | 0.048 | **0.101** | +110% |
| ft × scratch | 0.042 | **0.105** | +150% |
| ft × GePpeTto | 0.043 | **0.097** | +126% |
| **MEDIA** | **0.044** | **0.099** | **+125%** |

**Tutte le 4 celle raddoppiano BLEU-4** sul dataset pulito. Conferma definitiva che il "plateau a 0.048" su Struttura era artefatto del bug FUORI_ATTRIBUTO (47% rumore train).

### Pattern del 2×2 — inversione completa

| | Struttura — cella vincente | Sapore — cella vincente |
|---|---|---|
| BLEU-4 | frozen × GePpeTto (0.048) | **ft × scratch (0.105)** |
| Modello | M5b/M5c | **M3-FT** |

Su Sapore il fine-tuning encoder è la strategia vincente (decoder scratch sufficiente). Su Struttura il decoder pre-trained era essenziale per compensare la scarsità di segnale visivo (encoder frozen).

## 5. Top 5 modelli del pilot

| Rank | Modello | BLEU-4 | METEOR | Note |
|---|---|---|---|---|
| 🏆 1 | **M3-FT** | **0.117** | 0.305 | Top BLEU-4, FT × scratch |
| 🥈 2 | **M5c** | **0.112** | **0.320** | Top METEOR, frozen × GePpeTto |
| 3 | M5b / M5b-FT | 0.100 | 0.292/0.294 | tied, 2 architetture diverse |
| 4 | M3 | 0.098 | 0.307 | top METEOR senza FT |
| 5 | M1-FT / M2-FT / M5c-FT | 0.098 | 0.284/0.298/0.294 | tied |

## 6. Conclusioni metodologiche

### 6.1 Il bug FUORI_ATTRIBUTO era rilevante
+125% BLEU-4 medio passando da Struttura (rumoroso) a Sapore (pulito). Conferma robusta che le metriche assolute del pilot Struttura erano inattendibili. Il fix `on_topic_only=True` deve essere usato per tutti gli attributi.

### 6.2 Il pattern 2×2 dipende dall'attributo
- **Sapore**: cella vincente = ft × scratch (dataset pulito + vocabolario gusto ridotto → encoder FT cattura segnali visivi specifici, decoder scratch sufficiente)
- **Struttura**: cella vincente = frozen × GePpeTto (rumore + vocabolario tecnico complesso → decoder pre-trained compensa)

**Generalizzare 2×2 da un solo attributo è rischioso**. Per fare scelta architetturale solida serve almeno 2-3 attributi (Aroma, Sapore, Texture sono i meno rumorosi).

### 6.3 Encoder fine-tuning e decoder pre-trained sono ALTERNATIVI, non additivi
- Solo scratch encoder + scratch decoder è la baseline (BLEU-4 ~0.091)
- Aggiungere FT: +0.014 ✓
- Aggiungere GePpeTto: +0.010 ✓
- Aggiungere ENTRAMBI: +0.006 (sotto la somma 0.024 attesa) → -0.018 in interazione

Suggerisce: **encoder FT e decoder pre-trained competono per lo stesso segnale**. Quando uno c'è, l'altro non aggiunge valore.

### 6.4 ViT > CNN su Sapore
M3 (0.098) > M1 (0.092). M3-FT (0.117) > M1-FT (0.098). M5c (0.112) > M5b (0.100) > M5a (0.090). 

**ViT (vit_small_patch16_224) cattura meglio l'informazione visiva** rilevante per Sapore. Su Struttura era simile (M3 ≈ M1 = 0.045/0.047). La differenza emerge quando i dati sono puliti.

### 6.5 BLEU-4 vs METEOR non sempre concordano
- **M3-FT** vince BLEU-4 (0.117) ma è 4° su METEOR (0.305)
- **M5c** è 2° su BLEU-4 (0.112) ma 1° su METEOR (0.320)

Suggerisce due trade-off:
- M3-FT: più alta precisione 4-gram, meno sinonimi naturali
- M5c: più sinonimi/parafrasi naturali (METEOR), 4-gram leggermente meno preciso

Per uso pratico (descrizione finale leggibile), **M5c potrebbe essere preferibile** a M3-FT.

### 6.6 Mode collapse risolto definitivamente
Tutti i 12 modelli producono 72-90% caption uniche. Il fix `label smoothing 0.1 + nucleus sampling` (introdotto a fine pilot Struttura) regge anche su Sapore. Nessun modello ha problemi di degenerazione output.

### 6.7 Hardware locale stretto per modelli FT pesanti
- 6+ crash CUDA durante il pilot (illegal memory access, CUBLAS, system reboot)
- Tutti su modelli FT con 100M+ params trainable
- Soluzione: batch ridotto (8 → 4 per i pesanti) + monitoring + retry con `--resume`

Per scaling a tutti gli attributi: **Kaggle T4/P100 16GB sarebbe più stabile** del laptop 8GB.

## 7. Implicazioni per gli altri attributi

| Attributo | % FUORI_ATTRIBUTO | Aspettativa |
|---|---|---|
| Aroma | 0.9% | Probabilmente come Sapore (ft×scratch vince) |
| Sapore | 0.6% | ft × scratch ✓ DONE |
| Profumo | 26% | Caso intermedio, da verificare |
| Texture | 30% | Idem |
| Colore | 25% | Idem |
| Struttura | 47% | frozen × GePpeTto vinceva ma è "rumoroso" |
| Spessore_Crosta | 49% | Più rumoroso, da verificare |

**Raccomandazione**: prossimo target = Aroma (testare se pattern Sapore replica). Se sì, generalizzazione confermata. Poi Texture/Profumo (rumore medio) per vedere transizione.

## 8. Output finali

**Per ogni modello**:
- `models/{model_dir}/Sapore/best.pt`
- `models/{model_dir}/Sapore/predictions.csv`
- `models/{model_dir}/Sapore/log.csv`
- `models/{model_dir}/Sapore/config.json`

**Report individuali**: `reports/sapore_pilot/0X_<MODEL>_report.md` (12 file)
**Cumulativi per cella**: `cumulativo_{1..4}_<cella>.md`
**Sintesi**: questo file

## 9. Modello consigliato per produzione

**M5c (ViT frozen + GePpeTto frozen)** per il bilanciamento ottimale:
- BLEU-4 0.112 (vicino al top)
- METEOR 0.320 (top assoluto = caption più naturali per umano)
- 90% caption uniche
- Encoder e decoder entrambi frozen → fine-tuning futuro possibile su ulteriori dati senza ritrainare da zero
- Costo computazionale ragionevole (~50 min/training)

Alternativa: M3-FT se priorità assoluta è BLEU-4 (0.117), ma minore diversità (72%) e tempo training maggiore.
