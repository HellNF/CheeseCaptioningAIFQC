# REGOLE PULIZIA COMMENTI GRANA TRENTINO

**Data:** 2026-02-11
**Basato su:** reports/01_analisi_esplorativa.md
**Dataset:** 10.104 commenti (2018-2021)

---

## 1. VOCABOLARIO CONTROLLATO PER ATTRIBUTO

### 1.1 PROFUMO (Media 2018: 7.30, Std: 0.79)

**Scala Intensità basata su correlazioni punteggi-termini:**

**PUNTEGGI ALTI (8-10) - Termini positivi associati:**
- burro (93 occorrenze in punteggi alti)
- panna (80 occorrenze)
- latte (77 occorrenze)
- cotto (55 occorrenze)
- intenso (31 occorrenze)
- brodo (30 occorrenze)
- tostato (28 occorrenze)
- fuso (27 occorrenze)
- grana (26 occorrenze)
- fruttato (25 occorrenze)

**Mappatura qualitativa:**
- Questi termini indicano profumo "pronunciato", "intenso", "ricco"

**PUNTEGGI BASSI (1-4) - Termini negativi associati:**
- putrido (4 occorrenze - DIFETTO GRAVE)
- marcio (2 occorrenze - DIFETTO GRAVE)
- pozzo (2 occorrenze - DIFETTO)
- puzza (1 occorrenza - DIFETTO GRAVE)

**Mappatura qualitativa:**
- Questi termini indicano profumo "sgradevole", "difettoso", "inadeguato"

**PUNTEGGI MEDI (5-7):**
- leggero (frequente, neutro/positivo)
- delicato (neutro/positivo)
- vegetale (neutro)
- fermentato (neutro, tipico del formaggio)

**REGOLE:**
1. Preservare TUTTI i termini positivi elencati sopra
2. Preservare TUTTI i difetti (termini negativi)
3. "leggero" + punteggio 5-7 → "profumo delicato ma presente"
4. "leggero" + punteggio <5 → "profumo debole"
5. Termini come "all'apertura", "intensità" preservare sempre

---

### 1.2 SAPORE (Media 2018: 6.98, Std: 0.88)

**ATTENZIONE:** Sapore è complesso - alcuni termini appaiono sia in punteggi alti che bassi

**PUNTEGGI ALTI (8-10):**
- dolce (69 occorrenze - SEMPRE POSITIVO)
- equilibrato (60 occorrenze - SEMPRE POSITIVO)
- piccante (48 occorrenze - CONTESTUALE, vedi sotto)
- amaro (27 occorrenze - CONTESTUALE, vedi sotto)
- salato (24 occorrenze - neutro/positivo)
- umami (23 occorrenze - positivo)
- leggermente (18 occorrenze - modificatore importante)

**PUNTEGGI BASSI (1-4):**
- amaro (5 occorrenze - quando ECCESSIVO)
- piccante (4 occorrenze - quando ECCESSIVO)
- acido (3 occorrenze - quando ECCESSIVO)

**REGOLE CONTESTUALI (CRITICHE):**

1. **PICCANTE:**
   - "leggermente piccante" → POSITIVO
   - "piccante equilibrato" → POSITIVO
   - "troppo piccante" → NEGATIVO
   - "piccante" da solo + punteggio >7 → POSITIVO
   - "piccante" da solo + punteggio <5 → NEGATIVO

2. **AMARO:**
   - "leggermente amaro" → POSITIVO
   - "amaro" + "equilibrato" → POSITIVO
   - "troppo amaro" → NEGATIVO
   - "amaro" da solo + punteggio <5 → NEGATIVO

3. **MODIFICATORI DA PRESERVARE:**
   - "troppo" (indica eccesso, negativo)
   - "leggermente" (indica moderazione, positivo)
   - "abbastanza" (neutro)
   - "molto" (intensificatore)

**Gusti base da preservare sempre:**
dolce, salato, amaro, acido, umami, sapido, piccante

---

### 1.3 AROMA (Media 2018: 7.07, Std: 0.83)

**Simile a Profumo ma retronasale**

**PUNTEGGI ALTI (8-10):**
- cotto (46 occorrenze)
- burro (40 occorrenze)
- panna (34 occorrenze)
- latte (28 occorrenze)
- fuso (15 occorrenze)
- formaggio (13 occorrenze)
- crosta (12 occorrenze)
- brodo (11 occorrenze)
- tostato (9 occorrenze)

**PUNTEGGI BASSI (1-4):**
- fermentato (2 occorrenze - quando eccessivo)
- fieno (1 occorrenza)
- pungente (1 occorrenza)
- animale (1 occorrenza - quando eccessivo)
- marcio (1 occorrenza - DIFETTO GRAVE)
- gorgonzola (1 occorrenza - aroma atipico)
- disgustoso (1 occorrenza - DIFETTO GRAVE)

**REGOLE:**
1. Preservare note aromatiche positive (burro, panna, latte, cotto, tostato)
2. "fermentato" può essere neutro/positivo se moderato, negativo se eccessivo
3. "animale" contestuale (può essere tipico se lieve, difetto se forte)

---

### 1.4 TEXTURE (Media 2018: 7.09, Std: 0.83)

**PUNTEGGI ALTI (8-10):**
- cristalli (73 occorrenze - CARATTERISTICA POSITIVA FORTE)
- friabile (51 occorrenze - POSITIVO)
- solubile (41 occorrenze - POSITIVO)
- asciutto (30 occorrenze - POSITIVO)
- bocca (25 occorrenze - contesto "si scioglie in bocca")
- buona (24 occorrenze)
- fine (24 occorrenze)
- abbastanza (24 occorrenze - modificatore)
- granuloso (22 occorrenze - POSITIVO)
- morbido (17 occorrenze - POSITIVO)

**PUNTEGGI BASSI (1-4):**
- molle (1 occorrenza - NEGATIVO)
- solubilità/friabilità (scarse) - NEGATIVO

**Scale qualitative:**
- OTTIMA: "friabile", "cristalli evidenti", "solubile", "granuloso"
- BUONA: "morbido", "cedevole", "asciutto", "compatto"
- INADEGUATA: "molle", "pastoso eccessivo", "umido eccessivo"

**REGOLE:**
1. "cristalli" e "tirosina" sono sempre positivi (cristalli di aminoacido)
2. "friabile" è positivo (caratteristica Grana)
3. "solubile in bocca" è positivo
4. "pastoso" può essere neutro se moderato, negativo se eccessivo
5. "umido" vs "asciutto": dipende dal contesto e punteggio

---

### 1.5 STRUTTURA DELLA PASTA (Media 2018: 7.01, Std: 0.98)

**PUNTEGGI ALTI (8-10):**
- grana (126 occorrenze - CARATTERISTICA FONDAMENTALE)
- frattura (114 occorrenze - tipo di rottura)
- regolare (86 occorrenze - POSITIVO)
- fine (74 occorrenze - grana fine, POSITIVO)
- omogenea (62 occorrenze - POSITIVO)
- bella (55 occorrenze - giudizio estetico positivo)
- granulosa (38 occorrenze - POSITIVO)

**PUNTEGGI BASSI (1-4):**
- mm (misure di difetti)
- occhi (buchi grandi - DIFETTO)
- brutta (2 occorrenze - giudizio negativo)
- essudato (1 occorrenza - DIFETTO)

**Caratteristiche tecniche da preservare:**
- grana (texture granulare - fondamentale)
- frattura (tipo di rottura: stirata, regolare, irregolare)
- microocchiatura (piccoli buchi - può essere OK se diffusa)
- occhiatura (buchi - DIFETTO se eccessiva)
- granulosa (positivo)
- grossolana (neutro, descrittivo)

**REGOLE:**
1. "bella grana" → SEMPRE POSITIVO
2. "frattura regolare" → POSITIVO
3. "frattura stirata" → descrittivo, preservare
4. "omogenea" → POSITIVO
5. "irregolare" + punteggio basso → DIFETTO
6. "microocchiatura diffusa" → OK, tipica
7. "occhi" o "occhiatura" grossi → DIFETTO

---

### 1.6 COLORE DELLA PASTA (Media 2018: 7.12, Std: 0.95)

**PUNTEGGI ALTI (8-10):**
- chiaro (96 occorrenze - POSITIVO)
- omogeneo (94 occorrenze - POSITIVO FORTE)
- paglierino (58 occorrenze - colore tipico)
- carico (46 occorrenze - ma CONTESTUALE, vedi sotto)
- giallo (45 occorrenze - colore tipico)
- uniforme (23 occorrenze - POSITIVO)

**PUNTEGGI BASSI (1-4):**
- carico (7 occorrenze - quando ECCESSIVO)
- rosa (4 occorrenze - DIFETTO se diffuso)
- alone centrale (3 occorrenze - DIFETTO)
- macchie (3 occorrenze - DIFETTO)
- anello (2 occorrenze - DIFETTO)

**Difetti da preservare:**
- alone centrale / alone rosato
- macchie rosa
- fascia centrale
- disomogeneo
- anello

**REGOLE CONTESTUALI:**
1. "carico" + punteggio alto → colore intenso (OK)
2. "carico" + punteggio basso → troppo scuro (DIFETTO)
3. "chiaro omogeneo" → OTTIMO
4. "paglierino" → colore tipico, POSITIVO
5. Qualsiasi riferimento a "alone", "macchie", "fascia" → preservare come DIFETTO

---

### 1.7 SPESSORE DELLA CROSTA (Media 2018: 7.14, Std: 0.78)

**PUNTEGGI ALTI (8-10):**
- mm/cm (misure precise - descrittivo)
- media (27 occorrenze - POSITIVO)
- sottile (24 occorrenze - POSITIVO)
- fine (17 occorrenze - POSITIVO)
- piatti (21 occorrenze - riferimento anatomico)

**PUNTEGGI BASSI (1-4):**
- spessa (4 occorrenze - NEGATIVO)
- crostone (1 occorrenza - NEGATIVO)

**Scale qualitative:**
- OTTIMA: "sottile", "fine", "media"
- ACCETTABILE: "media"
- DIFETTOSA: "spessa", "crostone", "eccessiva"

**Termini anatomici da preservare:**
- scalzo/scalzi (lato verticale)
- piatti/piatto (superfici piane)
- angoli, spigoli
- sottocrosta (zona sotto crosta)

**REGOLE:**
1. Preservare misure numeriche quando presenti (es. "5-6 mm")
2. "sottile" e "fine" → POSITIVI
3. "spessa" → NEGATIVO
4. Termini anatomici (scalzo, piatti) → preservare sempre

---

## 2. ESPANSIONI ABBREVIAZIONI

**Basato su analisi sezione 3.2 e 3.4 del report**

### Abbreviazioni identificate con alta frequenza:

| Abbreviazione | Espansione | Frequenza | Contesto Esempio |
|---------------|------------|-----------|------------------|
| leg | leggermente | 61 | "leg cotto" → "leggermente cotto" |
| legg | leggermente | 47 | variante di "leg" |
| legg. | leggermente | 3 | con punto finale |
| abb | abbastanza | 22 | "abb carico" → "abbastanza carico" |
| sol | solubile | 47 | "abbastanza sol" → "abbastanza solubile" |
| po | poco | 99 | "un po" → "un poco" |
| po' | poco | 146 | già corretto con apostrofo, preservare |
| piu | più | 24 | "piu chiaro" → "più chiaro" |
| all | all' | 119 | "all olfatto" → "all'olfatto" |
| ben | bene/ben | 66 | "ben intenso" → preservare |
| nan | [VUOTO] | 49 | valore mancante, rimuovere |

### Apostrofi mancanti (caratteri accentati):

| Forma Errata | Forma Corretta |
|--------------|----------------|
| intensita' | intensità |
| sapidit' | sapidità |
| solubilit' | solubilità |
| friabilit' | friabilità |

### Punti finali inutili:

| Forma | Azione |
|-------|--------|
| fine. | rimuovi punto → "fine" |
| sale. | rimuovi punto → "sale" |
| cm. | rimuovi punto → "cm" |
| mm. | rimuovi punto → "mm" |

**REGOLA GENERALE:**
- Espandi abbreviazioni comuni (leg, abb, sol)
- Correggi apostrofi mancanti
- Rimuovi punti finali quando inappropriati
- Preserva terminologia tecnica anche se abbreviata (es. "mm", "cm" OK senza espansione a millimetri/centimetri)

---

## 3. TERMINI TECNICI CASEARI (NON MODIFICARE)

**Questi termini appartengono al dominio tecnico caseario e vanno preservati invariati:**

### Anatomia della forma:
- **scalzo/scalzi** (lato verticale cilindrico della forma)
- **piatti/piatto** (superfici piane superiore e inferiore)
- **sottocrosta** (zona della pasta immediatamente sotto la crosta)
- **angoli, spigoli** (bordi tra piatti e scalzo)

### Caratteristiche struttura:
- **microocchiatura** (piccoli buchi <2mm nella pasta)
- **occhiatura** (buchi più grandi nella pasta)
- **grana** (texture granulare tipica - NON confondere con il formaggio "grana")
- **frattura** (tipo di rottura della pasta: stirata, radiale, ecc.)
- **stirata** (tipo specifico di frattura)
- **cristalli/tirosina** (cristalli di aminoacido - caratteristica positiva)
- **granulosa/granuloso** (texture granulare fine)
- **grossolana** (texture granulare grossa)

### Riferimenti a formaggi/processi:
- **nostrano** (formaggio tipo Trentingrana molto stagionato)
- **insilato** (odore di foraggio insilato - difetto)
- **gorgonzola** (quando usato come riferimento olfattivo)

### Altri termini specialistici:
- **solubile/solubilità** (riferito a come si scioglie in bocca)
- **friabile/friabilità** (riferito a come si sbriciola)
- **compatto/compattezza**
- **cedevole**

**REGOLA:** Se un termine appare nella lista sopra, NON espandere, NON modificare, NON tradurre.

---

## 4. GESTIONE COMMENTI VUOTI

### 4.1 Per anno 2018 (con punteggi individuali)

**Logica basata su punteggio numerico del panelista:**
IF commento_vuoto AND punteggio >= 6.5 AND punteggio <= 7.5:
→ sostituisci con "nella norma" o "regolare"
IF commento_vuoto AND punteggio < 5:
→ FLAG per review manuale (possibile difetto non commentato)
→ tag: [REVIEW_BASSO_PUNTEGGIO_NO_COMMENT]
IF commento_vuoto AND punteggio > 8.5:
→ FLAG per review manuale (ottimo ma non spiegato)
→ tag: [REVIEW_ALTO_PUNTEGGIO_NO_COMMENT]
IF commento_vuoto AND punteggio tra 5-6.5 OR 7.5-8.5:
→ mantieni vuoto, annota in metadata
→ sarà escluso dall'aggregazione se altri panelisti hanno commentato

### 4.2 Per anni 2019-2021 (senza punteggi individuali)

**Strategia:**
1. Cercare punteggio aggregato giuria in file `Risultati_2019-21.xlsx`
2. Se disponibile, applicare logica simile al 2018 ma su media giuria
3. Se NON disponibile → lasciare vuoto, flaggare per potenziale esclusione

**Statistiche commenti vuoti (da report 4.2):**
- 2018: 685-700 per attributo (44-43%)
- 2019-2021: 1-17 per attributo (1-37%)

**REGOLA:** I commenti vuoti sono accettabili se punteggio medio ~7. Flaggare outlier.

---

## 5. PULIZIA ENCODING E NORMALIZZAZIONE

### 5.1 Encoding

**Problema:** File 2021 contengono 430 caratteri `\xa0` (non-breaking space)

**Soluzione:**
```python
# Applicare sistematicamente a tutti i commenti
text = text.replace('\xa0', ' ')    # non-breaking space → spazio normale
text = text.replace('\u00a0', ' ')  # forma Unicode alternativa
text = re.sub(r'\s+', ' ', text)    # doppi/multipli spazi → spazio singolo
text = text.strip()                  # rimuovi spazi inizio/fine
```

### 5.2 Capitalizzazione Attributi

**Standardizzazione nomi attributi (problema sezione 4.4):**

| Variante Trovata | Forma Standard |
|------------------|----------------|
| Spessore della crosta | Spessore della Crosta |
| spessore della crosta | Spessore della Crosta |
| Struttura della pasta | Struttura della Pasta |
| struttura della pasta | Struttura della Pasta |
| Colore della pasta | Colore della Pasta |
| colore della pasta | Colore della Pasta |
| Profumo | Profumo |
| Sapore | Sapore |
| Aroma | Aroma |
| Texture | Texture |

**REGOLA:** Maiuscola su ogni parola principale.

### 5.3 Punteggiatura

**Normalizzazioni:**
- Rimuovere punti finali isolati (es. "fine." → "fine")
- Normalizzare virgole in liste (es. "burro,panna, latte" → "burro, panna, latte")
- Preservare apostrofi (es. "all'apertura", "po'")
- Rimuovere spazi prima di punteggiatura (es. "burro ." → "burro.")

---

## 6. SINONIMI DA UNIFICARE

**Basato su analisi top 20 parole (sezione 3.1)**

### Varianti morfologiche:

| Varianti | Forma Canonica | Ragione |
|----------|----------------|---------|
| lattico, lattici | lattico | singolare preferito |
| cotto, cotti | cotto | singolare preferito |
| nota, note | note | plurale più comune (78 vs 50+88) |
| omogeneo, omogenea | omogeneo | maschile standard |
| chiaro, chiara | chiaro | maschile standard |
| grossolana, grossa | grossolana | forma più specifica |
| granuloso, granulosa | granuloso | maschile standard |
| rosato, rosa (aggettivo) | rosato | forma aggettivale |
| piatto, piatti | piatti | preservare entrambi (singolare vs plurale ha significato) |
| scalzo, scalzi | scalzo/scalzi | preservare entrambi (sing/plur hanno senso) |

### Sinonimi concettuali:

| Sinonimi | Forma Preferita | Note |
|----------|-----------------|------|
| uniforme, omogeneo | omogeneo | "omogeneo" più frequente (271 vs 80) |
| regolare, nella norma | regolare | "regolare" più tecnico |
| buono, buona, bello, bella | buono/bello | preservare in contesto ("bella grana" ≠ "buona grana") |

**REGOLA:** Unificare morfologia ma preservare significati contestuali diversi.

---

## 7. GESTIONE TERMINI CONTESTUALI

**Alcuni termini cambiano significato in base a modificatori o punteggio**

### 7.1 PICCANTE (frequenza: 449)

**Contesti POSITIVI:**
- "piccante" + punteggio ≥7 → caratteristica tipica grana, POSITIVO
- "leggermente piccante" → SEMPRE POSITIVO
- "piccante equilibrato" → POSITIVO
- "piccante al punto giusto" → POSITIVO

**Contesti NEGATIVI:**
- "troppo piccante" → SEMPRE NEGATIVO
- "piccante" + punteggio ≤4 → NEGATIVO
- "eccessivamente piccante" → NEGATIVO

**REGOLA:** Preservare SEMPRE il modificatore ("leggermente", "troppo", "molto")

### 7.2 AMARO (frequenza: 301)

**Contesti POSITIVI:**
- "leggermente amaro" → POSITIVO (complessità)
- "amaro equilibrato" → POSITIVO
- "nota amara" + punteggio alto → POSITIVO

**Contesti NEGATIVI:**
- "amaro" da solo + punteggio ≤5 → NEGATIVO
- "troppo amaro" → SEMPRE NEGATIVO
- "amarognolo sgradevole" → NEGATIVO

### 7.3 CARICO (frequenza: 485)

**Contesti POSITIVI (Colore):**
- "giallo carico" + punteggio alto → colore intenso, POSITIVO
- "colore carico omogeneo" → POSITIVO

**Contesti NEGATIVI (Colore):**
- "carico" + punteggio basso → troppo scuro, DIFETTO
- "troppo carico" → DIFETTO

### 7.4 Modificatori Chiave

**Preservare SEMPRE questi modificatori:**
- **troppo** → indica ECCESSO (negativo)
- **leggermente** → indica MODERAZIONE (positivo/neutro)
- **abbastanza** → neutro
- **molto** → intensificatore (contestuale)
- **eccessivamente** → eccesso (negativo)
- **appena** → lieve presenza
- **ben** → buona qualità

---

## 8. STRATEGIA AGGREGAZIONE MULTI-PANELISTA

**Basato su varianza inter-panelista (sezione 2.2): Std media ~0.7-0.8**

### 8.1 Approccio generale

**La varianza 0.7-0.8 indica buona concordanza** → aggregazione fattibile

**Pipeline:**
1. Normalizzare ogni commento individualmente (espandi abbreviazioni, encoding, ecc.)
2. Estrarre concetti chiave da ogni commento
3. Confrontare concetti tra panelisti
4. Generare commento consenso

### 8.2 Strategia concreta

**CASO 1: Accordo forte (>70% panelisti concordano)**
- Esempio: 7/10 dicono "burro", 2/10 "panna", 1/10 vuoto
- Output: "Profumo di burro e panna"

**CASO 2: Accordo parziale (40-70%)**
- Esempio: 4/10 "intenso", 3/10 "moderato", 3/10 "leggero"
- Soluzione: Usare punteggio numerico medio
  - Se media ≥7.5 → "intenso"
  - Se media 6.5-7.5 → "moderato"
  - Se media <6.5 → "leggero"

**CASO 3: Disaccordo (nessuna maggioranza)**
- Esempio: tutti termini diversi, nessuna sovrapposizione
- Soluzione: Riportare range o termini multipli
  - "Profumo variabile con note di burro, vegetale e tostato"

**CASO 4: Difetti (preservare SEMPRE)**
- Se anche 1 solo panelista riporta difetto → PRESERVARE
- Esempio: 9/10 "OK", 1/10 "alone centrale"
- Output: "Colore generalmente omogeneo con possibile alone centrale in alcuni campioni"

### 8.3 Gestione commenti generici

**Commenti tipo "ok", "buono", "regolare" (sezione 3.2):**
- Se punteggio disponibile → interpretare:
  - "ok" + punteggio 7-8 → "nella norma, qualità buona"
  - "ok" + punteggio 6-7 → "regolare"
  - "ok" + punteggio <6 → flag per review
- Se punteggio NON disponibile → considerare poco informativo, dare peso minore

### 8.4 Esempio pratico di aggregazione

**Input (3 panelisti, stesso campione, attributo Profumo):**
- Panelista 1 (punteggio 7.5): "burro e panna, leg intenso"
- Panelista 2 (punteggio 7.2): "latte cotto, abbastanza forte"
- Panelista 3 (punteggio 7.8): "burro, tostato"

**Output aggregato:**
"Profumo pronunciato con note predominanti di burro e panna, accompagnate da sentori di latte cotto e tostato"

---

## 9. PRIORITÀ IMPLEMENTAZIONE

### FASE A - Pulizia Minima (IMMEDIATA)
**Obiettivo:** Rendere i dati leggibili e consistenti

1. **Encoding:**
   - Sostituire `\xa0` → spazio
   - Rimuovere doppi spazi
   - Trim inizio/fine

2. **Abbreviazioni comuni:**
   - leg → leggermente
   - abb → abbastanza
   - sol → solubile
   - po → poco
   - piu → più

3. **Apostrofi:**
   - intensita' → intensità
   - sapidit' → sapidità
   - solubilit' → solubilità

4. **Capitalizzazione attributi:**
   - Standardizzare a "Maiuscola Ogni Parola"

5. **Rimozione punti finali:**
   - "fine." → "fine"

**Output:** Dataset leggibile, pronto per analisi

### FASE B - Normalizzazione Termini (SUCCESSIVA)
**Obiettivo:** Unificare vocabolario

1. **Sinonimi:**
   - lattico/lattici → lattico
   - omogeneo/omogenea → omogeneo
   - chiaro/chiara → chiaro

2. **Espansione completa:**
   - Tutte le abbreviazioni rimanenti
   - Correzione typo evidenti

3. **Gestione commenti vuoti:**
   - Applicare logica basata su punteggi
   - Flaggare outlier

**Output:** Vocabolario consistente

### FASE C - Arricchimento (FINALE)
**Obiettivo:** Generare caption di qualità

1. **Applicazione vocabolario controllato:**
   - Mappare termini → scale qualitative
   - Gestire contesti (troppo/leggermente)

2. **Aggregazione multi-panelista:**
   - Sintetizzare commenti multipli
   - Preservare difetti

3. **Costruzione frasi complete:**
   - Da "leg cotto, burro" → "Profumo leggermente cotto con note di burro"

**Output:** Caption eleganti e complete

---

## 10. ESEMPI CONCRETI DI APPLICAZIONE

### Esempio 1: PROFUMO (Fase A → Fase B → Fase C)

**Originale (grezzo):**
"leg  cotto, burro intensita' media"

**Dopo Fase A (pulizia minima):**
"leggermente cotto, burro intensità media"

**Dopo Fase B (normalizzazione):**
"leggermente cotto, burro, intensità media"

**Dopo Fase C (arricchimento):**
"Profumo moderatamente intenso con note di cotto e burro"

---

### Esempio 2: SAPORE (gestione contestuale)

**Originale:**
"troppo piccante, abb amaro"

**Dopo Fase A:**
"troppo piccante, abbastanza amaro"

**Dopo Fase B:**
"troppo piccante, abbastanza amaro"

**Dopo Fase C (con punteggio 4.5 - basso):**
"Sapore sbilanciato con piccantezza eccessiva e amaro marcato (difetto)"

**Alternativa (con punteggio 7.5 - alto):**
"Sapore complesso con piccantezza pronunciata ed equilibrato retrogusto amarognolo"

---

### Esempio 3: COLORE PASTA (aggregazione multi-panelista)

**Input (3 panelisti):**
- P1 (punt. 8.0): "chiaro, omogeneo, paglierino"
- P2 (punt. 7.5): "giallo chiaro uniforme"
- P3 (punt. 6.5): "alone centrale rosa, resto ok"

**Output aggregato (Fase C):**
"Colore giallo paglierino chiaro, generalmente omogeneo con presenza di alone rosato centrale in zona limitata"

**Ragione:** Preservato il difetto (alone) riportato da 1 panelista

---

### Esempio 4: STRUTTURA PASTA (termini tecnici)

**Originale:**
"frattura stirata, grana fine, bella microocchiatura diffusa"

**Dopo Fase A:**
"frattura stirata, grana fine, bella microocchiatura diffusa"
(NESSUNA modifica - termini tecnici preservati)

**Dopo Fase C:**
"Struttura con frattura stirata regolare, grana fine e microocchiatura diffusa ben distribuita"

---

### Esempio 5: TEXTURE (commento vuoto con punteggio)

**Originale:**
[commento vuoto], punteggio: 7.2

**Dopo Fase A-B:**
"nella norma"

**Dopo Fase C (con contesto altri attributi se disponibili):**
"Texture regolare, nella norma per la tipologia"

---

## 11. VALIDAZIONE E CONTROLLO QUALITÀ

**Dopo l'applicazione delle regole, verificare:**

1. **Consistenza vocabolario:**
   - Nessun sinonimo residuo
   - Abbreviazioni tutte espanse
   - Capitalizzazione uniforme

2. **Preservazione difetti:**
   - Tutti i termini negativi preservati
   - Nessuna censura di problemi

3. **Leggibilità:**
   - Frasi grammaticalmente corrette
   - Lunghezza caption ragionevole (30-100 parole)

4. **Tracciabilità:**
   - Log di tutte le modifiche
   - Possibilità di risalire al commento originale

---

## 12. NOTE FINALI

**Statistiche dataset pulito attese:**
- Commenti totali: ~10.000
- Commenti utilizzabili (post-pulizia): ~8.500-9.000
- Caption aggregate finali: ~600-800 (uno per campione)

**Principi guida:**
1. Preservare informazione > Eleganza formale
2. Difetti sempre espliciti
3. Terminologia tecnica invariata
4. Tracciabilità completa

---

**Fine documento regole pulizia**
