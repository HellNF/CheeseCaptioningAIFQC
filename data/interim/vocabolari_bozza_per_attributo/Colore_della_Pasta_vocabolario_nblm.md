# Vocabolario Bozza — Colore della Pasta

**Generato:** 2026-04-09 21:10
**Notebook NotebookLM:** `9a5189f4-0ad6-4b99-8be4-5c23cc264590`
**Stato:** BOZZA — richiede revisione umana prima di procedere con script 09

---

## Orientamento iniziale NotebookLM

Ho letto il documento "Contesto Analisi" relativo al progetto sul formaggio Grana Trentino, il cui obiettivo è costruire un dizionario di normalizzazione per i termini sensoriali legati all'attributo "Colore della Pasta" [1, 2]. 

Ecco le conferme che hai richiesto:

*   **Fonti CSV:** Hai caricato esattamente **7 file CSV** che contengono i dati e i risultati delle valutazioni (l'ottava fonte è il file di testo con il contesto del progetto).
*   **Range temporale:** I dati raccolti coprono le sessioni di valutazione comprese tra il **2018 e il 2021** [1].
*   **Colonna da analizzare:** Le annotazioni scritte in testo libero dai panelisti durante la degustazione si trovano nella colonna **"Commenti"** [3].

---

## Query 1 — Inventario termini

Di seguito l'estrazione di tutti i termini e le espressioni distinte (compresi errori ortografici, termini tecnici, descrittori insoliti e dialettalismi) utilizzati dai panelisti per descrivere il "Colore della Pasta", ordinati per frequenza stimata decrescente.

| Termine / Espressione | Occorrenze (stima) | Anni in cui compare | Esempio di frase completa |
| :--- | :--- | :--- | :--- |
| **Carico / Carica** | > 150 | 2018-2021 | "Giallo carico omogeneo" [1]. |
| **Alone** | > 150 | 2018-2021 | "Alone centrale più scuro" [2]. |
| **Chiaro / Chiara** | > 150 | 2018-2021 | "Abbastanza omogeneo e chiARO" [2]. |
| **Omogeneo / Omogenea / Uniforme** | > 150 | 2018-2021 | "Colorazione omogenea su tutta la sezione" [3]. |
| **Giallo** | > 150 | 2018-2021 | "Giallo carico scuro" [2]. |
| **Centro / Centrale** | > 150 | 2018-2021 | "Giallo piu scuro al centro" [2]. |
| **Rosa / Rosato / Rosata** | > 100 | 2018-2021 | "Macchie rosa centrali" [2]. |
| **Paglierino** | > 100 | 2018-2021 | "Giallo paglierino omogeneo abbastanza carico" [2]. |
| **Scuro / Scura** | > 100 | 2018-2021 | "Striscia più scura in corrispondenza di un piatto" [2]. |
| **Piatto / Piatti** | > 100 | 2018-2021 | "Un piatto e più scuro" [4]. |
| **Macchia / Macchie / Macchioline** | > 80 | 2018-2021 | "Macchie arancio chiaro e rosate" [5]. |
| **Verso / Sotto / Vicino** | > 80 | 2018-2021 | "Più chiaro verso gli scalzi" [3]. |
| **Leggero / Lieve / Appena / Lievemente** | > 50 | 2018-2021 | "Leggero alone colore tendente chiaro" [2]. |
| **Non omogeneo / Disomogeneo / Disomogeneità** | > 40 | 2018-2021 | "Disomogeneo concentrarti al centro" [3]. |
| **Scalzo / Scalzi** | > 30 | 2018-2021 | "Più chiara agli scalzi per rosata" [2]. |
| **Grigio / Grigiastro / Grigetta** | > 30 | 2018-2021 | "Tendente al grigio" [2]. |
| **Fascia / Fasce** | > 30 | 2018-2021 | "Fascia più scura su un piatto" [6]. |
| **Arancio / Aranciato / Arancione** | > 20 | 2018-2021 | "Giallo piuttosto carico e aranciato" [5]. |
| **Nocciola** | > 20 | 2018-2021 | "Giallo medio carico tendente al nocciola" [4]. |
| **Verde / Verdastro / Verdognolo / Verdolino** | > 15 | 2018-2021 | "Zone verdastre sugli angoli" [6]. |
| **Zona / Zone / Area / Aree** | > 15 | 2018-2021 | "A zone paglierino." [3]. |
| **Sfumatura / Sfumato / Sfumature** | > 15 | 2018-2021 | "Sfumatura rosa vicino a sottocrosta" [7]. |
| **Marrone / Bruno / Bruna** | > 10 | 2018-2021 | "Pasta dal colore bruno" [8]. |
| **Bianco / Biancastro / Candido** | > 10 | 2018-2021 | "1/4 della superficie di colore molto chiaro, quasi bianco" [9]. |
| **Striscia / Strisce / Striature** | > 10 | 2018-2021 | "Strisce rosa su alone centrale" [10]. |
| **Chiazza / Chiazze** | > 10 | 2018-2020 | "Base chiara ma disomogenea con chiazze più scure" [1]. |
| **Saturo** | > 10 | 2018-2021 | "Abbastanza omogeneo ma saturo verso il giallo" [11]. |
| **Bordo / Bordi / Esterno / Lateralmente** | > 10 | 2018-2021 | "Non omogeneo chiaro ai bordi" [3]. |
| **Sottocrosta / Sottoposta** | > 10 | 2018-2021 | "Omogenea tranne nel sottocrosta" [12]. |
| **Intenso / Marcato / Accentuato** | > 10 | 2018-2021 | "Giallo grigio intenso" [5]. |
| **Cristalli / Tirosina** | > 5 | 2018-2020 | "Omogenea presenza dicristalli bianchi evidenti" [11]. |
| **Rossastro / Rossiccio / Rosso** | > 5 | 2018, 2021 | "Area centrale rossastra..." [12]. |
| **Bello / Positivo** | > 5 | 2018-2020 | "Bello" [1]. |
| **Frattura / Strappo / Rottura / Fessura** | > 5 | 2018-2021 | "Alone centrale con fascia circolare che segue la frattura" [2]. |
| **Occhiatura / Microocchiatura / Occhio** | > 5 | 2018, 2020-2021 | "In corrispondenza dell'occhio con siero" [13]. |
| **Ossidato / Ossidazione / Ossidatura** | > 3 | 2020-2021 | "Carico quasi ossidato con due macchie rosa" [14]. |
| **Disidratato / Disidratata** | > 3 | 2019-2021 | "Pasta disidratata sotto crosta" [15]. |
| **Scarico** | > 3 | 2018-2019 | "Omogeneo e scarico. Bello" [16]. |
| **Spugna / Spugnosa** | > 3 | 2018, 2020 | "Chiaro, ma leggeremacchie rosa dove c è laspugna" [17]. |
| **Salmone / Salmonato** | > 3 | 2021 | "Alone color salmone" [18]. |
| **Gessato** | 2 | 2018, 2020 | "A parte le zone gessate, omogeneo e bello " [19]. |
| **Non tipico / Anomalo** | 2 | 2018 | "Colore chiaro uniforme ma con una tonalità non tipica" [19]. |
| **Difettoso / Difetto** | 2 | 2018 | "Struttura a tratti difettosa con stiratura" [5]. |
| **Bi color / 3colori** | 2 | 2018 | "Bi color. Al centro molto saturo" [20]. |
| **Risata / Rodata / Arrangiato** *(Refusi per rosata/aranciato)* | 3 | 2018 | "Netto alone ad anello rosato" [10] / "Colore carico on leggero alone" [21]. |
| **Chuaro / Chiarimenti** *(Refusi per chiaro/chiari)* | 2 | 2018 | "Appena più chiarimenti scalzi" [22]. |
| **Hiroshima** *(Refuso o autocorrezione per Tirosina)* | 1 | 2018 | "Cristalli di Hiroshima bianchi omogeneamente diffusi" [23]. |
| **Cipria** | 1 | 2020 | "Bianco cipria" [24]. |
| **Pompelmo** | 1 | 2020 | "Alone centrale tendente al rosa pompelmo" [25]. |
| **Ambrato** | 1 | 2018 | "Omogeneamente paglierino carico ambrato" [26]. |
| **Dorato** | 1 | 2018 | "Dorato" [27]. |
| **Vergognose** *(Refuso per verdognole)* | 1 | 2018 | "Verso il giallo carico, con aree vergognose o nocciola carico" [28]. |
| **Imbrunito** | 1 | 2018 | "Sarebbe anche giallo paglierino ma presenta zona con alone imbrunito" [5]. |
| **Sganciato** | 1 | 2018 | "Chiara ma alone sganciato centrale" [1]. |
| **Pastoso** | 1 | 2021 | "Un aspetto bagnato pastoso" [29]. |
| **Bagnato** | 1 | 2021 | "Un aspetto bagnato pastoso" [29]. |
| **Muffa** | 1 | 2020 | "Grossa macchia di muffa" [24]. |
| **Puntini neri** | 1 | 2020 | "Zona con fitti puntini neri (muffa?)" [15]. |
| **Gonfalone** | 1 | 2018 | "Giallo gonfalone centrale" [12]. |
| **Eterogeneo** | 1 | 2018 | "Un po' eterogeneo, più carico al centro" [22]. |

---

## Query 2 — Cluster semantici

Basandomi sulle espressioni estratte e seguendo l'obiettivo di creare un dizionario di normalizzazione [1], ho raggruppato i termini in cluster semantici. Come richiesto, ho separato rigorosamente i termini tecnici caseari, che rimangono invariabili [2].

### Cluster di Normalizzazione Sensoriale

**Cluster: Tonalità Base (Paglierino)**
- Varianti trovate nei dati: giallo, paglierino, dorato, ambrato, gonfalone
- Forma canonica proposta: Giallo paglierino
- Motivazione della scelta: È il descrittore standard del settore per indicare il colore corretto del formaggio stagionato [3].
- Frequenza stimata del cluster: 253

**Cluster: Intensità Alta**
- Varianti trovate nei dati: carico, carica, saturo, intenso, marcato, accentuato
- Forma canonica proposta: Carico
- Motivazione della scelta: "Carico" è il termine di gran lunga più diffuso e immediato impiegato dai panelisti per descrivere l'alta saturazione cromatica [4].
- Frequenza stimata del cluster: 170

**Cluster: Intensità Bassa**
- Varianti trovate nei dati: chiaro, chiara, scarico, chuaro, chiarimenti
- Forma canonica proposta: Chiaro
- Motivazione della scelta: Termine più frequente e chiaro per denotare una colorazione poco intensa, assorbe anche errori di battitura tipici o abbreviazioni [1, 4].
- Frequenza stimata del cluster: 157

**Cluster: Assenza di Difetti (Uniformità)**
- Varianti trovate nei dati: omogeneo, omogenea, uniforme, bello, positivo
- Forma canonica proposta: Omogeneo
- Motivazione della scelta: Rappresenta il descrittore principe per confermare un colore regolare su tutta la sezione, privo di macchie [3, 4].
- Frequenza stimata del cluster: 155

**Cluster: Difetto Concentrico (Alonatura)**
- Varianti trovate nei dati: alone, sganciato
- Forma canonica proposta: Alone
- Motivazione della scelta: Identifica in modo standardizzato il difetto visivo tipico di un'area circolare irregolare (mentre "sganciato" è gergale) [1, 3].
- Frequenza stimata del cluster: 151

**Cluster: Localizzazione Centrale**
- Varianti trovate nei dati: centro, centrale
- Forma canonica proposta: Centrale
- Motivazione della scelta: È l'aggettivo di riferimento per ubicare visivamente un'anomalia nel cuore della forma [4].
- Frequenza stimata del cluster: 150

**Cluster: Tonalità Anomala (Rosata)**
- Varianti trovate nei dati: rosa, rosato, rosata, rossastro, rossiccio, rosso, salmone, salmonato, pompelmo, risata, rodata
- Forma canonica proposta: Rosato
- Motivazione della scelta: Termine univoco per indicare uno dei difetti cromatici più noti, aggregando tutte le sfumature vicine al rosso e i vari refusi [1, 3].
- Frequenza stimata del cluster: 112

**Cluster: Tonalità Anomala (Scura)**
- Varianti trovate nei dati: scuro, scura, marrone, bruno, bruna, imbrunito
- Forma canonica proposta: Scuro
- Motivazione della scelta: Riunisce le descrizioni di imbrunimento non conforme al range cromatico atteso [3].
- Frequenza stimata del cluster: 111

**Cluster: Maculatura**
- Varianti trovate nei dati: macchia, macchie, macchioline, chiazza, chiazze, puntini neri
- Forma canonica proposta: Macchiato
- Motivazione della scelta: Standardizza le alterazioni localizzate a "spot", distinguendole nettamente dalle alterazioni circolari (alone) o lineari [1, 4].
- Frequenza stimata del cluster: 91

**Cluster: Localizzazione Periferica / Gradiente**
- Varianti trovate nei dati: verso, sotto, vicino, bordo, bordi, esterno, lateralmente
- Forma canonica proposta: Esterno
- Motivazione della scelta: Sintetizza le indicazioni posizionali che si allontanano dal centro per spostarsi verso i lati o le facce esterne [3, 4].
- Frequenza stimata del cluster: 90

**Cluster: Gradazione Lieve**
- Varianti trovate nei dati: leggero, lieve, appena, lievemente, sfumatura, sfumato, sfumature
- Forma canonica proposta: Lieve
- Motivazione della scelta: Modificatore di intensità essenziale per codificare quei difetti cromatici appena percettibili [1, 4].
- Frequenza stimata del cluster: 65

**Cluster: Disomogeneità Generale**
- Varianti trovate nei dati: non omogeneo, disomogeneo, disomogeneità, eterogeneo, bi color, 3colori, zona, zone, area, aree
- Forma canonica proposta: Disomogeneo
- Motivazione della scelta: Traduce i molti modi colloquiali con cui i giudici segnalano la presenza di variazioni disordinate di colore [1, 3].
- Frequenza stimata del cluster: 58

**Cluster: Tonalità Anomala (Verde-Grigia)**
- Varianti trovate nei dati: grigio, grigiastro, grigetta, verde, verdastro, verdognolo, verdolino, vergognose
- Forma canonica proposta: Grigio-Verdastro
- Motivazione della scelta: Raggruppa i viraggi di tonalità verso lo spettro freddo/grigio, citati chiaramente tra i difetti [3].
- Frequenza stimata del cluster: 46

**Cluster: Tonalità Anomala (Calda/Ossidata)**
- Varianti trovate nei dati: arancio, aranciato, arancione, arrangiato, nocciola
- Forma canonica proposta: Aranciato/Nocciola
- Motivazione della scelta: Raccoglie deviazioni cromatiche troppo calde o intense, assimilabili ad ossidazione del colore [1].
- Frequenza stimata del cluster: 43

**Cluster: Distribuzione Lineare**
- Varianti trovate nei dati: fascia, fasce, striscia, strisce, striature
- Forma canonica proposta: A strisce
- Motivazione della scelta: Utile per tracciare un difetto distribuito in bande nette (spesso parallele ai piatti) anziché a macchia [1].
- Frequenza stimata del cluster: 40

**Cluster: Tonalità Anomala (Estrema Pallidezza)**
- Varianti trovate nei dati: bianco, biancastro, candido, cipria
- Forma canonica proposta: Bianco
- Motivazione della scelta: Identifica una tonalità insufficientemente sviluppata rispetto al giallo atteso o segnali di demineralizzazione [1, 3].
- Frequenza stimata del cluster: 11

**Cluster: Alterazioni Cromatiche da Struttura**
- Varianti trovate nei dati: ossidato, ossidazione, ossidatura, disidratato, disidratata, spugna, spugnosa, gessato, bagnato, pastoso, muffa, difettoso
- Forma canonica proposta: Anomalo per difetto strutturale
- Motivazione della scelta: Accorpa le rare annotazioni dove il colore anomalo è solo un riflesso di una marcata degradazione fisica o biologica della pasta [3].
- Frequenza stimata del cluster: 18

***

### CLUSTER INVARIABILI (Termini Tecnici Caseari)
*Questi termini possiedono un significato tecnico preciso nella caseificazione e per regola rigorosa **non sono stati normalizzati** o sostituiti con sinonimi generici [2].*

**Cluster: Piatto / Piatti**
- Varianti trovate nei dati: piatto, piatti
- Forma canonica proposta: Piatto / Piatti
- Motivazione della scelta: Termine tecnico caseario INVARIABILE [2].
- Frequenza stimata del cluster: 100+

**Cluster: Scalzo / Scalzi**
- Varianti trovate nei dati: scalzo, scalzi
- Forma canonica proposta: Scalzo / Scalzi
- Motivazione della scelta: Termine tecnico caseario INVARIABILE [2].
- Frequenza stimata del cluster: 30+

**Cluster: Sottocrosta**
- Varianti trovate nei dati: sottocrosta, sottoposta (riflette un refuso evidente per sottocrosta)
- Forma canonica proposta: Sottocrosta
- Motivazione della scelta: Termine tecnico caseario INVARIABILE per indicare l'area sotto la crosta [2, 3].
- Frequenza stimata del cluster: 10+

**Cluster: Angoli**
- Varianti trovate nei dati: angoli
- Forma canonica proposta: Angoli
- Motivazione della scelta: Termine tecnico caseario INVARIABILE [2].
- Frequenza stimata del cluster: 2+

**Cluster: Frattura**
- Varianti trovate nei dati: frattura, rottura, strappo, fessura
- Forma canonica proposta: Frattura
- Motivazione della scelta: Termine tecnico caseario INVARIABILE [2] sotto il quale si raggruppano i concetti di strappi e fessure della pasta.
- Frequenza stimata del cluster: 5+

**Cluster: Occhiatura / Microocchiatura**
- Varianti trovate nei dati: occhiatura, microocchiatura, occhio
- Forma canonica proposta: Occhiatura / Microocchiatura
- Motivazione della scelta: Termine tecnico caseario INVARIABILE [2].
- Frequenza stimata del cluster: 5+

**Cluster: Cristalli / Tirosina**
- Varianti trovate nei dati: cristalli, tirosina, hiroshima (refuso da autocorrettore per tirosina)
- Forma canonica proposta: Cristalli / Tirosina
- Motivazione della scelta: Termine tecnico caseario INVARIABILE [2].
- Frequenza stimata del cluster: 6+

**Cluster: Stirata**
- Varianti trovate nei dati: stiratura
- Forma canonica proposta: Stirata
- Motivazione della scelta: Termine tecnico caseario INVARIABILE [2].
- Frequenza stimata del cluster: 2+

---

## Query 3 — Anomalie e termini quantitativi

| Termine trovato | Tipo (1–5) | Proposta di normalizzazione | Confidenza (alta/media/bassa) | Note |
| :--- | :--- | :--- | :--- | :--- |
| **"abb" / "abb."** | 1 | Abbastanza | Alta | Abbreviazione usata molto di frequente dai panelisti (es. "abb chiaro", "abb omogeneo") [1-3]. |
| **"legg." / "legg"** | 1 | Leggermente | Alta | Abbreviazione diffusa per indicare una sfumatura debole (es. "Legg alone") [4]. |
| **"unif" / "unif."** | 1 | Uniforme | Alta | Termine contratto scritto per velocità ("abbastanza unif") [5, 6]. |
| **"vs"** | 1 | Verso | Alta | Abbreviazione per indicare la direzione di un colore/difetto ("vs un piatto") [7, 8]. |
| **"sganciato"** | 2 | Netto / Evidente | Media | Termine gergale usato per descrivere un alone o una macchia molto marcati ("alone sganciato") [9-11]. |
| **"gonfalone"** | 2 | Alone centrale ampio | Bassa | Probabile espressione colloquiale o dialettale usata per indicare un grosso alone al centro del formaggio [12]. |
| **"Bi color" / "3colori"** | 2 | Disomogeneo a fasce | Alta | Espressioni informali per descrivere una netta disomogeneità cromatica [13-15]. |
| **"pochetto"** | 2 | Leggermente | Alta | Espressione colloquiale ("Pochetto disomogenea") [16]. |
| **"hiroshima"** | 3 | Tirosina | Alta | Evidente correzione automatica del tablet/smartphone (es. "Cristalli di Hiroshima bianchi") [17]. |
| **"risata" / "rodata"** | 3 | Rosata | Alta | Errore di battitura estremamente ricorrente per "rosata" (es. "sfumatura risata", "macchia rodata") [9, 10, 18, 19]. |
| **"vergognose"** | 3 | Verdognole | Alta | Errore del correttore ortografico ("aree vergognose o nocciola") [20]. |
| **"L'amore"** | 3 | L'alone | Alta | Correzione automatica in un commento del 2020: "L'amore è spostato verso uno dei due piatti" [21]. |
| **"Acconciatura"** | 3 | Occhiatura | Alta | Errore ortografico causato dal correttore ("Acconciatura presente solo su un lato") [16]. |
| **"arrangiato" / "tranciato"** | 3 | Aranciato | Alta | Typo per "aranciato" in vari commenti ("Chiaro arrangiato", "Tranciato con alone") [18, 22]. |
| **"sottoposta" / "sottoposto"** | 3 | Sottocrosta | Alta | Errore di inserimento ricorrente ("Il sottoposta di una faccia è più chiaro") [2, 9, 17]. |
| **"1/4 della superficie"** | 4 | Area anomala estesa | Alta | Punteggio 2018 associato: **6.8** (C0A, Seduta 5). L'anomalia cromatica copre molta superficie visibile [13]. |
| **"5 cm disputati"** | 4 | Fascia profonda | Media | Punteggio 2018 associato: **6.6** (C0D, Seduta 4). ("Disputati" è un typo, probabilmente per "dai piatti") [23]. |
| **"circa 1mm"** | 4 | Difetto marginale | Alta | Punteggio 2018 associato: **7.0** (C0E, Seduta 6). Misura riferita a un difetto lieve/superficiale [16]. |
| **"almeno 6mm"** | 4 | Occhiatura grande | Alta | Punteggio 2018 associato: **7.5** (C0F, Seduta 6). Dimensione riferita alla struttura ma annotata nel colore [17]. |
| **"di 10 15 cm"** | 4 | Macchia estesa | Alta | Punteggio 2018 associato: **5.5** (C0M, Seduta 17). Estensione misurata di una "chiazza allungata rodata" [10]. |
| **"3,5cm" e "4 cm"** | 4 | Frattura evidente | Alta | Punteggi 2018 associati: **9.1** e **8.1** (C0I e C0M, Seduta 11). Quantifica un difetto di struttura segnalato qui ma che non penalizza pesantemente il colore [24, 25]. |
| **Opposti su C0O (Seduta 5, 2018)** | 5 | Verifica anomalia panel | Alta | Il panelista Q_02 valuta **5.0** annotando "Alone centrale Macchie rosa", mentre TG_24 valuta **8.9** indicando "Giallo chiaro piuttosto omogeneo" [26, 27]. |
| **Opposti su C0R (Seduta 3, 2018)** | 5 | Verifica anomalia panel | Alta | Il panelista TG_05 valuta **8.5** con "Omogeneo", mentre TG_13 valuta **5.8** definendolo "Colore giallo carico a macchie, negativo" [1, 28]. |
| **Opposti su C0D (Seduta 1, 2018)** | 5 | Verifica anomalia panel | Alta | Il panelista TG_04 dà **6.9** per "Colorazione omogenea su tutta la sezione", ma Q_02 dà **8.5** (con voto paradossalmente più alto) per "Disomogeneo concentrarti al centro" [29]. |

---

## Query 4 — Dubbi per revisione umana

Di seguito l'elenco esaustivo dei casi ambigui in cui i panelisti hanno utilizzato termini anomali, errori di battitura o espressioni gergali per cui non è possibile stabilire una normalizzazione certa al 100% senza un intervento umano.

---
**DUBBIO 1:** "Giallo gonfalone centrale"
- **Perché è ambiguo:** "Gonfalone" non è un termine descrittivo standard per l'analisi sensoriale del formaggio. Può indicare una forma o un colore specifico.
- **Opzione A:** "Alone ampio/evidente" (inteso come una macchia grande e visibile come una bandiera/gonfalone).
- **Opzione B:** "Giallo dorato/intenso" (riferito alla tonalità giallo acceso tipica di alcuni stendardi locali).
- **Suggerimento NotebookLM:** Preferirei l'Opzione A (Alone ampio/evidente), in quanto la parola è seguita da "centrale", aggettivo usato prevalentemente per descrivere la posizione dell'alone nel Grana [1].
- **Dati a supporto:** "Giallo gonfalone centrale" (Q_09, Seduta 3, 2018) [1].

---
**DUBBIO 2:** "sganciato" / "sganciato carico"
- **Perché è ambiguo:** Espressione gergale usata da più panelisti, ma con accezioni apparentemente opposte a seconda del contesto.
- **Opzione A:** "Netto / Evidente / Ben delimitato" (un difetto cromatico che "stacca" visivamente dal resto).
- **Opzione B:** "Scarico / Sbiadito" (un colore che ha "sganciato" saturazione).
- **Suggerimento NotebookLM:** Preferirei l'Opzione A. L'espressione "Sganciato carico" esclude che significhi sbiadito. Indica piuttosto una divisione cromatica netta.
- **Dati a supporto:** "Chiara ma alone sganciato centrale" [2], "Paglierino sganciato omogeneoamente distribuito" [3], "Sganciato carico" [4].

---
**DUBBIO 3:** "Immatricolata"
- **Perché è ambiguo:** Evidente errore di autocorrezione del tablet o smartphone durante la valutazione.
- **Opzione A:** "Incartatura" / "Marchiatura" (la placca/fascetta esterna sullo scalzo che può trasferire colore alla pasta).
- **Opzione B:** "Microocchiatura".
- **Suggerimento NotebookLM:** Preferirei l'Opzione A ("Incartatura/Marchiatura"). Il commento specifica che il colore rosato è "solo pochi cm dopo la crosta", suggerendo una migrazione di colore dall'esterno [5, 6].
- **Dati a supporto:** "Immatricolata conferisce quasi un colore rosato, ma solo pochi cm dopo la crosta" (TG_28, 2020) [5, 6].

---
**DUBBIO 4:** "L'amore"
- **Perché è ambiguo:** Altro classico errore del correttore automatico inserito nello stesso momento di "immatricolata".
- **Opzione A:** "L'alone".
- **Opzione B:** "Il colore".
- **Suggerimento NotebookLM:** Preferirei l'Opzione A. "Amore" e "Alone" hanno forte vicinanza su tastiera, e l'espressione "spostato verso uno dei due piatti" descrive perfettamente il comportamento tipico dell'alone nel Grana Trentino [6].
- **Dati a supporto:** "L'amore è spostato verso uno dei due piatti" (TG_28, 2020) [6].

---
**DUBBIO 5:** "Bocciature"
- **Perché è ambiguo:** Termine non caseario, probabile refuso vocale o di battitura.
- **Opzione A:** "Occhiature / Microocchiature" (difetto strutturale attorno al quale si concentra colore anomalo).
- **Opzione B:** "Bollature" (irregolarità sulla crosta menzionate altrove nei dati).
- **Suggerimento NotebookLM:** Preferirei l'Opzione A. È estremamente comune che le alterazioni cromatiche si sviluppino vicino agli "occhi" della pasta. Essendo un termine invariabile [7], se si accetta "Occhiature" non andrà normalizzato.
- **Dati a supporto:** "Alone centrale in qualche sfumatura risata in corrispondenza delle bocciature più importanti" (TG_19, 2018) [8]. Altrove si cita "bollatura allungata" [9].

---
**DUBBIO 6:** "Ragionevoli scuro"
- **Perché è ambiguo:** Sintassi anomala, causata da scrittura frettolosa o autocorrezione.
- **Opzione A:** "Ragionevolmente scuro" (modificatore di intensità).
- **Opzione B:** "Aloni scuri" o "Riflesso scuro".
- **Suggerimento NotebookLM:** Preferirei l'Opzione A ("Ragionevolmente scuro"), come semplice avverbio per quantificare il livello di imbrunimento.
- **Dati a supporto:** "Molto carico grigiastro con ragionevoli scuro e chiazza allungata rodata..." (Q_09, 2018) [3].

---
**DUBBIO 7:** "Concezione"
- **Perché è ambiguo:** Il termine non ha senso logico nel contesto descrittivo di un taglio di formaggio.
- **Opzione A:** "Al centro" (errore del correttore automatico per "centrale" o "al centro").
- **Opzione B:** "A zone" o "Come percezione".
- **Suggerimento NotebookLM:** Preferirei l'Opzione A ("Al centro"). "Più al centro sembrano due zone" è una frase strutturalmente e tecnicamente molto più sensata.
- **Dati a supporto:** "Più concezione sembrano due zone di colore" (TG_04, Seduta 20, 2021) [10].

---
**DUBBIO 8:** "Vasca"
- **Perché è ambiguo:** Termine anomalo per descrivere una forma all'interno della pasta del formaggio.
- **Opzione A:** "Fascia" (striscia di colore).
- **Opzione B:** "Tasca" (intesa come fessura/strappo nella struttura della pasta).
- **Suggerimento NotebookLM:** Preferirei l'Opzione A ("Fascia"). Il termine "Fascia della frattura" è coerente con il difetto visivo che accompagna gli strappi della pasta. 
- **Dati a supporto:** "La vasca della frattura tende al rosa arancio, più chiaro sotto un piatto" (TG_19, 2018) [11].

---
**DUBBIO 9:** "Originale"
- **Perché è ambiguo:** Descrivere una zona chiara come "originale" in una valutazione oggettiva è insolito. 
- **Opzione A:** "Marginale" (la zona periferica, vicino alla crosta).
- **Opzione B:** "Anomala / Insolita".
- **Suggerimento NotebookLM:** Preferirei l'Opzione A ("Marginale"). Da un punto di vista topografico, spesso si segnalano zone chiare ai margini (scalzi o sottocrosta). "Marginale" e "Originale" sono molto simili ortograficamente.
- **Dati a supporto:** "Rosa e originale zona chiara" (TG_15, 2018) [12].

---
**DUBBIO 10:** "Tranciato"
- **Perché è ambiguo:** Può indicare il difetto di colore o descrivere l'azione del taglio.
- **Opzione A:** "Aranciato" (refuso di battitura come "arrangiato").
- **Opzione B:** "Tagliato" (riferito alla valutazione della fetta appena tranciata).
- **Suggerimento NotebookLM:** Preferirei l'Opzione A ("Aranciato"). Tra i panelisti i typo da T9 per "aranciato" sono diffusissimi (es. "arrangiato" in "Chiaro arrangiato" [13]), ed è perfettamente coerente con "alone".
- **Dati a supporto:** "Tranciato con alone" (Q_09, 2018) [14].

---

## Istruzioni per la revisione umana

1. Leggi ogni sezione e valida / correggi le proposte di normalizzazione
2. Risolvi ogni dubbio in Query 4 scegliendo Opzione A, B o altra
3. Per Spessore della Crosta: confronta soglie script vs analisi NBLM e scegli i range definitivi
4. Salva le decisioni finali in: `data/interim/vocabolari_validati_per_attributo/Colore_della_Pasta_vocabolario.json`
5. Usa come template: `docs/template_vocabolario_validato.json` (generato da questo script)
