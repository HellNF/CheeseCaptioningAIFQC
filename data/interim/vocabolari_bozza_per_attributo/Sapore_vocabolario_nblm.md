# Vocabolario Bozza — Sapore

**Generato:** 2026-04-09 20:44
**Notebook NotebookLM:** `d911d865-fed6-40e0-8a4d-7efc631991c1`
**Stato:** BOZZA — richiede revisione umana prima di procedere con script 09

---

## Orientamento iniziale NotebookLM

Ecco le informazioni confermate in base al documento di contesto e ai file forniti per il progetto di analisi sensoriale del Grana Trentino:

*   **Numero di fonti CSV:** Delle 8 fonti caricate, **7 sono file CSV** contenenti i dati grezzi e le medie di giuria, mentre l'ottava è un file Markdown testuale contenente il contesto dell'analisi [1-176]. 
*   **Range temporale dei dati:** Le sessioni di valutazione sensoriale presenti nei dati coprono il periodo che va dal **2018 al 2021** [172].
*   **Colonna da analizzare:** La colonna che contiene il testo libero scritto dai panelisti durante le degustazioni è la colonna **"Commenti"** [173].

---

## Query 1 — Inventario termini

| Termine / Espressione | Occorrenze (stima) | Anni in cui compare | Esempio di frase completa |
| :--- | :--- | :--- | :--- |
| **Piccante / Piccantezza / Piccantino / Pizzica** | Alta (>350) | 2018, 2019, 2020, 2021 | "sapidità elevata con umami marcato, buona piccantezza comunque equilibrato" [1] |
| **Salato / Sapido / Sale / Sapidità / Sciapo / Insipido** | Alta (>350) | 2018, 2019, 2020, 2021 | "salato&umami prevalenti anche se non disequilibrato" [1] |
| **Amaro / Amarognolo / Amarezza** | Alta (>200) | 2018, 2019, 2020, 2021 | "amaro salato e dolciastro" [2] |
| **Dolce / Dolcezza / Dolciastro** | Alta (>200) | 2018, 2019, 2020, 2021 | "dolcezza marcata, sapido e umami ok" [1] |
| **Equilibrato / Equilibrio / Armonico / Disarmonico / Sbilanciato** | Alta (>150) | 2018, 2019, 2020, 2021 | "equilibrato con note anche dolci sebbene leggero piccante" [1] |
| **Umami / Glutammato** | Alta (>120) | 2018, 2019, 2020, 2021 | "tanto umami" [3] |
| **Acido / Acidità / Acidulo / Acre** | Alta (>100) | 2018, 2019, 2020, 2021 | "nel complesso leggermente acido e amaro" [1] |
| **Piatto / Neutro / Blando / Anonimo** | Media (~30) | 2018, 2019, 2020, 2021 | "abbastanza neutro, piatto" [4] |
| **Bruciante / Brucia / Irrita** | Media (~30) | 2018, 2019, 2020, 2021 | "piccante, quasi bruciante" [3] |
| **Pungente / Pungenza** | Media (~25) | 2018, 2019, 2020, 2021 | "Sembra un formaggio piu' vecchio. Scarno e pungente." [3] |
| **Scarno / Povero / Manca pienezza / Incompleto** | Media (~20) | 2018, 2019, 2020 | "manca rotondita' e pienezza, poco umami" [5] |
| **Persistente / Persistenza / Evanescente** | Media (~20) | 2018, 2019, 2020, 2021 | "piccante leggero ma persistente" [6] |
| **Pieno / Rotondo / Complesso** | Media (~15) | 2018, 2019, 2020 | "Pieno, non dolce. piccante." [4] |
| **Astringente / Allappante / Asciuga** | Media (~15) | 2018, 2019, 2020, 2021 | "quasi astringente, asciug atroppo in bocca" [7] |
| **Grasso / Unto / Burroso** | Bassa (~10) | 2018, 2020 | "unto, troppo sapido..." [8] |
| **Vecchio / Maturo / Passato / Sovramaturazione** | Bassa (~10) | 2018 | "formaggio maturo tendente alla sovramaturazione" [9] |
| **Cotto / Formaggio cotto / Latte cotto** | Bassa (~8) | 2018 | "buon bilanciamento, sentore di formaggio cotto" [10] |
| **Crosta / Sapore di crosta** | Bassa (~5) | 2018, 2020 | "crosta di formaggio" [11] |
| **Tostato / Bruciato / Pane tostato** | Bassa (~5) | 2018 | "finale leggermente amaro&tostato" [12] |
| **Nostrano / Non da grana / Atipico** | Bassa (~5) | 2018, 2020, 2021 | "Il sapore anomalo. Atipico del grana" [13] |
| **Acerbo / Giovane** | Bassa (~3) | 2020, 2021 | "Non ancora pronto, acerbo" [14] |
| **Latte fresco / Panna / Burro** | Bassa (~3) | 2018 | "latte e burro" [10] |
| **Brodo** | Bassa (~3) | 2018 | "brodo" [9] |
| **Rinfrescante** | Bassa (~3) | 2018 | "lieve tendenza rinfrescante" [15] |
| **Sgraziato / Slegato** | Bassa (~3) | 2018, 2020 | "Sgraziato. Troppo amaro" [16] |
| **Umano (Refuso per Umami)** | Bassa (~3) | 2020 | "Tanto umano, troppo" [16] |
| **Metallico** | Unica (1) | 2018 | "bella sapidit', umami ok, piccantezza media, forse leggera acidit', metallico" [4] |
| **Gorgonzola (Quasi da gorgonzola)** | Unica (1) | 2018 | "molto piccante, quasi da gorgonzola" [7] |
| **Stalla** | Unica (1) | 2018 | "piccante e credo sappia di stalla" [17] |
| **Tossico** | Unica (1) | 2018 | "amaro tossico e piccante" [18] |
| **Miami (Refuso per Umami)** | Unica (1) | 2019 | "Poco Miami," [19] |
| **Bresso (Dolce come i Bresso)** | Unica (1) | 2020 | "Amaro il retrogusto e dolce come i Bresso!" [20] |
| **Sapone** | Unica (1) | 2020 | "Sapone" [21] |
| **Polvere** | Unica (1) | 2021 | "Polvere" [22] |
| **Mentolato** | Unica (1) | 2021 | "Mentolato!" [22] |

---

## Query 2 — Cluster semantici

Basandomi sui termini identificati nei commenti dei panelisti [1-172] e applicando la regola per i termini tecnici invariabili indicata nel contesto del progetto [173], ecco il raggruppamento in cluster semantici per l'attributo "Sapore".

**Cluster: Piccantezza**
- Varianti trovate nei dati: piccante, piccantezza, piccantino, pizzica
- Forma canonica proposta: Piccante
- Motivazione della scelta: È il termine tecnico primario e formale per descrivere l'irritazione trigeminale moderata tipica dei formaggi stagionati [1, 4, 11].
- Frequenza stimata del cluster: >350

**Cluster: Sapidità**
- Varianti trovate nei dati: salato, sapido, sale, sapidità, salatino
- Forma canonica proposta: Salato
- Motivazione della scelta: "Salato" identifica in modo diretto e inequivocabile il gusto base corrispondente. "Sapido" è usato come sinonimo, ma "salato" è il descrittore primario standard nell'analisi sensoriale [1-3].
- Frequenza stimata del cluster: >350

**Cluster: Amarezza**
- Varianti trovate nei dati: amaro, amarognolo, amarezza
- Forma canonica proposta: Amaro
- Motivazione della scelta: È il termine che identifica il gusto base. "Amarognolo" ne indica solo una minore intensità, riducibile a "amaro" per la standardizzazione [1, 2, 4].
- Frequenza stimata del cluster: >200

**Cluster: Dolcezza**
- Varianti trovate nei dati: dolce, dolcezza, dolciastro
- Forma canonica proposta: Dolce
- Motivazione della scelta: Identifica il gusto base positivo, molto ricercato nel Grana Trentino per bilanciare la sapidità [1, 2, 5].
- Frequenza stimata del cluster: >200

**Cluster: Acidità**
- Varianti trovate nei dati: acido, acidità, acidulo, acre, acidino
- Forma canonica proposta: Acido
- Motivazione della scelta: Rappresenta il gusto base legato all'acido lattico. Le varianti sono diminutivi o sinonimi che indicano la stessa percezione [1, 4, 11].
- Frequenza stimata del cluster: >100

**Cluster: Umami**
- Varianti trovate nei dati: umami, glutammato, umano, miami
- Forma canonica proposta: Umami
- Motivazione della scelta: "Umami" è il termine scientifico per indicare il quinto gusto (tipico del parmigiano/grana). "Glutammato" ne è l'origine chimica, mentre "umano" e "miami" sono evidenti errori del correttore automatico dei dispositivi usati dai panelisti [1-3, 71].
- Frequenza stimata del cluster: ~125

**Cluster: Equilibrio e Armonia**
- Varianti trovate nei dati: equilibrato, equilibrio, armonico, bilanciato
- Forma canonica proposta: Equilibrato
- Motivazione della scelta: Indica la corretta proporzione tra i gusti base (specialmente dolce e salato) senza picchi sgradevoli [1, 2, 4].
- Frequenza stimata del cluster: ~130

**Cluster: Squilibrio Gustativo**
- Varianti trovate nei dati: disarmonico, sbilanciato, squilibrato, slegato, sgraziato
- Forma canonica proposta: Squilibrato
- Motivazione della scelta: Sintetizza efficacemente la mancanza di armonia tra i gusti o la prevaricazione di una singola nota (es. troppo sale o troppo acido) [1, 8, 17].
- Frequenza stimata del cluster: ~25

**Cluster: Pungenza e Bruciore**
- Varianti trovate nei dati: bruciante, brucia, irrita, pungente, pungenza, raschia in gola
- Forma canonica proposta: Pungente
- Motivazione della scelta: Differisce dal semplice "piccante"; indica un'irritazione trigeminale fastidiosa, tattile ed eccessiva sulle mucose o in gola [2, 5, 27].
- Frequenza stimata del cluster: ~55

**Cluster: Carenza di Sapidità**
- Varianti trovate nei dati: sciapo, insipido, carente di sale, manca sale, poco salato
- Forma canonica proposta: Sciapo
- Motivazione della scelta: Raggruppa i concetti di anomala mancanza di sale, difetto che altera l'espressione del prodotto [1, 13, 74].
- Frequenza stimata del cluster: ~15

**Cluster: Assenza di Carattere**
- Varianti trovate nei dati: neutro, blando, anonimo, insapore, scarno, povero, manca pienezza, incompleto
- Forma canonica proposta: Neutro
- Motivazione della scelta: Riunisce le valutazioni di formaggi privi di spiccate caratteristiche gustative e carenti di complessità [2, 9, 21].
- Frequenza stimata del cluster: ~50

**Cluster: Pienezza**
- Varianti trovate nei dati: pieno, rotondo, complesso, completo
- Forma canonica proposta: Pieno
- Motivazione della scelta: Contrario di neutro/scarno, indica una ricca ampiezza dei descrittori gustativi e una buona percezione al palato [4, 9, 15].
- Frequenza stimata del cluster: ~15

**Cluster: Astringenza**
- Varianti trovate nei dati: astringente, allappante, asciuga
- Forma canonica proposta: Astringente
- Motivazione della scelta: È il termine tecnico corretto per la sensazione tattile di secchezza nel cavo orale (precipitazione delle proteine salivari) [3, 7, 19].
- Frequenza stimata del cluster: ~15

**Cluster: Persistenza**
- Varianti trovate nei dati: persistente, persistenza, evanescente (in negativo)
- Forma canonica proposta: Persistente
- Motivazione della scelta: Rappresenta il tempo in cui il sapore permane in bocca dopo la deglutizione [4, 6, 17].
- Frequenza stimata del cluster: ~20

**Cluster: Note Lattiche e Grasse**
- Varianti trovate nei dati: grasso, unto, burroso, latte fresco, panna, burro
- Forma canonica proposta: Lattico
- Motivazione della scelta: Riunisce i descrittori olfatto-gustativi riconducibili ai derivati primari del latte e ai grassi [1, 5, 21].
- Frequenza stimata del cluster: ~13

**Cluster: Note di Cotto e Tostato**
- Varianti trovate nei dati: cotto, formaggio cotto, latte cotto, crosta, sapore di crosta, tostato, bruciato, pane tostato
- Forma canonica proposta: Tostato/Cotto
- Motivazione della scelta: Raggruppa sentori retronasali specifici dovuti ai processi termici e alla stagionatura della parte esterna del formaggio [11, 16, 28].
- Frequenza stimata del cluster: ~18

**Cluster: Sovramaturazione**
- Varianti trovate nei dati: vecchio, maturo, passato, sovramaturazione
- Forma canonica proposta: Sovramaturo
- Motivazione della scelta: Identifica in modo tecnico il difetto di un formaggio andato oltre la sua finestra ideale di maturazione [5, 18, 31].
- Frequenza stimata del cluster: ~10

**Cluster: Off-Flavor (Difetti atipici)**
- Varianti trovate nei dati: brodo, metallico, gorgonzola, stalla, tossico, bresso, sapone, polvere, mentolato
- Forma canonica proposta: Off-flavor
- Motivazione della scelta: Raduna tutti i sentori anomali, rari e chiaramente estranei al profilo del Grana Trentino, molti dei quali appaiono una sola volta [18, 25, 79, 89].
- Frequenza stimata del cluster: ~11

---
### Termini Tecnici INVARIABILI

Come da regola [173], i seguenti termini trovati nei dati non vengono ricondotti a sinonimi ma mantenuti nella loro forma esatta.

**Cluster: piatto**
- Varianti trovate nei dati: piatto, piatti
- Forma canonica proposta: piatto
- Motivazione della scelta: *Termine INVARIABILE*. Sebbene nei commenti sul sapore sia usato per indicare un sapore "anonimo", il vocabolario del progetto vieta di normalizzarlo [9, 49, 76, 89].
- Frequenza stimata del cluster: ~10

**Cluster: nostrano**
- Varianti trovate nei dati: nostrano
- Forma canonica proposta: nostrano
- Motivazione della scelta: *Termine INVARIABILE*. Viene usato dai panelisti per indicare un sapore atipico, rustico o casereccio che si discosta dallo standard [30, 49, 78, 86]. 
- Frequenza stimata del cluster: ~6

**Cluster: grana**
- Varianti trovate nei dati: grana (es. "non da grana", "atipico del grana")
- Forma canonica proposta: grana
- Motivazione della scelta: *Termine INVARIABILE*. Utilizzato per definire l'identità o la mancanza di tipicità rispetto alla denominazione del formaggio [45, 58, 82, 89].
- Frequenza stimata del cluster: ~6

---

## Query 3 — Anomalie e termini quantitativi

| Termine trovato | Tipo (1–5) | Proposta di normalizzazione | Confidenza (alta/media/bassa) | Note |
| :--- | :--- | :--- | :--- | :--- |
| **"leg" / "legg" / "legg."** | 1 | leggermente | Alta | Abbreviazione diffusissima usata per mitigare l'intensità di un descrittore, ad esempio "leg acido" o "legg salato" [1-3]. |
| **"abb" / "abb."** | 1 | abbastanza | Alta | Trovato in contesti come "abb equilib", contrazione per indicare un'intensità moderata [4]. |
| **"pic" / "picc"** | 1 | piccante | Alta | Termine troncato usato spesso in appunti veloci come "leg amaro e pic" [5]. |
| **"equilib"** | 1 | equilibrato | Alta | Abbreviazione comune per indicare il bilanciamento dei gusti, ad esempio "non equilib" [3]. |
| **"ghe ne'"** | 2 | presente / percepibile | Alta | Espressione dialettale veneto-trentina per indicare la presenza di un sapore, trovata in "umami ghe ne'" [6]. |
| **"sciapotto"** | 2 | sciapo / poco salato | Alta | Alterazione colloquiale per descrivere un formaggio carente di sale [7]. |
| **"da passeggio"** | 2 | formaggio giovane / non da grana | Media | Colloquialismo ("Buono da passeggio") per indicare un sapore fresco e privo della complessità tipica della stagionatura [8]. |
| **"sale, sale, sale" / "troppppppo" / "ammmmmaro"** | 2 | molto salato / molto amaro | Alta | Ripetizioni enfatiche o allungamenti vocalici usati in modo informale per indicare un'intensità eccessiva e sgradevole [9-11]. |
| **"umano" / "umani"** | 3 | umami | Alta | Classico errore del correttore automatico di smartphone/tablet (es. "tanto umano, troppo" o "poco umani") [12-14]. |
| **"miami"** | 3 | umami | Alta | Altro refuso sistematico causato dalla correzione automatica ("Poco Miami", "Leggermente Miami!!") [15, 16]. |
| **"ecquilibrato" / "escuilibrato" / "ecuilibrato"** | 3 | equilibrato | Alta | Errori ortografici molto frequenti nell'inserimento del testo [17-19]. |
| **"sapidit'" / "acidit'" / "acididt'"** | 3 | sapidità / acidità | Alta | Uso dell'apice al posto dell'accento o errori di digitazione [2, 20]. |
| **"pi fante"** | 3 | piccante | Alta | Evidente errore di battitura o di inserimento vocale ("Troppo pi fante") [21]. |
| **"2 porzioni"** | 4 | disomogeneo | Media | Trovato nell'espressione "2 porzioni leggermente amare" nel file 2018; corrisponde a un punteggio di 7 e indica una disomogeneità interna al campione [22]. |
| **Campione C0D (Seduta 2, 2018)** | 5 | [Nessuna - mantenere il dato] | Alta | Contraddizione netta: il panelista Q_02 lo definisce "acido piccante persistente" assegnando 5,98, mentre il panelista TG_35 lo definisce "Equilibrato, spicca una nota dolce finale" assegnando 9,04 [23]. |
| **Campione C0I (Seduta 1, 2018)** | 5 | [Nessuna - mantenere il dato] | Alta | Contraddizione evidente: TG_20 nota una "dolcezza marcata" (punteggio 5,98), mentre TG_24 lo trova "salato troppo prevalente" (6,28) e TG_13 lo definisce "quasi bruciante sulla lingua" (6,76) [2, 24]. |
| **Campione C0Q (Seduta 14, 2018)** | 5 | [Nessuna - mantenere il dato] | Alta | Divergenze di percezione: Q_02 lo sente "TENDENTE ALL'AMARO ACIDO" (5,74), TG_04 nota "salato, dolce assente" (6,94), mentre TG_20 lo ritiene "abbastanza equilibrato" (7,54) [25, 26]. |

---

## Query 4 — Dubbi per revisione umana

Ecco i casi individuati nei dati dell'attributo "Sapore" che presentano ambiguità semantica, di contesto o probabili errori di battitura complessi. Per questi termini, la normalizzazione automatica rischia di alterare il significato originale, ed è quindi richiesta una decisione umana.

---
**DUBBIO 1:** "brodo"
- **Perché è ambiguo:** Nel mondo caseario, il sentore di "brodo" può indicare sia una forte e positiva nota di Umami (brodo di carne/glutammato), sia un difetto fermentativo ben preciso ("sapore di carne bollita/brodo").
- **Opzione A:** Normalizzare nel cluster "Umami".
- **Opzione B:** Normalizzare nel cluster "Off-flavor (Difetto: brodo/carne bollita)".
- **Suggerimento NotebookLM:** Preferirei l'**Opzione B**. I panelisti di questo progetto usano spessissimo il termine tecnico "umami" (>100 occorrenze) [1]. Se il panelista TG_11 ha usato specificamente la parola "brodo", è probabile che volesse indicare un sentore anomalo. I punteggi associati bassi (es. 5,02 e 6,52) supportano l'ipotesi di un difetto [2, 3].
- **Dati a supporto:** Il panelista TG_11 annota "brodo" in due sessioni diverse [2, 3], assegnando punteggi medio-bassi (6,52 e 5,02).

---
**DUBBIO 2:** "dolce come i Bresso!"
- **Perché è ambiguo:** Il panelista fa un paragone con un marchio specifico ("Bresso" o "Bressot"), che è un formaggio fresco, spalmabile e molto delicato/dolce. Non è chiaro se voglia solo indicare "molto dolce" o se stia segnalando una grave anomalia di maturazione.
- **Opzione A:** Normalizzare semplicemente come "Dolce / Molto dolce".
- **Opzione B:** Normalizzare come "Atipico / Formaggio fresco / Lattico", indicando un profilo inadeguato per un Grana stagionato.
- **Suggerimento NotebookLM:** Preferirei l'**Opzione B**. Paragonare un Grana Trentino a un formaggio fresco spalmabile suggerisce una mancanza di complessità e una dolcezza lattica che devia dallo standard [4].
- **Dati a supporto:** "Amaro il retrogusto e dolce come i Bresso!" scritto da TG_24 [4].

---
**DUBBIO 3:** "Leggero umani respiro..."
- **Perché è ambiguo:** "Umani" è chiaramente un errore del correttore automatico per "Umami". Tuttavia, la parola "respiro" è criptica. Può essere un altro refuso, oppure un riferimento tecnico alla percezione per via retronasale (quando si espira).
- **Opzione A:** Normalizzare a "Umami leggero per via retronasale".
- **Opzione B:** Normalizzare semplicemente a "Leggero umami" (considerando "respiro" come refuso, ad esempio per "residuo").
- **Suggerimento NotebookLM:** Preferirei l'**Opzione B**. Vista l'alta frequenza di errori del correttore automatico su questi dispositivi ("umani", "miami") [5, 6], è molto probabile che "respiro" sia un'anomalia di digitazione piuttosto che un descrittore tecnico complesso.
- **Dati a supporto:** Commento di TG_24: "Leggero umani respiro..." [7].

---
**DUBBIO 4:** "Polvere"
- **Perché è ambiguo:** Può indicare un vero e proprio "Off-flavor" (sapore di polvere/terra, dovuto a muffe) oppure una sensazione tattile in bocca (struttura farinosa/polverosa che asciuga il palato).
- **Opzione A:** Normalizzare come difetto aromatico "Off-flavor (Sapore di polvere/terra)".
- **Opzione B:** Normalizzare nel cluster tattile "Astringente / Allappante".
- **Suggerimento NotebookLM:** Preferirei l'**Opzione B**. Lo stesso panelista (TG_19) usa altrove il termine "Allappante" [6, 8, 9], dimostrando una sensibilità per la secchezza del cavo orale. "Polvere" potrebbe essere un sinonimo per quella sensazione tattile percepita durante l'assaggio.
- **Dati a supporto:** Singola parola "Polvere" inserita da TG_19 in una sessione del 2021 [9].

---
**DUBBIO 5:** "ddpiccante" / "ddleggermente piccante" / "dddddddd"
- **Perché è ambiguo:** Il prefisso "dd" o la stringa di "d" non hanno significato in italiano. Non è chiaro se sia un tentativo di scrivere un rafforzativo o un errore hardware.
- **Opzione A:** Normalizzare come rafforzativo (es. "ddpiccante" -> "Molto piccante").
- **Opzione B:** Considerarlo un errore di battitura (tasto incantato) e ignorare le "d" (es. "ddpiccante" -> "Piccante").
- **Suggerimento NotebookLM:** Preferirei l'**Opzione B**. La presenza della stringa "dddddddd" indica quasi certamente un problema tecnico con la tastiera del dispositivo usato dal panelista in quella seduta.
- **Dati a supporto:** Tutte le occorrenze anomale si concentrano sul panelista TG_05, nella seduta 25 [10, 11].

---
**DUBBIO 6:** "unto" / "grasso"
- **Perché è ambiguo:** Sebbene siano inseriti nella colonna "Sapore", "unto" e "grasso" sono termini che in analisi sensoriale descrivono la Struttura e la Consistenza (sensazioni tattili palatali), non i gusti base.
- **Opzione A:** Mantenerli nel dizionario del Sapore e normalizzarli nel cluster "Lattico / Burro".
- **Opzione B:** Rimuoverli dal dizionario del Sapore e trasferire questi specifici descrittori all'analisi dell'attributo "Struttura/Texture".
- **Suggerimento NotebookLM:** Preferirei l'**Opzione B**. C'è un'evidente sovrapposizione: i panelisti a volte scrivono tutto nel campo "Sapore". Per il rigore del progetto, le sensazioni di scivolosità/grassezza vanno separate dal gusto [8, 12, 13].
- **Dati a supporto:** Es. TG_24: "sapido, amaro, unto" [12]. TG_19: "Grasso" [13]. 

---
**DUBBIO 7:** "Mentolato!"
- **Perché è ambiguo:** Termine estremamente anomalo per il Grana Trentino. Potrebbe essere un reale difetto aromatico derivante da flora pabulare (erbe specifiche del pascolo), oppure un errore del correttore per una parola simile (es. "Mescolato"?).
- **Opzione A:** Normalizzare come difetto raro "Off-flavor (Mentolato / Balsamico)".
- **Opzione B:** Etichettare come dato dubbio/inutilizzabile per sospetto refuso.
- **Suggerimento NotebookLM:** Preferirei l'**Opzione A**. La presenza del punto esclamativo suggerisce che il panelista è rimasto genuinamente colpito e sorpreso da questa specifica e insolita percezione [9].
- **Dati a supporto:** "Mentolato!" scritto da TG_19 nel 2021 [9].

---
**DUBBIO 8:** "sa di vecchio" / "crosta di formaggio"
- **Perché è ambiguo:** "Sapore di crosta" o "cotto" possono talvolta essere tollerati come note positive di stagionatura. Tuttavia, "sa di vecchio" ha una connotazione marcatamente peggiorativa. Non è chiaro se vadano riuniti sotto un unico concetto.
- **Opzione A:** Normalizzare come descrittore positivo "Complesso / Tostato / Cotto".
- **Opzione B:** Normalizzare nel cluster dei difetti "Sovramaturo / Ossidato".
- **Suggerimento NotebookLM:** Preferirei l'**Opzione B**. Quando appaiono espressioni come "sa di vecchio" o "crosta", i punteggi del Sapore associati sono tendenzialmente penalizzati rispetto alla media [2, 14, 15]. Questo indica che i panelisti percepiscono una nota stantia e non una piacevole evoluzione della maturazione.
- **Dati a supporto:** "sa di @vecchio@" annotato da TG_11 (punteggio 6.52) [14]; "crosta, sa di vecchio" annotato da TG_11 (punteggio 5.86) [16].

---

## Istruzioni per la revisione umana

1. Leggi ogni sezione e valida / correggi le proposte di normalizzazione
2. Risolvi ogni dubbio in Query 4 scegliendo Opzione A, B o altra
3. Per Spessore della Crosta: confronta soglie script vs analisi NBLM e scegli i range definitivi
4. Salva le decisioni finali in: `data/interim/vocabolari_validati_per_attributo/Sapore_vocabolario.json`
5. Usa come template: `docs/template_vocabolario_validato.json` (generato da questo script)
