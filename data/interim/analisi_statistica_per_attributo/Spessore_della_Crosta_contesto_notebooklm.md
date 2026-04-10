# Contesto Analisi Sensoriale Grana Trentino — Spessore della Crosta

## Il formaggio
Il TrentinGrana (Grana Trentino) è un formaggio a pasta dura e cotta prodotto in Trentino,
tutelato da disciplinare. Le sessioni di valutazione sensoriale (2018–2021) coinvolgono un
panel di assaggiatori professionisti che valutano ogni campione su 7 attributi sensoriali.
Ogni panelista compila una scheda individuale con punteggio numerico (1–10) e commento
testuale libero, scritto durante la degustazione — quindi spesso telegrafico.

## Questo attributo: Spessore della Crosta
Lo Spessore della Crosta misura lo spessore della crosta esterna in mm o cm, su piatti (facce piane) e scalzi (bordi laterali). Include anche la regolarità (omogeneo vs disomogeneo) e difetti (piatti senza crosta, spigoli molto accentuati). I commenti spesso riportano misure esplicite: '1cm', '10mm', '0,8 piatti 1,4 scalzi'. Un range tipico per TrentinGrana è 7–14mm su piatti, maggiore sugli scalzi.

## Come leggere i CSV caricati

I file CSV che hai come sorgenti contengono i dati originali non modificati.

- **Colonna "Commenti"**: il testo libero scritto dal panelista — **questa è la colonna da analizzare**
- **Colonna "Prodotto" / "Prod"**: codice anonimo del campione (es. "C0A", "TN302")
- **Colonna "Panelista" / "Sogg"**: codice anonimo del valutatore (es. "Q_02", "TG_20")
- **File 2018**: la 4a colonna (`Spessore della Crosta`) è il **punteggio numerico individuale**
  assegnato dallo stesso panelista (formato con virgola: "7,48" = 7.48 su scala 1–10)
- **File Risultati_Medie Giuria***: punteggi medi di giuria per campione (medie su tutti i panelisti)

## Statistiche dei commenti per Spessore della Crosta

| Anno | Totale righe | Commenti validi | % vuoti | Lungh. media (char) |
|------|-------------|-----------------|---------|---------------------|
| 2018 | 1621 | 920 | 43.2% | 22.8 |
| 2019 | 45 | 28 | 37.8% | 28.8 |
| 2020 | 73 | 69 | 5.5% | 26.1 |
| 2021 | 50 | 41 | 18.0% | 32.8 |

**Termini più frequenti (top 20):** "media", "mm", "cm", "piatto", "spessa", "crosta", "colore", "piatti", "spigoli", "sottile", "scalzo", "scalzi", "sottocrosta", "angoli", "evidente", "sfumata", "fine", "sotto", "lato", "unghia"

## Caratteristiche importanti dei commenti

I commenti sono spesso telegrafici perché scritti in tempo reale durante la degustazione:
- Termini singoli: `"burro"`, `"panna"`, `"stalla"`, `"nella norma"`
- Elenchi: `"burro, fruttato, intenso"`
- Giudizi sintetici: `"non tipico"`, `"difetto"`, `"ok"`
- Abbreviazioni: `"legg."` (= leggermente), `"mediam."` (= mediamente)
- Termini dialettali o colloquiali possibili

Non aggiungere interpretazioni non presenti nel testo originale.
Non interpretare l'assenza di commento come dato negativo.

## Nota speciale — Termini quantitativi in Spessore della Crosta

Questo attributo contiene spesso misure numeriche nei commenti (mm, cm).
Da una analisi preliminare su 362 misure del dataset 2018:

| Range mm | Categoria stimata | Score medio associato |
|----------|------------------|----------------------|
| < 7 mm   | molto_sottile    | (vedi tabella stats)  |
| 7–12 mm  | nella_norma      | (vedi tabella stats)  |
| 12–18 mm | spessa           | (vedi tabella stats)  |
| > 18 mm  | molto_spessa     | (vedi tabella stats)  |

Queste sono **stime preliminari** — il tuo obiettivo è confermare o correggere
questi range basandoti su tutti i commenti, non solo quelli con misure esplicite.

## Obiettivo della tua analisi

Costruire un **dizionario di normalizzazione** per l'attributo Spessore della Crosta:
identificare tutti i termini usati dai panelisti e proporre una forma standard,
raggruppando sinonimi, varianti ortografiche, abbreviazioni e dialettalismi
che descrivono lo stesso concetto sensoriale.

## Termini tecnici INVARIABILI — non normalizzarli mai

`scalzo, scalzi, piatti, piatto, sottocrosta, angoli, spigoli, microocchiatura, occhiatura, grana, frattura, stirata, cristalli, tirosina, nostrano, insilato, solubile, solubilità, friabile, friabilità, compatto, compattezza, cedevole`

Questi termini hanno significato tecnico preciso in caseificazione.
Non sostituirli con sinonimi generici.
