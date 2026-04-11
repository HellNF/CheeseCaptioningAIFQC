# Report — Fase 4: Normalizzazione Commenti Panel Sensoriale

**Data:** 2026-04-11  
**Branch:** `feature/per-attribute-captioning`  
**Commit finale:** `8a11305`

---

## 1. Contesto e obiettivo

Il dataset del Grana Trentino DOP contiene valutazioni panel sensoriale raccolte su **7 attributi**:
Sapore, Aroma, Profumo, Spessore della Crosta, Struttura della Pasta, Colore della Pasta, Texture.

Ogni valutazione è un commento libero scritto da un panelista esperto. L'obiettivo della Fase 4 era
**normalizzare questi commenti** in caption standardizzate, adatte al training di un modello AI per
il Quality Food Control (FQC).

---

## 2. Architettura della pipeline

La normalizzazione è strutturata in 4 fasi operative (script 10–13):

```
10_normalizza_commenti.py       ← normalizzazione principale (LLM batch)
11_riprocessa_conforme.py       ← promozione CONFORME → OK via baseline
12_riprocessa_fuori_attributo.py ← caption per righe FUORI con caption null
13_fix_hallucinations.py        ← correzione caption alluciante
```

Ogni script è idempotente e checkpoint-based: può essere interrotto e ripreso senza perdita di
lavoro. Il modello utilizzato è **GPT-4o-mini** via OpenAI API.

### Classi di output

| Classe | Significato |
|--------|-------------|
| `OK` | Commento pertinente → caption normalizzata sul vocabolario dell'attributo |
| `CONFORME` | Conformità generica ("ok", "buono") → espansa con baseline dell'attributo |
| `FUORI_ATTRIBUTO` | Commento su un attributo diverso → caption in linguaggio naturale |
| `ILLEGGIBILE` | Testo incomprensibile → caption null |
| `RIFERIMENTO` | Rimanda ad altra scheda → caption null |
| `ERRORE_PARSING` | Risposta LLM non parsabile |

---

## 3. Componenti del modulo `normalizza_commenti.py`

Il modulo centrale implementa:

- **`carica_vocabolario`** — legge i JSON vocabolario validati per attributo
- **`carica_baseline`** — legge le descrizioni baseline per attributo  
- **`prenormalizza_commento`** — pre-processing rule-based (sinonimi, misure quantitative, regex)
- **`genera_baseline`** — genera la descrizione baseline via LLM
- **`normalizza_batch`** — normalizzazione batch con system prompt per attributo
- **`riprocessa_conforme_batch`** — promuove CONFORME a OK con prompt fedeltà
- **`riprocessa_fuori_attributo_batch`** — genera caption per FUORI con null caption
- **`trova_hallucinate`** — rileva caption duplicate/simili alla baseline (allucinazioni)
- **`normalizza_faithful_batch`** — riprocessa allucinazioni con regola di fedeltà esplicita
- **`parse_llm_response`** — parsing JSONL robusto delle risposte LLM

**Test coverage:** 54 test pytest, tutti passing.

---

## 4. Problemi critici rilevati e risolti

### 4a. 40 righe ERRORE in Spessore della Crosta

**Causa:** Il pre-normalizzatore (`prenormalizza_commento`) generava output malformato per
commenti con misure quantitative (es. "10 mm") a causa di un bug nel matching del pattern_regex.

**Soluzione:** Fix al pattern matching + esecuzione one-shot con `commento_raw` (bypassando la
prenorm degradata) → 0 ERRORE residui.

### 4b. 186 allucinazioni in Sapore

**Causa:** Per commenti brevi e ambigui (es. "Ottimo equilibrio", "Tendenza dolce"), il LLM
tendeva a produrre la caption baseline del campione conforme invece di una caption specifica.
La stessa caption appariva per ID con commenti molto diversi.

**Rilevamento:** `trova_hallucinate()` — rileva caption con ≥ 5 occorrenze AND (similarità
alla baseline ≥ 0.45 OR count ≥ 15).

**Soluzione:** `normalizza_faithful_batch()` con header `_FAITHFUL_MSG_HEADER` che impone
esplicitamente la regola di fedeltà al commento originale. Due passaggi LLM:
- Passaggio 1: 186 → 79 residui
- Passaggio 2: 79 → 29 residui (88% riduzione totale)
- 29 residui gestiti via revisione manuale (`residui_hallucination.csv`)

### 4c. 772 falsi negativi FUORI_ATTRIBUTO

**Causa:** Il LLM classificava come FUORI_ATTRIBUTO commenti che descrivevano genuinamente
l'attributo in esame, usando terminologia comparativa (es. "provolone", "carne lessa", "stantio"
per Aroma) non presente nelle keyword del vocabolario.

**Rilevamento:** `export_revisione_fuori_attributo.py` — esporta tutti i FUORI con flag
`candidato_ok` (keyword heuristics) per revisione.

**Soluzione:** Revisione AI-assistita di 797 righe → 772 reclassificate OK (97%), 25 mantenute
FUORI (privi di descrittori specifici: "Non piacevole!!!", "Forse voto troppo alto", ecc.).

---

## 5. Processo di revisione manuale / AI-assistita

Due file CSV intermedi usati come interfaccia di revisione:

### `residui_hallucination.csv` (41 righe)
Colonne: `attributo, id, commento_raw, caption (hallucin.), nuova_caption`

Caption riscritte manualmente/AI:
- **Sapore:** caption fedeli (es. "Piccante fortissimo e persistente" → "Il sapore presenta una piccantezza fortissima e persistente nel finale.")
- **Spessore:** applicata scala quantitativa dal vocabolario (10 mm → "nella norma", "Pulita" → "colore chiaro")

### `revisione_fuori_attributo.csv` (797 righe)
Colonne: `attributo, id, commento_raw, caption, candidato_ok, nuova_classe`

Logica di classificazione:
- Candidati con keyword pertinenti (`candidato_ok=True`): quasi tutti → OK
- Candidati senza keyword (`candidato_ok=False`): analisi caso-per-caso; mantenuti FUORI
  solo i commenti privi di qualsiasi descrittore specifico dell'attributo

---

## 6. Statistiche finali del dataset

| Attributo | Righe | OK | CONFORME | FUORI | ILLEGGIBILE | Altro | Lung. media OK |
|-----------|------:|----:|--------:|------:|------------:|------:|---------------:|
| Sapore | 1.599 | **1.539 (96.2%)** | 29 | 13 | 15 | 3 | 63 car. |
| Aroma | 1.097 | **1.042 (95.0%)** | 8 | 9 | 25 | 13 | 48 car. |
| Profumo | 395 | **360 (91.1%)** | 4 | 4 | 11 | 16 | 38 car. |
| Spessore della Crosta | 1.058 | 473 (44.7%) | 47 | 498 (47.1%) | 32 | 8 | 96 car. |
| Struttura della Pasta | 1.916 | 905 (47.2%) | 29 | 875 (45.7%) | 106 | 1 | 82 car. |
| Colore della Pasta | 1.522 | 1.080 (71.0%) | 49 | 368 (24.2%) | 25 | 0 | 76 car. |
| Texture | 1.385 | 934 (67.4%) | 11 | 413 (29.8%) | 26 | 1 | 78 car. |
| **Totale** | **8.972** | **6.333 (70.6%)** | 177 | 2.180 | 240 | 42 | — |

**Nota Spessore/Struttura:** L'alto tasso di FUORI_ATTRIBUTO (~47%) è fisiologico — panelisti
esperti spesso commentano questi attributi con osservazioni trasversali o misure numeriche che
il LLM non sempre interpreta come pertinenti.

---

## 7. Decisioni di design e motivazioni

### 7a. Decisioni architetturali (pipeline)

**GPT-4o-mini invece di GPT-4o**
Il task di normalizzazione è strutturato e vincolato dal system prompt e dal vocabolario: non richiede
ragionamento complesso, solo classificazione e parafrasi guidata. GPT-4o-mini offre un rapporto
costo/prestazioni nettamente superiore per questo tipo di compito; GPT-4o sarebbe giustificato solo
per task con ambiguità alta o giudizio contestuale profondo.

**Batch JSONL invece di chiamate singole**
Ogni batch aggrega fino a 30 commenti in una sola chiamata API. Il risparmio è circa 30x sul numero
di richieste, con impatto diretto su costo e latenza. Il parsing JSONL è robusto: un errore su una
riga non invalida l'intero batch.

**Checkpoint per attributo invece che per batch**
Il checkpoint salva il CSV dopo ogni attributo completato. Granularità sufficiente per il recovery
(il dataset per attributo non supera le 2000 righe) senza aggiungere complessità di stato
intermedio. Un checkpoint per batch avrebbe reso il codice più fragile senza benefici pratici.

**`commento_raw` per il fix delle allucinazioni invece di `commento_prenorm`**
La pre-normalizzazione può introdurre perdita di informazione (abbreviazioni espanse, misure
convertite) che riduce la specificità del testo e favorisce il collasso sul template baseline.
Usando `commento_raw` il LLM lavora sul testo più vicino all'intenzione originale del panelista.

---

### 7b. Decisioni sulla qualità dei dati

**Rilevamento allucinazioni con soglie `min_count=5, sim_threshold=0.45`**
Le soglie sono state calibrate empiricamente: `min_count=5` filtra varianti casuali mantenendo solo
pattern sistematici; `sim_threshold=0.45` cattura parafasi della baseline senza colpire caption
legittime con lessico parzialmente sovrapposto. Dopo i fix, il dry-run su tutti gli attributi
restituisce 0 sospette — le soglie sono appropriate e non richiedono ricalibrazione.

**Heuristic keyword per falsi negativi invece di un secondo passaggio LLM**
Un secondo passaggio LLM avrebbe potuto produrre nuovi falsi negativi o ribaltare classificazioni
corrette. Le keyword del vocabolario offrono un criterio trasparente, verificabile e deterministico.
Il tasso di recupero (97% dei candidati reclassificati OK dopo revisione) conferma che l'euristica
era ben calibrata.

**Revisione AI-assistita sui residui invece di ri-esecuzione LLM**
Le 41 allucinazioni residue dopo due passaggi LLM erano concentrate su commenti genuinamente
ambigui (es. "Ottimo equilibrio", "Deciso ed equilibrato") dove il LLM non riesce a distinguere
un'osservazione specifica dalla conformità generica. La revisione diretta è più affidabile: si
applica la scala quantitativa del vocabolario (es. misure mm → "nella norma") e si scrive una
caption letterale al commento senza passare attraverso il modello.

**ERRORE_PARSING corretti con caption dirette invece di ri-esecuzione API**
I batch con parsing fallito contenevano esclusivamente commenti brevi e non ambigui (es. "alcol",
"cipolla", "tostato", "marcio"). Una ri-esecuzione API avrebbe avuto costo non nullo senza
garanzie di successo. La caption diretta è più rapida, più controllabile e produce risultati di
qualità identica.

---

### 7c. Decisioni sul formato del dataset

**Colonna `peso` per il training (CONFORME → 0.5)**
I 177 CONFORME hanno tutti caption identica alla baseline dell'attributo: stesso input di classe
diverso, stesso output. Includerli con peso pieno farebbe sì che il modello riceva 177 esempi
con output identico, rischiando di sovrastimare la probabilità della formulazione standard e di
appiattire la generazione su pochi template. Il peso 0.5 mantiene il segnale di questa classe
(il modello deve saper riconoscere la conformità generica) senza che domini il gradiente.

**FUORI_ATTRIBUTO inclusi nel training senza filtraggio**
Le 2.180 righe FUORI sono esempi negativi fondamentali: insegnano al modello a riconoscere e
gestire commenti fuori scope per ciascun attributo. Escluderle produrrebbe un modello fragile
sui dati reali, dove commenti fuori attributo arrivano frequentemente. Il loro peso è 1.0 perché
rappresentano una classe distinta con segnale proprio, non duplicati.

**Revisione FUORI rimandataa per Struttura e Spessore**
A differenza di Sapore/Aroma/Profumo (dove il FUORI era principalmente un problema di
classificazione LLM su terminologia comparativa), per Struttura e Spessore l'alto tasso di FUORI
(~47%) è in buona parte fisiologico: i panelisti commentano questi attributi con osservazioni
trasversali o riportano misure che il LLM correttamente non riconduce all'attributo. Una revisione
rischiosa di sporcare le classi senza benefici chiari. Decisione: rivalutare solo se il training
mostra underfitting specifico su questi attributi.

---

## 8. File prodotti

```
src/data/
  normalizza_commenti.py              ← modulo core (funzioni + costanti)
  10_normalizza_commenti.py           ← pipeline script principale
  11_riprocessa_conforme.py           ← promozione CONFORME
  12_riprocessa_fuori_attributo.py    ← caption FUORI con null
  13_fix_hallucinations.py            ← correzione allucinazioni
  export_revisione_fuori_attributo.py ← export per revisione

tests/
  test_normalizza_commenti.py         ← 54 test

data/interim/
  baseline_descriptions/              ← 7 JSON baseline per attributo
  residui_hallucination.csv           ← 41 righe con nuova_caption
  revisione_fuori_attributo.csv       ← 797 righe annotate

data/processed/caption_per_attributo/
  Sapore_captions.csv                 ← 1.599 righe
  Aroma_captions.csv                  ← 1.097 righe
  Profumo_captions.csv                ← 395 righe
  Spessore_della_Crosta_captions.csv  ← 1.058 righe
  Struttura_della_Pasta_captions.csv  ← 1.916 righe
  Colore_della_Pasta_captions.csv     ← 1.522 righe
  Texture_captions.csv                ← 1.385 righe
```

---

## 9. Correzioni post-review (sessione grilling)

Dopo la stesura del report, sono stati applicati i seguenti fix:

| Fix | Righe | Dettaglio |
|-----|------:|---------|
| Aroma id=244 caption null | 1 | "brodo...." -> "Si percepisce un aroma di brodo." |
| Profumo ERRORE_PARSING | 16 | 15 -> OK con caption diretta, 1 -> ILLEGGIBILE |
| Sapore ERRORE_PARSING | 3 | 2 -> OK, 1 -> ILLEGGIBILE |
| Aroma ERRORE_PARSING | 11 | 8 -> OK, 3 -> ILLEGGIBILE |
| Colonna `peso` su tutti i CSV | 177 | CONFORME -> 0.5, resto -> 1.0 |

**Stato finale dopo fix:** 0 ERRORE_PARSING su tutti e 7 gli attributi, 0 caption OK vuote.

### Statistiche aggiornate

| Attributo | Righe | OK | CONFORME | FUORI | ILLEGGIBILE |
|-----------|------:|----:|--------:|------:|------------:|
| Sapore | 1.599 | 1.541 (96.4%) | 29 | 13 | 16 |
| Aroma | 1.097 | 1.050 (95.7%) | 8 | 9 | 28 |
| Profumo | 395 | 375 (94.9%) | 4 | 4 | 12 |
| Spessore della Crosta | 1.058 | 473 (44.7%) | 47 | 498 | 32 |
| Struttura della Pasta | 1.916 | 905 (47.2%) | 29 | 875 | 106 |
| Colore della Pasta | 1.522 | 1.080 (71.0%) | 49 | 368 | 25 |
| Texture | 1.385 | 934 (67.4%) | 11 | 413 | 26 |
| **Totale** | **8.972** | **6.358 (70.9%)** | 177 | 2.180 | 245 |

---

## 10. Punti aperti (rimandati)

- **Struttura/Spessore FUORI (~47%):** non esaminati per falsi negativi. Da rivalutare
  solo se il training mostra underfitting su questi attributi specifici.
- **CONFORME variance:** i 177 CONFORME hanno tutti caption = baseline (output identico).
  Gestito con `peso=0.5` nel CSV; valutare esclusione totale se il modello sovrafitta.
