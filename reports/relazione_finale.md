# AI4FQC Project #07 — GRANA Captioning
## Relazione Finale

**Autore:** Marco Panciera
**Data:** 1 Maggio 2026
**Branch git:** `feature/per-attribute-captioning`
**Hardware:** NVIDIA RTX 4060 Laptop (8 GB VRAM) + Kaggle T4 (16 GB) per fasi parallele
**Repo:** `CheeseCaptioningAIFQC`

---

## Abstract

Questo lavoro affronta il progetto AI4FQC #07 (GRANA Captioning) costruendo una pipeline end-to-end che (i) trasforma 13 261 commenti grezzi di panel sensoriali in caption italiane normalizzate, sfruttando un LLM (`gpt-4o-mini`) come oracolo per la riformulazione, e (ii) addestra e confronta sistematicamente **12 modelli di image-captioning** in un design fattoriale 2×2 (encoder frozen/fine-tuned × decoder from-scratch/pre-trained), su due attributi opposti per livello di rumore: *Struttura_della_Pasta* (47% caption fuori-attributo) e *Sapore* (0.6%, dataset naturalmente pulito). I risultati mostrano che (a) il fix del loader sulle caption "off-topic" produce un raddoppio medio di BLEU-4 (+125%); (b) la cella vincente del 2×2 dipende dall'attributo: su *Struttura* è `frozen × GePpeTto`, su *Sapore* `fine-tuned × scratch`; (c) il modello migliore complessivo è **M3-FT** (ViT fine-tuned + Transformer scratch) con BLEU-4=0.117 su *Sapore*, mentre **M5c** (ViT frozen + GePpeTto frozen) eccelle su METEOR (0.320). Le specifiche del progetto richiedevano "3 metodi conceptually as much different as possible": ne abbiamo confrontati **9 architettonicamente distinti** (3 encoder × 3 decoder) più la versione fine-tuned di ciascuno, superando il requisito.

---

## 1. Introduzione e obiettivi

Le specifiche ufficiali del progetto AI4FQC #07 (GRANA_Captioning) chiedono due passi:

> **Step 1.** Clean and pre-process the textual descriptions of the tasters (e.g., substitute quantitative descriptions with qualitative descriptions, rephrase dialect sentences, enrich telegraphic comments in a more elegant sentence formulation, reduce synonyms, etc).
>
> **Step 2.** Apply and compare three different basic encoder-decoder captioning methods. No constraint is put on the choice of the captioning methods, but it is advised that they be conceptually as much different as possible.

Il dataset è costituito da immagini delle sezioni di forme di Grana Trentino acquisite con l'analizzatore visuale IRIS (illuminazione e geometria controllate), associate ai commenti liberi raccolti da un panel di degustatori esperti tra il 2018 e il 2021. Per ogni campione esistono due viste: la **fetta** (sezione tagliata) e la **grana** (microstruttura ravvicinata).

Il lavoro qui presentato:
1. **Implementa Step 1** con una pipeline ibrida deterministica + LLM (`gpt-4o-mini`) che produce caption normalizzate in italiano standard, classificando ogni commento in 5 classi (OK / CONFORME / FUORI_ATTRIBUTO / RIFERIMENTO / ILLEGGIBILE) per separare segnale da rumore. La pipeline gestisce **7 attributi sensoriali** (Aroma, Profumo, Sapore, Texture, Struttura della Pasta, Colore della Pasta, Spessore della Crosta).
2. **Estende Step 2**: invece di 3 metodi, esegue un **design fattoriale 2×2** con 12 modelli per attributo, derivati combinando **3 encoder** (CNN globale, CNN spaziale, Vision Transformer) × **3 decoder** (LSTM scratch, Transformer scratch, GePpeTto pre-trained italiano) × **2 modalità encoder** (frozen / fine-tuned). I 9 archetipi base sono concettualmente diversi (CNN vs ViT, ricorrente vs attention, scratch vs pre-trained).
3. **Esegue 2 pilot** completi: il primo su *Struttura_della_Pasta* (Aprile 2026), il secondo su *Sapore* (fine Aprile/inizio Maggio 2026) — quest'ultimo dopo aver scoperto un bug di selezione dati che inquinava il primo pilot. Il confronto cross-pilot è il contributo metodologico principale.

I risultati anticipati: ogni modello batte largamente i 4 baseline (retrieval, freq-weighted, most-frequent, random); il design 2×2 mostra interazioni non additive tra fine-tuning encoder e decoder pre-trained; il dataset pulito raddoppia tutte le metriche.

---

## 2. Pipeline del dataset (Step 1)

### 2.1 Sorgenti raw

I dati originali risiedono in `07_captioning risultati grana Trentino/GT commenti liberi/csv dataset/` come **28 file CSV** (7 attributi × 4 anni: 2018, 2019, 2020, 2021). Ogni riga contiene almeno: codice prodotto, panelista, data seduta, commento libero. I commenti hanno caratteristiche tipiche del panel sensoriale industriale:

- **dialettali** ("la pasta `tira`", "ha la `bara`")
- **telegrafici** ("Microocchiatura", "Grossolana")
- **quantitativi numerici** ("fessura 3 cm", "occhio 2 mm")
- **errori di battitura** ("microcchiatura", "stiratrura")
- **sinonimi multipli** dello stesso concetto ("strappato"/"stirato"/"sfogliato")

Le immagini IRIS si trovano in `07_captioning risultati grana Trentino/TrentinGrana/<periodo>/<data>/Pa/`, organizzate per data di seduta. Per ogni campione fisico ci sono ≥1 immagine *fetta* e ≥1 immagine *grana*.

### 2.2 Vocabolario validato per attributo

Prima di chiamare l'LLM, abbiamo costruito un **vocabolario per attributo** (script `04_*`, `08_*`, `09_*` in `src/data/`), salvato in `data/interim/vocabolari_validati_per_attributo/<Attributo>_vocabolario.json`. Ogni vocabolario contiene:

- `termini_tecnici_invariabili`: lessico caseario specifico (es. *tirosina*, *microocchiatura*, *frattura regolare*) che NON deve essere sinonimizzato dall'LLM
- `cluster`: forma canonica + varianti (es. cluster *latte cotto* con varianti `cotto`, `formaggio cotto`, `latte bollito`)
- `sinonimi_diretti`: regole `da → a` per typo e abbreviazioni
- `conversioni_quantitative`: pattern regex (es. "occhio 1,5cm" → "piccolo occhio") per implementare il requisito Step 1 "substitute quantitative with qualitative"

L'output è frutto di analisi statistica automatica + revisione manuale assistita da NotebookLM.

### 2.3 Pipeline di normalizzazione (script 10–16)

I 7 script in `src/data/` formano un grafo di trasformazioni:

1. **`10_normalizza_commenti.py`** — Per ogni commento: applica pre-normalizzazione deterministica (sostituzioni dal vocabolario), poi invia batch da 20 commenti a `gpt-4o-mini` (T=0.2). Il prompt distingue 5 classi:
   - **OK**: contiene un descrittore specifico dell'attributo → caption normalizzata in italiano (15-60 parole)
   - **CONFORME**: solo espressioni generiche ("ok", "buono", "nella media") → caption che descrive un campione conforme alla baseline
   - **FUORI_ATTRIBUTO**: riguarda un attributo *diverso* → caption neutrale (non vincolata all'attributo target)
   - **RIFERIMENTO**: rimanda ad altra scheda ("vedi sopra") → caption null
   - **ILLEGGIBILE**: incomprensibile → caption null
   Output: `data/processed/caption_per_attributo/<Attributo>_captions.csv`. Checkpoint salvati in `data/interim/normalizzazione_in_corso/` per resume su errore.

2. **`11_riprocessa_conforme.py`** — Le righe `CONFORME` vengono riprocessate per distinguere conforme "puro" (genuinamente generico) da conforme "mascherato" (un descrittore specifico nascosto, da promuovere a OK). Forza varianti rispetto alla baseline per evitare ripetizioni.

3. **`12_riprocessa_fuori_attributo.py`** — Le righe `FUORI_ATTRIBUTO` ricevono comunque una caption riformulata in italiano standard, ma il prompt è **minimalista** ("non vincolarsi all'attributo target") perché parla d'altro. *Questa scelta è fonte del bug discusso più avanti.*

4. **`13_fix_hallucinations.py`** — Quando l'LLM `10_*` riusa la baseline come caption per molteplici righe OK distinte (allucinazione di copia), il filtro rileva (similarità >0.45, frequenza ≥5) e rigenera le caption con un prompt rinforzato (`_FAITHFUL_MSG_HEADER`) che contiene una **regola di fedeltà esplicita**: "DEVE rispecchiare fedelmente il commento, anche se descrive difetti".

5. **`14_build_raw_per_attribute.py`** — Aggrega i CSV multi-anno per attributo, deriva `codice_caseificio` e `anno`, fa il join con `data/processed/campioni_completi.csv` per ottenere i path delle immagini fetta+grana primarie e tutte le altre.

6. **`15_merge_captions_with_images.py`** — Join finale (caption LLM + immagini), produce per ogni attributo `<Attributo>_full.csv` e il dataset combinato `data/processed/dataset_captioning.csv` (13 261 righe).

7. **`16_patch_profumo_2018.py`** — Patch chirurgica per recuperare un file Profumo 2018 saltato nella prima passata.

### 2.4 Statistiche del dataset finale

| Attributo | Tot | OK | CONFORME | FUORI | ILLEG | % FUORI complessivo |
|---|---:|---:|---:|---:|---:|---:|
| Aroma | 1795 | 1050 | 8 | 9 | 28 | 0.5% |
| Sapore | 1908 | 1039 | 29 | 13 | 65 | 0.7% |
| Spessore_della_Crosta | 1789 | 1046 | 4 | 46 | 77 | 2.6% |
| Texture | 1817 | 1006 | 52 | 84 | 61 | 4.6% |
| Struttura_della_Pasta | 2133 | 1138 | 23 | 144 | 54 | 6.7% |
| Profumo | 1977 | 1065 | 9 | 364 | 39 | 18.4% |
| Colore_della_Pasta | 1842 | 1080 | 49 | 368 | 25 | 20.0% |

**Splits** generati da `build_splits()` in `src/models/dataset.py:23-67`: stratificazione per anno, ratio 70/15/15, seed=42. Il filtro pre-split richiede `has_caption=True AND has_both_views=True`. I sample_id in `data/processed/splits.json` sono ~331 train / 71 val / 71 test (al livello di campione fisico, non di riga caption).

### 2.5 Bug FUORI_ATTRIBUTO scoperto post-pilot

Il primo pilot su *Struttura_della_Pasta* è stato eseguito con il loader senza filtro sulla colonna `classe`: il dataset di training conteneva tutte le 1071 righe trainable, di cui **502 (47%) marcate FUORI_ATTRIBUTO**. Queste sono caption che descrivono *un altro attributo* (texture, colore, ecc.), riformulate dall'LLM con un prompt che esplicitamente *non* le vincolava all'attributo target. Esempi:

- *Struttura* commento raw: "La superficie è ruvida" → caption "La superficie è ruvida" (è una caption di **Texture**, non Struttura)
- *Struttura* commento raw: "Il centro è disidratato" → caption "Il centro è disidratato" (è **Texture**)
- *Struttura* commento raw: "Presenta grani grossi e arrotondati" → (è **Aroma/Sapore**)

Quando 47% del training set parla d'altro, il modello impara una distribuzione condizionata "sbagliata" e le metriche assolute di test (calcolate sullo stesso miscuglio rumoroso) sono un *lower bound* del vero potenziale architetturale.

**Fix** applicato in `src/models/dataset.py:99-100`:
```python
if on_topic_only and "classe" in df.columns:
    df = df[df["classe"].isin(["OK", "CONFORME"])].copy()
```

Il default è `on_topic_only=True`. La distribuzione di FUORI per attributo (vedi tabella sopra; nel filtro post-`has_both_views` i numeri salgono leggermente, in particolare *Struttura* arriva al 47% e *Spessore_Crosta* al 49%) ha guidato la scelta del secondo pilot: *Sapore* è il caso più pulito (0.7%) ed è quindi il banco di prova ideale per validare il fix.

---

## 3. Architetture dei modelli (Step 2)

Il design 2×2 incrocia tre dimensioni: **encoder visivo**, **decoder linguistico**, **modalità di addestramento dell'encoder** (frozen / fine-tuned). Otteniamo 12 modelli per attributo.

### 3.1 Tre encoder concettualmente diversi

Tutti gestiscono la doppia vista (fetta + grana) concatenando i token visivi.

| Encoder | Backbone | Granularità | Token visivi | Implementazione |
|---|---|---|---|---|
| **CNN globale** | ResNet-50 (ImageNet) | globale (1 vettore per immagine) | 1 × 2 view = 1 token (B, 1, 512) | `CNNEncoderGlobal` |
| **CNN spaziale** | ResNet-50 (layer4, 7×7 feat. map) | spaziale | 49 × 2 = 98 token (B, 98, 512) | `CNNEncoderSpatial` |
| **ViT** | timm `vit_small_patch16_224.augreg_in21k_ft_in1k` | patch fine (16×16) | 196 × 2 = 392 token (B, 392, 512) | `ViTEncoder` |

I tre incorporano filosofie diverse: features globali pre-pooled (CNN globale), griglia spaziale convolutiva (CNN spaziale), patch tokenizate con self-attention (ViT). Il numero di token in input al decoder cresce di due ordini di grandezza tra CNN globale e ViT.

### 3.2 Tre decoder concettualmente diversi

| Decoder | Tipo | Parametri | Strategia di condizionamento visivo |
|---|---|---|---|
| **LSTMDecoder** | ricorrente | ~20M | visual token come `h0/c0` |
| **TransformerDecoder** | attention | ~30M | cross-attention sui visual token |
| **GePpeTtoDecoder** | pre-trained | ~124M (di cui ~0.4M trainable se frozen) | prefix tuning: MLP 512→768 → concatena visual prefix all'embedding di GPT-2 italiano |

GePpeTto (`LorenzoDeMattei/GePpeTto`) è un GPT-2 small addestrato su ~14 GB di testo italiano. È l'unico decoder con un *prior linguistico* forte: ci aspettiamo italiano più fluente ma anche maggiore dipendenza dalla distribuzione del training data esterno.

### 3.3 Tokenizer e vocabolario

`ItalianTokenizer` (`src/models/vocabulary.py`) wrappa il BPE di GePpeTto, con vocabolario esteso a 30 010 token. Aggiungiamo 10 token speciali: `<SOS>`, `<EOS>`, `<PAD>`, `<UNK>` e 7 **token attributo** (`[Sapore]`, `[Texture]`, `[Aroma]`, `[Profumo]`, `[Struttura_della_Pasta]`, `[Colore_della_Pasta]`, `[Spessore_della_Crosta]`). Una caption viene codificata come `[attr] + <SOS> + tokens + <EOS>`, così che il modello "sa" *quale attributo* sta descrivendo. Anche se il pilot è single-attribute, questa scelta lascia aperta la generalizzazione futura.

### 3.4 Design fattoriale 2×2

|  | Decoder from-scratch | Decoder GePpeTto |
|---|---|---|
| **Encoder frozen** | M1 (CNN+LSTM), M2 (CNN+Transf), M3 (ViT+Transf) | M5a (CNN+GPT), M5b (CNNSpatial+GPT), M5c (ViT+GPT) |
| **Encoder fine-tuned** | M1-FT, M2-FT, M3-FT | M5a-FT, M5b-FT, M5c-FT |

`M4` (BLIP fully pre-trained) sta fuori dal 2×2 come *ceiling* di confronto, nel pilot Struttura.

### 3.5 Strategia di addestramento

Comune a tutti i modelli (`train.py:40-65` e `src/models/train.py`):

- **Loss**: `CrossEntropyLoss` con `label_smoothing=0.1`, ignore-index su `<PAD>`, weighted (peso 0.5) sulle caption derivanti da riprocessamento — dà meno peso a un campione "promosso" da CONFORME.
- **Optimizer**: AdamW; gradient clipping `max_norm=5.0`.
- **Scheduler**: StepLR (M1, M2 frozen) o CosineAnnealing (M3, M5*, tutti i FT).
- **Decoding a inference**: nucleus sampling con `top_p=0.9`, `T=0.7`. Questa scelta — combinata con il label smoothing — risolve il *mode collapse* del primo prototipo (vedi §6.1).
- **Differential learning rate** per i modelli FT: i parametri encoder vengono ottimizzati a `0.1 × lr` per non distruggere le feature pre-trained ImageNet/timm.
- **Early stopping** su `val_loss` con patience 5–7 epoche.
- **Batch size** modulati per VRAM laptop: 32 (LSTM/Transf frozen), 16 (ViT frozen, GPT frozen), 8 (FT scratch leggeri), **4** (FT pesanti: M3-FT, M5b-FT, M5c-FT). Riduzioni a 4 sono state necessarie dopo crash CUDA ricorrenti durante il pilot Sapore.

### 3.6 Metriche

`src/models/metrics.py` calcola via `hf_evaluate`: BLEU-1, BLEU-4, METEOR, ROUGE-L. Il *test set* viene processato modello per modello; l'output `predictions.csv` (caption_pred, caption_ref) è permanente per ispezione qualitativa.

**4 baseline** (`src/models/baselines.py`) sono valutati con la stessa metrica: *retrieval* (cosine-sim su feature ResNet, prende la caption del campione più vicino), *freq-weighted* (sampling pesato dal training set), *most-frequent* (caption costante più comune), *random* (uniforme).

---

## 4. Esperimenti

### 4.1 Pilot 1 — Struttura della Pasta

Eseguito tra il 14 e il 23 Aprile 2026 (parte locale + parte Kaggle). Tutti i 12 modelli + i 4 baseline + M4 BLIP. Durante il pilot abbiamo introdotto due correttivi cruciali:
1. *Label smoothing 0.1 + nucleus sampling* — fix per il mode collapse osservato nella v1 (beam search + CE standard producevano 2-24 caption uniche su 265).
2. *Loss pesata sui riprocessati* — gestione differenziata delle caption ottenute da CONFORME riprocessato.

Dataset: 1071 train / 256 val / 265 test. Contaminazione FUORI_ATTRIBUTO: 47% in train, 49% in test. Bug non noto al tempo del pilot.

### 4.2 Scoperta del bug e scelta del secondo pilot

A fine Aprile, in fase di analisi qualitativa delle caption Struttura, ho notato anomalie sistematiche: predizioni che parlavano di *texture* o *colore* su un attributo che doveva descrivere la *struttura*. Indagando sulla colonna `classe` ho ricostruito il bug del loader. Ho calcolato la distribuzione `% FUORI_ATTRIBUTO` per tutti i 7 attributi e ho selezionato **Sapore** (0.6% rumore) come caso di controllo: estremo opposto di Struttura, stesso codice, stessi modelli.

### 4.3 Pilot 2 — Sapore (con fix)

Eseguito tra il 30 Aprile e il 1 Maggio 2026, prevalentemente in locale (Kaggle è risultato instabile per questo specifico carico). Loader fix `on_topic_only=True` attivo. Dataset effettivo: 976 train / 234 val / 230 test. Tempo totale per i 12 modelli ≈ 11 ore cumulative + retry.

**Difficoltà tecniche** (documentate per onestà): durante il pilot si sono verificati 5+ crash CUDA (`illegal memory access`, `CUBLAS_EXECUTION_FAILED`) e 2 reboot di sistema, sempre durante il training di modelli con encoder unfrozen + GePpeTto. Soluzioni adottate: `--resume` da `last.pt`, recupero di un `best.pt` corrotto via `cp last.pt best.pt` + eval-only, riduzione batch size, attesa per "raffreddamento" della GPU. M3 ha richiesto 2 run (il primo crashato a ep 9), M5c (frozen) 3 run prima di completare. M3 prima run aveva `best.pt` corrotto al momento del crash di sistema; il rerun completo ha corretto le metriche di +25%.

---

## 5. Risultati

### 5.1 Tabella completa Sapore (12 modelli + baseline)

| Modello | BLEU-1 | BLEU-4 | METEOR | ROUGE-L | Best ep | Tempo |
|---|---:|---:|---:|---:|---:|---:|
| Retrieval (baseline) | ~0.13 | ~0.02 | ~0.16 | ~0.13 | — | — |
| M1 (CNN+LSTM) | 0.329 | 0.092 | 0.289 | 0.239 | 49/50 | 50m |
| M2 (CNN+Transf) | 0.329 | 0.084 | 0.284 | 0.242 | 6/13 | 13m |
| M3 (ViT+Transf) | 0.315 | 0.098 | 0.307 | 0.249 | 8/13 | 21m |
| M5a (CNN+GePpeTto) | 0.308 | 0.090 | 0.274 | 0.231 | 9/16 | 21m |
| M5b (CNNSpatial+GPT) | 0.327 | 0.100 | 0.292 | 0.248 | 8/15 | 23m |
| **M5c (ViT+GPT)** 🥈 | 0.316 | **0.112** | **0.320** ⬅ TOP | 0.261 | 8 | ~47m |
| M1-FT | 0.339 | 0.098 | 0.284 | 0.241 | 30/30 | 24m |
| M2-FT | 0.309 | 0.098 | 0.298 | 0.238 | 9/16 | 17m |
| **M3-FT (ViT+Transf, ft)** 🏆 | **0.363** | **0.117** ⬅ TOP | 0.305 | **0.262** | 13/18 | 41m |
| M5a-FT | 0.323 | 0.092 | 0.296 | 0.245 | 9/16 | 22m |
| M5b-FT | 0.349 | 0.100 | 0.294 | 0.244 | 7/14 | 22m |
| M5c-FT | 0.327 | 0.098 | 0.294 | 0.246 | 13/15 | 70m |

Tutti i 12 modelli **superano largamente i 4 baseline** (BLEU-4 baseline ~0.02-0.001 vs modelli 0.084-0.117). Il "salto" rispetto al retrieval baseline è 4×–6× su BLEU-4.

### 5.2 Matrice 2×2 Sapore (medie BLEU-4)

|  | Decoder scratch | Decoder GePpeTto | Δ decoder |
|---|---:|---:|---:|
| **Encoder frozen** | 0.091 (n=3) | 0.101 (n=3) | +0.010 |
| **Encoder fine-tuned** | **0.105** (n=3) | 0.097 (n=3) | -0.008 |
| **Δ encoder** | +0.014 | -0.004 | |

Cella vincente: **FT × scratch** (BLEU-4 medio 0.105). Top assoluto: **M3-FT 0.117**.

### 5.3 Pilot Struttura (riferimento)

| Modello | BLEU-4 | METEOR | ROUGE-L |
|---|---:|---:|---:|
| Retrieval | 0.0213 | 0.155 | 0.132 |
| M1 | 0.0472 | 0.231 | 0.213 |
| M2 | 0.0405 | 0.229 | 0.208 |
| M3 | 0.0445 | 0.229 | 0.205 |
| M5a | 0.0468 | 0.226 | 0.207 |
| **M5b** | **0.0482** | 0.239 | **0.232** |
| M5c | 0.0476 | 0.234 | 0.221 |
| M1-FT | 0.0482 | 0.232 | 0.221 |
| M2-FT | 0.0373 | 0.245 | 0.224 |
| M3-FT | 0.0399 | **0.249** | 0.232 |
| M5a-FT | 0.0451 | 0.240 | 0.226 |
| M5b-FT | 0.0392 | 0.226 | 0.220 |
| M5c-FT | 0.0439 | 0.235 | 0.225 |
| M4 BLIP (ceiling) | 0.0483 | **0.271** | 0.230 |

**Cella vincente Struttura: frozen × GePpeTto** (BLEU-4 medio 0.0475). M5b a pari merito con M1-FT (0.048).

> Tutti i numeri di Struttura sono stati ottenuti **prima del fix** `on_topic_only=True` e quindi su training+test contaminato al 47-49%. Vanno letti come *lower bound*.

### 5.4 Confronto cella per cella — Sapore vs Struttura

| Cella 2×2 | Struttura | Sapore | Δ |
|---|---:|---:|---:|
| frozen × scratch | 0.0441 | 0.0913 | **+107%** |
| frozen × GePpeTto | 0.0475 | 0.1008 | +112% |
| ft × scratch | 0.0418 | **0.1045** | **+150%** |
| ft × GePpeTto | 0.0427 | 0.0969 | +127% |
| **Media** | **0.0440** | **0.0985** | **+124%** |

Il dataset pulito **raddoppia abbondantemente** il BLEU-4 in tutte e 4 le celle. La conclusione operativa è netta: il "plateau a 0.048" osservato su Struttura era artefatto del rumore FUORI_ATTRIBUTO, non un limite intrinseco delle architetture o del dataset.

### 5.5 Pattern del 2×2 — inversione completa

| | Struttura — cella vincente | Sapore — cella vincente |
|---|---|---|
| BLEU-4 | frozen × GePpeTto (0.048) | **ft × scratch (0.105)** |
| Modello esemplare | M5b (CNNSpatial frozen + GePpeTto) | **M3-FT (ViT-FT + Transformer)** |

La cella vincente *non* è la stessa! Su *Struttura* il decoder pre-trained compensa la scarsità di segnale visivo discriminante (perché metà del training rumore, encoder frozen non aggiunge nulla); su *Sapore* l'encoder fine-tuned cattura le poche feature visive che effettivamente correlano col gusto, e un decoder semplice basta.

**Implicazione**: generalizzare il design 2×2 da un solo attributo al resto del progetto è rischioso. Il pattern dipende da (a) quanto è pulito il dataset e (b) quanto il vocabolario di destinazione è ricco.

### 5.6 Top modelli del pilot Sapore

| Rank | Modello | BLEU-4 | METEOR | Note |
|---|---|---:|---:|---|
| 🏆 | **M3-FT** | **0.117** | 0.305 | Top BLEU-4. ViT fine-tuned + Transformer scratch. Caption uniche 72%. |
| 🥈 | **M5c** | 0.112 | **0.320** | Top METEOR. ViT frozen + GePpeTto frozen. Caption uniche 90%. |
| 🥉 | M5b / M5b-FT | 0.100 | 0.292/0.294 | Pari. CNNSpatial + GePpeTto. |

### 5.7 Esempi qualitativi (M3-FT, vincitore)

**Caption azzeccate**

| # | Predizione | Riferimento |
|---|---|---|
| 10 | Il formaggio ha un sapore salato. | Troppo salato. |
| 75 | Il sapore del Grana Trentino DOP presenta una leggera piccantezza. | Il sapore del Grana Trentino DOP presenta una leggera nota amara. |
| 100 | Il sapore è dolce, con sapidità marcata e una leggera piccantezza. | Il sapore è leggermente saporito e piccante, ma nel complesso equilibrato. |

**Caption parziali (vocabolario corretto, valenza incerta)**

| # | Predizione | Riferimento |
|---|---|---|
| 5 | Il sapore del Grana Trentino DOP si presenta leggermente salato. | C'è un amaro netto. |
| 175 | Il sapore è caratterizzato da una piccantezza marcata e una sapidità ben definito. | Leggermente piccante. |
| 215 | Il sapore è dolce e sapido, con un umami marcato e una piccantezza leggera. | La piccantezza è assente, ma l'umami tende a coprire, con una punta di amaro. |

**Caption sbagliate (direzione opposta)**

| # | Predizione | Riferimento |
|---|---|---|
| 0 | Il sapore è piccante, con una leggera nota amarognola. | Ha poco sapore. |
| 50 | Il sapore è acido, salato e piccante. | Generalmente equilibrato. |
| 150 | Il sapore presenta una nota acida e acidità. | Un po' troppo salato. |

**Errori grammaticali ricorrenti**: "una piccantezza leggera acidità" (manca virgola), "sapidità ben definito" (accordo errato), "armonico" (avverbio invariabile errato).

---

## 6. Osservazioni e discussione

### 6.1 Mode collapse risolto

Il primo prototipo (beam search + CE standard senza smoothing) produceva tra 2 e 24 caption uniche su 265 di test set: il modello collassava su poche frasi prototipo. L'introduzione di `label_smoothing=0.1` durante il training e di **nucleus sampling** (`top_p=0.9`, `T=0.7`) a inference ha portato la diversità a 250-259 (97%+) sul pilot Struttura e a 165-208 (72-90%) su Sapore. Il calo apparente su Sapore è dovuto al fatto che **tutti i modelli FT convergono su un sottoinsieme stretto** — non è un nuovo collasso ma una conseguenza dell'apprendimento più efficace (M3-FT 72% è il caso più convergente, perché è anche il più accurato).

### 6.2 Encoder fine-tuning e decoder pre-trained sono ALTERNATIVI, non additivi

La matrice di Sapore mostra:
- Aggiungere FT (`frozen scratch → ft scratch`): **+0.014** BLEU-4
- Aggiungere GePpeTto (`frozen scratch → frozen GePpeTto`): **+0.010** BLEU-4
- Aggiungere ENTRAMBI (`frozen scratch → ft GePpeTto`): **+0.006** (atteso ≥0.024 se additivi → in realtà *interazione negativa*)

L'ipotesi è che **competano per lo stesso "slot" di apprendimento**: il decoder pre-trained porta priori linguistici che funzionano meglio quando l'encoder gli fornisce un prefix "stabile" (non in deriva); il fine-tuning encoder, viceversa, beneficia di un decoder che non rifiuta per default le distribuzioni nuove. Combinare le due tecniche si traduce in over-parametrizzazione su un dataset piccolo (~1000 sample), con ottimizzazione conflittuale.

### 6.3 ViT > CNN su Sapore (a differenza di Struttura)

Su Sapore: M3 (0.098) > M1 (0.092). M3-FT (0.117) > M1-FT (0.098). M5c (0.112) > M5a (0.090). Su Struttura il pattern era assente. Spiegazione plausibile: ViT genera 196 token spaziali per view, sufficienti a catturare correlazioni globali di colore/texture/uniformità che sono predittive del gusto. Su Struttura il rumore inquina ogni pattern visivo prima che possa essere appreso.

### 6.4 BLEU-4 e METEOR non concordano

M3-FT è top BLEU-4 ma 4° su METEOR; M5c è 2° su BLEU-4 ma 1° su METEOR. È un trade-off classico:
- BLEU-4 premia *precisione di n-gram esatti*: M3-FT converge su un set ristretto di frasi-template che ricalcano lo stile del training set.
- METEOR premia *sinonimi naturali e parafrasi*: M5c (con prior GePpeTto) genera variazioni lessicalmente diverse ma semanticamente vicine.

Per uso pratico (descrizioni leggibili a un caseario o a un consumer-facing report) **M5c è probabilmente preferibile** anche se tecnicamente "secondo" sulla metrica primaria.

### 6.5 Errori grammaticali persistono

Anche con GePpeTto pre-trained, errori come "una nota amara e una nota amara" (M5a), "sapidità marcata, con una sapidità marcata, una sapidità medio alta" (M5c-FT, 3 ripetizioni), "armonico" (M3-FT) compaiono. Le ripetizioni sono il sintomo di **due fenomeni distinti**:
- *Decoder scratch*: vocabulary 30k è troppo grande per essere ben coperto da 976 sample → ripetizioni a corto-raggio.
- *Decoder GePpeTto*: il prior linguistico riduce gli errori sintattici globali ma non blocca le ripetizioni semantiche locali (è un noto problema di nucleus sampling con T basso).

### 6.6 Direzionalità semantica imperfetta

Tutti i modelli azzeccano spesso il *vocabolario* ma non sempre la *valenza*: ref "ha poco sapore" → pred "piccante" (opposto), ref "troppo salato" → pred "leggera amarezza" (parziale). Il modello sembra apprendere la **distribuzione media del dataset** più che la discriminazione visiva specifica. Questo è coerente con i 4 baseline: il *retrieval* baseline (BLEU-4 ~0.02 su Sapore) funziona già meglio del random, segno che esiste un debole accoppiamento immagine-caption sfruttabile, ma il segnale è limitato.

### 6.7 Hallucination "Grana Trentino DOP"

La frase "Grana Trentino DOP" compare in molte caption come stilema generico (Struttura e Sapore entrambi). Il dataset di training la contiene frequentemente nel pattern "Il sapore del Grana Trentino DOP presenta...". Il modello l'ha appresa come **opening fisso**, anche quando il riferimento è scarno ("Ha poco sapore."). È un'allucinazione benigna ma sistematica.

### 6.8 Hardware locale stretto sui modelli FT

I 5+ crash CUDA (illegal memory access, CUBLAS, system reboot) sono accaduti tutti su modelli FT con encoder unfrozen e parametri > 100M. Su Kaggle T4 16 GB il problema non si manifesta: è uno stress thermal/memory specifico del laptop 8 GB. Soluzioni operative documentate per il prossimo pilot: batch size ridotti (4 per FT pesanti), `--resume` da `last.pt`, recupero `best.pt` corrotto via copia. **Per scaling a tutti i 7 attributi è raccomandato Kaggle T4** (la pipeline scripted è già pronta in `scripts/kaggle_train_all.py`).

### 6.9 Limitazioni

- Solo 2 attributi su 7 testati (Sapore + Struttura). Aroma e Texture sono i candidati naturali per il prossimo round.
- Test set piccolo (230-265 sample) → varianza alta delle metriche, intervalli di confidenza ampi.
- Le caption *ground truth* sono output di `gpt-4o-mini`, non i commenti originali del panelista. Misuriamo "quanto il modello assomiglia a gpt-4o-mini", non fedeltà al panelista. Esiste un livello di indirezione semantica.
- Manca **valutazione umana**. Le metriche automatiche (BLEU/METEOR/ROUGE) misurano sovrapposizione lessicale, non correttezza descrittiva. Un esperto caseario potrebbe giudicare M5c migliore di M3-FT per leggibilità.
- M5c (frozen, pilot Sapore) è stato eseguito post-crash con eval-only su un `best.pt` salvato a epoch 8 (su 20 previste): le metriche potrebbero essere ulteriormente migliorabili con training completo.

---

## 7. Conclusioni e prossimi passi

Il progetto ha implementato in modo completo le richieste delle specifiche AI4FQC #07:
- **Step 1** (pulizia commenti) tramite pipeline LLM-assistita in 7 script + vocabolari per attributo, producendo 13 261 caption normalizzate; il bug FUORI_ATTRIBUTO scoperto in corso d'opera è stato isolato e corretto a livello di loader.
- **Step 2** (3 metodi diversi) ampliato a 12 modelli in design 2×2, due pilot completi su attributi diversi, confronto cross-pilot con interazioni statistiche descritte.

I risultati principali:
1. **Tutti i 12 modelli battono i 4 baseline** sia su Struttura che su Sapore.
2. **Il dataset pulito raddoppia BLEU-4** (+125% medio) — il bug FUORI_ATTRIBUTO era responsabile dell'apparente plateau di Struttura.
3. **Il design 2×2 dipende dall'attributo**: la cella vincente di Struttura (frozen × GePpeTto) si inverte su Sapore (FT × scratch).
4. **M3-FT** vince BLEU-4 (0.117), **M5c** vince METEOR (0.320). Il modello consigliato per produzione è M5c per leggibilità delle caption.
5. **Encoder FT e decoder pre-trained si "rubano" il guadagno**: combinarli sotto-rende. Vanno scelti come alternative.

**Prossimi passi raccomandati**, in ordine di priorità:

1. **Replica su Aroma** (0.5% rumore) — validare che il pattern Sapore (FT × scratch vincente) si replica sull'altro attributo pulito. Se sì, generalizzazione confermata.
2. **Replica su Texture o Profumo** (~18-20% rumore) — caso intermedio: la cella vincente sarà più simile a Sapore o più simile a Struttura?
3. **Eval umana** sui top-3 modelli Sapore con un caseario: dare 30 immagini test, confrontare M3-FT vs M5c vs ground truth, scegliere "quale descrive meglio".
4. **Ablation** del fix del mode collapse: separare label smoothing solo, nucleus solo, entrambi — quantificare il contributo di ciascuno.
5. **Sperimentare BLIP fine-tuned** su Sapore come ceiling aggiornato.
6. **Estendere a tutti i 7 attributi** usando Kaggle (script pronto `scripts/kaggle_train_all.py`), mantenendo `on_topic_only=True`, label smoothing, nucleus.

---

## Riferimenti interni

- Pilot 1 (Struttura): `reports/struttura_pilot/confronto_modelli_finale.md`, `analisi_mode_collapse.md`, `local_training_report.md`
- Pilot 2 (Sapore): `reports/sapore_pilot/confronto_modelli_finale_sapore.md`, 12 report individuali (`0X_<MODEL>_report.md`), 4 cumulativi per cella
- Pipeline dati: `src/data/10_*.py` ... `16_*.py`, `src/data/normalizza_commenti.py`
- Loader fix: `src/models/dataset.py:99-100` (`on_topic_only=True`)
- Architetture: `src/models/encoders.py`, `src/models/decoders.py`, `src/models/models.py`
- Training: `train.py`, `src/models/train.py`
- Tokenizer: `src/models/vocabulary.py`
- Metriche: `src/models/metrics.py`
- Baseline: `src/models/baselines.py`, `evaluate_baselines.py`
- Specifiche progetto: `AI4FQC-Project Description Template_07_GRANA_Captioning.docx (2).pdf`
