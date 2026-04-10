# Design: Normalizzazione Commenti per Attributo (Fase 4)

**Data:** 2026-04-10  
**Branch:** feature/per-attribute-captioning  
**Stato:** APPROVATO

---

## Contesto

I commenti raw del panel sensoriale (~10.005 non vuoti, 7 attributi) devono essere trasformati in caption in linguaggio naturale italiano pronte per addestrare modelli encoder-decoder di image captioning. I commenti presentano forme anomale: dialetto, misure quantitative, abbreviazioni, telegrafico, fuori contesto.

La Fase 3 ha già prodotto 7 vocabolari JSON validati per attributo. La Fase 4 li usa per normalizzare i commenti.

---

## Approccio: Ibrido (programmatico + LLM)

**Step 1 — Programmatico (gratuito, deterministico):** applica le regole dei vocabolari JSON per sostituire sinonimi, typo, abbreviazioni e convertire misure quantitative in descrizioni qualitative.

**Step 2 — LLM (GPT-4o-mini, ~$0.50 totali con batching):** riceve il commento pre-normalizzato e lo riscrive in linguaggio naturale, classificandolo e producendo la caption finale.

---

## Sezione 1: Architettura

```
Per ogni attributo (7 totali):
  [Step 0 - una tantum]
    → LLM legge il vocabolario validato
    → Genera descrizione_baseline (campione conforme alla norma)
    → Salvata in data/interim/baseline_descriptions/{attributo}_baseline.json

  [Step 1 - programmatico]
    → Carica CSV raw 2018–2021 per l'attributo
    → Filtra righe con commento non vuoto
    → Carica vocabolario tramite modulo compila_vocabolari.py (già testato)
    → Applica regole vocabolario: sinonimi, typo, abbreviazioni, conversioni quantitative
    → Output: commento pre-normalizzato

  [Step 2 - LLM, batch da BATCH_SIZE commenti (default 20, configurabile)]
    → System prompt: contesto caseario + attributo + baseline + vocabolario
    → User message: lista commenti pre-normalizzati numerati
    → Output JSON: {id, classe, caption}
    → Salvataggio incrementale per batch

  [Output finale per attributo]
    → CSV: anno, prodotto, panelista, commento_raw, commento_prenorm, caption, classe
    → Report: distribuzione classi, 10 esempi before/after, % scartati
```

**File di input:**
- `07_captioning risultati grana Trentino/GT commenti liberi/csv dataset/*.csv`
- `data/interim/vocabolari_validati_per_attributo/{attributo}_vocabolario.json`

**File di output:**
- `data/interim/normalizzazione_in_corso/{attributo}_batch_{N}.json` (checkpoint)
- `data/processed/caption_per_attributo/{attributo}_captions.csv`
- `data/interim/baseline_descriptions/{attributo}_baseline.json`
- `reports/normalizzazione_{attributo}.md`

---

## Sezione 2: Prompt LLM e formato I/O

### Descrizioni attributo (hardcoded, 7 stringhe)

`descrizione_attributo` è una stringa fissa per ciascuno dei 7 attributi, definita nel modulo `normalizza_commenti.py`. Descrive brevemente cosa valuta l'attributo nel contesto del Grana Trentino (es. per Texture: *"Valuta le caratteristiche tattili della pasta: compattezza, granulosità, elasticità, presenza di difetti strutturali."*).

### System prompt (struttura fissa, compilata per attributo)

```
[CONTESTO CASEARIO]
Il Grana Trentino è un formaggio DOP a pasta dura stagionato prodotto in Trentino.
Le valutazioni provengono da un panel sensoriale esperto che assegna punteggi
e commenti liberi su campioni di formaggio.
Queste caption descrivono le caratteristiche sensoriali dei campioni e saranno
usate per addestrare modelli encoder-decoder di image captioning cheese-fetta → caption.
Il linguaggio deve essere tecnico ma naturale, in italiano standard.
Lunghezza target per caption: 15–60 parole.

[ATTRIBUTO CORRENTE]
Attributo: {nome_attributo}
Definizione: {descrizione_attributo}
Descrizione baseline (campione conforme alla norma):
  {descrizione_baseline}

[VOCABOLARIO VALIDATO]
Termini tecnici canonici: {lista_termini}
Cluster semantici: {cluster}
Conversioni quantitative: {conversioni}
Normalizzazioni (sinonimi → canonico): {sinonimi}
```

### User message (per ogni batch)

```
Normalizza i seguenti commenti di panel sensoriale. Per ciascuno restituisci
un oggetto JSON su una riga separata:
{"id": N, "classe": "OK|CONFORME|FUORI_ATTRIBUTO|RIFERIMENTO|ILLEGGIBILE", "caption": "..."|null}

Classi:
- OK: commento con contenuto specifico sull'attributo → caption normalizzata
- CONFORME: commento breve/generico che esprime conformità allo standard
  (es. "ok", "buono", "nella media") → espandi con la descrizione baseline
- FUORI_ATTRIBUTO: il commento riguarda un attributo diverso → caption null
- RIFERIMENTO: rimanda ad altra scheda (es. "vedi sopra") → caption null
- ILLEGGIBILE: incomprensibile o corrotto → caption null

Commenti:
1. "{commento_1}"
2. "{commento_2}"
...
```

### Output atteso (una riga JSON per commento)

```json
{"id": 1, "classe": "OK", "caption": "La struttura della pasta presenta stiratura diffusa con una frattura pronunciata."}
{"id": 2, "classe": "CONFORME", "caption": "La struttura della pasta risulta nella norma, compatta e omogenea, tipica del Grana Trentino."}
{"id": 3, "classe": "RIFERIMENTO", "caption": null}
{"id": 4, "classe": "FUORI_ATTRIBUTO", "caption": null}
```

---

## Sezione 3: Gestione errori, validazione e testing

### Resilienza

**Checkpoint incrementale:**
- Ogni batch completato viene salvato immediatamente in `data/interim/normalizzazione_in_corso/{attributo}_batch_{N}.json`
- Alla ripresa dello script, i batch già salvati vengono saltati
- Il CSV finale viene assemblato solo a tutti i batch completati

**Retry su errore API:**
- Retry automatico max 3 volte con backoff esponenziale (1s, 2s, 4s)
- Se dopo 3 retry il JSON è ancora invalido o malformato: i commenti del batch vengono marcati `ERRORE` nel CSV e loggati separatamente
- L'esecuzione prosegue senza bloccarsi

**Validazione JSON response:**
- Parsing riga per riga (jsonlines)
- Se un id manca o la classe è fuori enum → riga marcata `ERRORE_PARSING`
- Se il numero di righe restituite è diverso dal batch → warning + log

### Report di validazione

Generato al termine di ogni attributo in `reports/normalizzazione_{attributo}.md`:
- Distribuzione classi (conteggi e percentuali)
- Alert se % scartati (FUORI_ATTRIBUTO + RIFERIMENTO + ILLEGGIBILE) > 20%
- 10 esempi casuali before/after per revisione manuale
- Numero totale caption prodotte per il training

### Testing

| Test | Tipo | Cosa verifica |
|------|------|---------------|
| `test_step1_vocabolario` | Unit | Sostituzioni programmatiche corrette su fixture |
| `test_step2_parsing_json` | Unit | Parser jsonlines gestisce OK/CONFORME/null/ERRORE |
| `test_batch_resilienza` | Unit | Script riprende da batch parziale senza duplicati |
| `test_report_generazione` | Integration | File report prodotto con struttura attesa |
| `test_pipeline_end_to_end` | Integration (mock API) | CSV finale corretto da fixture di input |

---

## Stima costi

| Scenario | Modello | Costo stimato |
|----------|---------|---------------|
| Pilot (50 commenti/attributo) | GPT-4o-mini | ~$0.01 |
| Produzione completa | GPT-4o-mini | ~$0.50 |
| Produzione alta qualità | GPT-4o | ~$8.00 |

Raccomandazione: pilot su GPT-4o-mini, poi decidere.

---

## Script

`src/data/10_normalizza_commenti.py`

Modulo core separato: `src/data/normalizza_commenti.py` (testabile indipendentemente)

---

## Parametri configurabili

| Parametro | Default | Descrizione |
|-----------|---------|-------------|
| `BATCH_SIZE` | 20 | Commenti per chiamata API |
| `MAX_RETRY` | 3 | Retry su errore API |
| `MODEL` | `gpt-4o-mini` | Modello LLM da usare |
| `ALERT_SCARTATI_PCT` | 20 | Soglia % scartati per alert nel report |

---

## Decisioni aperte

Nessuna.
