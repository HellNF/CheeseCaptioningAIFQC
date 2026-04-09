# Pipeline Per-Attributo — Grana Trentino Captioning

**Documento di progettazione:** decisioni architetturali e pipeline di esecuzione  
**Creato:** 2026-04-09  
**Branch:** `feature/per-attribute-captioning`  
**Stato:** in sviluppo

---

## 1. Contesto e Motivazione

Il progetto genera caption testuali descrittive per campioni di formaggio Grana Trentino (TrentinGrana) a partire da immagini BMP + commenti sensoriali di un panel di assaggiatori professionisti (2018–2021).

### Perché il pivot a per-attributo

Il dataset unificato (`captions_finali.csv`, branch `main`) produce **348 coppie immagine–caption** — troppo poche per addestrare modelli encoder-decoder. La strategia per-attributo produce **~1400–1700 righe** (una per ogni coppia campione×attributo con almeno un commento), aumentando il dato di addestramento di 4–5×.

**Scopo:** addestrare modelli di image captioning. Tutti e 7 gli attributi vengono mantenuti, indipendentemente dalla loro ancorabilità visiva (Profumo, Sapore, Aroma non sono predibili dall'immagine, ma vengono inclusi comunque per completezza del dataset).

---

## 2. Attributi Sensoriali

| Attributo | Visivo | Note |
|---|---|---|
| Struttura della Pasta | ✅ True | frattura, grana, stiratura, microocchiatura |
| Colore della Pasta | ✅ True | tonalità, alone centrale, disomogeneità |
| Spessore della Crosta | ✅ True | mm/cm → soglie qualitative |
| Texture | ✅ True | solubilità, friabilità, cristalli, tirosina |
| Profumo | ❌ False | olfattivo — non visibile |
| Sapore | ❌ False | gustativo — non visibile |
| Aroma | ❌ False | retrolfattivo — non visibile |

La colonna `is_visual_attribute` nel dataset finale codifica questa distinzione.

---

## 3. Sorgenti Dati Raw

### File originali per NotebookLM (NON usare fase_B)
```
07_captioning risultati grana Trentino/GT commenti liberi/csv dataset/
  Commenti TOT_2018_{Attributo}.csv          ← schema: Sogg, Seduta, Prod, {Score}, Commenti
  Commenti liberi_QTG_2019_{Attributo}.csv   ← schema: Data Seduta, N° Seduta, Bimestre, Data Prod, Panelista, Prodotto, Commenti
  Commenti liberi_QTG_2020_{Attributo}.csv
  Commenti liberi_TEST_2021_{Attributo}.csv
07_captioning risultati grana Trentino/GT commenti liberi/codifiche/
  Risultati_2019-21_Medie Giuria2019_Q.csv   ← punteggi aggregati giuria 2019
  Risultati_2019-21_Medie Giuria2020_Q .csv  ← punteggi aggregati giuria 2020
  Risultati_2019-21_Medie Giuria2021_Q.csv   ← punteggi aggregati giuria 2021
```

### Schema 2018 (unico con punteggi individuali per panelista)
- La colonna 4 (`{Attributo}`) contiene il **punteggio numerico individuale** (es. "7,48" con virgola italiana)
- Utile per calibrare soglie quantitativo→qualitativo (es. per Spessore della Crosta: misura mm vs punteggio)

### Schema 2019–2021
- Nessun punteggio individuale nei file per-attributo
- Punteggi aggregati di giuria in `Risultati_2019-21_*.csv`

---

## 4. Pipeline di Esecuzione

```
FASE 1  →  Script 08_analisi_per_attributo.py
FASE 2  →  NotebookLM [step manuale + automatizzato via CLI]
FASE 3  →  Revisione umana vocabolari [step manuale]
FASE 4  →  Script 09_normalizza_commenti_per_attributo.py
FASE 5  →  Script 10_genera_caption_per_attributo.py
```

---

### FASE 1 — Analisi statistica per attributo

**Script:** `src/data/08_analisi_per_attributo.py`  
**Input:** `csv dataset/*.csv` (raw, tutti gli anni)  
**Output:** `data/interim/analisi_statistica_per_attributo/`

Per ogni attributo genera:
- `{Attributo}_statistiche.md` — distribuzione termini, top-N parole, % vuoti, lunghezza media commenti
- `{Attributo}_contesto_notebooklm.md` — context report da caricare su NotebookLM
- `{Attributo}_soglie_quantitative.md` — **solo per Spessore della Crosta**: correlazione misure mm/cm con punteggi 2018 → soglie qualitative stimate

**Soglie quantitative Spessore della Crosta (calibrate su 2018):**
Logica: aggrega misure testuali (es. "1cm", "10mm", "12 mm") e i relativi punteggi individuali → stima range qualitativo.
Output atteso:
```
< 7mm  → "molto sottile"
7–12mm → "nella norma"
12–18mm → "spessa"
> 18mm → "molto spessa"
(valori da validare con revisione umana)
```

---

### FASE 2 — NotebookLM (automatizzata via CLI)

**Script:** integrato in `08_analisi_per_attributo.py` (sezione NotebookLM)  
**Tool:** `notebooklm-py` v0.3.4 (già installato e autenticato)

Per ogni attributo:
1. Crea notebook: `"Grana Trentino — {Attributo}"`
2. Carica sorgenti:
   - 4 CSV raw (2018, 2019, 2020, 2021)
   - 3 CSV punteggi aggregati (2019–2021)
   - 1 context report generato da Fase 1
3. Attende elaborazione sorgenti
4. Esegue 4 query sequenziali (vedi §5)
5. Salva risposte come note nel notebook
6. Scarica vocabolario bozza in `data/interim/vocabolari_bozza_per_attributo/`

**Output:** `data/interim/vocabolari_bozza_per_attributo/`
```
{Attributo}_vocabolario_nblm.md     ← risposta aggregata delle 4 query
{Attributo}_dubbi_revisione.md      ← dubbi estratti dalla Query 4
```

---

### FASE 3 — Revisione umana [STEP MANUALE]

**Input:** `data/interim/vocabolari_bozza_per_attributo/`  
**Output:** `data/interim/vocabolari_validati_per_attributo/{Attributo}_vocabolario.json`

Il revisore umano:
1. Legge `{Attributo}_vocabolario_nblm.md` e `{Attributo}_dubbi_revisione.md`
2. Confronta con `{Attributo}_soglie_quantitative.md` (per Spessore della Crosta)
3. Compila `{Attributo}_vocabolario.json` con le regole di normalizzazione approvate

**Formato JSON vocabolario validato:**
```json
{
  "attributo": "Spessore della Crosta",
  "versione": "1.0",
  "data_validazione": "YYYY-MM-DD",
  "termini_tecnici_invariabili": ["scalzo", "piatti", "sottocrosta", ...],
  "cluster": [
    {
      "nome_cluster": "spessore_normale",
      "forma_canonica": "nella norma",
      "varianti": ["normale", "regolare", "ok", "1cm", "10mm", "9-10mm"],
      "range_mm": [7, 12]
    }
  ],
  "sinonimi": [
    {"da": "legg.", "a": "leggermente"},
    {"da": "cristali", "a": "cristalli"}
  ],
  "dialettalismi": [
    {"da": "...", "a": "..."}
  ],
  "dubbi_non_risolti": []
}
```

---

### FASE 4 — Normalizzazione commenti

**Script:** `src/data/09_normalizza_commenti_per_attributo.py`  
**Input:** `csv dataset/*.csv` (raw) + `vocabolari_validati_per_attributo/*.json`  
**Output:** `data/interim/commenti_normalizzati_per_attributo/`

Per ogni coppia (attributo, anno):
- Applica sinonimi, dialettalismi, abbreviazioni dal vocabolario validato
- Converte termini quantitativi in qualitativi (Spessore della Crosta)
- Arricchisce commenti telegrafici (via GPT-4o-mini con vocabolario come contesto)
- Genera: `{Attributo}_{Anno}_normalizzato.csv`

**Colonne output:**
```
Prodotto, Panelista, Anno, Commento_originale, Commento_normalizzato, 
Modifiche_applicate, Flag_arricchimento_LLM
```

---

### FASE 5 — Generazione caption per attributo

**Script:** `src/data/10_genera_caption_per_attributo.py`  
**Input:** `commenti_normalizzati_per_attributo/` + `campioni_completi.csv` (per path immagini)  
**Output:** `data/processed/captions_per_attributo/` — **un CSV per attributo**

```
captions_Aroma.csv
captions_Colore_della_Pasta.csv
captions_Profumo.csv
captions_Sapore.csv
captions_Spessore_della_Crosta.csv
captions_Struttura_della_Pasta.csv
captions_Texture.csv
```

**Schema long format (colonne per CSV):**
```
sample_id, anno, codice_caseificio, data_seduta,
path_fetta_primaria, path_grana_primaria,
is_visual_attribute,
attributo, caption,
n_panelisti, n_commenti_usati, tokens_usati, timestamp_generazione
```

**Soglia inclusione:** almeno 1 commento non vuoto dopo normalizzazione.  
**Modello:** GPT-4o-mini, temperature 0.3, max_tokens 300 (caption singolo attributo → più brevi)

---

## 5. Prompt NotebookLM — 4 Query per Attributo

Le query vengono eseguite sequenzialmente. Ogni risposta viene salvata come nota nel notebook.

### Query 1 — Inventario termini
```
Nei CSV caricati, la colonna "Commenti" contiene le valutazioni scritte a mano 
dai panelisti durante le sessioni di degustazione del Grana Trentino.
Per l'attributo {ATTRIBUTO}: estrai TUTTI i termini e le espressioni distinte 
dalla colonna "Commenti" di tutte le fonti. Per ogni termine indica:
| Termine | Occorrenze | Anni presenti | Esempio frase completa |
Includi anche termini che compaiono una sola volta.
```

### Query 2 — Cluster semantici e forma canonica
```
Raggruppa i termini identificati in cluster semantici: ogni cluster rappresenta 
un concetto sensoriale unico per {ATTRIBUTO}.
Per ogni cluster:
**Cluster: [nome concetto]**
- Varianti trovate: termine1, termine2, ...
- Forma canonica proposta: [termine più chiaro e corretto]
- Motivazione: [perché questa forma]

I seguenti termini tecnici caseari sono INVARIABILI — non normalizzarli:
scalzo, piatti, sottocrosta, microocchiatura, occhiatura, grana, frattura,
stirata, cristalli, tirosina, nostrano, insilato, solubile, friabile, compatto
```

### Query 3 — Anomalie e termini quantitativi
```
Identifica nella colonna "Commenti" per {ATTRIBUTO}:
1. ABBREVIAZIONI: termini troncati (es. "legg." → cosa significa nel contesto?)
2. DIALETTALISMI: termini in dialetto o colloquiali non standard
3. ERRORI ORTOGRAFICI: typo o parole scritte in modo errato
4. ESPRESSIONI QUANTITATIVE: numeri, misure (mm, cm, %), scale numeriche.
   Per ogni quantitativo: confrontalo con i punteggi numerici nelle colonne 
   di score del file 2018 o nei file Risultati — a che punteggio corrisponde?
5. CONTRADDIZIONI: frasi opposte di panelisti diversi sullo stesso campione

Formato: | Termine trovato | Tipo | Proposta normalizzazione | Confidenza |
```

### Query 4 — Dubbi per revisione umana
```
Lista i casi dove non sei sicuro della normalizzazione corretta e serve 
una decisione umana. Per ogni dubbio:

**DUBBIO:** "[termine o espressione]"
- Ambiguità: perché non è chiaro
- Opzione A: [prima interpretazione]
- Opzione B: [seconda interpretazione]
- Suggerimento NotebookLM: [quale preferiresti e perché]
- Dati a supporto: [citazioni dal testo o punteggi che orientano la scelta]
```

---

## 6. Template Context Report per NotebookLM

*(generato da script 08 per ogni attributo)*

```markdown
# Analisi Sensoriale Grana Trentino — {ATTRIBUTO}

## Il formaggio
Il TrentinGrana (Grana Trentino) è un formaggio a pasta dura e cotta prodotto 
in Trentino. Le sessioni di valutazione sensoriale (2018–2021) coinvolgono un 
panel di assaggiatori professionisti che valutano ogni campione su 7 attributi.

## Questo attributo: {ATTRIBUTO}
{DESCRIZIONE_SPECIFICA_ATTRIBUTO}

## Come leggere i CSV caricati
- "Commenti": testo libero scritto dal panelista — QUESTO è il dato da analizzare
- "Prodotto"/"Prod": codice anonimo del campione di formaggio
- "Panelista"/"Sogg": codice anonimo del valutatore
- File 2018: colonna "{ATTRIBUTO}" = punteggio numerico (1–10) dello stesso panelista
- File Risultati_*: punteggi medi di giuria per campione (utile per calibrazione)

## Caratteristiche dei commenti
I commenti sono spesso telegrafici (1–5 parole) perché scritti durante 
la degustazione in tempo reale. Non interpretare silenzi o assenze come dati.
Non aggiungere interpretazioni non presenti nel testo originale.

## Obiettivo
Costruire un dizionario di normalizzazione: identificare tutti i termini usati 
e proporre una forma standard, raggruppando sinonimi, varianti ortografiche, 
abbreviazioni e dialettalismi dello stesso concetto sensoriale.

## Termini tecnici INVARIABILI (non normalizzare mai questi)
scalzo, piatti, sottocrosta, microocchiatura, occhiatura, grana, frattura,
stirata, cristalli, tirosina, nostrano, insilato, solubile, friabile, compatto,
scalzi, spigoli, angoli, cedevole, solubilità, friabilità, compattezza
```

---

## 7. Struttura Cartelle del Branch

```
data/
  interim/
    analisi_statistica_per_attributo/     ← Fase 1: stats, soglie quantitative
    vocabolari_bozza_per_attributo/        ← Fase 2: output NotebookLM (bozza)
    vocabolari_validati_per_attributo/     ← Fase 3: vocabolari approvati da umano
    commenti_normalizzati_per_attributo/   ← Fase 4: commenti post-normalizzazione
  processed/
    captions_per_attributo/               ← Fase 5: caption finali, un CSV per attributo
      captions_Aroma.csv
      captions_Colore_della_Pasta.csv
      captions_Profumo.csv
      captions_Sapore.csv
      captions_Spessore_della_Crosta.csv
      captions_Struttura_della_Pasta.csv
      captions_Texture.csv
src/
  data/
    08_analisi_per_attributo.py
    09_normalizza_commenti_per_attributo.py
    10_genera_caption_per_attributo.py
reports/
  08_analisi_per_attributo.md
  09_normalizzazione_commenti.md
  10_captions_per_attributo.md
docs/
  pipeline_per_attributo.md              ← questo file
```

---

## 8. Decisioni Architetturali (log)

| Decisione | Scelta | Motivazione |
|---|---|---|
| Formato dataset | Long format (sample × attributo) | Flessibilità al training: filtra per attributo senza riscrivere schema |
| Attributi non visivi | Inclusi (Profumo, Sapore, Aroma) | Completezza dataset, colonna `is_visual_attribute` discrimina |
| Sorgenti NBLM | File raw (`csv dataset/`) non fase_B | Contesto originale non contaminato dalla nostra pulizia |
| Vocabolario sinonimi | Generato da NBLM + validazione umana | Corpus-wide, non biased da conoscenza pregressa |
| Termini quantitativi | Score 2018 (individuali) + interpretazione NBLM | Doppia fonte, decisione umana finale |
| Formato dubbi | `.md` human-readable | Editabile senza strumenti speciali |
| Vocabolario validato | JSON strutturato | Machine-readable per script 09 |
| Modello enrichment | GPT-4o-mini | Coerente con pipeline esistente, già configurato |
| Output Fase 5 | Un CSV per attributo (7 file) | Più leggibile, facile da filtrare per training |
| Branch strategy | `feature/per-attribute-captioning` | Main mantiene le 348 caption unificate come fallback |

---

## 9. Relazione con Pipeline Esistente (branch main)

Il branch `main` contiene la pipeline originale **non toccata**:
- Script 01–07 invariati
- `data/processed/captions_finali.csv` — 348 caption unificate

Questo branch aggiunge script 08–10 e nuove cartelle senza modificare nulla di esistente.  
Al merge futuro: nessun conflitto atteso su file esistenti.

---

## 10. Stato Avanzamento

- [x] Design architetturale concordato
- [x] Prompt NotebookLM definiti
- [x] Struttura cartelle definita
- [ ] Branch creato
- [ ] Script 08 — analisi statistica per attributo
- [ ] Script 08 — integrazione NotebookLM (creazione notebook + upload + query)
- [ ] Fase 3 — revisione umana vocabolari
- [ ] Script 09 — normalizzazione commenti
- [ ] Script 10 — generazione caption per attributo
