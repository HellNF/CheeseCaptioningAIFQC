# Overview: 07_captioning risultati grana Trentino

Questa cartella contiene i dati del progetto di valutazione sensoriale del formaggio **Grana Trentino (TrentinGrana)**, raccolti nell'ambito di un programma di quality control che si estende dal 2018 al 2022. Include immagini delle forme di formaggio (fette e grana) e dati tabulari con punteggi sensoriali, commenti liberi dei panelisti e metadati delle sessioni di analisi.

---

## Struttura della Cartella

```
07_captioning risultati grana Trentino/
├── TrentinGrana/                          # Immagini BMP delle forme di formaggio
│   ├── 2018-2019_Trentingrana/            # 633 immagini, 28 sessioni (cartelle per data)
│   ├── 2019-2020_Trentingrana/            # 592 immagini, 5 bimestri (I-V)
│   ├── 2020-2021_Trentingrana/            # 836 immagini, 6 bimestri (I-VI)
│   └── 2021-2022_Trentingrana/            # 684 immagini, 31 sedute
├── GT commenti liberi/                    # Dati tabulari (Excel + CSV)
│   ├── codifiche/                         # Tabelle di codifica e risultati aggregati
│   ├── csv dataset/                       # Export CSV dei dati (per attributo sensoriale)
│   ├── Commenti TOT_2018.xlsx
│   ├── Commenti liberi_QTG_2019.xlsx
│   ├── Commenti liberi_QTG_2020.xlsx
│   └── Commenti liberi_TEST_2021.xlsx
└── validation_reports/                    # Report di validazione dati
    └── session_validation_report.csv
```

---

## 1. Immagini BMP (TrentinGrana/)

**Totale: 2.745 immagini BMP** distribuite su 4 annate.

### Contenuto
Ogni sessione di valutazione produce fotografie di forme di formaggio in due viste:
- **FETTA** (1.285 immagini): vista della sezione/fetta del formaggio
- **GRANA** (1.360 immagini): vista della grana/texture della pasta

### Convenzione di Naming dei File

Il formato del nome file si e' evoluto nel tempo:

| Annata | Formato | Esempio |
|---|---|---|
| 2018-2019 | `P{pos}{lato}_{codice}_{vista}.bmp` | `P1a_302_fetta.bmp` |
| 2019-2020 | `P{pos}{lato}_TN{codice}_{vista}.bmp` | `P1a_TN302_Fetta.bmp` |
| 2020-2021 | `P{pos}{LATO}_TN{codice}_{id}_{VISTA}.bmp` | `P1A_TN302_527_FETTA.bmp` |
| 2021-2022 | `P{pos}_TN{codice}_{id}_{VISTA}_{replica}.bmp` | `P1_TN302_680_FETTA_A.bmp` |

**Componenti del nome:**
- **P{numero}**: posizione della camera (P1-P6)
- **{lato}** o **{LATO}**: lato della forma (a/b oppure A/B)
- **TN{codice}**: codice caseificio trentino (es. TN302, TN305)
- **{id}**: numero identificativo della forma (3 cifre, presente dal 2020-2021)
- **{VISTA}**: tipo di immagine (`FETTA` o `GRANA`)
- **{replica}**: replica A o B (presente solo dal 2021-2022)

### Organizzazione per Annata

| Annata | N. Immagini | Organizzazione Cartelle | N. Sessioni |
|---|---|---|---|
| 2018-2019 | 633 | Per data (es. `2018-08-29`) | 28 |
| 2019-2020 | 592 | Per bimestre (I-V), poi per seduta | 26 |
| 2020-2021 | 836 | Per bimestre (I-VI), poi per seduta | 29 |
| 2021-2022 | 684 | Per seduta (1°-31° Seduta) | 31 |

---

## 2. File Excel - Commenti Liberi

Questi file contengono i commenti testuali dei panelisti durante le valutazioni sensoriali del formaggio. Esistono **due formati distinti** tra il 2018 e gli anni successivi.

### 2.1 Commenti TOT_2018.xlsx

**8 fogli** (7 attributi sensoriali + 1 mapping date)

#### Fogli degli attributi (7 fogli) - Schema "2018"

| Colonna | Tipo | Descrizione |
|---|---|---|
| `Sogg` | int | ID del panelista/soggetto |
| `Seduta` | int | Numero della sessione di valutazione |
| `Prod` | string | Codice prodotto (es. C0A, C0B) |
| `{Attributo}` | string/float | Punteggio numerico per l'attributo (formato italiano con virgola, es. "7,48") |
| `Commenti` | string | Commento libero testuale in italiano |

**Attributi valutati (nomi dei fogli):**
- `Profumo` (~1.574 righe)
- `Sapore` (~1.574 righe)
- `Aroma` (~1.562 righe)
- `Texture` (~1.574 righe)
- `Spessore della Crosta` (~1.622 righe)
- `Struttura della Pasta` (~1.574 righe)
- `Colore della Pasta` (~1.574 righe)

**Nota:** Questo e' il dataset piu' grande. Contiene sia punteggi individuali che commenti per ogni panelista/prodotto/sessione. I punteggi per Profumo/Sapore/Aroma sono stringhe con virgola decimale; quelli per Spessore/Struttura/Colore sono float.

#### Foglio `date_sedute_2018`

| Colonna | Tipo | Descrizione |
|---|---|---|
| `Session` | int | Numero della sessione |
| `Date` | string | Data della sessione (formato YYYY-MM-DD) |

Contiene 29 righe che mappano il numero della sessione alla data effettiva.

---

### 2.2 Commenti liberi_QTG_2019.xlsx

**7 fogli** (uno per attributo sensoriale) - Schema "2019-2021"

| Colonna | Tipo | Descrizione |
|---|---|---|
| `Data Seduta di valutazione` | date | Data della sessione di valutazione |
| `N Seduta` | int | Numero progressivo della sessione |
| `Bimestre di Valutazione` | string | Bimestre di appartenenza (es. "I", "II") |
| `Data Produzione` | date | Data di produzione del formaggio |
| `Panelista` | string | ID del panelista (es. TG_19, Q_10) |
| `Prodotto` | string | Codice prodotto (es. C0A, C0N) |
| `Commenti` | string | Commento libero testuale in italiano |

**Righe per attributo:**

| Foglio | Righe |
|---|---|
| Profumo | 115 |
| Sapore | 72 |
| Aroma | 63 |
| Texture | 84 |
| Spessore della crosta | 46 |
| Struttura della pasta | 141 |
| Colore della pasta | 60 |

**Nota:** A differenza del 2018, questo formato NON contiene punteggi numerici, solo commenti.

---

### 2.3 Commenti liberi_QTG_2020.xlsx

**7 fogli**, stesso schema del 2019 (7 colonne).

**Eccezione:** Il foglio `Profumo` ha una **8a colonna** aggiuntiva (senza nome) che sembra contenere versioni rielaborate/pulite dei commenti.

| Foglio | Righe |
|---|---|
| Profumo | 234 (8 colonne) |
| Sapore | 211 |
| Aroma | 118 |
| Texture | 114 |
| Spessore della crosta | 74 |
| Struttura della pasta | 337 |
| Colore della pasta | 148 |

---

### 2.4 Commenti liberi_TEST_2021.xlsx

**7 fogli**, stesso schema del 2019 (7 colonne).

| Foglio | Righe |
|---|---|
| Profumo | 58 |
| Sapore | 55 |
| Aroma | 56 |
| Texture | 49 |
| Spessore della Crosta | 51 |
| Struttura della Pasta | 85 |
| Colore della Pasta | 64 |

**Nota:** I commenti del 2021 contengono caratteri non-breaking space (`\xa0`) che potrebbero richiedere pulizia.

---

## 3. File Excel - Codifiche e Risultati Aggregati

### 3.1 codifica caseifici.xlsx (in codifiche/)

**2 fogli:** `codici caseifici` (25 righe), `Foglio2` (16 righe)

Tabella di lookup che mappa i codici caseificio:

| Colonna | Esempio | Descrizione |
|---|---|---|
| Colonna 1 | `TN_302` | Codice caseificio trentino completo |
| Colonna 2 | `C0A` | Codice prodotto abbreviato |
| Colonna 3 | `A` | Lettera identificativa singola |

**Nota:** Il file non ha una riga di intestazione esplicita; la prima riga contiene gia' dati.

---

### 3.2 Risultati_2019-21.xlsx (in codifiche/)

**3 fogli** con le medie dei punteggi della giuria per anno.

#### Foglio `Medie Giuria2019_Q` (180 righe x 16 colonne)

| Colonna | Descrizione |
|---|---|
| `Prod` | Codice prodotto |
| `Forma` | Identificativo forma |
| `Bimestre` | Bimestre di valutazione |
| `Data analisi` | Data dell'analisi |
| `Product` | Codice prodotto alternativo |
| `Spessore della Crosta` | Punteggio medio - spessore crosta |
| `Struttura della Pasta` | Punteggio medio - struttura pasta |
| `Colore della Pasta` | Punteggio medio - colore pasta |
| `Aspetto Esteriore` | Punteggio medio - aspetto esterno |
| `Profumo` | Punteggio medio - profumo |
| `Sapore` | Punteggio medio - sapore |
| `Aroma` | Punteggio medio - aroma |
| `Punteggio Complessivo` | Punteggio complessivo medio |

#### Foglio `Medie Giuria2020_Q` (163 righe x 15 colonne)

Schema simile al 2019, con aggiunta di `N seduta` (numero sessione). L'ordine delle colonne degli attributi e' diverso: Profumo/Sapore/Aroma precedono gli attributi visivi.

#### Foglio `Medie Giuria2021_Q` (167 righe x 21 colonne)

Schema piu' ricco con colonne aggiuntive:

| Colonna | Descrizione |
|---|---|
| `ANNO` | Anno |
| `BIM` | Bimestre |
| `MESE` | Mese |
| `N` | Numero progressivo |
| `CODICE CASEINA` | Codice caseina |
| `SIGLA` | Sigla del caseificio |
| `CODICE FOMA` | Codice forma |
| `CODICE P` | Codice prodotto |
| `GIORNO ANALISI` | Giorno dell'analisi |
| `N SESSIONE` | Numero sessione |
| `Product` | Codice prodotto |
| `Spessore della Crosta` | Punteggio medio |
| `Struttura della Pasta` | Punteggio medio |
| `Colore della Pasta` | Punteggio medio |
| `Aspetto Esteriore` | Punteggio medio |
| `Profumo` | Punteggio medio |
| `Sapore` | Punteggio medio |
| `Aroma` | Punteggio medio |
| **`Texture`** | **Punteggio medio (solo 2021)** |
| `Punteggio Complessivo` | Punteggio complessivo medio |

---

## 4. File CSV (csv dataset/)

I file CSV sono export diretti dei fogli Excel, separati per attributo sensoriale e per anno. Tutti usano la **virgola** come delimitatore.

### Struttura dei CSV

Esistono **4 gruppi** che rispecchiano i file Excel:

| Gruppo | Pattern Nome File | N. File | Schema |
|---|---|---|---|
| 2018 | `Commenti TOT_2018_{Attributo}.csv` | 8 | 5 colonne (Sogg, Seduta, Prod, Attributo, Commenti) |
| 2019 | `Commenti liberi_QTG_2019_{Attributo}.csv` | 7 | 7 colonne (Data Seduta, N Seduta, Bimestre, Data Prod., Panelista, Prodotto, Commenti) |
| 2020 | `Commenti liberi_QTG_2020_{Attributo}.csv` | 7 | 7 colonne (stesso schema 2019) |
| 2021 | `Commenti liberi_TEST_2021_{Attributo}.csv` | 7 | 7 colonne (stesso schema 2019) |

**Attributi coperti in ogni gruppo:** Profumo, Sapore, Aroma, Texture, Spessore della crosta/Crosta, Struttura della pasta/Pasta, Colore della pasta/Pasta.

### CSV aggiuntivi in codifiche/

| File | Righe | Contenuto |
|---|---|---|
| `codifica caseifici_codici caseifici.csv` | 24 | Mapping codici caseificio |
| `Risultati_2019-21_Medie Giuria2019_Q.csv` | 179 | Medie giuria 2019 |
| `Risultati_2019-21_Medie Giuria2020_Q .csv` | 162 | Medie giuria 2020 |
| `Risultati_2019-21_Medie Giuria2021_Q.csv` | 166 | Medie giuria 2021 |

---

## 5. Report di Validazione

### session_validation_report.csv (validation_reports/)

**1.454 righe x 9 colonne** - Log di problemi di qualita' dati rilevati durante la validazione.

| Colonna | Descrizione |
|---|---|
| `csv_file` | File CSV sorgente del problema |
| `line_number` | Riga nel file originale |
| `issue_type` | Tipo di problema (es. `missing_prodotto`) |
| `detail` | Dettaglio del problema |
| `data_seduta` | Data della sessione |
| `seduta_number` | Numero sessione |
| `prodotto` | Codice prodotto |
| `caseificio` | Codice caseificio |
| `session_folder` | Cartella della sessione |

---

## 6. Attributi Sensoriali Valutati

Gli 8 attributi sensoriali valutati dalla giuria (panel) sono:

| Attributo | Categoria | Descrizione |
|---|---|---|
| **Spessore della Crosta** | Visivo | Spessore della crosta esterna |
| **Struttura della Pasta** | Visivo | Struttura interna della pasta del formaggio |
| **Colore della Pasta** | Visivo | Colore della pasta interna |
| **Aspetto Esteriore** | Visivo | Aspetto generale esterno (solo nei risultati aggregati) |
| **Profumo** | Olfattivo | Odore percepito al naso |
| **Sapore** | Gustativo | Gusto percepito in bocca |
| **Aroma** | Gustativo/Olfattivo | Aroma retronasale |
| **Texture** | Tattile | Consistenza e texture (aggiunto dal 2021) |

---

## 7. Note sulla Qualita' dei Dati

1. **Formato decimale inconsistente:** I punteggi del 2018 usano la virgola italiana (es. "7,48") come stringa, mentre altri sono float.
2. **Encoding:** I commenti del 2021 contengono caratteri non-breaking space (`\xa0`) che appaiono come mojibake.
3. **Schema non uniforme:** Lo schema delle colonne varia tra il 2018 (5 colonne con punteggio) e 2019-2021 (7 colonne senza punteggio).
4. **Colonne extra:** Il foglio Profumo del 2020 ha una 8a colonna non documentata.
5. **Capitalizzazione inconsistente:** I nomi degli attributi variano (es. `crosta` vs `Crosta`, `pasta` vs `Pasta`).
6. **File codifica senza header:** `codifica caseifici.xlsx` non ha riga di intestazione; la prima riga e' gia' un dato.
7. **Ordine colonne variabile:** Nei risultati aggregati, l'ordine degli attributi sensoriali cambia tra 2019, 2020 e 2021.
8. **Date in formati diversi:** `date_sedute_2018.csv` usa DD-MM-YYYY, il CSV derivato dall'Excel usa YYYY-MM-DD.
9. **Problemi di validazione:** 1.454 issue rilevate nel validation report, principalmente `missing_prodotto`.

---

## 8. Riepilogo Quantitativo

| Dato | Valore |
|---|---|
| **Immagini BMP totali** | 2.745 |
| **Annate coperte** | 4 (2018-2022) |
| **Sessioni totali (stimate)** | ~114 |
| **Attributi sensoriali** | 8 |
| **File Excel** | 6 |
| **File CSV** | 35 |
| **Righe commenti 2018** | ~1.574 per attributo (con punteggi) |
| **Righe commenti 2019** | 46-141 per attributo |
| **Righe commenti 2020** | 73-337 per attributo |
| **Righe commenti 2021** | 48-85 per attributo |
| **Righe risultati aggregati** | 179 (2019) + 162 (2020) + 166 (2021) = 507 |
