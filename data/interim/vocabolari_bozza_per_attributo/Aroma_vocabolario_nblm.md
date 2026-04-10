# Vocabolario Bozza — Aroma

**Generato:** 2026-04-09 20:26
**Notebook NotebookLM:** `8721a403-3952-439f-948b-e75f553ee673`
**Stato:** BOZZA — richiede revisione umana prima di procedere con script 09

---

## Orientamento iniziale NotebookLM

Ho compreso l'obiettivo del progetto: l'analisi sensoriale del formaggio Grana Trentino per l'attributo "Aroma", finalizzata alla creazione di un dizionario di normalizzazione che raggruppi sinonimi e varianti dei termini scritti dai panelisti [1, 2].

Ecco le conferme richieste:
*   **Numero di fonti CSV**: Delle 8 fonti totali fornite, **7 sono file CSV** contenenti i dati originali o i risultati delle medie di giuria.
*   **Range temporale dei dati**: Le sessioni di valutazione coprono gli anni dal **2018 al 2021** [1, 3].
*   **Colonna da analizzare**: La colonna di interesse, che raccoglie il testo libero scritto dai valutatori, si chiama **"Commenti"** [4].

---

## Query 1 — Inventario termini

Ecco l'estrazione di tutti i termini e le espressioni utilizzate dai panelisti per descrivere l'attributo "Aroma", organizzati per frequenza decrescente. Dato l'elevato numero di varianti testuali e commenti liberi sparsi in migliaia di righe, le occorrenze sono stimate in fasce (Alta, Media, Bassa, Singola) [1].

| Termine / Espressione | Occorrenze (stima) | Anni in cui compare | Esempio di frase completa |
| :--- | :--- | :--- | :--- |
| **Cotto** / Latte cotto / Formaggio cotto / Lattici cotti | Alta (>50) | 2018, 2019, 2020, 2021 | "latte cotto, burro cotto, brodo, abbastanza equilibrato" [2, 3] |
| **Burro** / Burro fuso / Burro cotto / Burroso / Burro fresco | Alta (>50) | 2018, 2019, 2020 | "lattico netto di burro fuso, lieve sentore propionico" [4, 5] |
| **Brodo** / Brodo di carne / Brodo vegetale / Dado / Umami | Alta (>50) | 2018, 2019, 2020 | "emerge molto il burro e il latte cotto... equilibrato dado da brodo" [6-8] |
| **Crosta** / Crosta di formaggio / Crosta di grana | Alta (>40) | 2018, 2019, 2020, 2021 | "crosta, da grana vecchio, speziato, animale" [6, 9] |
| **Panna** / Panna cotta / Panna fresca / Panna acida | Alta (>40) | 2018, 2019, 2020 | "rimangono le note lattiche della panna e del burro fuso, equilibrato" [3, 10] |
| **Animale** / Stalla / Stallatico / Vacca / Letame | Media (15-30) | 2018, 2019, 2020 | "confermo un animale\stalla" [3, 11] |
| **Ossidato** / Stantio / Vecchio / Passato / Rancido | Media (15-30) | 2018, 2019, 2020 | "stantio, tostato forte, animale... rancido MODERATO" [3, 12, 13] |
| **Tostato** / Bruciato / Latte bruciato | Media (15-30) | 2018, 2019, 2020, 2021 | "cotto quasi bruciato, legna secca vecchia" [14, 15] |
| **Fermentato** / Frutta fermentata / Vegetale fermentato | Media (15-30) | 2018, 2019, 2020 | "note lattiche fermentate, ossiadto, sapone" [16, 17] |
| **Fieno** / Erba / Erbaceo / Erbe amare / Vegetale | Media (15-30) | 2018, 2019, 2020 | "brodo animale con punte di erbe amare" [3, 18] |
| **Frutta** / Fruttato / Frutta matura | Media (10-20) | 2018, 2019, 2020 | "torna forte la nota fruttata *sembra ananas*" [3, 19] |
| **Glutammato** / Umami | Bassa (5-10) | 2018, 2020 | "Poco complesso, nota di glutammato prevalente" [3, 15] |
| **Sapone** / Saponoso / Nota saponata | Bassa (5-10) | 2018, 2019, 2020, 2021 | "nota di sapone, di ossidato, meno sgradevole che al naso" [3, 20, 21] |
| **Nostrano** / Provolone / Emmenthal / Gorgonzola / Taleggio | Bassa (5-10) | 2018, 2019, 2020 | "poco caratteristico come al naso, note di emmental" [3, 10] |
| **Nocciola** / Frutta secca / Mandorla amara | Bassa (5-10) | 2018, 2020, 2021 | "tostato male, mandorla amara, brodo animale" [5, 21, 22] |
| **Verdure lesse** / Minestrone / Cipolla / Sedano / Cavolfiore | Bassa (5-10) | 2018, 2019, 2020 | "aroma di verdure lesse, brodo vegetale, formaggio cotto" [3, 23] |
| **Latte acido** / Yogurt | Bassa (3-6) | 2018, 2021 | "latte acidificato e yogurt intensità alta" [9, 24] |
| **Muffa** / Fungo | Bassa (3-6) | 2018 | "aroma di muffa/fungo/crosta intensità bassa" [25, 26] |
| **Caramello** / Mou | Bassa (3-6) | 2018, 2020 | "lieve nota di bruciato, caramella mou" [15, 27] |
| **Propionico** / Propionica | Bassa (3-6) | 2018 | "note di emmental, propioniche, frutta tropicale" [28] |
| **Polvere** / Polveroso | Bassa (2-5) | 2020, 2021 | "Polvere!!!!" [21, 29] |
| **Metallico** | Bassa (2-5) | 2019, 2021 | "Leggermente metallico" [3, 21] |
| **Carne lessa** | Bassa (2-5) | 2020 | "Erbe amare, carne lessa" [3] |
| **Cacao** / Cacao amaro | Bassa (2-4) | 2018, 2020 | "Cacao amaro vecchio, medicinale" [3, 28] |
| **Liquirizia** | Bassa (2-4) | 2018, 2020 | "quasi bruciato, liquirizia, caramello, legno" [5, 30] |
| **Mela** / Pera / Banana / Ananas | Bassa (2-4) | 2018, 2020, 2021 | "Troppo ananas banana che non sono tipici" [31, 32] |
| **Farmaco** / Farmacia / Medicinale | Bassa (2-3) | 2018, 2021 | "nota aromatica non tipica del trentingrana, quasi di medicina / farmaco" [9, 33] |
| **Sangue,,,** | Singola occorrenza | 2021 | "Sangue,,," [21] |
| **Vinavil** | Singola occorrenza | 2021 | "Vinavil" [21] |
| **Mentolato** | Singola occorrenza | 2021 | "Mentolato!" [21] |
| **Pratomagno** | Singola occorrenza | 2021 | "Pratomagno" [21] |
| **Bitter** | Singola occorrenza | 2021 | "Bitter" [21] |
| **Acqua di fogna** | Singola occorrenza | 2018 | "pessimo, poco caratteristico, acqua di fogna, marcio" [34] |
| **Armadio della nonna** | Singola occorrenza | 2020 | "Pessimo all'aroma, armadio della nonna " [5] |
| **Vomitevole** | Singola occorrenza | 2020 | "Vomitevole" [17] |
| **Salame** | Singola occorrenza | 2020 | "Salame" [17] |
| **Sentore di ragù** | Singola occorrenza | 2020 | "Sentore di ragù" [17] |
| **Acciuga e salamoia** | Singola occorrenza | 2020 | "Acciuga e salamoia leggere" [29] |
| **Clostridium sporogenes** | Singola occorrenza | 2019 | "Immangiabile Fermentazione da Clostridium sporogenes" [3] |
| **Idrocarburi** | Singola occorrenza | 2019 | "Idrocarburi" [3] |
| **Lettiera** | Singola occorrenza | 2019 | "Lettiera" [3] |
| **Zafferano** | Singola occorrenza | 2020 | "Zafferano" [5] |
| **Crauti** | Singola occorrenza | 2019 | "Crauti" [3] |
| **Cristalli di sale** | Singola occorrenza | 2021 | "Cristalli di sale" [32] |
| **Plastica** | Singola occorrenza | 2018 | "plastica ?" [33] |

**Nota per la normalizzazione**: I commenti dimostrano come l'Aroma venga spesso descritto non solo con concetti codificati (es. *latte cotto, burro, brodo*), ma anche attraverso metafore insolite (*armadio della nonna, acqua di fogna, vinavil*) che indicano difetti specifici come stantio, putrido o note chimiche [1, 5, 21, 34, 35]. Molti di questi termini estremi appaiono una volta sola e richiederanno di essere accorpati alla famiglia di difetto più appropriata nel dizionario finale.

---

## Query 2 — Cluster semantici

**Cluster: Latte Cotto**
- Varianti trovate nei dati: cotto, latte cotto, formaggio cotto, lattici cotti, latte bollito, panna cotta, formaggio fuso [1-4].
- Forma canonica proposta: Latte cotto
- Motivazione della scelta: Rappresenta il descrittore positivo primario, e standardizzato, utilizzato per indicare il sentore lattico sottoposto a trattamento termico [5, 6].
- Frequenza stimata del cluster: > 150

**Cluster: Burro**
- Varianti trovate nei dati: burro, burro fuso, burro cotto, burroso, burro fresco, burro sciolto [1, 7-10].
- Forma canonica proposta: Burro
- Motivazione della scelta: "Burro" (spesso descritto come fuso) è uno dei termini canonici fondamentali per l'aroma del formaggio Grana e racchiude tutte le percezioni lipidiche dolci [5, 6].
- Frequenza stimata del cluster: > 120

**Cluster: Brodo / Umami**
- Varianti trovate nei dati: brodo, brodo di carne, brodo vegetale, dado, glutammato, umami, carne lessa, sentore di ragù, acciuga e salamoia, brodo di pollo [1, 8, 11-14].
- Forma canonica proposta: Brodo
- Motivazione della scelta: Tutti questi termini indicano la medesima percezione sapida (umami) derivante dai peptidi della stagionatura, tradizionalmente codificata come "brodo" [5, 6].
- Frequenza stimata del cluster: > 100

**Cluster: Panna / Latte fresco**
- Varianti trovate nei dati: panna, panna fresca, latte, lattico fresco, panna vegetale, latte UHT [1, 11, 15, 16].
- Forma canonica proposta: Panna
- Motivazione della scelta: Raccoglie le sensazioni lattiche dolci non cotte, distinguendole nettamente dall'aroma di latte bollito o cotto [5].
- Frequenza stimata del cluster: ~ 80

**Cluster: Crosta**
- Varianti trovate nei dati: crosta, crosta di formaggio, crosta pulita [7, 11, 17, 18].
- Forma canonica proposta: Crosta
- Motivazione della scelta: Identifica in modo chiaro la sensazione olfattiva esterna della forma che rientra durante la masticazione [6, 19].
- Frequenza stimata del cluster: > 80

**Cluster: Tostato / Bruciato**
- Varianti trovate nei dati: tostato, bruciato, latte bruciato, crosta di pane, fumo, affumicato, legna secca, tostatura, formaggio fritto [2, 7, 12, 20, 21].
- Forma canonica proposta: Tostato
- Motivazione della scelta: "Tostato" è il termine tecnico adeguato per accorpare tutte le note di Maillard, spingendosi fino alle accezioni negative di "bruciato" [6, 19].
- Frequenza stimata del cluster: ~ 50

**Cluster: Animale / Stalla**
- Varianti trovate nei dati: animale, stalla, stallatico, vacca, letame, lettiera [1, 7, 12, 20-22].
- Forma canonica proposta: Animale
- Motivazione della scelta: Accorpa i descrittori legati all'ambiente di stalla e al bestiame, che costituiscono una ben nota famiglia di difetti sensoriali [5, 6].
- Frequenza stimata del cluster: ~ 40

**Cluster: Vegetale (Erbaceo / Fieno)**
- Varianti trovate nei dati: fieno, erba, erbaceo, erbe amare, vegetale, paglia, pratomagno [1, 4, 12, 13, 17, 23].
- Forma canonica proposta: Fieno
- Motivazione della scelta: Descrittore standard che riassume le percezioni olfattive riconducibili al foraggio secco o verde, tipiche del latte di partenza [5, 6].
- Frequenza stimata del cluster: ~ 40

**Cluster: Vegetale Cotto (Ortaggi)**
- Varianti trovate nei dati: verdure lesse, minestrone, cipolla, sedano, cavolfiore, verdura cotta, broccoli, crauti [3, 4, 8, 12, 21, 24].
- Forma canonica proposta: Verdure lesse
- Motivazione della scelta: Si differenzia dal fieno per la presenza di composti solforati (spesso sintomo di lievi anomalie fermentative) ed è più preciso di un generico "vegetale" [6].
- Frequenza stimata del cluster: ~ 30

**Cluster: Ossidato / Stantio**
- Varianti trovate nei dati: ossidato, stantio, vecchio, passato, rancido, armadio della nonna [7, 8, 11, 13, 25, 26].
- Forma canonica proposta: Ossidato
- Motivazione della scelta: Normalizza le varianti colloquiali o metaforiche sotto l'attributo tecnico "ossidato" (o rancido), tipico difetto di degradazione lipidica [5, 6].
- Frequenza stimata del cluster: ~ 50

**Cluster: Fermentato / Acido**
- Varianti trovate nei dati: fermentato, frutta fermentata, vegetale fermentato, latte acido, panna acida, yogurt, siero acido, Clostridium sporogenes [1, 2, 8, 11, 12].
- Forma canonica proposta: Fermentato
- Motivazione della scelta: Identifica tutte le note pungenti e lattico-acide dovute a eccesso di maturazione o a difetti microbiologici [6, 19].
- Frequenza stimata del cluster: ~ 40

**Cluster: Frutta Fresca**
- Varianti trovate nei dati: frutta, fruttato, frutta matura, ananas, mela, banana, pera, frutta tropicale [11, 12, 22, 27-29].
- Forma canonica proposta: Fruttato
- Motivazione della scelta: È il macrogruppo semantico che raccoglie gli esteri aromatici dolci e fruttati percepiti durante l'assaggio [5, 6].
- Frequenza stimata del cluster: ~ 30

**Cluster: Frutta Secca**
- Varianti trovate nei dati: nocciola, frutta secca, mandorla amara, castagne, noce [7, 12, 14, 30, 31].
- Forma canonica proposta: Frutta secca
- Motivazione della scelta: Rappresenta una categoria olfattiva separata rispetto alla frutta fresca, molto diffusa nei formaggi stagionati [6].
- Frequenza stimata del cluster: ~ 20

**Cluster: Dolce / Caramello**
- Varianti trovate nei dati: caramello, mou, cacao, cacao amaro, liquirizia, miele, biscotto, confetto [10, 17, 20, 21, 32].
- Forma canonica proposta: Caramello
- Motivazione della scelta: Definisce le sensazioni dolci e calde spesso collegate a note aromatiche tostate più rotonde [6].
- Frequenza stimata del cluster: ~ 15

**Cluster: Difetti Chimici / Putridi**
- Varianti trovate nei dati: sapone, saponoso, farmaco, farmacia, medicinale, metallico, vinavil, plastica, bitter, idrocarburi, acqua di fogna, vomitevole, putrido, marcio, sangue, mentolato [7, 12, 20, 22-24, 33].
- Forma canonica proposta: Difetto chimico / Putrido
- Motivazione della scelta: Raggruppa tutte le metafore atipiche e i vocaboli che denotano gravi alterazioni batteriche, chimiche o di inquinamento del campione [6].
- Frequenza stimata del cluster: ~ 30

**Cluster: Altri formaggi (Non tipici)**
- Varianti trovate nei dati: provolone, emmenthal, formaggio svizzero, taleggio, gorgonzola, sbrinz, formaggino, malga [1, 12, 17, 33-35].
- Forma canonica proposta: Altro formaggio
- Motivazione della scelta: Isola i commenti in cui il valutatore avverte un aroma estraneo al TrentinGrana paragonandolo esplicitamente ad altri prodotti caseari [6].
- Frequenza stimata del cluster: ~ 25

**Cluster: nostrano**
- Varianti trovate nei dati: nostrano [11, 24, 25, 35-38].
- Forma canonica proposta: nostrano
- Motivazione della scelta: Termine tecnico caseario contrassegnato come INVARIABILE dalle istruzioni di progetto e che non deve subire normalizzazioni [39].
- Frequenza stimata del cluster: ~ 15

**Cluster: grana**
- Varianti trovate nei dati: grana [1, 2, 7, 33, 40].
- Forma canonica proposta: grana
- Motivazione della scelta: Termine tecnico caseario identificato come INVARIABILE che va preservato nel testo originale [39].
- Frequenza stimata del cluster: ~ 40

**Cluster: insilato**
- Varianti trovate nei dati: insilato [41].
- Forma canonica proposta: insilato
- Motivazione della scelta: Termine tecnico caseario INVARIABILE richiesto esplicitamente dalle direttive del progetto [39].
- Frequenza stimata del cluster: 2

**Cluster: cristalli**
- Varianti trovate nei dati: cristalli, cristalli di sale [29].
- Forma canonica proposta: cristalli
- Motivazione della scelta: Termine tecnico caseario INVARIABILE (usato occasionalmente come appunto sulla struttura anche nel campo aroma) da lasciare non modificato [29, 39].
- Frequenza stimata del cluster: 2

**Cluster: solubile**
- Varianti trovate nei dati: solubile [12].
- Forma canonica proposta: solubile
- Motivazione della scelta: Termine tecnico caseario INVARIABILE, riportato eccezionalmente nei commenti dell'aroma, che deve mantenere la sua forma nativa [12, 39].
- Frequenza stimata del cluster: 1

---

## Query 3 — Anomalie e termini quantitativi

| Termine trovato | Tipo (1–5) | Proposta di normalizzazione | Confidenza (alta/media/bassa) | Note |
| :--- | :--- | :--- | :--- | :--- |
| **legg.** / **leg** | 1 (Abbreviazione) | leggermente | Alta | Frequente in tutti i file [1-5]. Il manuale stesso lo indica come abbreviazione standard [6]. |
| **mediam.** | 1 (Abbreviazione) | mediamente | Alta | Indicato esplicitamente nel documento di contesto come abbreviazione usata [6]. |
| **retroolfatt** | 1 (Abbreviazione) | retrolfattivo | Alta | Contrazione per indicare la via retrolfattiva [7]. |
| **quanta stalla, signora mia!** | 2 (Colloquialismo) | stalla | Alta | Espressione colorita e colloquiale per indicare un forte difetto animale [4]. |
| **miseria** | 2 (Colloquialismo) | poco intenso / scarso | Media | Esclamazione usata per descrivere un'intensità aromatica estremamente deludente [8]. |
| **desaparecido** | 2 (Colloquialismo) | assente | Alta | Usato metaforicamente per indicare un aroma che è del tutto svanito in bocca [9]. |
| **passato** | 2 (Colloquialismo) | ossidato / stravecchio | Alta | Termine gergale usato dai valutatori per un prodotto con difetti da eccessiva maturazione o cattiva conservazione [10-13]. |
| **scarico** | 2 (Colloquialismo) | poco intenso | Alta | Gergale per indicare bassa intensità della percezione retrolfattiva [5, 14, 15]. |
| **talla** ("Retrogusto di talla") | 3 (Typo) | stalla | Alta | Evidente refuso ortografico per "stalla" in un commento telegrafico [7]. |
| **trentunenne** | 3 (Typo) | trentingrana | Alta | Evidente correzione automatica (autocorrect) per "trentingrana" nel commento "troppo strano per essere trentunenne" [16]. |
| **emmethal** | 3 (Typo) | emmenthal | Alta | Errore ortografico per indicare il formaggio di paragone [17]. |
| **ossiadto** | 3 (Typo) | ossidato | Alta | Inversione di lettere [18]. |
| **fermantato** | 3 (Typo) | fermentato | Alta | Errore di battitura [19]. |
| **positicva** | 3 (Typo) | positiva | Alta | Errore di digitazione sulla tastiera [20]. |
| **2** ("le altre 2 no") | 4 (Espressione quantitativa) | muffa disomogenea (difetto localizzato) | Alta | Punteggio 2018 associato: **5,98** (Seduta 16, campione C0G, panelista Q_02). Si riferisce a porzioni di assaggio ("una porzione ha un aroma di muffa mentre le altre 2 no") [21]. |
| **1 punto** ("Abbassarsi il voto di 1 punto") | 4 (Espressione quantitativa) | penalizzazione grave per atipicità | Media | Trovato nel file 2021 (Seduta 17, campione C0A, panelista TG_04) [16]. Non è presente un punteggio corrispondente nel file 2018 per questo esatto commento. |
| **mezzo punto** ("abbasso di mezzo punto il voto") | 4 (Espressione quantitativa) | penalizzazione lieve per difetto | Media | Trovato nel file 2021 (Seduta 21, campione C0E, panelista TG_04) [22]. Non presente nel file 2018. |
| **Gorgonzola / Disgustoso** vs **Punteggio eccellente** | 5 (Contraddizione) | Non normalizzabile (mantenere le varianti) | Alta | 2018 (Seduta 8, campione C0B): il panelista TG_24 sente "gorgonzola... disgustoso" con voto **4,42**, mentre TG_19 dà un voto di **8,68** e TG_12 di **8,50** [3]. |
| **Marcio / Animale** vs **Note di vertice** | 5 (Contraddizione) | Non normalizzabile | Alta | 2018 (Seduta 6, campione C0F): TG_19 sente "animale, marcio" (voto **4,24**) mentre TG_12 assegna **9,34** [23]. |
| **Putrido / Marcio** vs **Relativamente Intenso** | 5 (Contraddizione) | Non normalizzabile | Alta | 2018 (Seduta 18, campione C0N): TG_20 sente "a tratti putrido, marcio" (**5,02**) mentre TG_04 trova un buon aroma di crosta valutandolo **7,90** [24]. |

---

## Query 4 — Dubbi per revisione umana

Ecco l'elenco esaustivo dei casi ambigui identificati nell'analisi della colonna "Aroma", per i quali è richiesta una decisione umana ai fini della normalizzazione:

---
**DUBBIO 1:** "Sangue,,,"
- **Perché è ambiguo:** Il termine "sangue" è anomalo per il formaggio. Può indicare una percezione ferrosa/ruggine dovuta a contaminazione, oppure un sentore di carne cruda legato a note animali.
- **Opzione A:** Metallico / Difetto chimico.
- **Opzione B:** Animale / Carne cruda.
- **Suggerimento NotebookLM:** Preferire l'Opzione A (Metallico). Nell'analisi sensoriale, il sangue è il descrittore principe per il sapore/aroma di ferro. Lo stesso panelista (TG_24) usa il termine "metallico" in altre sedute [1].
- **Dati a supporto:** Trovato nel file 2021 (Sedute 16 e 22, campioni C0Q e C0C, panelista TG_24) [1].

---
**DUBBIO 2:** "Armadio della nonna"
- **Perché è ambiguo:** È una metafora evocativa che non fa parte del vocabolario sensoriale codificato. Indica qualcosa di chiuso, polveroso o vecchio.
- **Opzione A:** Ossidato / Stantio (riferimento all'età e alla cattiva conservazione).
- **Opzione B:** Polvere / Muffa (riferimento all'ambiente chiuso).
- **Suggerimento NotebookLM:** Preferire l'Opzione A. Nel gergo dei panelisti, concetti come "vecchio" o "passato" sono spesso usati per descrivere l'ossidazione della pasta [2, 3].
- **Dati a supporto:** Trovato nel 2020 (Seduta 5, campione C0Q, panelista TG_20): "Pessimo all'aroma, armadio della nonna" [4].

---
**DUBBIO 3:** "Pratomagno"
- **Perché è ambiguo:** "Pratomagno" è un nome proprio (un massiccio montuoso toscano, noto anche per un consorzio di Prosciutto). Se inteso come "grande prato" indica erba; se inteso come "prosciutto" indica carne/brodo.
- **Opzione A:** Fieno / Erbaceo (derivato da "prato").
- **Opzione B:** Brodo / Carne stagionata (se il riferimento è al prosciutto).
- **Suggerimento NotebookLM:** Preferire l'Opzione A. L'erbaceo/fieno è un attributo comune ("erba", "fieno") e potrebbe essere un'iperbole del panelista per descrivere un forte sentore vegetale [5, 6].
- **Dati a supporto:** Trovato nel 2021 (Seduta 18, campione C0E, panelista TG_14) [1].

---
**DUBBIO 4:** "Vinavil"
- **Perché è ambiguo:** Riferimento a una specifica marca di colla (PVA). L'odore della colla vinilica può indicare un inquinamento chimico, ma in alcuni formaggi difettati gli acidi della fermentazione atipica ricordano proprio la colla/plastica.
- **Opzione A:** Difetto chimico / Solvente.
- **Opzione B:** Fermentato / Acido.
- **Suggerimento NotebookLM:** Preferire l'Opzione A. "Vinavil" è troppo specifico e artificiale; classificarlo come semplice "fermentato" farebbe perdere l'informazione sulla grave anomalia (possibile contaminazione o difetto enzimatico grave).
- **Dati a supporto:** Trovato nel 2021 (Seduta 18, campione C0N, panelista TG_14) [1].

---
**DUBBIO 5:** "Bitter"
- **Perché è ambiguo:** "Bitter" in inglese significa "amaro" (che è un sapore di base, non un aroma). Se inteso come la bevanda (es. Campari/bitter), indica un aroma di radici e spezie.
- **Opzione A:** Erbe amare / Vegetale (riferimento botanico retrolfattivo).
- **Opzione B:** Errore di compilazione (il panelista voleva indicare il Sapore amaro).
- **Suggerimento NotebookLM:** Preferire l'Opzione A. Molti panelisti usano l'espressione "erbe amare" nell'aroma [6, 7]. Assimilarlo a "erbe amare" salva l'informazione olfattiva.
- **Dati a supporto:** Trovato nel 2021 (Seduta 21, campione C0I, panelista TG_24) [1].

---
**DUBBIO 6:** "Zafferano"
- **Perché è ambiguo:** Lo zafferano è una spezia con un marcatore aromatico inconfondibile, del tutto atipico per il Grana Trentino.
- **Opzione A:** Fieno / Floreale (evoluzione anomala di note vegetali o fiorite).
- **Opzione B:** Mantenere invariato come "Atipico / Speziato".
- **Suggerimento NotebookLM:** Preferire l'Opzione B. Lo zafferano ha molecole troppo specifiche (safranale) per essere assorbito nel generico "fieno". Indica una decisa anomalia del latte o della lavorazione.
- **Dati a supporto:** Trovato nel 2020 (Seduta 5, campione C0Q, panelista Q_09) [4].

---
**DUBBIO 7:** "Acqua di fogna"
- **Perché è ambiguo:** Descrive materia organica in decomposizione e liquami. Si colloca al confine tra due gravi famiglie di difetti.
- **Opzione A:** Putrido / Marcio.
- **Opzione B:** Animale / Stalla / Letame.
- **Suggerimento NotebookLM:** Preferire l'Opzione A (Putrido). Il panelista lo associa esplicitamente alla parola "marcio" nella stessa frase, indicando proteolisi estrema piuttosto che semplice odore di stalla.
- **Dati a supporto:** Trovato nel 2018 (Seduta 17, campione C0R, panelista TG_20): "pessimo, poco caratteristico, acqua di fogna, marcio" [8].

---
**DUBBIO 8:** "Vomitevole"
- **Perché è ambiguo:** Esprime massimo disgusto senza specificare l'aroma. Nel formaggio, questo rifiuto estremo è solitamente causato dall'acido butirrico (odore di vomito) o da batteri putrefattivi.
- **Opzione A:** Fermentato (riferimento implicito alla fermentazione butirrica).
- **Opzione B:** Putrido / Gravemente difettoso.
- **Suggerimento NotebookLM:** Preferire l'Opzione A. Sensorialmente, il descrittore "vomito" è universalmente associato all'acido butirrico (tipico difetto da insilati o clostridi nel formaggio).
- **Dati a supporto:** Trovato nel 2020 (Seduta 3, campione C0B, panelista TG_04): "Vomitevole" [9].

---
**DUBBIO 9:** "Formaggio con presunta struttura stirata"
- **Perché è ambiguo:** Il commento si trova nella colonna "Aroma", ma parla chiaramente di "struttura" e contiene la parola "stirata", che per regola di progetto è INVARIABILE e non normalizzabile [1, 10].
- **Opzione A:** Lasciare intatto nel dizionario Aroma (perché contiene "struttura" e "stirata" che sono termini tecnici caseari intoccabili).
- **Opzione B:** Classificare come "Fuori contesto" ed escluderlo dall'analisi Aroma (spostandolo all'analisi della Texture).
- **Suggerimento NotebookLM:** Preferire l'Opzione B ai fini dell'aroma, avvisando però il data manager. Se va mantenuto qui per vincoli di tabella, usare l'Opzione A e lasciarlo letteralmente intatto.
- **Dati a supporto:** Trovato nel 2021 (Seduta 30, campione C0M, panelista Q_02) [1].

---

## Istruzioni per la revisione umana

1. Leggi ogni sezione e valida / correggi le proposte di normalizzazione
2. Risolvi ogni dubbio in Query 4 scegliendo Opzione A, B o altra
3. Per Spessore della Crosta: confronta soglie script vs analisi NBLM e scegli i range definitivi
4. Salva le decisioni finali in: `data/interim/vocabolari_validati_per_attributo/Aroma_vocabolario.json`
5. Usa come template: `docs/template_vocabolario_validato.json` (generato da questo script)
