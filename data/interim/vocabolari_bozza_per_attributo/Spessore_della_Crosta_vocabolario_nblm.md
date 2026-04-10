# Vocabolario Bozza — Spessore della Crosta

**Generato:** 2026-04-09 21:17
**Notebook NotebookLM:** `bb7dbaaf-6496-4560-8c0d-7a77b1e1bd7b`
**Stato:** BOZZA — richiede revisione umana prima di procedere con script 09

---

## Orientamento iniziale NotebookLM

Hai a disposizione **7 fonti in formato CSV**, mentre l'ottava fonte è il documento testuale di contesto [1, 2]. 

Il range temporale dei dati raccolti nelle sessioni di valutazione sensoriale è compreso **tra il 2018 e il 2021** [3, 4]. 

La colonna che contiene il testo libero dei panelisti, e che rappresenta il focus della tua analisi, si intitola **"Commenti"** [2].

---

## Query 1 — Inventario termini

| Termine / Espressione | Occorrenze (stima) | Anni in cui compare | Esempio di frase completa |
| :--- | :--- | :--- | :--- |
| **Numeri espliciti e unità di misura** (mm, cm) | 500+ | 2018, 2019, 2020, 2021 | "Maggiormente negli angoli ma mediamente 1 cm" [1]. |
| **Sottile / Molto sottile / Finissima** | 150+ | 2018, 2019, 2020, 2021 | "Molto sottile su i piatti" [1]. |
| **Spessa / Molto spessa** | 120+ | 2018, 2019, 2020, 2021 | "Crosta sempre superiore al cm. Su uno scalzi molto spessa" [2]. |
| **Sfumata / Limite sfumato** | 100+ | 2018, 2019, 2020, 2021 | "Crosta sfumata Scalzi e piatti media 9mm Spigoli 1,8" [3]. |
| **Fine** | 80+ | 2018, 2019, 2020, 2021 | "Crosta fine ma con unghia più spessa su un piatto." [4]. |
| **Evidente / Poco evidente / Ben visibile** | 70+ | 2018, 2019, 2020, 2021 | "Crosta evidente per colore, ma sottile, 10mm" [5]. |
| **Omogenea / Disomogenea / Omogeneo** | 60+ | 2018, 2019, 2020, 2021 | "Spessore abbastanza omogeneo su entrambi gli sbalzi e piatti" [5]. |
| **Regolare / Irregolare / Difforme / Poco regolare** | 50+ | 2018, 2019, 2020, 2021 | "Spessore non uniforme, maggiore degli scalzi, nella media 10" [6]. |
| **Media / Nella media** | 50+ | 2018, 2019, 2020, 2021 | "Intorno a 8 nella media" [7]. |
| **Grossa / Grossolana** | 40+ | 2018, 2019, 2020, 2021 | "Spigoli grossolani grossa" [8]. |
| **Accentuati / Pronunciati** (riferito a spigoli o unghia) | 40+ | 2018, 2019, 2020, 2021 | "Sottile nei piatti spigoli molto pronunciati" [9]. |
| **Unghia** (marcata, spessa, ampia, tanta) | 30+ | 2018, 2019, 2020, 2021 | "Crosta fine ma con molta unghia" [10]. |
| **Colore carico / Sfondo scuro / Tende al...** | 30+ | 2019, 2020, 2021 | "Colore di fondo molto carico rende meno netta la percezione della crosta" [11]. |
| **Netta / Limite netto** | 20+ | 2018, 2019, 2020, 2021 | "Limite molto netto" [12]. |
| **Colori specifici** (Grigiastro, Aranciato, Verde, Rossastro, Ocra) | 20+ | 2018, 2019, 2020, 2021 | "Colore sottocrosta grigiastro su sfondo molto carico" [13]. |
| **Chiaro / Chiara** | 15+ | 2018, 2019, 2020, 2021 | "Chiara ma spessa" [13]. |
| **Bella / Belli / Buona / Buoni / Ottimi** | 15+ | 2018, 2020, 2021 | "1 piatto molto bello" [14]. |
| **Alta / Bassa / Elevata** (riferito allo spessore) | 10+ | 2018, 2020, 2021 | "Troppo alta negli scalzi!" [15]. |
| **Indefinita / Difficile da misurare / Non distinguibile** | 5+ | 2018, 2020, 2021 | "Indefinita!!!! Media 13mm" [16]. |
| **Brutti / Orrendo / Disastroso** | 5+ | 2018, 2020, 2021 | "1 piatto orrendo, scalzi belli" [13]. |
| **Disidratato / Secco / Secchezza** | 4+ | 2018, 2019, 2020, 2021 | "Sotto scalzo zona disidratata e ammuffita" [11]. |
| **Occhiatura / Microocchiatura / Occhi** | 4+ | 2018, 2019, 2020 | "Sottocrosta con microcchiatura" [17]. |
| **Crostone** | 2 | 2018, 2019 | "Limite sfumato. Crostone" [18]. |
| **Muffa / Ammuffita** | 2 | 2019 | "Non considero la muffa" [11]. |
| **Macchia scura / Macchiato di nero** | 2 | 2018, 2021 | "Spessa e con macchia scura" [19]. |
| **Pulita** | 2 | 2019 | "Pulita" [11]. |
| **Tare** | 2 | 2021 | "Tare nella crosta e Sottocrosta" [13]. |
| **Stacco (tra crosta e pasta)** | 2 | 2021 | "lo stacco tra crosta e pasta si vede poco" [13]. |
| **Marciume** | 1 | 2021 | "Sotto crosta macchiato di nero sullo scalzo, marciume?" [13]. |
| **Carolata** | 1 | 2019 | "Carolata" [11]. |
| **Rosure** | 1 | 2019 | "Rosure" [11]. |

---

## Query 2 — Cluster semantici

Basandoti sui termini identificati in precedenza e applicando la regola sui termini tecnici caseari invariabili, ecco i cluster semantici per l'attributo "Spessore della Crosta" [1, 2]:

### Cluster Descrittivi da Normalizzare

**Cluster: Misure Quantitative**
- Varianti trovate nei dati: Numeri espliciti e unità di misura (mm, cm)
- Forma canonica proposta: Misura in mm
- Motivazione della scelta: Permette di uniformare tutte le valutazioni oggettive a un'unica unità di misura, come suggerito dalle linee guida dell'attributo [1].
- Frequenza stimata del cluster: 500+

**Cluster: Spessore Sottile**
- Varianti trovate nei dati: Sottile, Molto sottile, Finissima, Fine, Bassa
- Forma canonica proposta: Sottile
- Motivazione della scelta: È il termine tecnico standard e oggettivo per definire una crosta di dimensioni ridotte [1].
- Frequenza stimata del cluster: 240+

**Cluster: Spessore Elevato**
- Varianti trovate nei dati: Spessa, Molto spessa, Grossa, Grossolana, Alta, Elevata, Crostone
- Forma canonica proposta: Spessa
- Motivazione della scelta: È l'aggettivo tecnicamente opposto a "sottile", standardizzato per indicare abbondanza di crosta [1].
- Frequenza stimata del cluster: 172+

**Cluster: Limite Netto**
- Varianti trovate nei dati: Netta, Limite netto, Ben visibile, Evidente, Pronunciati, Accentuati, Stacco (tra crosta e pasta)
- Forma canonica proposta: Limite netto
- Motivazione della scelta: Descrive in modo chiaro la presenza di un confine visivo netto e non ambiguo tra la parte edibile e la crosta esterna.
- Frequenza stimata del cluster: 132+

**Cluster: Omogeneità**
- Varianti trovate nei dati: Omogenea, Omogeneo, Regolare, Bella, Belli, Buona, Buoni, Ottimi
- Forma canonica proposta: Regolare
- Motivazione della scelta: "Regolare" elimina i giudizi soggettivi (come "bella" o "buona") convertendoli in un dato oggettivo sull'uniformità dello spessore [3].
- Frequenza stimata del cluster: 125+

**Cluster: Limite Sfumato**
- Varianti trovate nei dati: Sfumata, Limite sfumato, Poco evidente, Indefinita, Difficile da misurare, Non distinguibile
- Forma canonica proposta: Limite sfumato
- Motivazione della scelta: È il termine tecnico più indicato per descrivere il graduale e impercettibile passaggio dalla crosta verso l'interno del formaggio.
- Frequenza stimata del cluster: 105+

**Cluster: Disomogeneità**
- Varianti trovate nei dati: Disomogenea, Irregolare, Difforme, Poco regolare, Brutti, Orrendo, Disastroso
- Forma canonica proposta: Irregolare
- Motivazione della scelta: Raggruppa in modo neutrale tutte le variazioni di spessore lungo il perimetro (es. tra piatti e scalzi), neutralizzando le espressioni negative e colloquiali [3, 4].
- Frequenza stimata del cluster: 65+

**Cluster: Pigmentazione Anomala o Scura**
- Varianti trovate nei dati: Colore carico, Sfondo scuro, Tende al..., Grigiastro, Aranciato, Verde, Rossastro, Ocra, Macchia scura, Macchiato di nero
- Forma canonica proposta: Pigmentazione anomala
- Motivazione della scelta: Aggrega tutte le colorazioni intense o atipiche che influenzano la percezione visiva del limite della crosta.
- Frequenza stimata del cluster: 52+

**Cluster: Spessore Medio**
- Varianti trovate nei dati: Media, Nella media
- Forma canonica proposta: Nella media
- Motivazione della scelta: Rappresenta la conformità dimensionale al range standard atteso per il prodotto (es. 7-12 mm) [1].
- Frequenza stimata del cluster: 50+

**Cluster: Estensione dell'Unghia**
- Varianti trovate nei dati: Unghia (marcata, spessa, ampia, tanta)
- Forma canonica proposta: Unghia evidente
- Motivazione della scelta: Isola il fenomeno specifico dell'ingrossamento dello strato corneo sottomesso alla crosta.
- Frequenza stimata del cluster: 30+

**Cluster: Pigmentazione Chiara**
- Varianti trovate nei dati: Chiaro, Chiara, Pulita
- Forma canonica proposta: Colore chiaro
- Motivazione della scelta: Distingue la crosta che non presenta sfumature scure, disidratate o pigmentazioni eccessive.
- Frequenza stimata del cluster: 17+

**Cluster: Difetti Fisico-Biologici**
- Varianti trovate nei dati: Disidratato, Secco, Secchezza, Muffa, Ammuffita, Marciume, Tare, Carolata, Rosure
- Forma canonica proposta: Difetto della crosta
- Motivazione della scelta: Consolida tutte le alterazioni fisiche, biologiche o da parassiti in una macro-categoria oggettiva per l'individuazione delle non conformità.
- Frequenza stimata del cluster: 11+

---

### Cluster dei Termini INVARIABILI
*(Come da regola, questi termini vengono inseriti in cluster dedicati senza subire normalizzazione, in quanto dotati di specifico significato tecnico [2])*

**Cluster: piatto**
- Varianti trovate nei dati: piatto
- Forma canonica proposta: piatto
- Motivazione della scelta: Termine tecnico caseario invariabile che indica la faccia piana della forma [2, 3].
- Frequenza stimata del cluster: Elevata

**Cluster: piatti**
- Varianti trovate nei dati: piatti
- Forma canonica proposta: piatti
- Motivazione della scelta: Termine tecnico caseario invariabile, plurale di piatto [2].
- Frequenza stimata del cluster: Elevata

**Cluster: scalzo**
- Varianti trovate nei dati: scalzo
- Forma canonica proposta: scalzo
- Motivazione della scelta: Termine tecnico caseario invariabile che indica il bordo laterale della forma [2, 3].
- Frequenza stimata del cluster: Elevata

**Cluster: scalzi**
- Varianti trovate nei dati: scalzi
- Forma canonica proposta: scalzi
- Motivazione della scelta: Termine tecnico caseario invariabile, plurale di scalzo [2].
- Frequenza stimata del cluster: Elevata

**Cluster: angoli**
- Varianti trovate nei dati: angoli
- Forma canonica proposta: angoli
- Motivazione della scelta: Termine tecnico caseario invariabile per i punti di incontro geometrici della forma [2].
- Frequenza stimata del cluster: Media

**Cluster: spigoli**
- Varianti trovate nei dati: spigoli
- Forma canonica proposta: spigoli
- Motivazione della scelta: Termine tecnico caseario invariabile che indica la linea periferica tra piatto e scalzo [2, 3].
- Frequenza stimata del cluster: Alta

**Cluster: sottocrosta**
- Varianti trovate nei dati: sottocrosta
- Forma canonica proposta: sottocrosta
- Motivazione della scelta: Termine tecnico caseario invariabile per la zona di transizione tra crosta e pasta [2].
- Frequenza stimata del cluster: Alta

**Cluster: occhiatura**
- Varianti trovate nei dati: occhiatura
- Forma canonica proposta: occhiatura
- Motivazione della scelta: Termine tecnico caseario invariabile che descrive la presenza di fori o cavità visibili [2].
- Frequenza stimata del cluster: Bassa (raro per questo attributo)

**Cluster: microocchiatura**
- Varianti trovate nei dati: microocchiatura
- Forma canonica proposta: microocchiatura
- Motivazione della scelta: Termine tecnico caseario invariabile che descrive un'occhiatura di minime dimensioni [2].
- Frequenza stimata del cluster: Bassa

**Cluster: grana**
- Varianti trovate nei dati: grana
- Forma canonica proposta: grana
- Motivazione della scelta: Termine tecnico caseario invariabile relativo alla granulometria e struttura della pasta [2].
- Frequenza stimata del cluster: Bassa

**Cluster: frattura**
- Varianti trovate nei dati: frattura
- Forma canonica proposta: frattura
- Motivazione della scelta: Termine tecnico caseario invariabile relativo alla rottura della pasta [2].
- Frequenza stimata del cluster: Bassa

---

## Query 3 — Anomalie e termini quantitativi

| Termine trovato | Tipo (1–5) | Proposta di normalizzazione | Confidenza (alta/media/bassa) | Note |
| :--- | :--- | :--- | :--- | :--- |
| **diff** | 1 | differenza | Alta | Contrazione usata per "evidente diff di spessore" [1]. |
| **x** | 1 | per | Alta | Abbreviazione usata in "x intensità" [2]. |
| **sottoc** | 1 | sottocrosta | Alta | Parola troncata in "Crosta e sottoc non distinguibili" [3]. |
| **Crostone** | 2 | Crosta molto spessa | Media | Termine gergale usato per indicare un eccesso di crosta [4-6]. |
| **Tanta unghia** | 2 | Unghia evidente | Alta | Espressione colloquiale per indicare un'estensione marcata dell'unghia [7, 8]. |
| **Orrendo / Disastroso** | 2 | Disomogeneo / Irregolare | Media | Giudizi soggettivi ed emotivi su piatti e scalzi [9, 10]. Si consiglia di mappare al difetto oggettivo di forma o spessore. |
| **Un Po** | 2 | Leggermente | Alta | Espressione colloquiale/typo ("Un Po spessa") [11-13]. |
| **km / kmm** | 3 | mm | Alta | Frequente errore di digitazione/autocorrezione del tablet per "mm" (es: "10 km", "15kmm") [4, 14-16]. |
| **sottoscritta / sittocrosta** | 3 | sottocrosta | Alta | Evidente correzione automatica errata del tablet [1, 17-22]. Termine caseario invariabile. |
| **sganciato / tranciato** | 3 | aranciato | Media | Probabile autocorrezione errata relativa al colore del sottocrosta ("colore tranciato", "sganciato sfuma") [21, 23-25]. |
| **Christine** | 3 | crosta | Bassa | Probabile autocorrezione bizzarra in "Christine sugli scalzi" [26]. |
| **N9n** | 3 | non | Alta | Errore di battitura ("N9n regolare") [26, 27]. |
| **5 mm / 0,5 cm** | 4 | Molto sottile | Alta | Corrisponde a punteggi ottimali nel 2018 (es. **9.0 - 9.5**) [28, 29]. In linea con la stima preliminare [30]. |
| **8 mm / 10 mm / 1 cm** | 4 | Nella norma | Alta | Corrisponde a punteggi buoni/medi nel 2018 (es. **7.0 - 8.3**) [4, 11, 31, 32]. Conferma la fascia 7-12mm [30]. |
| **12 mm / 14 mm / 15 mm** | 4 | Spessa | Alta | Corrisponde a punteggi penalizzati nel 2018 (es. **4.4 - 6.6**) [4, 17, 33, 34]. Spesso indicato come eccessivo su piatti o scalzi. |
| **20 mm / 22 mm** | 4 | Molto spessa | Alta | Corrisponde a punteggi severi nel 2018 (es. **5.6 - 6.0**) [4, 16, 35]. Spesso riferito a "spigoli". |
| **C0I (Seduta 1)** | 5 | *Non normalizzabile* (Richiede revisione panel leader) | Alta | Contraddizione netta: il panelista TG_35 valuta "Molto sottile" (punteggio **10.0**) [14], mentre TG_04 valuta "3 lati su 4 molto spessa" (punteggio **5.6**) [11]. |
| **C0D (Seduta 4)** | 5 | *Non normalizzabile* (Richiede revisione panel leader) | Media | Contraddizione: TG_26 commenta "Fine anche spigoli" (punteggio **8.0**), mentre TG_24 nota spessore "Superiore a 11" (punteggio **6.7**) [18]. |

---

## Query 4 — Dubbi per revisione umana

---
**DUBBIO 1:** "Christine sugli scalzi"
- **Perché è ambiguo:** Si tratta di un palese e bizzarro errore di autocorrezione del tablet utilizzato dal panelista, che ha sostituito un termine tecnico con un nome proprio.
- **Opzione A:** "Crosta" / "Croste" (il tablet ha corretto "croste" in "Christine"). In questo caso significherebbe "Crosta evidente/spessa sugli scalzi".
- **Opzione B:** "Crosticine" (riferito a piccole irregolarità o desquamazioni sullo scalzo).
- **Suggerimento NotebookLM:** Preferire l'**Opzione A**. Modificare "Christine" in "Crosta".
- **Dati a supporto:** Il commento appartiene a TG_26 sul campione C0Q [1], a cui assegna un punteggio di **7.0**. L'appunto segnala un difetto visibile ma non gravissimo sugli scalzi, compatibile con un eccesso di crosta.

---
**DUBBIO 2:** "Colore sottoscritta sganciato" / "Colore tranciato sottocrosta"
- **Perché è ambiguo:** Entrambi i termini ("sganciato" e "tranciato") non hanno alcun senso nel contesto della descrizione del colore del "sottocrosta" (scritto anche "sottoscritta" per colpa del correttore automatico). 
- **Opzione A:** Entrambi sono autocorrezioni errate per "Aranciato" (un colore anomalo frequentemente segnalato nel sottocrosta).
- **Opzione B:** "Sganciato" potrebbe essere un tentativo di scrivere "sfumato", e "tranciato" un tentativo di scrivere "taglio netto".
- **Suggerimento NotebookLM:** Preferire l'**Opzione A**. La somiglianza fonetica e di digitazione tra "aranciato", "sganciato" e "tranciato" è molto forte, ed è un difetto visivo comune nel dataset.
- **Dati a supporto:** I commenti sono tutti di Q_09 [2-4]. Lo stesso panelista, quando non sbaglia a digitare, descrive esplicitamente il colore come "aranciato molto carico" [5] o "colore sottocrosta aranciato" [6].

---
**DUBBIO 3:** "Carolata"
- **Perché è ambiguo:** È un termine inusuale, probabilmente di derivazione dialettale o gergale, che non fa parte del vocabolario standard di degustazione del formaggio.
- **Opzione A:** Variante di "Camolata" / "Tarlata", indicante l'azione degli acari del formaggio (camole) che erodono la crosta.
- **Opzione B:** Riferimento a una crosta "Screpolata" o che presenta un "carolo" (spaccatura o buco da fermentazione anomala).
- **Suggerimento NotebookLM:** Preferire l'**Opzione A**, mappandolo nel macro-cluster "Difetto della crosta".
- **Dati a supporto:** Il termine è usato da TG_19 sul campione C0M [7]. Nella stessa seduta (V, 2018-08-01), altri panelisti rilevano su quello stesso campione gravi difetti biologici: "Sotto scalzo zona disidratata e ammuffita" [7] e "Sotto crosta secco e occhi" [7]. 

---
**DUBBIO 4:** "Spessore dispari" / "Dispari Media 11mm"
- **Perché è ambiguo:** L'aggettivo "dispari" si usa normalmente per i numeri, non per misurare uno spessore. 
- **Opzione A:** È un sinonimo personale del panelista per "Disomogeneo" o "Irregolare" (es. spessore diverso tra un lato e l'altro).
- **Opzione B:** Indica un'asimmetria totale e molto pronunciata (es. crosta su un piatto sì e sull'altro no).
- **Suggerimento NotebookLM:** Preferire l'**Opzione A**. Può essere normalizzato in "Irregolare / Disomogeneo".
- **Dati a supporto:** Il termine è utilizzato ripetutamente da Q_02 [8-11]. Sostituisce l'uso di "Disomogenea", che lo stesso panelista usava nelle sedute precedenti [12, 13].

---
**DUBBIO 5:** "Crostone"
- **Perché è ambiguo:** È un termine colloquiale. Non è chiaro se indichi puramente un fattore dimensionale (crosta molto spessa) o un difetto materico (crosta indurita, secca e legnosa).
- **Opzione A:** Normalizzare in "Molto spessa" (valutazione puramente quantitativa).
- **Opzione B:** Creare un'etichetta di difetto specifica ("Crostone"), in quanto implica una durezza e un'invadenza eccessiva verso la pasta.
- **Suggerimento NotebookLM:** Richiede decisione umana. Se le linee guida per la normalizzazione prediligono misure oggettive, l'Opzione A è più sicura. Se l'obiettivo è tracciare i difetti di consistenza percepibili alla vista/tatto, serve l'Opzione B.
- **Dati a supporto:** È usato due volte: in [14] da TG_04 (punteggio **4.9**, molto penalizzato) e in [9] da TG_05 (punteggio **6.7**). 

---
**DUBBIO 6:** "Sotto ac1" / "Media 1"
- **Perché è ambiguo:** Manca l'unità di misura ed è presente un refuso ("ac1").
- **Opzione A:** Intesi come "Sotto a 1 cm" e "Media 1 cm" (quindi 10 mm).
- **Opzione B:** "1" si riferisce a una scala di valutazione interna (da 1 a 10) invece che ai centimetri.
- **Suggerimento NotebookLM:** Preferire l'**Opzione A**. Nei commenti caseari, i numeri singoli senza unità di misura ("1", "1,2", "0,8") si riferiscono immancabilmente ai centimetri.
- **Dati a supporto:** TG_26 usa queste espressioni: "Sotto ac1" [6] dando un punteggio ottimo di **8.0** (una crosta sotto 1 cm è premiata). Scrive anche "Uniforme 1 cm" in un campione e "Media 1" nel campione successivo [15, 16].

---
**DUBBIO 7:** "Rosure" / "Tare"
- **Perché è ambiguo:** Indicano alterazioni fisiche della crosta (attacchi di insetti/roditori per "rosure", crepe o danni meccanici per "tare"), che esulano dalla semplice misurazione dello spessore.
- **Opzione A:** Raggrupparli nella generica categoria "Difetto della crosta" per semplificare la tabella finale.
- **Opzione B:** Mantenerli come termini specifici di "Difetto biologico" e "Difetto meccanico", perché indicano non conformità gravi della forma che il Consorzio potrebbe voler tracciare separatamente.
- **Suggerimento NotebookLM:** Opzione B. Trattandosi di problemi esterni alla tecnica casearia (spesso problemi di stagionatura o stoccaggio), appiattirli su "difetto della crosta" farebbe perdere un'informazione preziosa.
- **Dati a supporto:** TG_26 rileva "Rosure" sul campione C0L nel 2017 [7]. TG_19 rileva "Tare nella crosta" sul C0Q nel 2022 [17]. Sono eventi rari ma molto puntuali.

---

## Istruzioni per la revisione umana

1. Leggi ogni sezione e valida / correggi le proposte di normalizzazione
2. Risolvi ogni dubbio in Query 4 scegliendo Opzione A, B o altra
3. Per Spessore della Crosta: confronta soglie script vs analisi NBLM e scegli i range definitivi
4. Salva le decisioni finali in: `data/interim/vocabolari_validati_per_attributo/Spessore_della_Crosta_vocabolario.json`
5. Usa come template: `docs/template_vocabolario_validato.json` (generato da questo script)
