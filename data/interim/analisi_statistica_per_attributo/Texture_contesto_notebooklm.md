# Contesto Analisi Sensoriale Grana Trentino — Texture

## Il formaggio
Il TrentinGrana (Grana Trentino) è un formaggio a pasta dura e cotta prodotto in Trentino,
tutelato da disciplinare. Le sessioni di valutazione sensoriale (2018–2021) coinvolgono un
panel di assaggiatori professionisti che valutano ogni campione su 7 attributi sensoriali.
Ogni panelista compila una scheda individuale con punteggio numerico (1–10) e commento
testuale libero, scritto durante la degustazione — quindi spesso telegrafico.

## Questo attributo: Texture
La Texture descrive le caratteristiche meccaniche percepite in bocca e visibili al taglio: solubilità (quanto si scioglie rapidamente), friabilità (tendenza a sbriciolarsi), durezza, presenza e dimensione di cristalli di tirosina, umidità residua. I cristalli di tirosina (bianchi, puntiformi) sono un indicatore positivo di stagionatura. Una texture 'nella norma' per il TrentinGrana è friabile, moderatamente solubile, con cristalli presenti.

## Come leggere i CSV caricati

I file CSV che hai come sorgenti contengono i dati originali non modificati.

- **Colonna "Commenti"**: il testo libero scritto dal panelista — **questa è la colonna da analizzare**
- **Colonna "Prodotto" / "Prod"**: codice anonimo del campione (es. "C0A", "TN302")
- **Colonna "Panelista" / "Sogg"**: codice anonimo del valutatore (es. "Q_02", "TG_20")
- **File 2018**: la 4a colonna (`Texture`) è il **punteggio numerico individuale**
  assegnato dallo stesso panelista (formato con virgola: "7,48" = 7.48 su scala 1–10)
- **File Risultati_Medie Giuria***: punteggi medi di giuria per campione (medie su tutti i panelisti)

## Statistiche dei commenti per Texture

| Anno | Totale righe | Commenti validi | % vuoti | Lungh. media (char) |
|------|-------------|-----------------|---------|---------------------|
| 2018 | 1573 | 1153 | 26.7% | 41.8 |
| 2019 | 83 | 79 | 4.8% | 18.9 |
| 2020 | 113 | 111 | 1.8% | 20.8 |
| 2021 | 48 | 42 | 12.5% | 18.6 |

**Termini più frequenti (top 20):** "cristalli", "solubile", "asciutto", "friabile", "morbido", "pastoso", "grana", "granuloso", "pochi", "bocca", "fine", "granulosa", "compatto", "umido", "microstruttura", "tirosina", "cedevole", "po", "lascia", "poca"

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

Costruire un **dizionario di normalizzazione** per l'attributo Texture:
identificare tutti i termini usati dai panelisti e proporre una forma standard,
raggruppando sinonimi, varianti ortografiche, abbreviazioni e dialettalismi
che descrivono lo stesso concetto sensoriale.

## Termini tecnici INVARIABILI — non normalizzarli mai

`scalzo, scalzi, piatti, piatto, sottocrosta, angoli, spigoli, microocchiatura, occhiatura, grana, frattura, stirata, cristalli, tirosina, nostrano, insilato, solubile, solubilità, friabile, friabilità, compatto, compattezza, cedevole`

Questi termini hanno significato tecnico preciso in caseificazione.
Non sostituirli con sinonimi generici.
