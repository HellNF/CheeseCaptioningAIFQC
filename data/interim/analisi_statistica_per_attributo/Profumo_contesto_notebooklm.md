# Contesto Analisi Sensoriale Grana Trentino — Profumo

## Il formaggio
Il TrentinGrana (Grana Trentino) è un formaggio a pasta dura e cotta prodotto in Trentino,
tutelato da disciplinare. Le sessioni di valutazione sensoriale (2018–2021) coinvolgono un
panel di assaggiatori professionisti che valutano ogni campione su 7 attributi sensoriali.
Ogni panelista compila una scheda individuale con punteggio numerico (1–10) e commento
testuale libero, scritto durante la degustazione — quindi spesso telegrafico.

## Questo attributo: Profumo
Il Profumo è la percezione olfattiva diretta (ortonasale), prima e durante il consumo. Include intensità (debole, moderato, intenso), qualità (caratteristico, atipico) e note specifiche: burro, latte, panna, frutta, vegetale, note di cantina, note anomale. Il profumo caratteristico del TrentinGrana è latteo con note di burro fuso e frutta secca.

## Come leggere i CSV caricati

I file CSV che hai come sorgenti contengono i dati originali non modificati.

- **Colonna "Commenti"**: il testo libero scritto dal panelista — **questa è la colonna da analizzare**
- **Colonna "Prodotto" / "Prod"**: codice anonimo del campione (es. "C0A", "TN302")
- **Colonna "Panelista" / "Sogg"**: codice anonimo del valutatore (es. "Q_02", "TG_20")
- **File 2018**: la 4a colonna (`Profumo`) è il **punteggio numerico individuale**
  assegnato dallo stesso panelista (formato con virgola: "7,48" = 7.48 su scala 1–10)
- **File Risultati_Medie Giuria***: punteggi medi di giuria per campione (medie su tutti i panelisti)

## Statistiche dei commenti per Profumo

| Anno | Totale righe | Commenti validi | % vuoti | Lungh. media (char) |
|------|-------------|-----------------|---------|---------------------|
| 2018 | 1573 | 0 | 100.0% | 0 |
| 2019 | 114 | 112 | 1.8% | 21.3 |
| 2020 | 233 | 233 | 0.0% | 24.4 |
| 2021 | 57 | 50 | 12.3% | 21.0 |

**Termini più frequenti (top 20):** "intensità", "intenso", "all", "apertura", "leggero", "complesso", "odore", "nota", "buona", "solo", "poi", "moderata", "peccato", "bruciata", "bruciato", "vegetale", "cotto", "alla", "burro", "elegante"

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

Costruire un **dizionario di normalizzazione** per l'attributo Profumo:
identificare tutti i termini usati dai panelisti e proporre una forma standard,
raggruppando sinonimi, varianti ortografiche, abbreviazioni e dialettalismi
che descrivono lo stesso concetto sensoriale.

## Termini tecnici INVARIABILI — non normalizzarli mai

`scalzo, scalzi, piatti, piatto, sottocrosta, angoli, spigoli, microocchiatura, occhiatura, grana, frattura, stirata, cristalli, tirosina, nostrano, insilato, solubile, solubilità, friabile, friabilità, compatto, compattezza, cedevole`

Questi termini hanno significato tecnico preciso in caseificazione.
Non sostituirli con sinonimi generici.
