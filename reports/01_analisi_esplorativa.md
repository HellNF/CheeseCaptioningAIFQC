# Analisi Esplorativa - Dataset Grana Trentino

**Data generazione:** 2026-02-10
**Script:** `src/data/01_exploratory_analysis.py`

---

## 1. Analisi Struttura File

### 1.1 File Excel Commenti Liberi

| File | Anno | N. Fogli | Fogli |
|------|------|----------|-------|
| Commenti TOT_2018.xlsx | 2018 | 8 | Profumo, Sapore, Aroma, Texture, Spessore della Crosta, Struttura della Pasta, Colore della Pasta, date_sedute_2018 |
| Commenti liberi_QTG_2019.xlsx | 2019 | 7 | Profumo, Sapore, Aroma, Texture, Spessore della crosta, Struttura della pasta, Colore della pasta |
| Commenti liberi_QTG_2020.xlsx | 2020 | 7 | Profumo, Sapore, Aroma, Texture, Spessore della crosta, Struttura della pasta, Colore della pasta |
| Commenti liberi_TEST_2021.xlsx | 2021 | 7 | Profumo, Sapore, Aroma, Texture, Spessore della Crosta, Struttura della Pasta, Colore della Pasta |

### 1.2 Dettaglio per Foglio

| File | Foglio | Righe | Colonne | Schema |
|------|--------|-------|---------|--------|
| Commenti TOT_2018.xlsx | Profumo | 1573 | 5 | Sogg, Seduta, Prod, Profumo , Commenti  |
| Commenti TOT_2018.xlsx | Sapore | 1573 | 5 | Sogg, Seduta, Prod, Sapore, Commenti |
| Commenti TOT_2018.xlsx | Aroma | 1561 | 5 | Sogg, Seduta, Prod, Aroma, Commenti |
| Commenti TOT_2018.xlsx | Texture | 1573 | 5 | Sogg, Seduta, Prod, Texture, Commenti |
| Commenti TOT_2018.xlsx | Spessore della Crosta | 1621 | 5 | Sogg, Seduta, Prod, Spessore della Crosta, Commenti |
| Commenti TOT_2018.xlsx | Struttura della Pasta | 1573 | 5 | Sogg, Seduta, Prod, Struttura della Pasta, Commenti |
| Commenti TOT_2018.xlsx | Colore della Pasta | 1573 | 5 | Sogg, Seduta, Prod, Colore della Pasta, Commenti |
| Commenti TOT_2018.xlsx | date_sedute_2018 | 28 | 2 | Session, Date |
| Commenti liberi_QTG_2019.xlsx | Profumo | 114 | 7 | Data Seduta di valutazione, N° Seduta, Bimestre di Valutazione , Data Produzione, Panelista, ... (+2) |
| Commenti liberi_QTG_2019.xlsx | Sapore | 71 | 7 | Data Seduta di valutazione, N° Seduta, Bimestre di Valutazione , Data Produzione, Panelista, ... (+2) |
| Commenti liberi_QTG_2019.xlsx | Aroma | 62 | 7 | Data Seduta di valutazione, N° Seduta, Bimestre di Valutazione , Data Produzione, Panelista, ... (+2) |
| Commenti liberi_QTG_2019.xlsx | Texture | 83 | 7 | Data Seduta di valutazione, N° Seduta, Bimestre di Valutazione , Data Produzione, Panelista, ... (+2) |
| Commenti liberi_QTG_2019.xlsx | Spessore della crosta | 45 | 7 | Data Seduta di valutazione, N° Seduta, Bimestre di Valutazione , Data Produzione, Panelista, ... (+2) |
| Commenti liberi_QTG_2019.xlsx | Struttura della pasta | 140 | 7 | Data Seduta di valutazione, N° Seduta, Bimestre di Valutazione , Data Produzione, Panelista, ... (+2) |
| Commenti liberi_QTG_2019.xlsx | Colore della pasta | 59 | 7 | Data Seduta di valutazione, N° Seduta, Bimestre di Valutazione , Data Produzione, Panelista, ... (+2) |
| Commenti liberi_QTG_2020.xlsx | Profumo | 233 | 8 | Data Seduta di valutazione, N° Seduta, Bimestre di Valutazione , Data Produzione, Panelista, ... (+3) |
| Commenti liberi_QTG_2020.xlsx | Sapore | 210 | 7 | Data Seduta di valutazione, N° Seduta, Bimestre di Valutazione , Data Produzione, Panelista, ... (+2) |
| Commenti liberi_QTG_2020.xlsx | Aroma | 117 | 7 | Data Seduta di valutazione, N° Seduta, Bimestre di Valutazione , Data Produzione, Panelista, ... (+2) |
| Commenti liberi_QTG_2020.xlsx | Texture | 113 | 7 | Data Seduta di valutazione, N° Seduta, Bimestre di Valutazione , Data Produzione, Panelista, ... (+2) |
| Commenti liberi_QTG_2020.xlsx | Spessore della crosta | 73 | 7 | Data Seduta di valutazione, N° Seduta, Bimestre di Valutazione , Data Produzione, Panelista, ... (+2) |
| Commenti liberi_QTG_2020.xlsx | Struttura della pasta | 336 | 7 | Data Seduta di valutazione, N° Seduta, Bimestre di Valutazione , Data Produzione, Panelista, ... (+2) |
| Commenti liberi_QTG_2020.xlsx | Colore della pasta | 147 | 7 | Data Seduta di valutazione, N° Seduta, Bimestre di Valutazione , Data Produzione, Panelista, ... (+2) |
| Commenti liberi_TEST_2021.xlsx | Profumo | 57 | 8 | Data Seduta di valutazione, N° Seduta, Bimestre di Valutazione , Data Produzione, Panelista, ... (+3) |
| Commenti liberi_TEST_2021.xlsx | Sapore | 54 | 7 | Data Seduta di valutazione, N° Seduta, Bimestre di Valutazione , Data Produzione, Panelista, ... (+2) |
| Commenti liberi_TEST_2021.xlsx | Aroma | 55 | 7 | Data Seduta di valutazione, N° Seduta, Bimestre di Valutazione , Data Produzione, Panelista, ... (+2) |
| Commenti liberi_TEST_2021.xlsx | Texture | 48 | 7 | Data Seduta di valutazione, N° Seduta, Bimestre di Valutazione , Data Produzione, Panelista, ... (+2) |
| Commenti liberi_TEST_2021.xlsx | Spessore della Crosta | 50 | 7 | Data Seduta di valutazione, N° Seduta, Bimestre di Valutazione , Data Produzione, Panelista, ... (+2) |
| Commenti liberi_TEST_2021.xlsx | Struttura della Pasta | 84 | 7 | Data Seduta di valutazione, N° Seduta, Bimestre di Valutazione , Data Produzione, Panelista, ... (+2) |
| Commenti liberi_TEST_2021.xlsx | Colore della Pasta | 63 | 7 | Data Seduta di valutazione, N° Seduta, Bimestre di Valutazione , Data Produzione, Panelista, ... (+2) |

### 1.3 Differenze Schema 2018 vs 2019-2021

**Schema 2018 (5 colonne):** `['Sogg', 'Seduta', 'Prod', 'Profumo ', 'Commenti ']`

**Schema 2019-2021 (7 colonne):** `['Data Seduta di valutazione', 'N° Seduta', 'Bimestre di Valutazione ', 'Data Produzione', 'Panelista', 'Prodotto', 'Commenti']`

**Nota:** Il 2018 ha punteggi numerici individuali per panelista (colonna con nome attributo). Il 2019-2021 ha solo commenti (7 colonne, senza punteggi). Inoltre il 2018 usa 'Sogg' e 'Seduta' come identificativi, mentre il 2019-2021 usa 'Panelista' e 'Data Seduta di valutazione'.

---

## 2. Analisi Punteggi Numerici

### 2.1 Punteggi Individuali 2018

| Attributo | N | Media | Mediana | Std | Min | Max | Q25 | Q75 |
|-----------|---|-------|---------|-----|-----|-----|-----|-----|
| Aroma | 1561 | 7.07 | 7.12 | 0.83 | 4.00 | 9.70 | 6.52 | 7.66 |
| Colore della Pasta | 1568 | 7.12 | 7.10 | 0.95 | 4.00 | 9.60 | 6.50 | 7.80 |
| Profumo | 1573 | 7.30 | 7.36 | 0.79 | 4.00 | 9.52 | 6.82 | 7.90 |
| Sapore | 1573 | 6.98 | 6.94 | 0.88 | 4.00 | 9.76 | 6.46 | 7.54 |
| Spessore della Crosta | 1616 | 7.14 | 7.00 | 0.78 | 4.00 | 10.00 | 6.70 | 7.60 |
| Struttura della Pasta | 1568 | 7.01 | 7.00 | 0.98 | 4.00 | 10.00 | 6.30 | 7.80 |
| Texture | 1561 | 7.09 | 7.00 | 0.83 | 4.00 | 9.82 | 6.52 | 7.66 |

### 2.2 Varianza Inter-Panelista (2018)

Questa misura indica quanto i panelisti concordano: una deviazione standard
bassa tra panelisti significa buona concordanza.

| Attributo | Std Media | Std Mediana | Std Max | N Campioni | Media Panelisti/Campione |
|-----------|-----------|-------------|---------|------------|--------------------------|
| Aroma | 0.769 | 0.745 | 1.502 | 155 | 10.1 |
| Colore della Pasta | 0.748 | 0.685 | 1.572 | 155 | 10.1 |
| Profumo | 0.736 | 0.711 | 1.482 | 155 | 10.1 |
| Sapore | 0.832 | 0.818 | 1.403 | 155 | 10.1 |
| Spessore della Crosta | 0.664 | 0.636 | 1.690 | 155 | 10.4 |
| Struttura della Pasta | 0.734 | 0.715 | 1.532 | 155 | 10.1 |
| Texture | 0.763 | 0.741 | 1.224 | 154 | 10.1 |

### 2.3 Punteggi Aggregati Giuria (2019-2021)

#### Anno 2019

| Attributo | N | Media | Mediana | Std | Min | Max |
|-----------|---|-------|---------|-----|-----|-----|
| Aroma | 149 | 7.01 | 7.06 | 0.35 | 5.42 | 7.86 |
| Aspetto Esteriore | 149 | 6.95 | 6.96 | 0.80 | 5.00 | 9.00 |
| Colore della Pasta | 149 | 7.28 | 7.35 | 0.61 | 5.01 | 8.87 |
| Profumo | 149 | 7.26 | 7.30 | 0.34 | 5.77 | 7.98 |
| Sapore | 149 | 6.99 | 7.00 | 0.30 | 6.15 | 7.61 |
| Spessore della Crosta | 149 | 7.16 | 7.19 | 0.30 | 6.30 | 8.06 |
| Struttura della Pasta | 149 | 7.07 | 7.21 | 0.72 | 5.19 | 8.35 |

#### Anno 2020

| Attributo | N | Media | Mediana | Std | Min | Max |
|-----------|---|-------|---------|-----|-----|-----|
| Aroma | 162 | 7.16 | 7.20 | 0.35 | 5.93 | 7.95 |
| Aspetto Esteriore | 162 | 6.82 | 6.75 | 0.81 | 4.94 | 8.62 |
| Colore della Pasta | 162 | 7.36 | 7.42 | 0.53 | 5.15 | 8.62 |
| Profumo | 162 | 7.34 | 7.37 | 0.33 | 6.10 | 8.04 |
| Sapore | 162 | 7.02 | 7.05 | 0.33 | 6.20 | 7.83 |
| Spessore della Crosta | 162 | 7.12 | 7.11 | 0.35 | 5.98 | 7.89 |
| Struttura della Pasta | 162 | 6.99 | 7.20 | 0.85 | 4.89 | 8.44 |

#### Anno 2021

| Attributo | N | Media | Mediana | Std | Min | Max |
|-----------|---|-------|---------|-----|-----|-----|
| Aroma | 166 | 7.00 | 7.07 | 0.42 | 5.78 | 7.85 |
| Aspetto Esteriore | 166 | 6.79 | 6.75 | 0.87 | 5.16 | 8.77 |
| Colore della Pasta | 166 | 7.02 | 7.10 | 0.73 | 4.48 | 8.50 |
| Profumo | 166 | 7.13 | 7.21 | 0.44 | 5.59 | 7.92 |
| Sapore | 166 | 6.83 | 6.83 | 0.43 | 5.59 | 7.74 |
| Spessore della Crosta | 166 | 6.97 | 6.96 | 0.47 | 6.03 | 8.18 |
| Struttura della Pasta | 166 | 6.75 | 6.83 | 0.96 | 4.67 | 8.69 |
| Texture | 166 | 6.75 | 6.71 | 0.52 | 5.47 | 8.07 |

### 2.4 Grafici

![punteggi_2018_distribuzione](reports\figures\punteggi_2018_distribuzione.png)

![punteggi_aggregati_boxplot](reports\figures\punteggi_aggregati_boxplot.png)

![correlazione_attributi_2018](reports\figures\correlazione_attributi_2018.png)

![varianza_inter_panelista_2018](reports\figures\varianza_inter_panelista_2018.png)

---

## 3. Analisi Testuale Commenti

### 3.1 Top 20 Parole per Attributo (tutti gli anni)

#### Aroma

| # | Parola | Frequenza |
|---|--------|-----------|
| 1 | cotto | 238 |
| 2 | burro | 142 |
| 3 | formaggio | 136 |
| 4 | crosta | 128 |
| 5 | latte | 111 |
| 6 | panna | 96 |
| 7 | brodo | 93 |
| 8 | grana | 81 |
| 9 | note | 78 |
| 10 | lattico | 53 |
| 11 | fuso | 50 |
| 12 | leggero | 50 |
| 13 | nota | 50 |
| 14 | tostato | 49 |
| 15 | animale | 44 |
| 16 | vegetale | 38 |
| 17 | aroma | 36 |
| 18 | fermentato | 36 |
| 19 | cotti | 33 |
| 20 | lattici | 33 |

#### Colore della Pasta

| # | Parola | Frequenza |
|---|--------|-----------|
| 1 | carico | 485 |
| 2 | alone | 364 |
| 3 | chiaro | 282 |
| 4 | omogeneo | 271 |
| 5 | giallo | 263 |
| 6 | centrale | 232 |
| 7 | centro | 192 |
| 8 | colore | 154 |
| 9 | rosa | 139 |
| 10 | paglierino | 132 |
| 11 | piatto | 116 |
| 12 | scuro | 106 |
| 13 | abbastanza | 93 |
| 14 | verso | 91 |
| 15 | chiara | 86 |
| 16 | uniforme | 80 |
| 17 | tendente | 71 |
| 18 | sotto | 65 |
| 19 | rosato | 64 |
| 20 | macchia | 64 |

#### Profumo

| # | Parola | Frequenza |
|---|--------|-----------|
| 1 | burro | 253 |
| 2 | cotto | 243 |
| 3 | latte | 218 |
| 4 | panna | 172 |
| 5 | intenso | 142 |
| 6 | leggero | 141 |
| 7 | brodo | 120 |
| 8 | intensità | 118 |
| 9 | note | 107 |
| 10 | vegetale | 102 |
| 11 | crosta | 98 |
| 12 | fuso | 93 |
| 13 | formaggio | 89 |
| 14 | nota | 88 |
| 15 | tostato | 77 |
| 16 | frutta | 69 |
| 17 | all | 66 |
| 18 | apertura | 60 |
| 19 | fermentato | 59 |
| 20 | fruttato | 57 |

#### Sapore

| # | Parola | Frequenza |
|---|--------|-----------|
| 1 | piccante | 449 |
| 2 | salato | 425 |
| 3 | amaro | 301 |
| 4 | dolce | 247 |
| 5 | umami | 237 |
| 6 | acido | 210 |
| 7 | leggermente | 177 |
| 8 | equilibrato | 176 |
| 9 | po | 99 |
| 10 | sapido | 90 |
| 11 | troppo | 64 |
| 12 | piccantezza | 62 |
| 13 | sale | 60 |
| 14 | nota | 53 |
| 15 | medio | 52 |
| 16 | abbastanza | 50 |
| 17 | leg | 48 |
| 18 | legg | 47 |
| 19 | finale | 47 |
| 20 | leggero | 43 |

#### Spessore della Crosta

| # | Parola | Frequenza |
|---|--------|-----------|
| 1 | mm | 312 |
| 2 | media | 140 |
| 3 | cm | 139 |
| 4 | piatto | 112 |
| 5 | spessa | 92 |
| 6 | crosta | 89 |
| 7 | colore | 88 |
| 8 | piatti | 79 |
| 9 | spigoli | 75 |
| 10 | sottile | 68 |
| 11 | scalzo | 62 |
| 12 | scalzi | 60 |
| 13 | sottocrosta | 54 |
| 14 | angoli | 50 |
| 15 | evidente | 49 |
| 16 | sfumata | 49 |
| 17 | fine | 47 |
| 18 | sotto | 43 |
| 19 | lato | 40 |
| 20 | circa | 33 |

#### Struttura della Pasta

| # | Parola | Frequenza |
|---|--------|-----------|
| 1 | frattura | 531 |
| 2 | grana | 481 |
| 3 | stirata | 280 |
| 4 | regolare | 251 |
| 5 | centrale | 206 |
| 6 | struttura | 184 |
| 7 | microocchiatura | 183 |
| 8 | omogenea | 181 |
| 9 | fine | 172 |
| 10 | occhiatura | 160 |
| 11 | grossolana | 148 |
| 12 | bella | 139 |
| 13 | centro | 137 |
| 14 | granulosa | 124 |
| 15 | irregolare | 109 |
| 16 | diffusa | 107 |
| 17 | presenza | 105 |
| 18 | abbastanza | 102 |
| 19 | qualche | 98 |
| 20 | mm | 98 |

#### Texture

| # | Parola | Frequenza |
|---|--------|-----------|
| 1 | cristalli | 382 |
| 2 | solubile | 273 |
| 3 | asciutto | 254 |
| 4 | friabile | 203 |
| 5 | morbido | 174 |
| 6 | pastoso | 154 |
| 7 | grana | 125 |
| 8 | granuloso | 123 |
| 9 | pochi | 100 |
| 10 | bocca | 96 |
| 11 | fine | 88 |
| 12 | granulosa | 87 |
| 13 | abbastanza | 79 |
| 14 | compatto | 78 |
| 15 | umido | 75 |
| 16 | microstruttura | 69 |
| 17 | tirosina | 64 |
| 18 | cedevole | 64 |
| 19 | po | 56 |
| 20 | lascia | 56 |

### 3.2 Pattern Telegrafici e Abbreviazioni

- **Commenti totali analizzati:** 10104
- **Commenti vuoti:** 0
- **Lunghezza media commento:** 33.9 caratteri

**Abbreviazioni più frequenti:**

| Abbreviazione | Frequenza |
|---------------|-----------|
| fine. | 37 |
| sale. | 9 |
| cm. | 7 |
| pane. | 6 |
| mm. | 5 |
| kiwi. | 4 |
| zone. | 4 |
| aree. | 3 |
| legg. | 3 |
| naso. | 2 |
| poco. | 2 |
| poi. | 2 |
| uht. | 2 |
| km. | 2 |
| zona. | 2 |
| fini. | 2 |
| alta. | 1 |
| che. | 1 |
| male. | 1 |
| all. | 1 |

**Commenti generici ricorrenti:**

- "regolare" (18x)
- "nella norma" (2x)
- "ok" (1x)
- "buono" (1x)
- "buona" (1x)

### 3.3 Termini Associati a Punteggi Alti vs Bassi (2018)

#### Aroma

| Punteggi Alti (8-10) | Freq | Punteggi Bassi (1-4) | Freq |
|----------------------|------|----------------------|------|
| cotto | 46 | fermentato | 2 |
| burro | 40 | fieno | 1 |
| panna | 34 | pungente | 1 |
| latte | 28 | animale | 1 |
| fuso | 15 | marcio | 1 |
| formaggio | 13 | gorgonzola | 1 |
| crosta | 12 | tipico | 1 |
| brodo | 11 | acido | 1 |
| tostato | 9 | disgustoso | 1 |
| grana | 8 | vecchio | 1 |

#### Colore della Pasta

| Punteggi Alti (8-10) | Freq | Punteggi Bassi (1-4) | Freq |
|----------------------|------|----------------------|------|
| chiaro | 96 | carico | 7 |
| omogeneo | 94 | rosa | 4 |
| paglierino | 58 | alone | 3 |
| carico | 46 | centrale | 3 |
| giallo | 45 | macchie | 3 |
| colore | 25 | paglierino | 3 |
| abbastanza | 24 | anello | 2 |
| uniforme | 23 | piatto | 2 |
| chiara | 19 | fascia | 2 |
| omogenea | 19 | centrali | 2 |

#### Profumo

| Punteggi Alti (8-10) | Freq | Punteggi Bassi (1-4) | Freq |
|----------------------|------|----------------------|------|
| burro | 93 | putrido | 4 |
| panna | 80 | pezzi | 2 |
| latte | 77 | marcio | 2 |
| cotto | 55 | pozzo | 2 |
| intenso | 31 | solo | 1 |
| brodo | 30 | spezzando | 1 |
| tostato | 28 | momento | 1 |
| fuso | 27 | frattura | 1 |
| grana | 26 | avverte | 1 |
| fruttato | 25 | puzza | 1 |

#### Sapore

| Punteggi Alti (8-10) | Freq | Punteggi Bassi (1-4) | Freq |
|----------------------|------|----------------------|------|
| dolce | 69 | amaro | 5 |
| equilibrato | 60 | piccante | 4 |
| piccante | 48 | acido | 3 |
| amaro | 27 | cotto | 1 |
| salato | 24 | salato | 1 |
| umami | 23 |  |  |
| leggermente | 18 |  |  |
| acido | 12 |  |  |
| nota | 11 |  |  |
| pieno | 11 |  |  |

#### Spessore della Crosta

| Punteggi Alti (8-10) | Freq | Punteggi Bassi (1-4) | Freq |
|----------------------|------|----------------------|------|
| mm | 60 | spessa | 4 |
| media | 27 | mm | 3 |
| sottile | 24 | piuttosto | 2 |
| cm | 22 | cm | 2 |
| piatti | 21 | piatti | 1 |
| fine | 17 | sottili | 1 |
| crosta | 16 | limite | 1 |
| spigoli | 13 | sfumato | 1 |
| spessore | 10 | crostone | 1 |
| sfumata | 10 | soprattutto | 1 |

#### Struttura della Pasta

| Punteggi Alti (8-10) | Freq | Punteggi Bassi (1-4) | Freq |
|----------------------|------|----------------------|------|
| grana | 126 | mm | 5 |
| frattura | 114 | occhi | 3 |
| regolare | 86 | grana | 2 |
| fine | 74 | brutta | 2 |
| omogenea | 62 | tipica | 2 |
| bella | 55 | stirata | 2 |
| granulosa | 38 | occhio | 2 |
| struttura | 37 | due | 1 |
| abbastanza | 28 | punti | 1 |
| grossolana | 23 | essudato | 1 |

#### Texture

| Punteggi Alti (8-10) | Freq | Punteggi Bassi (1-4) | Freq |
|----------------------|------|----------------------|------|
| cristalli | 73 | so | 1 |
| friabile | 51 | docuto | 1 |
| solubile | 41 | sputarlo | 1 |
| asciutto | 30 | fuori | 1 |
| bocca | 25 | standard | 1 |
| buona | 24 | sbrinz | 1 |
| fine | 24 | solubilità | 1 |
| abbastanza | 24 | friabilità | 1 |
| granuloso | 22 | scarse | 1 |
| morbido | 17 | molle | 1 |

### 3.4 Termini Dialettali e Abbreviazioni Non Standard

| Termine | Tipo | Frequenza | Contesto Esempio |
|---------|------|-----------|------------------|
| non | possibile_abbreviazione | 984 | Non da grana |
| con | possibile_abbreviazione | 751 | Fascia bianca con zona diffusa rosa |
| più | possibile_abbreviazione | 585 | Più povero che all' olfatto |
| una | possibile_abbreviazione | 215 | Molte macchie rosa che ddanno una Fascia |
| po' | termine_con_apostrofo | 146 |  |
| che | possibile_abbreviazione | 143 | Più povero che all' olfatto |
| all | possibile_abbreviazione | 119 | Più povero che all' olfatto |
| piatti | termine_dominio_caseario | 106 | Alone è rivolto più verso uno dei due piatti |
| per | possibile_abbreviazione | 104 | Ok ti sentiti tutti molto leggeri di profumo. Forse perché l |
| scalzo | termine_dominio_caseario | 100 | Non ho tenuto conto della macchia dovuta ad una "correzione" |
| nel | possibile_abbreviazione | 99 | Presenza di una potenziale macchia al centro NON CONSIDERATA |
| scalzi | termine_dominio_caseario | 94 | Diverso tra i due scalzi |
| del | possibile_abbreviazione | 92 | Colore buono senza calcolare la zona del difetto vicino allo |
| poi | possibile_abbreviazione | 68 | Al primo olfatto e poi all'Aroma sentori di nostrano, che va |
| ben | possibile_abbreviazione | 66 | Ben intenso |
| uno | possibile_abbreviazione | 62 | Alone è rivolto più verso uno dei due piatti |
| leg | possibile_abbreviazione | 61 | leg cotto |
| nan | possibile_abbreviazione | 49 | nan |
| sol | possibile_abbreviazione | 47 | grana e cristalli evidenti abbastanza sol |
| sapidit' | termine_con_apostrofo | 44 |  |
| gli | possibile_abbreviazione | 43 | Pasta disidratata sotto gli scalzi |
| nostrano | termine_dominio_caseario | 42 | Provolone o nostrano lievemente piccante |
| all'apertura | termine_con_apostrofo | 41 |  |
| due | possibile_abbreviazione | 39 | Alone è rivolto più verso uno dei due piatti |
| tra | possibile_abbreviazione | 38 | Prima olfazione: tra animale e stalla |
| piu | possibile_abbreviazione | 24 | Cavolo, odori piu evidenti all’apertura |
| solubilit' | termine_con_apostrofo | 23 |  |
| abb | possibile_abbreviazione | 22 | Giallo abb carico, piu chiaro vicino allo scalzo |
| intensita' | termine_con_apostrofo | 21 |  |
| insilato | termine_dominio_caseario | 18 | Insilato |

### 3.5 Grafici

![top20_parole_per_attributo](reports\figures\top20_parole_per_attributo.png)

![termini_alti_vs_bassi_profumo](reports\figures\termini_alti_vs_bassi_profumo.png)

![termini_alti_vs_bassi_sapore](reports\figures\termini_alti_vs_bassi_sapore.png)

![termini_alti_vs_bassi_aroma](reports\figures\termini_alti_vs_bassi_aroma.png)

![termini_alti_vs_bassi_texture](reports\figures\termini_alti_vs_bassi_texture.png)

![termini_alti_vs_bassi_spessore_della_crosta](reports\figures\termini_alti_vs_bassi_spessore_della_crosta.png)

![termini_alti_vs_bassi_struttura_della_pasta](reports\figures\termini_alti_vs_bassi_struttura_della_pasta.png)

![termini_alti_vs_bassi_colore_della_pasta](reports\figures\termini_alti_vs_bassi_colore_della_pasta.png)

---

## 4. Problemi Qualità Dati

### 4.1 Problemi di Encoding

| File | Tipo Problema | Conteggio | Dettaglio |
|------|---------------|-----------|-----------|
| Commenti liberi_TEST_2021_Aroma.csv | non_breaking_space | 25 | Trovati 25 caratteri \xa0 (non-breaking space) |
| Commenti liberi_TEST_2021_Colore della Pasta.csv | non_breaking_space | 60 | Trovati 60 caratteri \xa0 (non-breaking space) |
| Commenti liberi_TEST_2021_Profumo.csv | non_breaking_space | 31 | Trovati 31 caratteri \xa0 (non-breaking space) |
| Commenti liberi_TEST_2021_Sapore.csv | non_breaking_space | 42 | Trovati 42 caratteri \xa0 (non-breaking space) |
| Commenti liberi_TEST_2021_Spessore della Crosta.csv | non_breaking_space | 66 | Trovati 66 caratteri \xa0 (non-breaking space) |
| Commenti liberi_TEST_2021_Struttura della Pasta.csv | non_breaking_space | 196 | Trovati 196 caratteri \xa0 (non-breaking space) |
| Commenti liberi_TEST_2021_Texture.csv | non_breaking_space | 10 | Trovati 10 caratteri \xa0 (non-breaking space) |

### 4.2 Dati Mancanti

| File | Righe Totali | Righe Vuote | Commenti Vuoti |
|------|-------------|-------------|----------------|
| Commenti liberi_QTG_2019_Aroma.csv | 62 | 0 | 4 |
| Commenti liberi_QTG_2019_Colore della pasta.csv | 59 | 1 | 10 |
| Commenti liberi_QTG_2019_Profumo.csv | 114 | 0 | 2 |
| Commenti liberi_QTG_2019_Sapore.csv | 71 | 0 | 4 |
| Commenti liberi_QTG_2019_Spessore della crosta.csv | 45 | 0 | 17 |
| Commenti liberi_QTG_2019_Struttura della pasta.csv | 140 | 0 | 7 |
| Commenti liberi_QTG_2019_Texture.csv | 83 | 0 | 4 |
| Commenti liberi_QTG_2020_Aroma.csv | 117 | 0 | 1 |
| Commenti liberi_QTG_2020_Colore della pasta.csv | 147 | 0 | 0 |
| Commenti liberi_QTG_2020_Profumo.csv | 233 | 0 | 0 |
| Commenti liberi_QTG_2020_Sapore.csv | 210 | 0 | 0 |
| Commenti liberi_QTG_2020_Spessore della crosta.csv | 73 | 0 | 4 |
| Commenti liberi_QTG_2020_Struttura della pasta.csv | 336 | 0 | 0 |
| Commenti liberi_QTG_2020_Texture.csv | 113 | 0 | 2 |
| Commenti liberi_TEST_2021_Aroma.csv | 55 | 0 | 8 |
| Commenti liberi_TEST_2021_Colore della Pasta.csv | 63 | 0 | 7 |
| Commenti liberi_TEST_2021_Profumo.csv | 57 | 0 | 7 |
| Commenti liberi_TEST_2021_Sapore.csv | 54 | 0 | 9 |
| Commenti liberi_TEST_2021_Spessore della Crosta.csv | 50 | 0 | 9 |
| Commenti liberi_TEST_2021_Struttura della Pasta.csv | 84 | 0 | 3 |
| Commenti liberi_TEST_2021_Texture.csv | 48 | 0 | 6 |
| Commenti TOT_2018_Aroma.csv | 1561 | 0 | 685 |
| Commenti TOT_2018_Colore della Pasta.csv | 1573 | 0 | 303 |
| Commenti TOT_2018_Profumo.csv | 1573 | 0 | 490 |
| Commenti TOT_2018_Sapore.csv | 1573 | 0 | 296 |
| Commenti TOT_2018_Spessore della Crosta.csv | 1621 | 0 | 700 |
| Commenti TOT_2018_Struttura della Pasta.csv | 1573 | 0 | 207 |
| Commenti TOT_2018_Texture.csv | 1573 | 0 | 420 |

### 4.3 Cross-Check con Validation Report

**Totale issue:** 362

**Issue per tipo:**

- `sessione_inesistente`: 191
- `missing_prodotto`: 102
- `asset_mancante`: 67
- `missing_date`: 1
- `missing_seduta`: 1

**Issue per anno:**

- 2018: 48
- 2019: 115
- 2020: 106
- 2021: 93

### 4.4 Inconsistenze Trovate

- **colonna_extra** in `Commenti liberi_QTG_2020.xlsx` foglio `Profumo`: Attese 7 colonne, trovate 8. Colonne: ['Data Seduta di valutazione', 'N° Seduta', 'Bimestre di Valutazione ', 'Data Produzione', 'Panelista', 'Prodotto', 'Commenti', 'Unnamed: 7']
- **colonna_extra** in `Commenti liberi_TEST_2021.xlsx` foglio `Profumo`: Attese 7 colonne, trovate 8. Colonne: ['Data Seduta di valutazione', 'N° Seduta', 'Bimestre di Valutazione ', 'Data Produzione', 'Panelista', 'Prodotto', 'Commenti', 'Unnamed: 7']
- **capitalizzazione_inconsistente** in `multipli` foglio `spessore della crosta`: Varianti trovate: {'Spessore della Crosta', 'Spessore della crosta'}
- **capitalizzazione_inconsistente** in `multipli` foglio `struttura della pasta`: Varianti trovate: {'Struttura della pasta', 'Struttura della Pasta'}
- **capitalizzazione_inconsistente** in `multipli` foglio `colore della pasta`: Varianti trovate: {'Colore della pasta', 'Colore della Pasta'}

### 4.5 Correzioni Applicate in Memoria

> **NOTA:** Le correzioni seguenti sono state applicate **solo in memoria** durante
> l'analisi. I file originali su disco NON sono stati modificati. Questo garantisce
> che le statistiche e i grafici riflettano dati puliti, preservando i dati grezzi.

**Totale correzioni applicate:** 2620

**Riepilogo per tipo:**

| Tipo Correzione | Occorrenze | Descrizione |
|-----------------|------------|-------------|
| `virgola_italiana_convertita` | 1848 | Punteggi convertiti da formato virgola ('7,48') a float |
| `date_normalizzate` | 633 | Date normalizzate a formato ISO (YYYY-MM-DD) |
| `xa0_sostituiti` | 91 | Sostituiti caratteri \xa0 con spazio normale |
| `spazi_nomi_colonne` | 31 | Rimossi spazi trailing dai nomi colonne |
| `colonne_unnamed_rimosse` | 6 | Rimosse colonne 'Unnamed:' (artefatti export) |
| `nome_attributo_normalizzato` | 6 | Nomi attributi normalizzati (capitalizzazione) |
| `righe_vuote_rimosse` | 5 | Rimosse righe completamente vuote (tutte NaN) |

**Dettaglio per file (prime 30 correzioni):**

| File | Tipo | Dettaglio |
|------|------|-----------|
| Commenti TOT_2018.xlsx/Profumo | `spazi_nomi_colonne` | Rimossi spazi trailing da 2 nomi colonne |
| Commenti TOT_2018.xlsx | `virgola_italiana_convertita` | Convertiti 234 punteggi da formato '7,48' a float in 'Profumo' |
| Commenti TOT_2018.xlsx | `virgola_italiana_convertita` | Convertiti 234 punteggi da formato '7,48' a float in 'Sapore' |
| Commenti TOT_2018.xlsx | `virgola_italiana_convertita` | Convertiti 222 punteggi da formato '7,48' a float in 'Aroma' |
| Commenti TOT_2018.xlsx | `virgola_italiana_convertita` | Convertiti 174 punteggi da formato '7,48' a float in 'Texture' |
| Commenti TOT_2018.xlsx | `virgola_italiana_convertita` | Convertiti 60 punteggi da formato '7,48' a float in 'Struttura della Pasta' |
| Risultati_2019-21.xlsx/Medie Giuria2019_Q | `spazi_nomi_colonne` | Rimossi spazi trailing da 1 nomi colonne |
| Risultati_2019-21.xlsx/Medie Giuria2019_Q | `colonne_unnamed_rimosse` | Rimosse 3 colonne artefatto: ['Unnamed: 13', 'Unnamed: 14', 'Unnamed: 15'] |
| Risultati_2019-21.xlsx/Medie Giuria2019_Q | `righe_vuote_rimosse` | Rimosse 4 righe completamente vuote |
| Risultati_2019-21.xlsx/Medie Giuria2021_Q | `spazi_nomi_colonne` | Rimossi spazi trailing da 2 nomi colonne |
| Risultati_2019-21.xlsx/Medie Giuria2021_Q | `colonne_unnamed_rimosse` | Rimosse 1 colonne artefatto: ['Unnamed: 20'] |
| Risultati_2019-21.xlsx/Medie Giuria2021_Q | `xa0_sostituiti` | Sostituiti \xa0 → spazio in 2 celle |
| Risultati_2019-21.xlsx/Medie Giuria2020_Q  | `spazi_nomi_colonne` | Rimossi spazi trailing da 1 nomi colonne |
| Risultati_2019-21.xlsx/Medie Giuria2020_Q  | `colonne_unnamed_rimosse` | Rimosse 1 colonne artefatto: ['Unnamed: 9'] |
| Commenti TOT_2018.xlsx/Profumo | `spazi_nomi_colonne` | Rimossi spazi trailing da 2 nomi colonne |
| Commenti TOT_2018.xlsx | `virgola_italiana_convertita` | Convertiti 234 punteggi da formato '7,48' a float in 'Profumo' |
| Commenti TOT_2018.xlsx | `virgola_italiana_convertita` | Convertiti 234 punteggi da formato '7,48' a float in 'Sapore' |
| Commenti TOT_2018.xlsx | `virgola_italiana_convertita` | Convertiti 222 punteggi da formato '7,48' a float in 'Aroma' |
| Commenti TOT_2018.xlsx | `virgola_italiana_convertita` | Convertiti 174 punteggi da formato '7,48' a float in 'Texture' |
| Commenti TOT_2018.xlsx | `virgola_italiana_convertita` | Convertiti 60 punteggi da formato '7,48' a float in 'Struttura della Pasta' |
| Commenti liberi_QTG_2019_Aroma.csv | `spazi_nomi_colonne` | Rimossi spazi trailing da 1 nomi colonne |
| Commenti liberi_QTG_2019_Aroma.csv | `date_normalizzate` | Normalizzate 35 date in 'Data Seduta di valutazione' a formato ISO |
| Commenti liberi_QTG_2019_Aroma.csv | `date_normalizzate` | Normalizzate 62 date in 'Data Produzione' a formato ISO |
| Commenti liberi_QTG_2019_Colore della pasta.csv | `spazi_nomi_colonne` | Rimossi spazi trailing da 1 nomi colonne |
| Commenti liberi_QTG_2019_Colore della pasta.csv | `righe_vuote_rimosse` | Rimosse 1 righe completamente vuote |
| Commenti liberi_QTG_2019_Colore della pasta.csv | `date_normalizzate` | Normalizzate 58 date in 'Data Produzione' a formato ISO |
| Commenti liberi_QTG_2019_Colore della pasta.csv | `nome_attributo_normalizzato` | Attributo 'Colore della pasta' → 'Colore della Pasta' |
| Commenti liberi_QTG_2019_Profumo.csv | `spazi_nomi_colonne` | Rimossi spazi trailing da 1 nomi colonne |
| Commenti liberi_QTG_2019_Profumo.csv | `date_normalizzate` | Normalizzate 114 date in 'Data Produzione' a formato ISO |
| Commenti liberi_QTG_2019_Sapore.csv | `spazi_nomi_colonne` | Rimossi spazi trailing da 1 nomi colonne |
| ... | ... | *(36 correzioni aggiuntive omesse)* |

---

## 5. Riepilogo e Prossimi Step

### Findings Principali

1. **Schema dati**: Il 2018 è l'unico anno con punteggi individuali per panelista (5 colonne). Dal 2019 al 2021 i file hanno 7 colonne con solo commenti.
2. **Punteggi**: I punteggi 2018 coprono una scala ~1-10. I punteggi aggregati 2019-2021 sono medie della giuria e si concentrano nella fascia 5-8.
3. **Commenti**: Brevi e telegrafici, spesso abbreviati. I panelisti usano un vocabolario specializzato del settore caseario.
4. **Qualità dati**: Problemi di encoding nel 2021 (\xa0), righe vuote, e prodotti mancanti sono i problemi principali.

### Azioni Suggerite per Fase 2

1. Definire mappatura punteggi -> termini qualitativi basata sulle correlazioni trovate
2. Creare dizionario espansione abbreviazioni basato sui pattern telegrafici identificati
3. Gestire i termini dialettali con mappatura a italiano standard
4. Pulire encoding (\xa0) e gestire righe con dati mancanti
5. Standardizzare capitalizzazione nomi attributi
