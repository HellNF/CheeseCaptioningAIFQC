# Vocabolario Bozza — Struttura della Pasta

**Generato:** 2026-04-09 21:01
**Notebook NotebookLM:** `ce6c1c95-1505-4804-895a-c8f4d43f6fad`
**Stato:** BOZZA — richiede revisione umana prima di procedere con script 09

---

## Orientamento iniziale NotebookLM

Ho letto il documento sul contesto dell'analisi. Ecco le conferme richieste:

* **Fonti CSV**: Delle 8 fonti caricate, **7 sono file CSV** (che includono i commenti dei panelisti e i risultati delle medie di giuria per gli anni di riferimento), mentre l'ottava è un file Markdown contenente il documento di contesto.
* **Range temporale**: Le sessioni di valutazione sensoriale presenti nei dati coprono il periodo che va dal **2018 al 2021** [1, 2].
* **Colonna da analizzare**: I testi liberi scritti dai panelisti durante la degustazione si trovano nella **colonna "Commenti"** [3].

---

## Query 1 — Inventario termini

| Termine / Espressione | Occorrenze (stima) | Anni in cui compare | Esempio di frase completa |
| :--- | :--- | :--- | :--- |
| Grana (fine, grossa, grossolana, assente, omogenea) | > 200 | 2018, 2019, 2020, 2021, 2022 | "Leggermente stirata con grana grossa" [1]. |
| Frattura (regolare, irregolare, discreta, a scaglie, ad arco) | > 200 | 2018, 2019, 2020, 2021, 2022 | "Frattura irregolare con striature e microocchiature 0,5 mm" [2]. |
| Microocchiatura (incluse varianti: microcchiatura, microocch., mic) | > 150 | 2018, 2019, 2020, 2021, 2022 | "Fitta microocchiatura con effetto sovrascrittura molto reg" [3]. |
| Stirata / Stiratura / Tendente allo stirato | > 100 | 2018, 2019, 2020, 2021, 2022 | "Non regolare con buona area tendente allo stirato" [1]. |
| Omogenea / Disomogenea | > 100 | 2018, 2019, 2020, 2021, 2022 | "Struttura a roccia ben distribuita ed omogenea" [1]. |
| Regolare / Irregolare / Non regolare | > 80 | 2018, 2019, 2020, 2021, 2022 | "Non regolare Tendente allo stirato Granulosa" [1]. |
| Occhiatura / Occhi / Occhio | > 80 | 2018, 2019, 2020, 2021, 2022 | "Occhiatura diffusa nella fascia centrale" [3]. |
| Fessura / Fessure / Fessurazioni | > 50 | 2018, 2019, 2020, 2021, 2022 | "Grandi fessure stirata" [4]. |
| Spacco / Spacchi / Spaccatura | > 50 | 2018, 2019, 2020, 2021 | "Grande spacco, grana piatta" [5]. |
| Strappo / Strappi / Strappetto | > 40 | 2018, 2019, 2020, 2021 | "Qualche piccolo strappo fessura" [6]. |
| Granulosa / Granulosità | > 30 | 2018, 2019, 2020, 2021 | "Pasta con Striature ma granulosa" [1]. |
| Spugnosa / Spugna / Spugnatura / Spugnosità | > 30 | 2018, 2019, 2020, 2021, 2022 | "Occhiatura spugnosa, grana bella" [6]. |
| Sfoglia / Sfogliata / Fogliata | > 20 | 2018, 2019, 2020, 2021 | "Sfogliata, gessata." [7]. |
| Scaglie / Scagliosa | > 20 | 2018, 2019, 2020, 2021, 2022 | "Frattura a scaglie grana con striature" [8]. |
| Cristalli / Tirosina | > 20 | 2018, 2019, 2020, 2021, 2022 | "Abbastanza regolare con cristalli bianchi" [9]. |
| Grandiosa / Grandiosità (Refuso per granulosa) | > 20 | 2018, 2019, 2020, 2021 | "Struttura grandiosa regolare" [9]. |
| Ruvida | > 15 | 2018, 2019, 2020, 2021, 2022 | "Un po' ruvida. Discreta frattura." [1]. |
| Asciutta / Disidratata / Secca | > 15 | 2018, 2019, 2020, 2021, 2022 | "Asciutta, granulosa, non molto solubile" [10]. |
| Crepa / Crepe | > 10 | 2018, 2019, 2020, 2021 | "Striature e crepa centrale" [11]. |
| Gessata / Gessato | > 10 | 2018, 2019, 2020 | "Leggermente stirata e gessosa" [6]. |
| Compatta / Compattata / Plastica | > 10 | 2018, 2019, 2020 | "A tratti stirata, compatta e poco granulosa" [12]. |
| Friabile / Friabilità | ~ 10 | 2018 | "Friabile ma morbido al morso." [10]. |
| Solubile / Solubilità | ~ 10 | 2018 | "Non asciutto. estremamente friabile. struttura molto fine. giusta adesivita'. cristalli fini" [13]. |
| Bocciatura / Bocciature (Refuso per occhiatura) | ~ 5 - 8 | 2018, 2019 | "Bocciature 1_2 mm centrali e verso crosta" [7]. |
| Spagnola (Refuso per spugnosa) | ~ 5 - 8 | 2018, 2019, 2020 | "Piccola area spagnola concentrata su uno scalzo" [14]. |
| Spinosa (Refuso per spugnosa) | ~ 5 - 8 | 2018, 2019, 2020 | "Spinosa con striature, non regolare" [15]. |
| Perle | ~ 5 | 2018, 2019, 2020 | "Evidenti cristalli perle e microocchiatura" [16]. |
| Impasta / Pastosa / Pastoso | ~ 5 | 2018 | "Compatto, umido, pastoso, poco granuloso" [17]. |
| Slegata / Slegato | ~ 4 | 2019, 2020, 2021 | "Struttura slegata, disomogenea. Presente una spacco" [18]. |
| Impugnatura (Refuso per spugnatura) | ~ 4 | 2018, 2021 | "Leggera impugnatura in zona centrale" [19]. |
| Dittatura (Refuso per occhiatura/fessuratura) | ~ 4 | 2018 | "Grossa dittatura centrale , vistoso spacco e caverna" [20]. |
| Sbrinz (Riferimento alla tipologia) | 3 | 2018, 2020, 2021 | "Zone stirato, presenza di microocchiature e struttura sbrinz" [21]. |
| Caverna / Cavernosa | 2 | 2018 | "Bella frattura e bella grana, presenza di piccole sfoglie e di una zona cavernosa" [22]. |
| Saponosa / Saponea | 2 | 2018 | "Tutta saponea e stirata frattura irregolare" [23]. |
| Vasca | 2 | 2018, 2020 | "Frattura con vasca, micro occhiatura diffusa" [24]. |
| Sabbiosa / Sabbia | 2 | 2021, 2022 | "Sfatta, disunita, sabbiosa" [25]. |
| Demineralizzato / Demoralizzato (Refuso) | 2 | 2018 | "Un sottopiatto demineralizzato con strappi" [26]. |
| Disunita | 1 | 2022 | "Sfatta, disunita, sabbiosa" [25]. |
| Scollata | 1 | 2021 | "Pasta un po' scollata in un sotto piatto" [27]. |
| Gommoso | 1 | 2018 | "Compatto, quasi gommoso e deformabile, non friabile" [28]. |
| Grano di riso | 1 | 2022 | "Grossolana. A grano di riso" [29]. |
| Occhio di Sauron (Termine insolito/iperbole) | 1 | 2020 | "L'occhio di Sauron" [30]. |
| Pratomagno (Riferimento atipico) | 1 | 2021 | "A larghi tratti ha struttura da pratomagno" [31]. |
| Carta vetro (Similitudine) | 1 | 2021 | "Area centrale verso un sottopiatto ruvida TIPO CARTA VETRO" [32]. |
| Bombardamento (Similitudine) | 1 | 2018 | "Frattura da bombardamento." [33]. |
| Microsoft (Refuso evidente per microocchiatura) | 1 | 2018 | "Sporadiche Microsoft, ampie zone stirate" [16]. |
| Carolatura (Refuso probabile per carotatura) | 1 | 2020 | "Carolatura sotto un piatto" [34]. |
| Ideologizzata (Refuso incomprensibile) | 1 | 2018 | "Ideologizzata diffusa con mancanza di struttura" [35]. |
| Rigeneratrice (Refuso) | 1 | 2018 | "Rigeneratrice nel senso del piatto altrimenti grana omogenea" [7]. |
| MaceRO (Refuso / Errore di battitura) | 1 | 2018 | "MaceRO FRATTURA A T DUE OCCHIATURE VARIE MICROOCCHIATURE STIRATA" [23]. |
| Stamattina (Refuso) | 1 | 2018 | "A tratti sembra appena accennata. A tratti stamattina." [5]. |
| Anna (Refuso per grana) | 1 | 2018 | "Struttura Anna regolare" [36]. |
| Cessata (Refuso per gessata) | 1 | 2018 | "Strappi e pasta cessata sotto 1 piatto disomogenea" [37]. |
| Cratere | 1 | 2018 | "Frattura con cratere." [38]. |
| Sottoscala (Refuso per sottocrosta) | 1 | 2020 | "Nel commento sottoscala disidratato intendo disidratazione però più nei piatti" [39]. |
| Amore (Refuso probabile per 'ampie') | 1 | 2018 | "Amore zone stirate" [40]. |
| Pugnosa (Refuso per spugnosa) | 1 | 2018 | "centralmente area pugnosa poco estesa" [41]. |

---

## Query 2 — Cluster semantici

**Cluster: Grana**
- Varianti trovate nei dati: Grana, Anna
- Forma canonica proposta: grana
- Motivazione della scelta: Termine tecnico caseario INVARIABILE richiesto dalle regole. "Anna" è un evidente refuso generato dalla correzione automatica.
- Frequenza stimata del cluster: > 200

**Cluster: Frattura**
- Varianti trovate nei dati: Frattura, Bombardamento, MaceRO
- Forma canonica proposta: frattura
- Motivazione della scelta: Termine tecnico caseario INVARIABILE. "Bombardamento" è un'iperbole usata per descriverne una tipologia estrema, "MaceRO" un probabile refuso/errore di digitazione adiacente al termine.
- Frequenza stimata del cluster: > 200

**Cluster: Microocchiatura**
- Varianti trovate nei dati: Microocchiatura, microcchiatura, microocch., mic, Microsoft
- Forma canonica proposta: microocchiatura
- Motivazione della scelta: Termine tecnico caseario INVARIABILE. Include tutte le normalizzazioni delle abbreviazioni e l'evidente correzione automatica del T9 in "Microsoft".
- Frequenza stimata del cluster: > 150

**Cluster: Stiratura della pasta**
- Varianti trovate nei dati: Stirata, Stiratura, Tendente allo stirato, st, strirata
- Forma canonica proposta: stirata
- Motivazione della scelta: Termine tecnico caseario INVARIABILE richiesto dalle regole. Raccoglie tutte le flessioni e le abbreviazioni.
- Frequenza stimata del cluster: > 100

**Cluster: Omogeneità**
- Varianti trovate nei dati: Omogenea, Disomogenea, Regolare, Irregolare, Non regolare
- Forma canonica proposta: Omogenea / Regolare (e rispettivi negativi Disomogenea / Irregolare)
- Motivazione della scelta: Sono gli aggettivi standard e più diffusi utilizzati per descrivere la coerenza visiva della struttura sull'intera sezione del formaggio.
- Frequenza stimata del cluster: > 180

**Cluster: Occhiatura**
- Varianti trovate nei dati: Occhiatura, Occhi, Occhio, Bocciatura, Dittatura, Carolatura, Occhio di Sauron
- Forma canonica proposta: occhiatura
- Motivazione della scelta: Termine tecnico caseario INVARIABILE. Questo cluster pulisce una grande quantità di refusi generati dal correttore ortografico (bocciatura, dittatura, carolatura) e raggruppa le iperboli.
- Frequenza stimata del cluster: > 95

**Cluster: Fessurazioni**
- Varianti trovate nei dati: Fessura, Fessure, Fessurazioni, Spacco, Spacchi, Spaccatura, Crepa, Crepe
- Forma canonica proposta: Fessurazione / Spaccatura
- Motivazione della scelta: Termini univoci e corretti per descrivere le aperture, rotture o discontinuità lineari non tipiche della pasta.
- Frequenza stimata del cluster: > 110

**Cluster: Granulosità**
- Varianti trovate nei dati: Granulosa, Granulosità, Grandiosa, Grandiosità, Grano di riso
- Forma canonica proposta: Granulosa / Granulosità
- Motivazione della scelta: Forma aggettivale e nominale corretta, essenziale per recuperare i numerosissimi refusi creati dal correttore automatico ("grandiosa" / "grandiosità").
- Frequenza stimata del cluster: > 50

**Cluster: Struttura Spugnosa**
- Varianti trovate nei dati: Spugnosa, Spugna, Spugnatura, Spugnosità, Spagnola, Spinosa, Impugnatura, Pugnosa
- Forma canonica proposta: Spugnosa
- Motivazione della scelta: È il termine corretto per descrivere il difetto visivo causato da fitta microocchiatura. Il cluster ripara una serie gravissima di refusi fonetici o di T9 (spagnola, spinosa, impugnatura).
- Frequenza stimata del cluster: > 45

**Cluster: Danni meccanici (Strappi)**
- Varianti trovate nei dati: Strappo, Strappi, Strappetto
- Forma canonica proposta: Strappo
- Motivazione della scelta: Distingue chiaramente i danni causati meccanicamente (es. dall'ago o dal coltello al momento del taglio) dalle fessurazioni o crepe naturali della forma.
- Frequenza stimata del cluster: > 40

**Cluster: Sfogliatura e Scagliosità**
- Varianti trovate nei dati: Sfoglia, Sfogliata, Fogliata, Scaglie, Scagliosa
- Forma canonica proposta: Sfoglia / A scaglie
- Motivazione della scelta: Identifica in modo standard la tendenza della pasta a separarsi per piani paralleli o a scagliarsi.
- Frequenza stimata del cluster: > 40

**Cluster: Cristallizzazione**
- Varianti trovate nei dati: Cristalli, Tirosina, Perle
- Forma canonica proposta: cristalli / tirosina
- Motivazione della scelta: Termini tecnici caseari INVARIABILI. "Perle" è un descrittore gergale dei panelisti per indicare i medesimi aggregati bianchi.
- Frequenza stimata del cluster: > 25

**Cluster: Ruvidità e Sabbiosità**
- Varianti trovate nei dati: Ruvida, Carta vetro, Sabbiosa, Sabbia
- Forma canonica proposta: Ruvida / Sabbiosa
- Motivazione della scelta: Descrive la specifica percezione tattile o visiva di superficie scabra, raggruppando anche la similitudine "carta vetro".
- Frequenza stimata del cluster: > 17

**Cluster: Disidratazione**
- Varianti trovate nei dati: Asciutta, Disidratata, Secca, Demineralizzato, Demoralizzato
- Forma canonica proposta: Disidratata / Asciutta
- Motivazione della scelta: Riunisce le descrizioni di pasta priva della corretta umidità visiva, sistemando evidenti refusi ("demoralizzato").
- Frequenza stimata del cluster: > 17

**Cluster: Gessatura**
- Varianti trovate nei dati: Gessata, Gessato, Cessata
- Forma canonica proposta: Gessata
- Motivazione della scelta: Identifica il difetto strutturale che fa somigliare la pasta a gesso, correggendo l'errore di battitura ("cessata").
- Frequenza stimata del cluster: > 11

**Cluster: Compattezza**
- Varianti trovate nei dati: Compatta, Compattata, Plastica
- Forma canonica proposta: compatto / compattezza
- Motivazione della scelta: Termine tecnico caseario INVARIABILE. Raccoglie anche il termine "plastica", spesso usato per indicare una pasta eccessivamente densa e deformabile.
- Frequenza stimata del cluster: > 10

**Cluster: Friabilità**
- Varianti trovate nei dati: Friabile, Friabilità
- Forma canonica proposta: friabile / friabilità
- Motivazione della scelta: Termine tecnico caseario INVARIABILE.
- Frequenza stimata del cluster: ~ 10

**Cluster: Solubilità**
- Varianti trovate nei dati: Solubile, Solubilità
- Forma canonica proposta: solubile / solubilità
- Motivazione della scelta: Termine tecnico caseario INVARIABILE.
- Frequenza stimata del cluster: ~ 10

**Cluster: Slegatura**
- Varianti trovate nei dati: Slegata, Slegato, Disunita, Scollata
- Forma canonica proposta: Slegata
- Motivazione della scelta: Standardizza il concetto di una struttura che non sta coerentemente insieme e tende a sfaldarsi in blocchi.
- Frequenza stimata del cluster: ~ 6

**Cluster: Pastosità / Adesività**
- Varianti trovate nei dati: Impasta, Pastosa, Pastoso, Gommoso
- Forma canonica proposta: Pastosa
- Motivazione della scelta: Unifica i concetti legati all'eccessiva deformabilità e alla tendenza della pasta a incollarsi.
- Frequenza stimata del cluster: ~ 6

**Cluster: Cedevolezza**
- Varianti trovate nei dati: Cedevole
- Forma canonica proposta: cedevole
- Motivazione della scelta: Termine tecnico caseario INVARIABILE.
- Frequenza stimata del cluster: ~ 4

**Cluster: Macrocavità**
- Varianti trovate nei dati: Caverna, Cavernosa, Vasca, Cratere
- Forma canonica proposta: Caverna / Vasca
- Motivazione della scelta: Raggruppa i termini figurativi usati dai panelisti per indicare buchi, occhi o avvallamenti di dimensioni anormalmente grandi.
- Frequenza stimata del cluster: ~ 5

**Cluster: Riferimenti Geografici / Atipici**
- Varianti trovate nei dati: Sbrinz, Pratomagno
- Forma canonica proposta: Riferimento atipico (Sbrinz / Pratomagno)
- Motivazione della scelta: Evidenzia le similitudini fatte dai panelisti con altri formaggi (Sbrinz) o luoghi per descrivere una struttura non tipica del Grana Trentino.
- Frequenza stimata del cluster: ~ 4

**Cluster: Localizzatori Anatomici (Posizione)**
- Varianti trovate nei dati: Sottoscala, scalzo, scalzi, piatti, piatto, sottocrosta, angoli, spigoli
- Forma canonica proposta: scalzo, piatti, piatto, sottocrosta, angoli, spigoli
- Motivazione della scelta: Termini tecnici INVARIABILI utilizzati per indicare la posizione dei difetti. Si corregge l'evidente errore di battitura di "sottoscala" riportandolo a "sottocrosta".
- Frequenza stimata del cluster: Alta (trasversale, applicati in abbinamento ad altri descrittori).

---

## Query 3 — Anomalie e termini quantitativi

Ecco i casi speciali di normalizzazione identificati all'interno dei commenti dei panelisti per l'attributo "Struttura della Pasta", classificati in base alle tue istruzioni e nel rispetto dei termini tecnici invariabili [1].

| Termine trovato | Tipo (1–5) | Proposta di normalizzazione | Confidenza (alta/media/bassa) | Note |
| :--- | :--- | :--- | :--- | :--- |
| **"legg."**, **"mediam."** | 1 | "leggermente", "mediamente" | Alta | Abbreviazioni comuni utilizzate per gli avverbi di intensità [2, 3]. |
| **"mic"**, **"microocch."** | 1 | "microocchiatura" | Alta | Abbreviazioni evidenti; la forma estesa è un termine tecnico invariabile [1, 4, 5]. |
| **"st"**, **"strirata"** | 1 | "stirata" | Alta | Troncamento o errore di battitura per "stirata", che deve rimanere invariabile [1, 6, 7]. |
| **"tipo carta vetro"** | 2 | "ruvida" | Alta | Similitudine colloquiale usata per descrivere una netta ruvidità al tatto/vista [8]. |
| **"da bombardamento"** | 2 | "frattura irregolare" | Alta | Iperbole usata per descrivere una frattura estremamente sconnessa e irregolare [9]. |
| **"grana grassa"** | 2 | "pasta pastosa / umida" | Media | Colloquialismo/gergo usato per indicare una pasta eccessivamente umida o untuosa [10]. |
| **"grandiosa"** | 3 | "granulosa" | Alta | Evidente intervento del correttore automatico (T9) al posto di "granulosa" [11, 12]. |
| **"Microsoft"** | 3 | "microocchiatura" | Alta | Singolare errore del correttore ortografico per "microocchiatura", termine invariabile [1, 13]. |
| **"bocciatura"**, **"dittatura"** | 3 | "occhiatura" | Alta | Frequenti refusi per "occhiatura", che deve essere preservata come termine tecnico invariabile [1, 11, 14]. |
| **"spagnola"**, **"spinosa"** | 3 | "spugnosa" | Alta | Comuni errori di battitura/T9 usati al posto del difetto "spugnosa" [15, 16]. |
| **"demoralizzato"**, **"demineralizzato"** | 3 | "disidratato" | Media | Errori del correttore ricorrenti per indicare una pasta priva di umidità (es. nel sottopiatto) [16, 17]. |
| **"0,5 mm"** | 4 | "fisiologica / tollerabile" | Alta | Nel 2018 questo valore è associato a un voto di **8,0** (difetto minimo o assente) [7]. |
| **"10-12 mm"** | 4 | "occhio grande" | Alta | Nel 2018 questo valore comporta un abbassamento del voto a **7,1** (difetto marcato per la tipologia) [4]. |
| **"frattura 8 cm"** | 4 | "spaccatura estesa (grave)" | Alta | Nel 2018 una fessurazione di questa misura corrisponde al voto **6,2** (grave difetto strutturale) [18]. |
| **Campione C0L** (2018, Sed. 2) | 5 | Nessuna (mantenere originale) | Alta | Contraddizione netta: il panelista TG_04 assegna **9,0** ("Ottima frattura"), mentre Q_02 assegna **5,5** ("Grave struttura irregolare") [14]. Rivela estrema eterogeneità della forma o profonda soggettività. |
| **Campione C0Q** (2018, Sed. 4) | 5 | Nessuna (mantenere originale) | Alta | Contraddizione netta: il panelista Q_09 assegna **8,8** ("Frattura e grana regolare"), mentre TG_11 valuta con **5,3** ("Spinosa centrale") [16]. |

---

## Query 4 — Dubbi per revisione umana

---
**DUBBIO 1:** "Ideologizzata"
- **Perché è ambiguo:** È un evidente, e bizzarro, errore del correttore ortografico automatico (T9) che stravolge completamente il senso della frase.
- **Opzione A:** "Occhiatura" (il correttore potrebbe aver trasformato una digitazione molto errata di occhiatura).
- **Opzione B:** "Spugnatura" / "Idratata" (altri termini che potrebbero precedere "diffusa").
- **Suggerimento NotebookLM:** Preferirei "Occhiatura". Nei dati, "occhiatura diffusa con mancanza di struttura" è una frase tipica e coerente con la penalizzazione che spesso l'accompagna [1].
- **Dati a supporto:** "Ideologizzata diffusa con mancanza di struttura" valutata con un punteggio basso (5.9) dal panelista TG_08 [1].

---
**DUBBIO 2:** "stamattina"
- **Perché è ambiguo:** Inserimento totalmente fuori contesto, tipico del completamento automatico dello smartphone durante la digitazione rapida.
- **Opzione A:** "Stiratina" / "Stirata" (foneticamente e tipograficamente simile).
- **Opzione B:** "Sfogliata" / "Spugnosa".
- **Suggerimento NotebookLM:** Preferirei "Stiratina" (da ricondurre al termine invariabile "stirata"). Il panelista contrappone il difetto "appena accennato" a tratti in cui è più evidente.
- **Dati a supporto:** "A tratti sembra appena accennata. A tratti stamattina. Altri punti grandiosa. Taglio solo discreto" [2].

---
**DUBBIO 3:** "degustazioni"
- **Perché è ambiguo:** Il termine non ha senso per descrivere visivamente la struttura della pasta; è chiaramente un refuso.
- **Opzione A:** "Fessurazioni".
- **Opzione B:** "Desquamazioni" / "Sfoglie".
- **Suggerimento NotebookLM:** Preferirei "Fessurazioni", in quanto "fessurazione" o "fessura" sono termini ampiamente usati nello stesso dataset per descrivere spaccature strutturali [3, 4].
- **Dati a supporto:** "Presenza di degustazioni, grosse scaglie.. La grana tende ad avere una direzione" [4].

---
**DUBBIO 4:** "discrezionalità"
- **Perché è ambiguo:** Termine amministrativo/giuridico inapplicabile all'analisi sensoriale visiva di una pasta casearia.
- **Opzione A:** "Direzionalità" (tendenza delle fibre della pasta a seguire una linea, precursore della "stiratura").
- **Opzione B:** "Disomogeneità".
- **Suggerimento NotebookLM:** "Direzionalità" è la correzione quasi certa. Il commento parla esplicitamente di "fibre" e di struttura "non omogenea" a causa di questo andamento [5, 6].
- **Dati a supporto:** "Una certa discrezionalità delle fibre centrale" [6] e "Grana non omogenea per una certa discrezionalità centrale" [5].

---
**DUBBIO 5:** "perla di Roma"
- **Perché è ambiguo:** "Perla" è un gergo usato dai panelisti per indicare grossi cristalli bianchi, ma l'aggiunta geografica "di Roma" è incomprensibile.
- **Opzione A:** "Perla rotonda" (errore del T9).
- **Opzione B:** "Perla da" (errore di battitura "di Roma" al posto di "da").
- **Suggerimento NotebookLM:** Preferirei "da". Il panelista sta chiaramente indicando la dimensione del cristallo ("5 mm"), quindi la frase logica è "perla da 5 mm" [5].
- **Dati a supporto:** "qualche perla di Roma 5 mm" [5].

---
**DUBBIO 6:** "Trans evidenti te"
- **Perché è ambiguo:** Stringa di testo troncata e sostituita dal correttore automatico.
- **Opzione A:** "Tracce evidenti" (es. tracce di occhiatura o stiratura).
- **Opzione B:** "Taglio evidente".
- **Suggerimento NotebookLM:** "Tracce evidenti". "Trans" e "te" sembrano i frammenti della parola "Tracce", divisa e mal corretta.
- **Dati a supporto:** "Trans evidenti te ma non omogenea Area con microocchiatura regolare" valutata 8.0 dal panelista TG_20 [7].

---
**DUBBIO 7:** "rigeneratrice"
- **Perché è ambiguo:** Termine fuori contesto per l'analisi visiva.
- **Opzione A:** "Rigatura" (inteso come linea di discontinuità o striatura).
- **Opzione B:** "Ruvidità".
- **Suggerimento NotebookLM:** Preferirei "Rigatura" o "Striatura", in quanto il commento specifica "nel senso del piatto", indicando un difetto lineare e direzionale [8].
- **Dati a supporto:** "Rigeneratrice nel senso del piatto altrimenti grana omogenea" [8].

---
**DUBBIO 8:** "realizzata"
- **Perché è ambiguo:** Aggettivo che non descrive un difetto visivo.
- **Opzione A:** "Ragnatela" (riferito all'intreccio di fitti strappi).
- **Opzione B:** "Sfilacciata" / "Gessata".
- **Suggerimento NotebookLM:** "Ragnatela" o "Sfilacciata". Entrambi rendono bene l'idea visiva descritta come "fitti strappi piccoli" [8].
- **Dati a supporto:** "Pasta irregolare con zona centrale con Fitti strappi piccoli sembra quasi realizzata" [8].

---
**DUBBIO 9:** "Amore"
- **Perché è ambiguo:** Errore del correttore automatico all'inizio della frase.
- **Opzione A:** "Ampie" (Ampie zone stirate).
- **Opzione B:** "Alcune" (Alcune zone stirate).
- **Suggerimento NotebookLM:** "Ampie". Tipograficamente "amore" è la prima correzione offerta dai telefoni quando si digita in modo errato "ampie" [9].
- **Dati a supporto:** "Amore zone stirate" [9].

---
**DUBBIO 10:** "congelata"
- **Perché è ambiguo:** I campioni vengono valutati a temperatura ambiente; "congelata" non è una caratteristica strutturale pertinente.
- **Opzione A:** "Compatta".
- **Opzione B:** "Conglomerata".
- **Suggerimento NotebookLM:** "Compatta". "Agglomerato compatto" descrive bene una pasta densa, ed è un termine molto più frequente in questo contesto caseario [10].
- **Dati a supporto:** "Agglomerato congelata poco presente e leggermente stirata" [10].

---
**DUBBIO 11:** "versata"
- **Perché è ambiguo:** "Versata" non è un descrittore strutturale codificato.
- **Opzione A:** "Gessata" (difetto visivo tipico).
- **Opzione B:** "Fessurata".
- **Suggerimento NotebookLM:** "Gessata". Spesso la struttura "plastica" viene associata a difetti di umidità o gessatura della pasta [11].
- **Dati a supporto:** "Plastica omogenea !un Po versata e un Po stirata" [11].

---

## Istruzioni per la revisione umana

1. Leggi ogni sezione e valida / correggi le proposte di normalizzazione
2. Risolvi ogni dubbio in Query 4 scegliendo Opzione A, B o altra
3. Per Spessore della Crosta: confronta soglie script vs analisi NBLM e scegli i range definitivi
4. Salva le decisioni finali in: `data/interim/vocabolari_validati_per_attributo/Struttura_della_Pasta_vocabolario.json`
5. Usa come template: `docs/template_vocabolario_validato.json` (generato da questo script)
