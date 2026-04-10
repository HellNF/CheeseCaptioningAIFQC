# Contesto Analisi Sensoriale Grana Trentino — Struttura della Pasta

## Il formaggio
Il TrentinGrana (Grana Trentino) è un formaggio a pasta dura e cotta prodotto in Trentino,
tutelato da disciplinare. Le sessioni di valutazione sensoriale (2018–2021) coinvolgono un
panel di assaggiatori professionisti che valutano ogni campione su 7 attributi sensoriali.
Ogni panelista compila una scheda individuale con punteggio numerico (1–10) e commento
testuale libero, scritto durante la degustazione — quindi spesso telegrafico.

## Questo attributo: Struttura della Pasta
La Struttura della Pasta descrive le caratteristiche visive e strutturali della sezione del formaggio. Include: grana (finezza/grossolanità), tipo di frattura (netta, irregolare, stirata), microocchiatura (piccoli fori diffusi), occhiatura (fori più grandi), disomogeneità (zone con caratteristiche diverse), colore interno. Una struttura 'nella norma' ha grana fine uniforme, frattura tipica, microocchiatura diffusa regolare.

## Come leggere i CSV caricati

I file CSV che hai come sorgenti contengono i dati originali non modificati.

- **Colonna "Commenti"**: il testo libero scritto dal panelista — **questa è la colonna da analizzare**
- **Colonna "Prodotto" / "Prod"**: codice anonimo del campione (es. "C0A", "TN302")
- **Colonna "Panelista" / "Sogg"**: codice anonimo del valutatore (es. "Q_02", "TG_20")
- **File 2018**: la 4a colonna (`Struttura della Pasta`) è il **punteggio numerico individuale**
  assegnato dallo stesso panelista (formato con virgola: "7,48" = 7.48 su scala 1–10)
- **File Risultati_Medie Giuria***: punteggi medi di giuria per campione (medie su tutti i panelisti)

## Statistiche dei commenti per Struttura della Pasta

| Anno | Totale righe | Commenti validi | % vuoti | Lungh. media (char) |
|------|-------------|-----------------|---------|---------------------|
| 2018 | 1573 | 1366 | 13.2% | 51.1 |
| 2019 | 140 | 133 | 5.0% | 35.3 |
| 2020 | 336 | 336 | 0.0% | 36.0 |
| 2021 | 84 | 81 | 3.6% | 37.1 |

**Termini più frequenti (top 20):** "frattura", "grana", "stirata", "regolare", "centrale", "struttura", "microocchiatura", "omogenea", "fine", "occhiatura", "grossolana", "bella", "centro", "granulosa", "irregolare", "diffusa", "presenza", "qualche", "pasta", "occhio"

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

Costruire un **dizionario di normalizzazione** per l'attributo Struttura della Pasta:
identificare tutti i termini usati dai panelisti e proporre una forma standard,
raggruppando sinonimi, varianti ortografiche, abbreviazioni e dialettalismi
che descrivono lo stesso concetto sensoriale.

## Termini tecnici INVARIABILI — non normalizzarli mai

`scalzo, scalzi, piatti, piatto, sottocrosta, angoli, spigoli, microocchiatura, occhiatura, grana, frattura, stirata, cristalli, tirosina, nostrano, insilato, solubile, solubilità, friabile, friabilità, compatto, compattezza, cedevole`

Questi termini hanno significato tecnico preciso in caseificazione.
Non sostituirli con sinonimi generici.
