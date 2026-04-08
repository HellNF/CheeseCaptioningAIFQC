# REPORT PULIZIA FASE A - Commenti Grana Trentino

**Data elaborazione:** 2026-02-13 18:01:58

---

## 1. STATISTICHE AGGREGATE

- **Righe totali processate:** 13261
- **Modifiche totali applicate:** 2840
- **Encoding fixes (\xa0, spazi):** 2214
- **Punti finali rimossi:** 253
- **Valori 'nan' sostituiti:** 3205

### 1.1 Espansioni Abbreviazioni

| Abbreviazione | Espansione | Occorrenze |
|---------------|------------|------------|
| legg | leggermente | 102 |
| leg | leggermente | 60 |
| sol | solubile | 47 |
| abb | abbastanza | 22 |
| piu | più | 16 |
| piu' | più | 8 |

### 1.2 Correzioni Apostrofi

| Forma Errata | Forma Corretta | Occorrenze |
|--------------|----------------|------------|
| sapidit' | sapidità | 43 |
| solubilit' | solubilità | 24 |
| intensita' | intensità | 22 |
| friabilit' | friabilità | 16 |
| umidit' | umidità | 13 |

## 2. ESEMPI DI MODIFICHE

### 2.1 Encoding Fixes (\xa0, doppi spazi)

**Esempio 1:**
- **Prima:** `Provolone `
- **Dopo:** `Provolone`

**Esempio 2:**
- **Prima:** `Provolone `
- **Dopo:** `Provolone`

**Esempio 3:**
- **Prima:** `Non da grana `
- **Dopo:** `Non da grana`

**Esempio 4:**
- **Prima:** `Alone  centrale  molto carico `
- **Dopo:** `Alone centrale molto carico`

**Esempio 5:**
- **Prima:** `Alone centrale  rosato `
- **Dopo:** `Alone centrale rosato`

**Esempio 6:**
- **Prima:** `Colore molto chiaro ma di diverse tonalità `
- **Dopo:** `Colore molto chiaro ma di diverse tonalità`

**Esempio 7:**
- **Prima:** `Vegetale balsamico `
- **Dopo:** `Vegetale balsamico`

**Esempio 8:**
- **Prima:** `Acre `
- **Dopo:** `Acre`

**Esempio 9:**
- **Prima:** `Quasi nota acetica `
- **Dopo:** `Quasi nota acetica`

**Esempio 10:**
- **Prima:** `Molto equilibrio e complessità  delle note`
- **Dopo:** `Molto equilibrio e complessità delle note`

### 2.2 Espansioni Abbreviazioni

**abb→abbastanza:**

1. Prima: `Giallo abb carico, piu  chiaro vicino allo scalzo ` → Dopo: `Giallo abbastanza carico, più chiaro vicino allo scalzo`
2. Prima: `Uniforme, abb  chiaro` → Dopo: `Uniforme, abbastanza chiaro`
3. Prima: `Omogeneo abb  carico` → Dopo: `Omogeneo abbastanza carico`
4. Prima: `assenza di odori negativi abb intenso e positivo` → Dopo: `assenza di odori negativi abbastanza intenso e positivo`
5. Prima: `abb equilib` → Dopo: `abbastanza equilib`

**legg→leggermente:**

1. Prima: `legg stantio` → Dopo: `leggermente stantio`
2. Prima: `legg stantio` → Dopo: `leggermente stantio`
3. Prima: `legg stantio` → Dopo: `leggermente stantio`
4. Prima: `Legg  alone  centrale` → Dopo: `leggermente alone centrale`
5. Prima: `Legg  disomogeneo` → Dopo: `leggermente disomogeneo`

**leg→leggermente:**

1. Prima: `leg cotto` → Dopo: `leggermente cotto`
2. Prima: `leg cotto` → Dopo: `leggermente cotto`
3. Prima: `panna leg cotto` → Dopo: `panna leggermente cotto`
4. Prima: `leg` → Dopo: `leggermente`
5. Prima: `leg odore anomalo che non riconsoco` → Dopo: `leggermente odore anomalo che non riconsoco`

**piu'→più:**

1. Prima: `sento un po' piu' di latte che al naso` → Dopo: `sento un po' più di latte che al naso`
2. Prima: `intensita' appena piu' che leggera. note lattee mature, cotte. sentore vegetale leggero` → Dopo: `intensità appena più che leggera. note lattee mature, cotte. sentore vegetale leggero`
3. Prima: `leggero sentore di corsta di fromaggio e cotto, piu' burro` → Dopo: `leggero sentore di corsta di fromaggio e cotto, più burro`
4. Prima: `Sembra un formaggio piu' vecchio. Scarno e pungente.` → Dopo: `Sembra un formaggio più vecchio. Scarno e pungente`
5. Prima: `Sento pungente sulle mucose, anche se non vero piccante sembra piu' sale, forse perche' il primo campione perche' non lo sento troppo salato` → Dopo: `Sento pungente sulle mucose, anche se non vero piccante sembra più sale, forse perche' il primo campione perche' non lo sento troppo salato`

**piu→più:**

1. Prima: `Cavolo, odori piu evidenti all’apertura` → Dopo: `Cavolo, odori più evidenti all’apertura`
2. Prima: `poco caratteristico come al naso, ricorda i formaggi svizzeri, forse un po piu presente il burro fuso rispetto al naso` → Dopo: `poco caratteristico come al naso, ricorda i formaggi svizzeri, forse un po più presente il burro fuso rispetto al naso`
3. Prima: `da nostrano piu che da grana` → Dopo: `da nostrano più che da grana`
4. Prima: `in bocca piu lattico che al naso, panna cotta, burro fuso, molto grasso, torna la nota fruttata` → Dopo: `in bocca più lattico che al naso, panna cotta, burro fuso, molto grasso, torna la nota fruttata`
5. Prima: `Giallo piu scuro al centro` → Dopo: `Giallo più scuro al centro`

### 2.3 Correzioni Apostrofi

**friabilit'→friabilità:**

1. Prima: `molti granuli, bella friabilit'` → Dopo: `molti granuli, bella friabilità`
2. Prima: `friabilit' non perfetta. un pochetto plastico, morbido` → Dopo: `friabilità non perfetta. un pochetto plastico, morbido`
3. Prima: `buona, con equilibrio tra umidit' e friabilit'` → Dopo: `buona, con equilibrio tra umidità e friabilità`

**intensita'→intensità:**

1. Prima: `gran intensita' e tostatura retroolfattiva` → Dopo: `gran intensità e tostatura retroolfattiva`
2. Prima: `discreta intensita',` → Dopo: `discreta intensità ,`
3. Prima: `Buona intensita', non grande la complessita'. tostato` → Dopo: `Buona intensità , non grande la complessita'. tostato`
4. Prima: `una nota di stalla, formaggio cotto, tanto,  e burro. discreta l-intensita'` → Dopo: `una nota di stalla, formaggio cotto, tanto, e burro. discreta l-intensità`
5. Prima: `seppur amaro, nessuna nota prevale. anche dolce . intensita' leggera` → Dopo: `seppur amaro, nessuna nota prevale. anche dolce . intensità leggera`

**sapidit'→sapidità:**

1. Prima: `poco complesso, persistenza aromatica corta, la debolezza aromatica fa risaltare la sapidit' e quindi la nota di brodo, note lattiche carenti` → Dopo: `poco complesso, persistenza aromatica corta, la debolezza aromatica fa risaltare la sapidità e quindi la nota di brodo, note lattiche carenti`
2. Prima: `dolce sapido con buona sapidit', umami equilibrato, piccantezza ok un po marcata` → Dopo: `dolce sapido con buona sapidità , umami equilibrato, piccantezza ok un po marcata`
3. Prima: `sapidit' e acidita (pungente) medi alta` → Dopo: `sapidità e acidita (pungente) medi alta`
4. Prima: `sapidit' e umami elevati, piuttosto piccante e quasi bruciante in chiusura, leggero retrogusto amaro` → Dopo: `sapidità e umami elevati, piuttosto piccante e quasi bruciante in chiusura, leggero retrogusto amaro`

**solubilit'→solubilità:**

1. Prima: `secco e farinoso, buoni i cristalli, media solubilit'` → Dopo: `secco e farinoso, buoni i cristalli, media solubilità`
2. Prima: `eterogenea a seconda del pezzo, da umida ad asciutta con solubilit' diversa` → Dopo: `eterogenea a seconda del pezzo, da umida ad asciutta con solubilità diversa`
3. Prima: `asciutto, poca solubilit'` → Dopo: `asciutto, poca solubilità`
4. Prima: `buona solubilit'` → Dopo: `buona solubilità`

**umidit'→umidità:**

1. Prima: `media con umidit' abbastanza prevalente` → Dopo: `media con umidità abbastanza prevalente`
2. Prima: `morbido e pastoso, umidit' media e granuli medio/alti` → Dopo: `morbido e pastoso, umidità media e granuli medio/alti`
3. Prima: `molto morbido .. umidit' e pastosita molto buone, pochi granuli` → Dopo: `molto morbido .. umidità e pastosita molto buone, pochi granuli`

### 2.4 Rimozione Punti Finali

**Esempio 1:**
- **Prima:** `Texture  da modificare, troppo friabile.`
- **Dopo:** `Texture da modificare, troppo friabile`

**Esempio 2:**
- **Prima:** `Alito al Caffè ...`
- **Dopo:** `Alito al Caffè`

**Esempio 3:**
- **Prima:** `Occhiatura centrale diffusa. `
- **Dopo:** `Occhiatura centrale diffusa`

**Esempio 4:**
- **Prima:** `Disidratata...`
- **Dopo:** `Disidratata`

**Esempio 5:**
- **Prima:** `Circa al carico..`
- **Dopo:** `Circa al carico`

**Esempio 6:**
- **Prima:** `Per lo più  giallo chiaro. Un quarto laterale più  saturo.`
- **Dopo:** `Per lo più giallo chiaro. Un quarto laterale più saturo`

**Esempio 7:**
- **Prima:** `Solo leggero alone...`
- **Dopo:** `Solo leggero alone`

**Esempio 8:**
- **Prima:** `Pochi sentori pannosi. `
- **Dopo:** `Pochi sentori pannosi`

**Esempio 9:**
- **Prima:** `Polvere...`
- **Dopo:** `Polvere`

**Esempio 10:**
- **Prima:** `Kiwi...`
- **Dopo:** `Kiwi`

## 3. COMMENTI NON MODIFICATI

**Totale commenti già puliti:** 7298 (55.0%)

Questi commenti non hanno richiesto alcuna modifica, indicando che erano già
ben formattati o che non contenevano abbreviazioni/errori comuni.

## 4. DETTAGLIO PER FILE

| File | Righe | Modifiche | Encoding | Abbreviazioni | Apostrofi | Punti |
|------|-------|-----------|----------|---------------|-----------|-------|
| Commenti TOT_2018_Aroma.csv | 1561 | 57 | 11 | 14 | 2 | 30 |
| Commenti TOT_2018_Colore della Pasta.csv | 1573 | 629 | 590 | 19 | 0 | 20 |
| Commenti TOT_2018_Profumo.csv | 1573 | 107 | 16 | 38 | 20 | 33 |
| Commenti TOT_2018_Sapore.csv | 1573 | 212 | 21 | 105 | 43 | 43 |
| Commenti TOT_2018_Spessore della Crosta.csv | 1621 | 290 | 278 | 1 | 0 | 11 |
| Commenti TOT_2018_Struttura della Pasta.csv | 1573 | 722 | 668 | 9 | 1 | 44 |
| Commenti TOT_2018_Texture.csv | 1573 | 184 | 26 | 68 | 52 | 38 |
| Commenti liberi_QTG_2019_Aroma.csv | 62 | 30 | 29 | 0 | 0 | 1 |
| Commenti liberi_QTG_2019_Colore della pasta.csv | 59 | 9 | 9 | 0 | 0 | 0 |
| Commenti liberi_QTG_2019_Profumo.csv | 114 | 31 | 30 | 0 | 0 | 1 |
| Commenti liberi_QTG_2019_Sapore.csv | 71 | 25 | 25 | 0 | 0 | 0 |
| Commenti liberi_QTG_2019_Spessore della crosta.csv | 45 | 3 | 3 | 0 | 0 | 0 |
| Commenti liberi_QTG_2019_Struttura della pasta.csv | 140 | 32 | 30 | 0 | 0 | 2 |
| Commenti liberi_QTG_2019_Texture.csv | 83 | 20 | 20 | 0 | 0 | 0 |
| Commenti liberi_QTG_2020_Aroma.csv | 117 | 42 | 42 | 0 | 0 | 0 |
| Commenti liberi_QTG_2020_Colore della pasta.csv | 147 | 47 | 44 | 0 | 0 | 3 |
| Commenti liberi_QTG_2020_Profumo.csv | 233 | 87 | 77 | 0 | 0 | 10 |
| Commenti liberi_QTG_2020_Sapore.csv | 210 | 65 | 56 | 0 | 0 | 9 |
| Commenti liberi_QTG_2020_Spessore della crosta.csv | 73 | 10 | 10 | 0 | 0 | 0 |
| Commenti liberi_QTG_2020_Struttura della pasta.csv | 336 | 104 | 101 | 0 | 0 | 3 |
| Commenti liberi_QTG_2020_Texture.csv | 113 | 31 | 28 | 0 | 0 | 3 |
| Commenti liberi_TEST_2021_Aroma.csv | 55 | 9 | 7 | 0 | 0 | 2 |
| Commenti liberi_TEST_2021_Colore della Pasta.csv | 63 | 20 | 20 | 0 | 0 | 0 |
| Commenti liberi_TEST_2021_Profumo.csv | 57 | 11 | 10 | 1 | 0 | 0 |
| Commenti liberi_TEST_2021_Sapore.csv | 54 | 8 | 8 | 0 | 0 | 0 |
| Commenti liberi_TEST_2021_Spessore della Crosta.csv | 50 | 14 | 14 | 0 | 0 | 0 |
| Commenti liberi_TEST_2021_Struttura della Pasta.csv | 84 | 33 | 33 | 0 | 0 | 0 |
| Commenti liberi_TEST_2021_Texture.csv | 48 | 8 | 8 | 0 | 0 | 0 |

---

**Note:**
- Modifiche totali possono includere più interventi sullo stesso commento
- I commenti vuoti ('nan') sono stati sostituiti con stringhe vuote
- Le abbreviazioni sono state espanse usando word boundaries per evitare falsi positivi
