# Vocabolario Bozza — Texture

**Generato:** 2026-04-09 20:53
**Notebook NotebookLM:** `266cde9d-883b-4eba-833f-853158140f7a`
**Stato:** BOZZA — richiede revisione umana prima di procedere con script 09

---

## Orientamento iniziale NotebookLM

Ho compreso il progetto di analisi sensoriale dell'attributo "Texture" per il Grana Trentino descritto nel documento di contesto [1, 2]. Ecco le risposte alle tue domande:

*   **Numero di fonti CSV:** Delle 8 fonti totali caricate, **7 sono file CSV** contenenti i dati originali e i risultati, mentre una è il documento di contesto in formato Markdown.
*   **Range temporale dei dati:** Le sessioni di valutazione sensoriale presenti nei dati coprono il periodo che va dal **2018 al 2021** [1, 3].
*   **Colonna da analizzare:** I testi liberi con le valutazioni dei panelisti si trovano nella colonna denominata **"Commenti"** [4].

---

## Query 1 — Inventario termini

Ecco la tabella completa con tutti i termini e le espressioni distinte utilizzate dai panelisti per descrivere l'attributo "Texture", estratti dai commenti liberi presenti nei CSV. 

Ho raggruppato le variazioni ortografiche o grammaticali dello stesso concetto (es. *asciutto/secco*), ma ho isolato meticolosamente tutte le espressioni insolite, gergali o rare, in quanto fondamentali per creare il tuo dizionario di normalizzazione.

| Termine / Espressione | Occorrenze (stima) | Anni in cui compare | Esempio di frase completa |
| :--- | :--- | :--- | :--- |
| **Cristalli / Microcristalli (di tirosina)** (molti, pochi, grossi, assenti) | > 300 | 2018-2022 | "asciutto cristalli sol" [1], "cristalli anche troppi" [2] |
| **Solubile / Solubilità** (si scioglie, solub., sol.) | > 250 | 2018-2022 | "granulosa, giustamente umida, solubile" [1] |
| **Asciutto / Secco** (leggermente asciutto, molto asciutto) | > 200 | 2018-2022 | "Molto asciutto. Quasi secco" [3], "friabile ma asciutto" [4] |
| **Friabile / Friabilità / Frantuma / Sbriciola** | > 150 | 2018-2022 | "friabile, un pochetto asciutto" [5], "si sbriciola in bocca" [6] |
| **Morbido / Molle / Tenero** | > 150 | 2018-2022 | "morbido. umido. poco friabile." [7], "Difetto é che troppo tenero" [8] |
| **Pastoso / Pastosità** | > 120 | 2018-2022 | "troppo pastoso, asciutto e farinoso" [5] |
| **Grana / Granuloso / Granulosità** (fine, grossolana) | > 100 | 2018-2022 | "bella presenza di granuli" [1], "Senza grana" [9] |
| **Umido / Umidità** | ~ 80 | 2018-2022 | "piuttosto umida, poco granulosa ma solubile" [10] |
| **Compatto / Compattezza** | ~ 80 | 2018-2022 | "molto compatto, non friabile, no cristalli" [11] |
| **Microstruttura / Struttura** (fine, inesistente, grossolana) | ~ 60 | 2018-2022 | "microstruttura grossolana.. elastico" [10] |
| **Cedevole / Cedevolezza** | ~ 40 | 2018-2020 | "cedevole, poco granulosa, quasi sabbiosa" [5] |
| **Sabbioso / Sabbiosità / Sabbietta** | ~ 30 | 2018-2021 | "un po di sabbiosita finale" [1], "lascia sabbietta finale" [12] |
| **Impasta / Incolla la bocca** | ~ 30 | 2018-2022 | "impasta la bocca. morbido, e fondente" [13], "Impasta" [14] |
| **Farinoso / Sensazione di farina / Polveroso** | ~ 20 | 2018-2020 | "poca durezza, ma discreta pastosita e farinosita" [1] |
| **Adesivo / Adesività** | ~ 20 | 2018-2021 | "umido, adesivo" [15], "adesivo, poco friabile" [16] |
| **Duro / Durezza** | ~ 20 | 2018-2021 | "poca durezza, ma discreta pastosita" [1] |
| **Ingozza** | ~ 15 | 2018, 2020-2021 | "buona friabilità, ma asciutto alla deglutizione ingozza" [17], "Ingozza" [18] |
| **Gommoso** | ~ 15 | 2018, 2021 | "legg gommoso e asciutto" [17] |
| **Deformabile / Malleabile** | ~ 10 | 2018-2019 | "Malleabile deformabile" [9], "deformabile, pastoso" [19] |
| **Residuo (in bocca)** | ~ 10 | 2018-2019 | "lascia residuo polveroso" [20], "leggero residuo alla fine" [15] |
| **Lega la bocca / Legato / Astringente / Allappante** | ~ 10 | 2018, 2020-2021 | "Lega in bocca!" [8], "Leggermente allappante" [21], "Astringente" [22] |
| **Perle (di tirosina)** | 5 | 2020-2022 | "Contiene perle piuttosto dure" [23], "Perle fastidiose" [2] |
| **Immaturo / Giovane / Non pronto / Fresco** | 6 | 2018, 2021-2022 | "Sembra più giovane" [2], "morbido, sembra giovane. Impasta. non pronto" [14] |
| **Pasta stirata / Struttura stirata (Tipo Sbrinz)** | 6 | 2018, 2021-2022 | "struttura stirata tipo sbrinz" [24], "Presunta struttura stirata" [2] |
| **Fondente / Si liquefa / Liquescente** | 5 | 2018 | "cedevole sotto identi. Fondente" [25], "si liquefa velocemente" [26] |
| **Plastico / Indeformabile** | 4 | 2018-2019 | "troppo plastico al morso" [27], "Indeformabile plastico" [9] |
| **Burroso / Unto / Untuosità** | 3 | 2018, 2021 | "patoso e burroso/unto, bei granuli" [28] |
| **Schioccante / Scricchiola** (o *scrocchiarelli*) | 3 | 2020 | "Scricchiola ma non per cristalli" [22], "Leggermente schioccante" [8] |
| **Si spappola / Si sfalda** | 3 | 2018, 2021-2022 | "si spappola senza essere granulosa" [2], "si sfalda in mano" [25] |
| **Scagliette** | 2 | 2018, 2021-2022 | "rimangono scagliette strane sotto i denti" [17], "Scagliette e non granuli" [2] |
| **Patatoso** | 2 | 2020 | "Molto patatoso" [23], "Anche patatoso.." [23] |
| **Colloso** | 2 | 2018 | "Umido, cedevole, quasi colloso" [29] |
| **Faticoso** | 2 | 2019, 2021 | "Leggermente poco solubile e faticoso?" [30] |
| **Molliccio** | 2 | 2018 | "tendente al molliccio" [4] |
| **Disidratata / Asciuga le fauci** | 2 | 2018, 2021 | "lascia la bocca disidratata" [31] |
| **Nostrano** (come formaggio) | 2 | 2018 | "ricorda più un nostrano che un grana" [32] |
| **Emmental** (riferimento a formaggio) | 2 | 2018 | "sembra la pasta dell emmental" [33], "fosse un emmental" [34] |
| **Gnocchetti duri** | 1 | 2020 | "Presenza di gnocchetti duri" [23] |
| **Pongo** (mangiare pongo) | 1 | 2018 | "Umido, cedevole, quasi colloso. Sembra di mangiare pongo" [29, 35] |
| **Crema** | 1 | 2018 | "diventa quasi crema in bocca" [36] |
| **Asiago** (riferimento a formaggio) | 1 | 2018 | "sembra quasi asiago" [37] |
| **Ingrossa** | 1 | 2020 | "Ingrossa un pochetto" [22] |
| **Franabile** | 1 | 2018 | "elastico, poco franabile" [10] |
| **Sputarlo** | 1 | 2018 | "non lo so, ho docuto sputarlo" [38] |

**Nota per la normalizzazione**: I termini altamente insoliti della parte finale della tabella (es. *perle, gnocchetti duri, scagliette, patatoso, pongo, scricchiola*) rappresentano criticità preziose. Ad esempio, parole come "perle", "gnocchetti" e "scagliette" indicano percezioni di difetti di cristallizzazione o coesione della pasta, mentre termini come "patatoso", "pongo" o "crema" rimandano a gravissime carenze di struttura/microstruttura del Grana.

---

## Query 2 — Cluster semantici

**Cluster: Cristalli di tirosina**
- Varianti trovate nei dati: cristalli, microcristalli, tirosina, perle, gnocchetti duri, scagliette, schioccante, scricchiola [1-4].
- Forma canonica proposta: cristalli, tirosina
- Motivazione della scelta: I termini "cristalli" e "tirosina" sono invariabili in quanto termini tecnici di caseificazione non modificabili [5]. Essi indicano formazioni visibili e percepibili positivamente legate alla stagionatura [6], ma raggruppano anche i termini gergali (come "perle" o "gnocchetti") usati dai panelisti per descrivere difetti nella loro percezione [3, 4].
- Frequenza stimata del cluster: 315

**Cluster: Solubilità**
- Varianti trovate nei dati: solubile, solubilità, sol., solub., si scioglie, fondente, si liquefa, liquescente [1, 7-10].
- Forma canonica proposta: solubile, solubilità
- Motivazione della scelta: Regola di invariabilità applicata a "solubile" e "solubilità" [5]. Il cluster cattura la rapidità con cui il formaggio fonde e scompare nel cavo orale [6], assorbendo abbreviazioni e sinonimi più estremi come "fondente" o "si liquefa".
- Frequenza stimata del cluster: 255

**Cluster: Assenza di umidità / Secchezza**
- Varianti trovate nei dati: asciutto, secco, disidratata, asciuga le fauci, secchezza [7, 11-13].
- Forma canonica proposta: asciutto
- Motivazione della scelta: "Asciutto" è il termine canonico più diffuso nei commenti per descrivere una pasta priva di umidità [14]. Assorbe sinonimi diretti e descrizioni dell'effetto fisiologico percepito (come "asciuga le fauci").
- Frequenza stimata del cluster: 202

**Cluster: Friabilità**
- Varianti trovate nei dati: friabile, friabilità, frantuma, sbriciola, franabile [7, 15-17].
- Forma canonica proposta: friabile, friabilità
- Motivazione della scelta: I termini "friabile" e "friabilità" sono rigorosamente invariabili [5]. Essi descrivono la tendenza corretta della pasta di Grana Trentino a rompersi in frammenti durante la masticazione [6].
- Frequenza stimata del cluster: 151

**Cluster: Morbidezza**
- Varianti trovate nei dati: morbido, molle, tenero, molliccio [1, 11, 18, 19].
- Forma canonica proposta: morbido
- Motivazione della scelta: "Morbido" è il descrittore base professionale, ampiamente usato dai panelisti [14]. Raggruppa anche le espressioni peggiorative o colloquiali come "molliccio" o "molle" mantenendo il riferimento alla scarsa resistenza meccanica.
- Frequenza stimata del cluster: 152

**Cluster: Pastosità**
- Varianti trovate nei dati: pastoso, pastosità, patatoso, pongo, crema [1, 3, 20, 21].
- Forma canonica proposta: pastoso
- Motivazione della scelta: Descrive la tendenza della pasta a formare una massa compatta e omogenea invece di frantumarsi [6]. In questo cluster convergono anche analogie estreme o dialettali utilizzate durante la degustazione ("pongo", "patatoso", "crema") [22].
- Frequenza stimata del cluster: 124

**Cluster: Granulosità**
- Varianti trovate nei dati: grana, granuloso, granulosità, granuli, granuolo [1, 7, 23, 24].
- Forma canonica proposta: grana, granuloso
- Motivazione della scelta: La parola "grana" è invariabile e non va alterata [5]. Il cluster mappa la presenza meccanica e tattile delle particelle della struttura casearia.
- Frequenza stimata del cluster: 100

**Cluster: Umidità**
- Varianti trovate nei dati: umido, umidità, unidita [1, 7, 25].
- Forma canonica proposta: umido
- Motivazione della scelta: Termine sensoriale diretto che quantifica il contenuto acquoso o la sensazione di bagnato percepita nella pasta, in opposizione ad asciutto [6].
- Frequenza stimata del cluster: 80

**Cluster: Compattezza**
- Varianti trovate nei dati: compatto, compattezza [4, 11, 26].
- Forma canonica proposta: compatto, compattezza
- Motivazione della scelta: Applicazione della regola di invariabilità per "compatto" e "compattezza" [5], termini che esprimono l'unione e la densità della matrice strutturale del formaggio.
- Frequenza stimata del cluster: 80

**Cluster: Architettura della pasta**
- Varianti trovate nei dati: struttura, microstruttura [7, 27, 28].
- Forma canonica proposta: struttura
- Motivazione della scelta: Entrambi i termini operano come descrittori generali utilizzati per commentare la griglia meccanica del formaggio e la sua finezza o grossolanità al morso [6].
- Frequenza stimata del cluster: 60

**Cluster: Cedevolezza**
- Varianti trovate nei dati: cedevole, cedevolezza [15, 29, 30].
- Forma canonica proposta: cedevole
- Motivazione della scelta: "Cedevole" è prescritto come termine tecnico invariabile [5]. Indica un formaggio che offre poca resistenza alla prima compressione dentale.
- Frequenza stimata del cluster: 40

**Cluster: Sensazione farinosa e sabbiosa**
- Varianti trovate nei dati: sabbioso, sabbiosità, sabbietta, farinoso, sensazione di farina, polveroso, residuo (in bocca) [1, 7, 11, 31].
- Forma canonica proposta: sabbioso / farinoso
- Motivazione della scelta: Raggruppa tutte le percezioni di micro-particelle insolubili (simili a polvere, sabbia o farina) che permangono come residuo fastidioso sul palato dopo la deglutizione [14, 22].
- Frequenza stimata del cluster: 60

**Cluster: Adesività**
- Varianti trovate nei dati: adesivo, adesività, impasta, incolla la bocca, colloso [20, 24, 32, 33].
- Forma canonica proposta: adesivo
- Motivazione della scelta: "Adesivo" standardizza concetti che indicano la forza richiesta per staccare il materiale dal palato e dai denti, includendo gli effetti pratici lamentati dai giudici (es. "incolla la bocca" o "impasta") [22].
- Frequenza stimata del cluster: 52

**Cluster: Plasticità / Elasticità**
- Varianti trovate nei dati: gommoso, elastico, plastico, indeformabile, deformabile, malleabile [1, 15, 34, 35].
- Forma canonica proposta: plastico / elastico
- Motivazione della scelta: Raccoglie i difetti strutturali di un formaggio a pasta dura che cede senza rompersi o che ricorda dinamiche gommose/plastiche, comportamenti anomali per la corretta friabilità del Grana [6].
- Frequenza stimata del cluster: 29

**Cluster: Astringenza e difficoltà di deglutizione**
- Varianti trovate nei dati: astringente, allappante, ingozza, ingrossa, lega la bocca, legato, faticoso [36-39].
- Forma canonica proposta: astringente / ingozza
- Motivazione della scelta: Centralizza le espressioni libere che identificano l'assorbimento sgradevole della saliva ("lega la bocca", "allappante") e lo sforzo ostruttivo al momento di deglutire il bolo ("ingozza") [22].
- Frequenza stimata del cluster: 28

**Cluster: Durezza**
- Varianti trovate nei dati: duro, durezza [1, 40, 41].
- Forma canonica proposta: duro
- Motivazione della scelta: Descrittore meccanico primario che riassume la forza applicata per spezzare il campione al primo morso [6].
- Frequenza stimata del cluster: 20

**Cluster: Riferimento a maturazione insufficiente**
- Varianti trovate nei dati: immaturo, giovane, non pronto, fresco [33, 36, 42].
- Forma canonica proposta: giovane
- Motivazione della scelta: Sintetizza i giudizi dei valutatori che associano un insieme di carenze di texture (es. elasticità o pastosità) a un Grana con difetto di stagionatura [22].
- Frequenza stimata del cluster: 6

**Cluster: Scarsa coesione strutturale**
- Varianti trovate nei dati: si spappola, si sfalda [40, 43, 44].
- Forma canonica proposta: si sfalda
- Motivazione della scelta: Descrive una scomposizione disordinata della pasta che viene giudicata in contrapposizione alla friabilità o alla granulometria attesa [22].
- Frequenza stimata del cluster: 3

**Cluster: Percezione lipidica**
- Varianti trovate nei dati: burroso, unto, untuosità [8, 45].
- Forma canonica proposta: burroso
- Motivazione della scelta: Riunisce le valutazioni incentrate sulla presenza distinta, scivolosa o scioglievole del grasso in bocca.
- Frequenza stimata del cluster: 3

**Cluster: Comparazioni con formaggi non conformi**
- Varianti trovate nei dati: nostrano, pasta stirata, struttura stirata (Tipo Sbrinz), emmental, asiago [2, 34, 46-48].
- Forma canonica proposta: nostrano, stirata
- Motivazione della scelta: Regola di invariabilità per "nostrano" e "stirata" [5]. Il cluster cattura tutti i casi in cui il panelista descrive una grave anomalia di texture menzionando altre tipologie casearie completamente diverse dal Grana Trentino.
- Frequenza stimata del cluster: 11

---

## Query 3 — Anomalie e termini quantitativi

| Termine trovato | Tipo (1–5) | Proposta di normalizzazione | Confidenza (alta/media/bassa) | Note |
| :--- | :--- | :--- | :--- | :--- |
| **sol.** / **solub.** | 1 | solubile / solubilità | alta | Troncamenti frequentissimi per il termine tecnico invariabile, usati per scrivere rapidamente [1-3]. |
| **legg.** | 1 | leggermente | alta | Abbreviazione standard e ricorrente nei commenti [2, 4, 5]. |
| **cris.** / **crist.** | 1 | cristalli | alta | Abbreviazioni del termine tecnico invariabile riferito ai cristalli di tirosina [6, 7]. |
| **un po-** | 1 | un po' | alta | Contrazione e probabile errore di battitura dovuto all'uso del trattino al posto dell'apostrofo [1, 8]. |
| **pongo** | 2 | pastoso / adesivo | alta | Termine colloquiale ("Sembra di mangiare pongo") usato per indicare estrema pastosità ed elevata adesività [9]. |
| **a gogo** | 2 | molti | alta | Espressione gergale ("cristalli a gogo") per segnalare una forte abbondanza [10]. |
| **patatoso** | 2 | pastoso / farinoso | media | Neologismo o colloquilialismo per definire una consistenza simile alla patata lessa [11]. |
| **scrocchiarelli** / **schioccante** | 2 | cristalli | alta | Onomatopee usate per tradurre il rumore meccanico della rottura dei cristalli sotto i denti [11, 12]. |
| **perle** / **gnocchetti duri** | 2 | cristalli | alta | Definizioni gergali utilizzate dai giudici per indicare agglomerati anomali o fastidiosi di tirosina [11, 13]. |
| **granuolo** / **granumelotria** | 3 | grana / granulometria | alta | Chiari errori di digitazione (typo) riguardanti i descrittori strutturali [2, 3, 14]. |
| **unidita** / **aciutto** | 3 | umidità / asciutto | alta | Comuni errori ortografici di trascrizione veloce [1, 15]. |
| **identi** | 3 | i denti | alta | Errore di spaziatura ("sotto identi") ricorrente [3]. |
| **firabile** / **rfiabile** | 3 | friabile | alta | Anagrammi accidentali (typo) del termine tecnico invariabile [16, 17]. |
| **(1)** | 4 | 5.92 → Intensità minima | media | Trovato nell'espressione "no cristalli (1)" per il campione C0A (seduta 21). Il file 2018 mostra un punteggio di 5.92. Probabile nota quantitativa personale del giudice [18]. |
| **3 porzioni / 1 porzione** | 4 | 7.54 → Campione eterogeneo | alta | Trovato nell'espressione "in 3 porzioni presenza di cristalli... 1 porzione senza" (campione C0E, seduta 21). Punteggio 2018 associato: 7.54. Indica forte disomogeneità [19]. |
| **4 porzioni** | 4 | 6.76 → Eterogeneità strutturale | alta | "Differente solubilità tra le 4 porzioni" per il campione C0N (seduta 12). Punteggio 2018 associato: 6.76 [20]. |
| **Asciutto** vs **Umido** | 5 | Incoerenza percettiva da verificare | alta | Seduta 4, campione C0A: il panelista Q_09 lo descrive "asciutto" (punteggio 8.74), mentre TG_04 lo trova "umido, cedevole" (punteggio 6.04) [5]. |
| **Duro** vs **Molle** | 5 | Incoerenza meccanica da verificare | alta | Seduta 11, campione C0M: TG_14 lo valuta "duro, asciutto" (punteggio 6.04), ma TG_13 annota "molle e senza grana" (punteggio 6.76) [21]. |
| **Molti cristalli** vs **Pochi** | 5 | Eterogeneità del campione | alta | Seduta 25, campione C0H: TG_35 rileva "cristalli grossi" (punteggio 8.02) mentre TG_24 dichiara "pochi cristalli" (punteggio 6.52) [22]. |
| **Troppo friabile** vs **Morbido** | 5 | Incoerenza strutturale | alta | Seduta 8, campione C0B: TG_24 nota che è "troppo friabile, asciutto" (punteggio 6.16), ma in netta opposizione TG_14 lo definisce "morbido" (punteggio 7) [23]. |

---

## Query 4 — Dubbi per revisione umana

---
**DUBBIO 1:** "Alleabile"
- **Perché è ambiguo:** È una parola inesistente nel vocabolario italiano, probabilmente un errore di battitura o un refuso dovuto a un sistema di dettatura vocale [1].
- **Opzione A:** Normalizzare in "Malleabile", coerente con i difetti di struttura plastica.
- **Opzione B:** Normalizzare in "Allappante", riferito alla sensazione di astringenza in bocca.
- **Suggerimento NotebookLM:** Preferire l'**Opzione A**. Il panelista Q_09 descrive molto spesso i formaggi con problemi di struttura usando il termine "deformabile" o "indeformabile plastico" [2-4]. "Malleabile" appartiene allo stesso campo semantico [2].
- **Dati a supporto:** Il panelista Q_09, nella seduta 17 del 2019 (campione C0M), scrive unicamente: "Alleabile" [1].

---
**DUBBIO 2:** "Ingrossa un pochetto"
- **Perché è ambiguo:** Non è chiaro se il termine descriva una reale reazione della pasta (che si gonfia o aumenta di volume assorbendo saliva) o se sia un errore introdotto dal correttore automatico dello smartphone/tablet.
- **Opzione A:** Normalizzare in "Ingozza" (difficoltà di deglutizione, bolo che si blocca).
- **Opzione B:** Mantenere come cluster separato o unire a "Impasta", per descrivere l'aumento di volume.
- **Suggerimento NotebookLM:** Preferire l'**Opzione A**. Il panelista TG_04 ricorre abitualmente e in modo sistematico al termine "ingozza" in decine di valutazioni [1, 5-7].
- **Dati a supporto:** Il commento è di TG_04 sul campione C0M (Seduta 16, 2020) [7]. Nelle sedute limitrofe, lo stesso panelista scrive ripetutamente "Ingozza" [7, 8].

---
**DUBBIO 3:** "Gestire mediocre"
- **Perché è ambiguo:** "Gestire" è un verbo anomalo per l'analisi sensoriale della texture, ed è sintatticamente scollegato dal resto [9].
- **Opzione A:** Errore di trascrizione (speech-to-text o battitura) per "Texture mediocre".
- **Opzione B:** Si riferisce alla "gestione" del bolo in bocca (es. la pasta è difficile da masticare o deglutire).
- **Suggerimento NotebookLM:** Preferire l'**Opzione A**. Nei dataset analizzati, i giudici tendono a emettere giudizi troncati sull'attributo generale, rendendo altamente plausibile uno scambio fonetico tra "Texture" e "Gestire".
- **Dati a supporto:** Valutazione del panelista TG_19, seduta 8 del 2021 (campione C0A) [9]. 

---
**DUBBIO 4:** "Perle" / "Perle fastidiose"
- **Perché è ambiguo:** La regola tecnica impone di non normalizzare "cristalli" e "tirosina" perché sono attributi invariabili positivi della stagionatura [10]. Tuttavia, i panelisti usano il termine "perle" distinguendole esplicitamente dai cristalli sani.
- **Opzione A:** Normalizzare forzatamente in "Cristalli", accorpandole al parametro tecnico.
- **Opzione B:** Mantenere "Perle" come descrittore di difetto strutturale (agglomerati insolubili, duri o anomali).
- **Suggerimento NotebookLM:** Preferire l'**Opzione B**. Le "perle" sono chiaramente identificate dalla giuria come un difetto che compromette la piacevolezza della masticazione, a differenza dei cristalli fini.
- **Dati a supporto:** TG_04 specifica: "Non cristalli, Ma probabile molte perle di tirosina" [9]. TG_14 lamenta: "Contiene perle piuttosto dure, non piacevoli alla masticazione" [11]. TG_19 aggiunge: "Perle fastidiose" [9].

---
**DUBBIO 5:** "Patatoso"
- **Perché è ambiguo:** È un termine colloquiale inventato dai panelisti che sfugge alla terminologia scientifica standard.
- **Opzione A:** Normalizzare in "Pastoso" (pasta cedevole, umida, che ricorda la patata lessa schiacciata).
- **Opzione B:** Normalizzare in "Farinoso / Sabbioso" (che ricorda l'amido asciutto della patata cruda).
- **Suggerimento NotebookLM:** Preferire l'**Opzione A**. Solitamente nei formaggi a pasta dura questo difetto denota una consistenza molle e impastante che si allontana dalla corretta friabilità.
- **Dati a supporto:** Il termine compare nelle sedute 7 e 8 del 2020: TG_35 scrive "Molto patatoso" e TG_24 commenta "Anche patatoso.." [11].

---
**DUBBIO 6:** "faticoso?"
- **Perché è ambiguo:** Esprime uno sforzo meccanico o fisiologico, ma omette la fase in cui avviene (al taglio dei denti o durante la deglutizione).
- **Opzione A:** Normalizzare in "Duro" (faticoso al primo morso).
- **Opzione B:** Normalizzare in "Astringente / Ingozza / Poco solubile" (faticoso da deglutire o trasformare in bolo).
- **Suggerimento NotebookLM:** Preferire l'**Opzione B**. La parola è abbinata alla scarsa solubilità, che genera uno sforzo di salivazione e deglutizione, tipico di una pasta che allappa [12].
- **Dati a supporto:** TG_24 (2021, seduta 20) annota: "Leggermente poco solubile e faticoso?" [12].

---
**DUBBIO 7:** "immagiabile"
- **Perché è ambiguo:** Evidente troncamento o refuso ortografico [2].
- **Opzione A:** Refuso per "immangiabile" (giudizio edonico su un difetto gravissimo di texture).
- **Opzione B:** Refuso per "immasticabile" (giudizio puramente meccanico).
- **Suggerimento NotebookLM:** Preferire l'**Opzione A**. La sintassi della frase suggerisce una preclusione totale al giudizio per scarsissima qualità.
- **Dati a supporto:** Q_02, seduta 9 del 2019 (campione C0F), commenta: "Difficile da giudicare perché immagiabile" [2].

---
**DUBBIO 8:** "(1)"
- **Perché è ambiguo:** Presenza anomala di una cifra isolata all'interno del campo di testo libero [13].
- **Opzione A:** È l'indicazione quantitativa dell'intensità del difetto/attributo (sulla scala sensoriale, punteggio 1 = assente).
- **Opzione B:** È un riferimento alla prima porzione o al primo cubetto degustato.
- **Suggerimento NotebookLM:** Preferire l'**Opzione A**. Nel commento, il numero "1" affianca la parola "no cristalli", validando l'ipotesi che il giudice abbia appuntato l'intensità minima della scala per l'attributo tirosina [13].
- **Dati a supporto:** Q_09 (seduta 21, 2018) scrive: "morbido poco granuloso no cristalli (1)" [13].

---
**DUBBIO 9:** "farino"
- **Perché è ambiguo:** Parola interrotta [14].
- **Opzione A:** Troncamento per "farinoso".
- **Opzione B:** Troncamento per "sensazione di farina".
- **Suggerimento NotebookLM:** Opzione A. Dal punto di vista pratico il risultato non cambia il cluster ("Sabbioso/Farinoso"), ma per pulizia del database è utile decidere lo standard morfologico.
- **Dati a supporto:** TG_13 (seduta 19, 2018) annota: "asciutto, farino e poco solubile" [14].

---

## Istruzioni per la revisione umana

1. Leggi ogni sezione e valida / correggi le proposte di normalizzazione
2. Risolvi ogni dubbio in Query 4 scegliendo Opzione A, B o altra
3. Per Spessore della Crosta: confronta soglie script vs analisi NBLM e scegli i range definitivi
4. Salva le decisioni finali in: `data/interim/vocabolari_validati_per_attributo/Texture_vocabolario.json`
5. Usa come template: `docs/template_vocabolario_validato.json` (generato da questo script)
