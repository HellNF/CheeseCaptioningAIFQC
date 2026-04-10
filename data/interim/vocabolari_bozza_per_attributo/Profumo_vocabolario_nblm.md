# Vocabolario Bozza — Profumo

**Generato:** 2026-04-09 20:36
**Notebook NotebookLM:** `caf696ac-d6ba-4edc-a365-757fe5744d5e`
**Stato:** BOZZA — richiede revisione umana prima di procedere con script 09

---

## Orientamento iniziale NotebookLM

Ho letto il documento "Contesto Analisi" relativo al progetto sull'attributo sensoriale "Profumo" del formaggio TrentinGrana [1]. 

Ecco le conferme che hai richiesto:

*   **Fonti CSV:** Delle 8 fonti totali caricate, **7 sono file in formato CSV** contenenti i dati originali e le medie (l'ottava fonte è il documento di testo Markdown con le istruzioni di contesto).
*   **Range temporale:** I dati raccolti dalle sessioni di valutazione sensoriale coprono un periodo che va dal **2018 al 2021** [1].
*   **Colonna da analizzare:** Il testo libero redatto dai valutatori durante la degustazione si trova all'interno della colonna **"Commenti"**; questa è la colonna specifica su cui effettuare l'analisi [2].

---

## Query 1 — Inventario termini

Di seguito trovi la tabella completa e ordinata per frequenza decrescente di tutti i termini e le espressioni distinte utilizzate dai panelisti per descrivere l'attributo "Profumo". 

Per facilitare la tua attività di normalizzazione, ho raggruppato nella stessa riga i sinonimi diretti, le varianti ortografiche e le espressioni strettamente correlate (es. *brodo vegetale* / *verdura lessa*), mantenendo però distinte le sfumature specifiche. I termini rari, anomali o dialettali/colloquiali sono stati mantenuti isolati in fondo alla tabella, in quanto fondamentali per mappare le eccezioni del dizionario [1].

### Tabella delle Espressioni Sensoriali - Attributo "Profumo"

| Termine / Espressione | Occorrenze (stima) | Anni in cui compare | Esempio di frase completa |
| :--- | :--- | :--- | :--- |
| **Panna / Pannoso** | Alta (>70) | 2018-2021 | "Panna e burro fuso molto presenti, segue il tostatofruttato e il brodo di carne" [2]. |
| **Burro fuso / sciolto** | Alta (>60) | 2018-2021 | "netto, burro fuso, e burro" [3]. |
| **Latte cotto** | Alta (>50) | 2018-2021 | "panna, latte lievemente cotto, burro fresco," [4]. |
| **Animale / Stalla / Cuoio / Letame / Cavallo** | Alta (>45) | 2018-2021 | "una porzione ripsetto alle altre ha un profumo di animale" [3]. |
| **Fermentato / Frutta fermentata / Erba fermentata** | Alta (>40) | 2018-2021 | "Fermentato deciso, dolciastro, solo allo spezzarsi dei pezzi" [5, 6]. |
| **Tostato / Tostatura / Pane tostato** | Alta (>40) | 2018-2021 | "formaggio, fiore, leggera tostatura" [3]. |
| **Burro / Burro fresco / Burro crudo** | Alta (>40) | 2018-2021 | "burro, latte, tostato e nocciola" [3]. |
| **Brodo vegetale / Verdura lessa o cotta / Minestrone** | Alta (>35) | 2018-2021 | "sbilanciato sul vegetale e sul brodo di verdura" [7]. |
| **Crosta di formaggio / Crosta di grana** | Media (~30) | 2018-2021 | "latte cotto, crosta. Brodo vegetale" [6]. |
| **Fruttato / Frutta matura / Frutta esotica** | Media (~25) | 2018-2021 | "complesso, abbastanza caratteristico ma con note di frutta fermentata molto volatili" [3]. |
| **Ossidato / Rancido / Stantio** | Media (~25) | 2018-2021 | "sentore di ossidato" [6]. |
| **Vegetale / Erbaceo / Erba tagliata** | Media (~25) | 2018-2021 | "Erbaceo all'apertura, poi classici" [8]. |
| **Fieno** | Media (~20) | 2018-2021 | "grana, nocciola, fieno" [9]. |
| **Brodo di carne / Dado / Glutammato** | Media (~20) | 2018-2020 | "Dado, glutammato molto forte e spiacevole" [10]. |
| **Latte fresco / Latte crudo / Latte intero** | Media (~20) | 2018-2020 | "latte, panna, burro fresco crudo" [11]. |
| **Nocciola** | Media (~15) | 2018-2020 | "grana tipico, nocciola e burro" [12]. |
| **Bruciato / Strinato / Fumo / Affumicato** | Media (~15) | 2018-2021 | "Peccato per il fondo di bruciato" [13]. |
| **Caramello / Mou** | Media (~15) | 2018-2021 | "CARAMELLA MOU, LATTE COTTO" [7]. |
| **Pane / Lievito / Biscotto / Mollica** | Media (~15) | 2018-2020 | "PANE LIEVITO" [14]. |
| **Floreale / Fiori** | Media (~15) | 2018-2020 | "Su un plateau di sensazioni mature spicca una forte nota floreale, addirittura fruttata" [9]. |
| **Cavolfiore / Cavolo / Crauti** | Media (~15) | 2018-2021 | "Crauti acidi" [15]. |
| **Marcio / Putrido** | Media (~15) | 2018-2021 | "marcio, putrido, fermentato e marcito" [16]. |
| **Formaggio cotto** | Media (~15) | 2018-2021 | "leggero formaggio cotto e crosta" [17]. |
| **Latte acido / Panna acida / Yogurt** | Media (~15) | 2018-2021 | "latte acido, panna yogurt" [18]. |
| **Ananas / Frutta tropicale** | Bassa (~12) | 2018-2021 | "Ananas e caramella mu" [15]. |
| **Insilato / Mais** | Bassa (~12) | 2018-2021 | "insilato di mais dominante" [19]. |
| **Solvente / Acetone / Chimico / Alcol** | Bassa (~12) | 2018-2020 | "strano.. acetone, fiore e solvente" [19]. |
| **Pozzo (di scarico) / Acqua stagnante / Fogna** | Bassa (~10) | 2018-2021 | "poco pulito, note pungenti al naso, sentori di pozzo e acqua stagnante" [20]. |
| **Burro cotto** | Bassa (~10) | 2018-2021 | "burro cotto, crosta, latte cotto o uht" [8]. |
| **Cipolla (lessa / passata)** | Bassa (~8) | 2018-2021 | "cipolla, minestrone verdura" [21]. |
| **Gomma bruciata / Plastica / Vinilico** | Bassa (~8) | 2018-2021 | "Gomma bruciata più evidente all’apertura" [15]. |
| **Frutta secca** | Bassa (~8) | 2018 | "panna e latte fresco, sentore di frutta secca" [21]. |
| **Pezze sporche / Stracci sporchi / Teli sporchi** | Bassa (~8) | 2018-2020 | "iniziale diverso (teli sporco) poi vegetali e eun po cotto" [22]. |
| **Ammoniaca / Propionico** | Bassa (~8) | 2018-2019 | "Ammoniaca iniziale, un po' di stantio, crosta di grana" [23]. |
| **Erbe balsamiche / Eucalipto** | Bassa (~8) | 2018-2021 | "Balsamico eucalipto" [15]. |
| **Caffè** | Bassa (~8) | 2018-2021 | "Alito di caffè" [24]. |
| **Polvere / Polveroso / Terra / Roccia** | Bassa (~7) | 2018-2021 | "Polvere anche,,," [15]. |
| **Cacao / Cioccolato** | Bassa (~7) | 2018-2021 | "Caffè,cacao amaro" [25]. |
| **Liquirizia / Radice** | Bassa (~6) | 2018-2021 | "Liquirizia radice" [15]. |
| **Vaniglia** | Bassa (~6) | 2018-2021 | "Vaniglia all’apertura" [15]. |
| **Fungo / Tartufo** | Bassa (~6) | 2018-2021 | "Funghi freschi" [15]. |
| **Speziato / Pepe / Noce moscata** | Bassa (~5) | 2018 | "cotti molto, speziato tipo pepe, animale, polveroso, crosta vecchia" [2, 26]. |
| **Kiwi** | Bassa (~5) | 2018-2020 | "Elegante... Kiwi" [27]. |
| **Formaggio stagionato** | Molto Bassa (~4) | 2018 | "forte persistente formaggio stagionato...." [2]. |
| **Formaggio fuso** | Molto Bassa (~4) | 2018 | "intenso grana e formaggio fuso" [20]. |
| **Mela** | Molto Bassa (~4) | 2018 | "crosta, fruttato mela" [28]. |
| **Agrumi / Pompelmo / Limone ammuffito** | Molto Bassa (~4) | 2019-2021 | "Agrumato" [15]. |
| **Emmenthal / Sbrinz / Svizzera / Camembert** | Molto Bassa (~4) | 2018-2021 | "quasi una nota di emmental che pero' non considero nel pu nteggio" [4]. |
| **Miele** | Rara (~3) | 2018-2019 | "paana, burro, miele..." [4]. |
| **Sottobosco / Muschio** | Rara (~3) | 2018-2020 | "leggero sottobosco e tostato" [6]. |
| **Sedano** | Rara (~3) | 2018-2021 | "nota di sedano, brodo vegetale, latte caramellato" [16, 29]. |
| **Banana (verde)** | Rara (~2) | 2018-2021 | "Banana" [15]. |
| **Siero acido** | Rara (~2) | 2018 | "siero acido intensità medio alta" [30]. |
| **Latte UHT** | Rara (~2) | 2018 | "latte uht, burro fuso, panna, lieve tostatura" [31]. |
| **Grasso di prosciutto crudo** | Rara (~2) | 2020 | "Sa di grasso di prosciutto crudo" [32]. |
| **Cimice / Cetriolo** | Singola (1) | 2018 | "lieve nota ossidata di cetriolo / cimice, per il resto piuttosto piatto" [12]. |
| **Topo morto** | Singola (1) | 2018 | "frutta matura, pozzo di scarico, topo morto" [17]. |
| **Uovo sodo / Zolfo** | Singola (1) | 2019 | "Soprattutto uovo sodo, zolfo" [33]. |
| **Urina** | Singola (1) | 2020 | "Sentore di urina..." [13]. |
| **Pesce** | Singola (1) | 2020 | "Strano. A tratti sentiva di pesce. Perplesso" [13]. |
| **Suola di scarpe** | Singola (1) | 2019 | "Ho segnato cuoio ma in realtà ho sentito odore di suola di scarpe, o gomma" [24]. |
| **Salame invecchiato** | Singola (1) | 2019 | "Sentore di grasso animale ossidato (eg: salame invecchiato)" [24]. |
| **Buccia anguria** | Singola (1) | 2021 | "Odore vegetale strano …,buccia anguria?" [15]. |
| **Pomata** | Singola (1) | 2021 | "Pomata" [34]. |
| **Formaggino / Confetto** | Singola (1) | 2018, 2021 | "semplice, lattico di panna, nota di formaggino" [35]. |
| **Pecorino** | Singola (1) | 2020 | "Pecorino" [32]. |
| **Gorgonzola** | Singola (1) | 2019 | "Il gorgonzola é un dubbio, non penalizzo troppo" [24]. |
| **Taleggio** | Singola (1) | 2018 | "una botta di taleggio al primo olfatto....poi il nulla" [36]. |

*Nota: Come indicato nel documento di contesto [1, 37], la normalizzazione non deve sovrascrivere o rimuovere la terminologia tecnica legata all'analisi sensoriale del formaggio (es. "Nostrano", "Insilato"), che ho volutamente isolato ove avessero funzione descrittiva specifica nel profumo, né uniformare sotto "difetto" le specificità (es. topo morto, gomma bruciata), che permettono una discriminazione molto utile a livello statistico.*

---

## Query 2 — Cluster semantici

**Cluster: Lattico Fresco**
- Varianti trovate nei dati: panna, pannoso, burro, burro fresco, burro crudo, latte fresco, latte crudo, latte intero [1-4].
- Forma canonica proposta: Panna / Burro fresco
- Motivazione della scelta: Identifica i profumi lattici dolci originari, non alterati dal calore, che rappresentano i descrittori primari e positivi del formaggio.
- Frequenza stimata del cluster: ~130

**Cluster: Lattico Cotto**
- Varianti trovate nei dati: burro fuso, burro sciolto, burro cotto, latte cotto, formaggio cotto, formaggio fuso, latte caramellato, latte UHT, formaggino, confetto [1, 2, 5-7].
- Forma canonica proposta: Latte cotto / Burro fuso
- Motivazione della scelta: Raggruppa tutte le sensazioni lattiche che hanno subito una trasformazione termica (Maillard leggera), altamente tipiche per un formaggio a pasta cotta.
- Frequenza stimata del cluster: ~130

**Cluster: Lattico Acido / Yogurt**
- Varianti trovate nei dati: latte acido, panna acida, yogurt, kefir, siero acido [8-11].
- Forma canonica proposta: Latte acido / Yogurt
- Motivazione della scelta: Separa le note lattiche caratterizzate da una marcata acidità e fermentazione lattica, utili per mappare deviazioni o specifiche caratteristiche fermentative.
- Frequenza stimata del cluster: ~17

**Cluster: Fruttato**
- Varianti trovate nei dati: fruttato, frutta matura, frutta esotica, frutta tropicale, ananas, kiwi, mela, banana, agrumi, pompelmo, buccia anguria, limone ammuffito [12-17].
- Forma canonica proposta: Fruttato / Frutta fresca
- Motivazione della scelta: Accorpa l'ampio spettro di descrittori legati alla frutta (fresca o esotica), unificando le singole tipologie usate dai panelisti per indicare esteri fruttati.
- Frequenza stimata del cluster: ~55

**Cluster: Tostato e Frutta Secca**
- Varianti trovate nei dati: tostato, tostatura, pane tostato, pane, lievito, biscotto, mollica, nocciola, frutta secca [1, 2, 16, 18].
- Forma canonica proposta: Tostato / Frutta secca
- Motivazione della scelta: Unisce le note derivanti dalla stagionatura e dalle reazioni di Maillard (crosta del pane, nocciola), tipiche del profilo aromatico del prodotto.
- Frequenza stimata del cluster: ~80

**Cluster: Note Dolci e Scure**
- Varianti trovate nei dati: caramello, mou, vaniglia, miele, caffè, cacao, cioccolato, liquirizia, radice [6, 8, 19-21].
- Forma canonica proposta: Caramello / Tostato scuro
- Motivazione della scelta: Raggruppa le sensazioni olfattive legate alla dolcezza (vaniglia/mou) e alle tostature più intense o speziate (cacao/caffè/liquirizia).
- Frequenza stimata del cluster: ~45

**Cluster: Brodo Vegetale e Verdura Cotta**
- Varianti trovate nei dati: brodo vegetale, verdura lessa, verdura cotta, minestrone, cipolla, cavolfiore, cavolo, crauti, sedano [3, 22-25].
- Forma canonica proposta: Brodo vegetale / Verdura cotta
- Motivazione della scelta: Distingue nettamente le note vegetali che hanno subito cottura (spesso associate ad un leggero difetto o a una fase evolutiva) dal vegetale fresco.
- Frequenza stimata del cluster: ~61

**Cluster: Vegetale Fresco ed Erbaceo**
- Varianti trovate nei dati: vegetale, erbaceo, erba tagliata, fieno, erbe balsamiche, eucalipto [9, 12, 19, 26, 27].
- Forma canonica proposta: Erbaceo / Fieno
- Motivazione della scelta: Riunisce gli aromi legati all'alimentazione bovina, al foraggio fresco ed essiccato, e alle note balsamiche volatili.
- Frequenza stimata del cluster: ~53

**Cluster: Floreale**
- Varianti trovate nei dati: floreale, fiori [23, 28, 29].
- Forma canonica proposta: Floreale
- Motivazione della scelta: Isola il descrittore dei fiori, che in analisi sensoriale indica una famiglia olfattiva a sé stante rispetto al fruttato.
- Frequenza stimata del cluster: ~15

**Cluster: Umami e Carne**
- Varianti trovate nei dati: brodo di carne, dado, glutammato, grasso di prosciutto crudo, salame invecchiato [1, 2, 5, 19, 21].
- Forma canonica proposta: Brodo di carne
- Motivazione della scelta: Raggruppa i sentori sapidi e proteici legati alla proteolisi avanzata (umami/dado).
- Frequenza stimata del cluster: ~23

**Cluster: Animale e Stalla**
- Varianti trovate nei dati: animale, stalla, cuoio, letame, cavallo [1, 17, 24, 30, 31].
- Forma canonica proposta: Animale / Stalla
- Motivazione della scelta: Unifica i difetti olfattivi legati all'ambiente di mungitura o a specifiche fermentazioni non desiderate.
- Frequenza stimata del cluster: ~45

**Cluster: Fermentato e Ossidato**
- Varianti trovate nei dati: fermentato, frutta fermentata, erba fermentata, ossidato, rancido, stantio [5, 12, 32, 33].
- Forma canonica proposta: Fermentato / Ossidato
- Motivazione della scelta: Raggruppa le alterazioni evolutive legate all'esposizione all'aria, invecchiamento o fermentazioni atipiche (non putride).
- Frequenza stimata del cluster: ~65

**Cluster: Putrido e Acqua Stagnante**
- Varianti trovate nei dati: marcio, putrido, marcito, pozzo di scarico, acqua stagnante, fogna, topo morto, pesce, urina [12, 23, 24, 30, 34].
- Forma canonica proposta: Putrido / Acqua stagnante
- Motivazione della scelta: Accorpa i difetti olfattivi più gravi (off-flavors), causati da batteri proteolitici anomali o contaminazioni.
- Frequenza stimata del cluster: ~28

**Cluster: Chimico e Bruciato**
- Varianti trovate nei dati: bruciato, strinato, fumo, affumicato, solvente, acetone, chimico, alcol, gomma bruciata, plastica, vinilico, suola di scarpe, pomata, zolfo, uovo sodo, ammoniaca, propionico [8, 9, 19, 21, 24, 32].
- Forma canonica proposta: Chimico / Bruciato
- Motivazione della scelta: Riunisce odori pungenti, artificiali o derivanti da difetti tecnici di lavorazione (eccesso di calore o contaminanti).
- Frequenza stimata del cluster: ~45

**Cluster: Terra, Umidità e Sporco**
- Varianti trovate nei dati: polvere, polveroso, terra, roccia, pezze sporche, stracci sporchi, teli sporchi, sottobosco, muschio, fungo, tartufo [12, 17, 19, 32, 35].
- Forma canonica proposta: Terra / Umidità / Sporco
- Motivazione della scelta: Raggruppa i difetti legati all'ambiente di cantina, alle muffe e alla gestione non ottimale dei teli/attrezzature.
- Frequenza stimata del cluster: ~24

**Cluster: Crosta di Formaggio**
- Varianti trovate nei dati: crosta di formaggio, crosta di grana, crosta [5, 9, 22].
- Forma canonica proposta: Crosta di formaggio
- Motivazione della scelta: Descrittore specifico e ricorrente per indicare il sentore esterno della forma, che i panelisti tengono distinto dalla pasta.
- Frequenza stimata del cluster: ~30

**Cluster: Formaggi Stagionati e Altri Formaggi**
- Varianti trovate nei dati: formaggio stagionato, emmenthal, sbrinz, svizzera, camembert, pecorino, gorgonzola, taleggio [8, 12, 36, 37].
- Forma canonica proposta: Formaggi stagionati / Altri formaggi
- Motivazione della scelta: Raggruppa le descrizioni per similitudine con altri prodotti caseari, indicando spesso una tipicità diversa dal Grana.
- Frequenza stimata del cluster: ~12

---

**Cluster: Termini Invariabili - Tipologia e Fermentazione**
- Varianti trovate nei dati: grana, nostrano, insilato [2, 9, 35, 36, 38].
- Forma canonica proposta: grana, nostrano, insilato
- Motivazione della scelta: Termini tecnici caseari INVARIABILI imposti da regola. Anche se usati per descrivere il profumo, devono mantenere la loro forma esatta.
- Frequenza stimata del cluster: ~45

**Cluster: Termini Invariabili - Struttura e Pasta**
- Varianti trovate nei dati: microocchiatura, occhiatura, frattura, stirata, cristalli, tirosina [12].
- Forma canonica proposta: microocchiatura, occhiatura, frattura, stirata, cristalli, tirosina
- Motivazione della scelta: Vocabolario tecnico strutturale INVARIABILE da mantenere intatto, utile per mappare quando un odore viene percepito in specifici momenti (es. "alla frattura").
- Frequenza stimata del cluster: >5

**Cluster: Termini Invariabili - Morfologia Esterna**
- Varianti trovate nei dati: scalzo, scalzi, piatti, piatto, sottocrosta, angoli, spigoli [39].
- Forma canonica proposta: scalzo, scalzi, piatti, piatto, sottocrosta, angoli, spigoli
- Motivazione della scelta: Descrittori tecnici morfologici della forma, INVARIABILI per regola di normalizzazione.
- Frequenza stimata del cluster: 0 (Non applicabili direttamente all'olfatto, ma inseriti per rigidità della regola).

**Cluster: Termini Invariabili - Reologia e Consistenza**
- Varianti trovate nei dati: solubile, solubilità, friabile, friabilità, compatto, compattezza, cedevole [39].
- Forma canonica proposta: solubile, solubilità, friabile, friabilità, compatto, compattezza, cedevole
- Motivazione della scelta: Termini tecnici tattili e masticatori, imposti come INVARIABILI dalla regola principale.
- Frequenza stimata del cluster: 0 (Propri di altri attributi sensoriali, mantenuti intatti a fini di dizionario globale).

---

## Query 3 — Anomalie e termini quantitativi

Ecco i casi che richiedono una normalizzazione speciale per l'attributo "Profumo", estratti dalle fonti fornite e classificati secondo le tue direttive:

| Termine trovato | Tipo (1–5) | Proposta di normalizzazione | Confidenza (alta/media/bassa) | Note |
| :--- | :--- | :--- | :--- | :--- |
| **leg** / **legg** / **leggerm** / **leggermete** | 1 (Abbreviazione) | leggermente (o leggero) | Alta | Abbreviazioni comunissime nei commenti veloci [1-6]. |
| **ins** | 1 (Abbreviazione) | insilato | Alta | Trovato in "ins mais" [4], che sta chiaramente per "insilato di mais". (Ricorda che "insilato" è termine invariabile). |
| **form.** | 1 (Abbreviazione) | formaggio | Alta | Usato per "form.fuso" [5]. |
| **veg** | 1 (Abbreviazione) | vegetale | Alta | Trovato in "cotto e brodo veg" [7]. |
| **strinato** | 2 (Dialettalismo) | bruciato | Alta | Termine regionale settentrionale che indica qualcosa di lievemente bruciato o eccessivamente tostato [2]. |
| **una botta di** (taleggio) | 2 (Colloquialismo) | intenso / forte | Alta | Espressione gergale per indicare un'intensità olfattiva molto elevata e improvvisa [8]. |
| **sa di puzzone** | 2 (Colloquialismo) | difetto fermentato (o Puzzone di Moena) | Media | Riferimento gergale al formaggio trentino "Puzzone", usato per indicare note fermentate o animali marcate [9]. |
| **come un presidente di Fondazione** | 2 (Colloquialismo) | impercettibile / inesistente | Alta | Battuta scherzosa di un panelista ("lievissimo, quasi inesistente, come un presidente di Fondazione") per indicare totale assenza di profumo [10]. |
| **paana** | 3 (Typo) | panna | Alta | Refuso di digitazione [1]. |
| **nanna** | 3 (Typo) | panna | Alta | Errore del correttore automatico o di battitura ("Tanta nanna e latte" o "Tanta nanna, ma nota di formaggio...") [9, 11]. |
| **congetto** | 3 (Typo) | confetto | Alta | Refuso in "brodo, congetto, lieve nota..." [12]. Il termine "confetto" o "confetteria" è usato correttamente in altre sedute dallo stesso panelista [13]. |
| **tostatofruttato** | 3 (Typo) | tostato fruttato | Alta | Mancanza di spazio tra due parole [2]. |
| **carcne** | 3 (Typo) | carne | Alta | Trovato in "brodo di carcne" [10]. |
| **sooidato** | 3 (Typo) | ossidato | Alta | Refuso di battitura [14]. |
| **verdora** / **probumo** | 3 (Typo) | verdura / profumo | Alta | Refusi di digitazione [15, 16]. |
| **3 su 4** (panna) / **in 1 pezzo** (marcio) | 4 (Quantitativo) | Campione disomogeneo (maggioranza panna / minoranza marcio) | Alta | Punteggio 2018 corrispondente: **5.98** (Seduta 11, Prod C0M, panelista TG_19) [17]. In profumo non ci sono mm/cm, ma i panelisti contano le porzioni fisiche ricevute nel piattino. |
| **una porzione su 4** (animale: letame) | 4 (Quantitativo) | Campione disomogeneo (difetto nel 25% dei pezzi) | Alta | Punteggio 2018 corrispondente: **5.98** (Seduta 18, Prod C0F, panelista Q_02) [18]. |
| **2 porzioni su 4** (odore negativo) | 4 (Quantitativo) | Campione disomogeneo (difetto nel 50% dei pezzi) | Alta | Punteggio 2018 corrispondente: **6.88** (Seduta 6, Prod C0E, panelista Q_02) [6]. |
| **Panna/burro fuso** (voto 9.16) VS **Marcio putrido** (voto 4.54) | 5 (Contraddizione) | Nessuna normalizzazione (anomalia del campione fisico) | Alta | Seduta 1 (2018), Prodotto C0I. Il panelista TG_35 sente aromi eccellenti [2], mentre TG_19 avverte "puzza di marcio putrido" [2]. Trattandosi di pezzi solidi, un valutatore ha quasi certamente ricevuto una porzione con un difetto locale gravissimo, assente negli altri pezzi dello stesso campione. |
| **Burro fuso/floreale** (voti ~8.8) VS **Putrido, tremendo** (voto 4.00) | 5 (Contraddizione) | Nessuna normalizzazione (anomalia del campione fisico) | Alta | Seduta 6 (2018), Prodotto C0F. I panelisti TG_08, TG_12, TG_04 danno voti tra 8.44 e 8.86 descrivendo note ottime [19], mentre TG_19 assegna un 4.00 netto descrivendolo "Putrido, trremendo" [19]. Identico caso di disomogeneità estrema della fetta originale. |

---

## Query 4 — Dubbi per revisione umana

---
**DUBBIO 1:** "Odore chimico tipo colpa o simili"
- **Perché è ambiguo:** Il termine "colpa" non ha alcun significato nel vocabolario sensoriale. Essendo associato all'aggettivo "chimico", è quasi certamente un errore di battitura o del correttore automatico.
- **Opzione A:** Considerarlo un refuso per "colla" (odore chimico di colla/solvente).
- **Opzione B:** Lasciare invariato "colpa" registrandolo come termine incomprensibile.
- **Suggerimento NotebookLM:** Preferirei l'Opzione A ("colla"). I panelisti usano spesso descrittori legati ai solventi (es. "plastica", "vinilico", "solvente acetone" [1-3]), e "colla" si adatta perfettamente alla descrizione di un odore chimico anomalo [4].
- **Dati a supporto:** Il commento è del panelista TG_19 nel 2021: "Odore chimico tipo colpa o simili" [4].

---
**DUBBIO 2:** "Tanta nanna e latte. Ben intenso"
- **Perché è ambiguo:** La parola "nanna" è chiaramente fuori contesto.
- **Opzione A:** Normalizzarlo come "panna" (errore di battitura "p" vs "n" sulla tastiera o correttore automatico).
- **Opzione B:** Ignorare il termine perché incerto.
- **Suggerimento NotebookLM:** Preferirei l'Opzione A. L'associazione logica "panna e latte" è una delle più frequenti nell'intero database per le descrizioni lattiche ad alta intensità.
- **Dati a supporto:** Commento del panelista TG_04: "Tanta nanna e latte. Ben intenso" [5].

---
**DUBBIO 3:** "congetto, lieve nota ossidata e pungente"
- **Perché è ambiguo:** "Congetto" è una parola inesistente in ambito alimentare/caseario.
- **Opzione A:** Normalizzarlo in "confetto" (nota lattica/dolce).
- **Opzione B:** Normalizzarlo in "cotto" (errore di battitura unito a latte/burro).
- **Suggerimento NotebookLM:** Preferirei l'Opzione A. Lo stesso panelista (TG_20) in un'altra seduta utilizza esplicitamente la dicitura "nota di confetto" e "confetteria" [6, 7].
- **Dati a supporto:** Commento di TG_20: "mediamente intenso, panna, burro fuso, brodo, congetto, lieve nota ossidata e pungente" [8].

---
**DUBBIO 4:** "nostrano" (usato per indicare un difetto o un'atipicità)
- **Perché è ambiguo:** Hai dato la regola rigida di mantenere "nostrano" come termine INVARIABILE. Tuttavia, i panelisti lo usano spesso non come semplice tipologia, ma per segnalare una chiara anomalia o deviazione dal profilo tipico del TrentinGrana.
- **Opzione A:** Mantenere "nostrano" senza ulteriori specifiche, seguendo la regola alla lettera.
- **Opzione B:** Normalizzarlo come "nostrano (difetto / atipico)" per non perdere l'intento negativo esplicito del valutatore.
- **Suggerimento NotebookLM:** Consiglierei l'Opzione B (o di fare un'eccezione alla regola), per preservare l'informazione statistica che in quella seduta il formaggio aveva un aroma difettato e non tipico.
- **Dati a supporto:** TG_04 afferma: "Prima olfazione non gradita. La definisco nostrano" [9] e "Sentore anomalo (nostrano)" [6]. TG_20 rileva: "note non caratteristiche da nostrano" [10] e "assoluntamente non caratteristico [...] formaggio nostrano" [11, 12].

---
**DUBBIO 5:** "cuoio" vs "stalla / letame"
- **Perché è ambiguo:** Nelle bozze precedenti abbiamo unito questi termini nel cluster "Animale / Stalla". Tuttavia, in analisi sensoriale, "cuoio" spesso indica una nota evoluta complessa e non penalizzante, mentre "letame/stalla" indica un difetto igienico o fermentativo grave.
- **Opzione A:** Lasciare "cuoio" nel cluster dei difetti animali ("Animale/Stalla").
- **Opzione B:** Separare "cuoio" spostandolo in un cluster di note tostate/evolute o creando un cluster "Animale (Evoluto)" distinto dai difetti.
- **Suggerimento NotebookLM:** Preferirei l'Opzione B. I panelisti spesso usano "cuoio" insieme a note calde o tostate, e in alcuni casi lo ritengono accettabile se non coprente.
- **Dati a supporto:** "una nota di cuoio su base di burro e panna" (TG_04) [13], "tostato, cuoio su base lattea" [14]. Al contrario, "letame" è associato a punteggi negativi: "animale: letame MODERATO" con punteggio olfattivo crollato a 5.98 [15].

---
**DUBBIO 6:** "Sentore di grasso animale ossidato (eg: salame invecchiato)" e "grasso di prosciutto crudo"
- **Perché è ambiguo:** Questi descrittori fanno riferimento a salumi e carni stagionate, ma portano con sé una chiara accezione di ossidazione lipidica.
- **Opzione A:** Raggrupparli nel cluster "Umami / Brodo di carne" in quanto derivati carnei.
- **Opzione B:** Raggrupparli nel cluster "Ossidato / Rancido" perché indicano un principio di degradazione dei grassi.
- **Suggerimento NotebookLM:** Preferirei l'Opzione B, in quanto il focus olfattivo del valutatore è sul "grasso ossidato" (difetto) e usa il salame/prosciutto solo come paragone esplicativo.
- **Dati a supporto:** TG_04 specifica "grasso animale ossidato" [16, 17] e TG_04 menziona "Grasso di prosciutto crudo" [18].

---
**DUBBIO 7:** "formaggio fritto"
- **Perché è ambiguo:** Diversi panelisti utilizzano questa espressione. Può indicare il sentore di formaggio scaldato alla piastra (reazione di Maillard) o un difetto di tostatura eccessiva (olio caldo/bruciato).
- **Opzione A:** Inserirlo nel cluster "Lattico Cotto / Burro fuso".
- **Opzione B:** Inserirlo nel cluster "Chimico / Bruciato / Strinato".
- **Suggerimento NotebookLM:** Preferirei l'Opzione A se i punteggi associati sono alti, ma i punteggi sono spesso altalenanti. Sarebbe saggio che un revisore umano valuti se per la giuria trentina "formaggio fritto" sia un difetto o una variante del formaggio cotto.
- **Dati a supporto:** Compare spesso: "formaggio fritto; e crosta di formaggio" [19], "formaggio fritto; bordo vegetale" [20], "latte cotto; formaggio fritto" [15]. 

---
**DUBBIO 8:** "leggermente propionico" / "lieve nota propionica"
- **Perché è ambiguo:** L'acido propionico dà il classico odore dolce/pungente tipico dell'Emmental, ma nel Grana è considerato un difetto fermentativo profondo.
- **Opzione A:** Inserirlo nel cluster "Formaggi stagionati / Altri formaggi" (vicino a Emmental/Svizzera).
- **Opzione B:** Inserirlo nel cluster "Chimico / Difetto" o "Fermentato" in virtù della sua natura tecnica di molecola.
- **Suggerimento NotebookLM:** Preferirei l'Opzione A (o creare un mapping specifico), perché i panelisti stessi spesso traducono "propionico" usando come sinonimo "emmenthal".
- **Dati a supporto:** "nota pungente all apertura e poi dolciastra, leggermente propionica" [21], "lieve nota propionica" [11, 22]. Altrove dicono "sa di emmental" [23].

---
**DUBBIO 9:** "crauti" / "salamoia crauti"
- **Perché è ambiguo:** Nel precedente raggruppamento è stato unito al "Brodo vegetale / cavolfiore / verdura cotta". Tuttavia, i crauti subiscono fermentazione lattica acida, quindi odorano molto diversamente dal minestrone o dalla verdura semplicemente lessata.
- **Opzione A:** Lasciarli in "Brodo vegetale / Verdura cotta".
- **Opzione B:** Spostarli nel cluster "Latte acido / Yogurt" (fermentazioni acide) o "Fermentato/Ossidato" (difetti).
- **Suggerimento NotebookLM:** Preferirei l'Opzione B. Il termine "crauti acidi" denota chiaramente una fermentazione pungente non riconducibile al semplice brodo vegetale dolce.
- **Dati a supporto:** TG_19: "Crauti acidi" [24], "Crauti" [24]. TG_14: "salamoia crauti" [25]. Q_02: "crauti MODERATO" con voto basso 6.52 [8].

---
**DUBBIO 10:** "balsamico liquirizia" e "erbe balsamiche"
- **Perché è ambiguo:** Il termine "balsamico" viene accoppiato a due mondi olfattivi diversi: quello fresco/vegetale ("erbe") e quello scuro/tostato dolce ("liquirizia").
- **Opzione A:** Spaccare le definizioni: "Erbe balsamiche" nel cluster Erbaceo, e "Liquirizia" nel cluster Caramello/Scuro.
- **Opzione B:** Creare un cluster "Balsamico" indipendente.
- **Suggerimento NotebookLM:** Preferirei l'Opzione A. Segue meglio la logica delle ruote degli aromi, dividendo la freschezza del vegetale dalle note speziate/dolci delle radici.
- **Dati a supporto:** Q_09 annota in una riga "Balsamico liquirizia" [26] e nella riga adiacente "Erbe Balsamiche" [24, 26]. TG_19 specifica "Liquirizia radice" [24].

Lascio al revisore umano la decisione finale su come gestire queste anomalie e raggruppamenti per il dizionario finale.

---

## Istruzioni per la revisione umana

1. Leggi ogni sezione e valida / correggi le proposte di normalizzazione
2. Risolvi ogni dubbio in Query 4 scegliendo Opzione A, B o altra
3. Per Spessore della Crosta: confronta soglie script vs analisi NBLM e scegli i range definitivi
4. Salva le decisioni finali in: `data/interim/vocabolari_validati_per_attributo/Profumo_vocabolario.json`
5. Usa come template: `docs/template_vocabolario_validato.json` (generato da questo script)
