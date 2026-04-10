# Contesto Analisi Sensoriale Grana Trentino — Colore della Pasta

## Il formaggio
Il TrentinGrana (Grana Trentino) è un formaggio a pasta dura e cotta prodotto in Trentino,
tutelato da disciplinare. Le sessioni di valutazione sensoriale (2018–2021) coinvolgono un
panel di assaggiatori professionisti che valutano ogni campione su 7 attributi sensoriali.
Ogni panelista compila una scheda individuale con punteggio numerico (1–10) e commento
testuale libero, scritto durante la degustazione — quindi spesso telegrafico.

## Questo attributo: Colore della Pasta
Il Colore della Pasta descrive la tonalità e l'uniformità della sezione del formaggio. Il range va da bianco latte (stagionatura breve) a giallo paglierino intenso (stagionatura avanzata). Include: presenza di alone centrale più scuro o rosato, disomogeneità, sottocrosta (zona immediatamente sotto la crosta, di solito più chiara). Difetti: colore anomalo (troppo scuro, verdastro, con aloni irregolari).

## Come leggere i CSV caricati

I file CSV che hai come sorgenti contengono i dati originali non modificati.

- **Colonna "Commenti"**: il testo libero scritto dal panelista — **questa è la colonna da analizzare**
- **Colonna "Prodotto" / "Prod"**: codice anonimo del campione (es. "C0A", "TN302")
- **Colonna "Panelista" / "Sogg"**: codice anonimo del valutatore (es. "Q_02", "TG_20")
- **File 2018**: la 4a colonna (`Colore della Pasta`) è il **punteggio numerico individuale**
  assegnato dallo stesso panelista (formato con virgola: "7,48" = 7.48 su scala 1–10)
- **File Risultati_Medie Giuria***: punteggi medi di giuria per campione (medie su tutti i panelisti)

## Statistiche dei commenti per Colore della Pasta

| Anno | Totale righe | Commenti validi | % vuoti | Lungh. media (char) |
|------|-------------|-----------------|---------|---------------------|
| 2018 | 1573 | 1270 | 19.3% | 33.2 |
| 2019 | 59 | 49 | 16.9% | 35.9 |
| 2020 | 147 | 147 | 0.0% | 29.5 |
| 2021 | 63 | 56 | 11.1% | 36.4 |

**Termini più frequenti (top 20):** "carico", "alone", "chiaro", "omogeneo", "giallo", "centrale", "centro", "colore", "rosa", "paglierino", "piatto", "scuro", "verso", "chiara", "uniforme", "tendente", "rosato", "macchia", "sotto", "leggero"

## Caratteristiche importanti dei commenti

I commenti sono spesso telegrafici perché scritti in tempo reale durante la degustazione:
- Termini singoli: `"burro"`, `"panna"`, `"stalla"`, `"nella norma"`
- Elenchi: `"burro, fruttato, intenso"`
- Giudizi sintetici: `"non tipico"`, `"difetto"`, `"ok"`
- Abbreviazioni: `"legg."` (= leggermente), `"mediam."` (= mediamente)
- Termini dialettali o colloquiali possibili

Non aggiungere interpretazioni non presenti nel testo originale.
Non interpretare l'assenza di commento come dato negativo.

## Obiettivo della tua analisi

Costruire un **dizionario di normalizzazione** per l'attributo Colore della Pasta:
identificare tutti i termini usati dai panelisti e proporre una forma standard,
raggruppando sinonimi, varianti ortografiche, abbreviazioni e dialettalismi
che descrivono lo stesso concetto sensoriale.

## Termini tecnici INVARIABILI — non normalizzarli mai

`scalzo, scalzi, piatti, piatto, sottocrosta, angoli, spigoli, microocchiatura, occhiatura, grana, frattura, stirata, cristalli, tirosina, nostrano, insilato, solubile, solubilità, friabile, friabilità, compatto, compattezza, cedevole`

Questi termini hanno significato tecnico preciso in caseificazione.
Non sostituirli con sinonimi generici.
