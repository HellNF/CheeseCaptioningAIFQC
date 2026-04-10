# Contesto Analisi Sensoriale Grana Trentino — Sapore

## Il formaggio
Il TrentinGrana (Grana Trentino) è un formaggio a pasta dura e cotta prodotto in Trentino,
tutelato da disciplinare. Le sessioni di valutazione sensoriale (2018–2021) coinvolgono un
panel di assaggiatori professionisti che valutano ogni campione su 7 attributi sensoriali.
Ogni panelista compila una scheda individuale con punteggio numerico (1–10) e commento
testuale libero, scritto durante la degustazione — quindi spesso telegrafico.

## Questo attributo: Sapore
Il Sapore copre le percezioni gustative: dolce, salato, amaro, acido, umami. Include equilibrio (tra i gusti), piccantezza, persistenza retrogustativa. Un Sapore equilibrato ha dolce e salato bilanciati, senza amaro o piccante eccessivi. Difetti tipici: eccessiva piccantezza, amarezza, acidità anomala, sapore piatto/anonimo.

## Come leggere i CSV caricati

I file CSV che hai come sorgenti contengono i dati originali non modificati.

- **Colonna "Commenti"**: il testo libero scritto dal panelista — **questa è la colonna da analizzare**
- **Colonna "Prodotto" / "Prod"**: codice anonimo del campione (es. "C0A", "TN302")
- **Colonna "Panelista" / "Sogg"**: codice anonimo del valutatore (es. "Q_02", "TG_20")
- **File 2018**: la 4a colonna (`Sapore`) è il **punteggio numerico individuale**
  assegnato dallo stesso panelista (formato con virgola: "7,48" = 7.48 su scala 1–10)
- **File Risultati_Medie Giuria***: punteggi medi di giuria per campione (medie su tutti i panelisti)

## Statistiche dei commenti per Sapore

| Anno | Totale righe | Commenti validi | % vuoti | Lungh. media (char) |
|------|-------------|-----------------|---------|---------------------|
| 2018 | 1573 | 1277 | 18.8% | 29.7 |
| 2019 | 71 | 67 | 5.6% | 28.8 |
| 2020 | 210 | 210 | 0.0% | 24.1 |
| 2021 | 54 | 45 | 16.7% | 22.1 |

**Termini più frequenti (top 20):** "piccante", "salato", "amaro", "dolce", "umami", "acido", "equilibrato", "po", "sapido", "troppo", "piccantezza", "sale", "anche", "nota", "medio", "leg", "legg", "finale", "leggero", "sapidit"

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

Costruire un **dizionario di normalizzazione** per l'attributo Sapore:
identificare tutti i termini usati dai panelisti e proporre una forma standard,
raggruppando sinonimi, varianti ortografiche, abbreviazioni e dialettalismi
che descrivono lo stesso concetto sensoriale.

## Termini tecnici INVARIABILI — non normalizzarli mai

`scalzo, scalzi, piatti, piatto, sottocrosta, angoli, spigoli, microocchiatura, occhiatura, grana, frattura, stirata, cristalli, tirosina, nostrano, insilato, solubile, solubilità, friabile, friabilità, compatto, compattezza, cedevole`

Questi termini hanno significato tecnico preciso in caseificazione.
Non sostituirli con sinonimi generici.
