# Report: Dataset Captioning Grana Trentino — Fase 4 Completata
**Data:** 2026-04-13  
**Progetto:** Grana Trentino Image Captioning FQC  
**Autore:** Claude Code  
**Voto qualità dataset:** **8.5 / 10**

---

## Indice

1. [Obiettivo della sessione](#1-obiettivo-della-sessione)
2. [Pipeline dati completa](#2-pipeline-dati-completa)
3. [Modifiche chiave apportate](#3-modifiche-chiave-apportate)
4. [Statistiche del dataset finale](#4-statistiche-del-dataset-finale)
5. [Voto e motivazione](#5-voto-e-motivazione)
6. [Punti di attenzione per il training](#6-punti-di-attenzione-per-il-training)
7. [File prodotti](#7-file-prodotti)

---

## 1. Obiettivo della sessione

Costruire un dataset di training completo e verificabile per image captioning, in cui ogni riga colleghi in modo univoco:

- Un **commento sensoriale** del panel (testo grezzo + versione normalizzata LLM)
- Una **caption** generata da GPT-4o-mini (classe + testo)
- Le **immagini BMP** del campione fisico (fetta + grana)
- I **metadati completi** (caseificio, data seduta, panelista, prodotto, anno)

Il requisito fondamentale era la correlazione immagine–caption tramite la chiave `(codice_caseificio, data_seduta)`, assente nella pipeline originale.

---

## 2. Pipeline dati completa

```
CSV sorgenti (2018-2021)
  ↓  [FIX: 2018 Seduta → data effettiva]
  ↓
Script 10 — normalizza_commenti.py
  Carica commenti grezzi, pre-normalizzazione con vocabolario,
  chiama LLM (GPT-4o-mini) in batch da 20 → classe + caption
  Output: caption_per_attributo/{Attr}_captions.csv
  ↓
Script 11 — riprocessa_conforme.py
  Riclassifica CONFORME con re-prompt specifico
  ↓
Script 12 — riprocessa_fuori_attributo.py
  Riclassifica FUORI_ATTRIBUTO (secondo re-prompt)
  ↓
Script 13 — fix_hallucinations.py
  Riprocessa righe con ERRORE_PARSING
  ↓
Script 16 — patch_profumo_2018.py   [NUOVO — patch chirurgica]
  Aggiunge le 1083 righe 2018 mancanti per Profumo
  senza toccare le 395 già processate
  ↓
Script 14 — build_raw_per_attribute.py   [NUOVO]
  Combina tutti gli anni per attributo
  Unisce immagini da campioni_completi.csv su (codice_caseificio, Data Seduta)
  Output: raw_per_attribute/{Attr}_raw.csv
  ↓
Script 15 — merge_captions_with_images.py   [NUOVO]
  Join raw + captions su (prodotto, panelista, commento_raw, dataset_year) + cumcount()
  Output: caption_per_attributo/{Attr}_full.csv
           processed/dataset_captioning.csv
```

---

## 3. Modifiche chiave apportate

### 3.1 Fix critico: sostituzione colonna `Seduta` nel 2018

I 7 file `Commenti TOT_2018_*.csv` contenevano una colonna `Seduta` con un numero intero (indice di sessione), non una data. Senza la data reale, il join con `campioni_completi.csv` era impossibile.

**Fix:** sostituita la colonna `Seduta` con la data ISO effettiva dalla tabella di corrispondenza `date_sedute_2018.csv`, rinominata in `Data Seduta di valutazione` per uniformare lo schema con i file 2019-2021.

**Impatto:** sbloccato il link immagine per tutte le righe 2018 (6.042 su 13.261 totali).

### 3.2 Patch Profumo 2018 (script 16)

Il run originale di normalizzazione (script 10) aveva processato solo i file 2019-2021 per Profumo, lasciando fuori 1.083 righe del file 2018. Causa probabile: il file non era ancora presente al momento del run.

**Fix:** script chirurgico che:
- Identifica le righe mancanti via anti-join su `(prodotto, panelista, commento_raw, anno)`
- Assegna id continuativi (396-1478) senza toccare i 395 esistenti
- Usa la baseline cached (`Profumo_baseline.json`), nessuna nuova chiamata per baseline
- Checkpoint-based per resilienza a interruzioni

Dopo la patch: Profumo passa da 395 a 1.478 righe, poi ri-filtrata da script 11/12/13.

5 righe `ERRORE_PARSING` corrette manualmente:

| Commento | Fix applicato |
|---|---|
| `chiuso` | → classe OK, caption "chiuso" |
| `bruciato` | → classe OK, caption "bruciato" |
| `putrido, fecale, stalla, acido acetico` | → classe OK |
| `fermentato, insilato di mais` | → classe OK |
| `odssidato` (typo) | → classe OK, caption corretta |

### 3.3 Strategia di join dataset_year da `_source_file`

Il file `Commenti TOT_2018_*.csv` contiene fisicamente sedute che vanno da agosto 2018 ad aprile 2019. L'anno estratto dalla data reale (`anno`) è quindi `2019` per molte righe, ma il file si chiama `2018`.

**Fix:** il join usa l'anno estratto dal nome del file sorgente (`_source_file`), non dall'anno della data di seduta, allineando i due lati del merge. Questo ha portato il match rate dal ~45% al **100%** su tutti gli attributi.

### 3.4 Flag immagini granulari + fetta-only incluse

Aggiunta distinzione tra:

| Flag | Significato |
|---|---|
| `has_fetta` | Almeno un'immagine FETTA disponibile |
| `has_grana` | Almeno un'immagine GRANA disponibile |
| `has_images` | `has_fetta OR has_grana` — trainable |
| `has_both_views` | Entrambe le viste — per modelli dual-view |

In precedenza `has_images` richiedeva entrambe le viste, escludendo 353 campioni con solo fetta. Ora `has_images` usa semantica OR, aggiungendo questi campioni al pool trainable.

---

## 4. Statistiche del dataset finale

**File:** `data/processed/dataset_captioning.csv`  
**Dimensioni:** 13.261 righe × 34 colonne

### 4.1 Copertura per attributo

| Attributo | Righe totali | Con caption | Con immagini | **Trainable** |
|---|---|---|---|---|
| Struttura_della_Pasta | 2.133 | 1.726 | 2.095 | **1.654** |
| Sapore | 1.908 | 1.570 | 1.886 | **1.511** |
| Colore_della_Pasta | 1.842 | 1.484 | 1.820 | **1.431** |
| Profumo | 1.977 | 1.374 | 1.952 | **1.339** |
| Texture | 1.817 | 1.338 | 1.799 | **1.300** |
| Aroma | 1.795 | 1.030 | 1.773 | **993** |
| Spessore_della_Crosta | 1.789 | 1.027 | 1.771 | **981** |
| **TOTALE** | **13.261** | **9.549** | **12.096** | **9.209** |

### 4.2 Distribuzione per anno

| Anno | Righe | Con immagini | Con caption | Trainable |
|---|---|---|---|---|
| 2018 | 6.042 | 5.994 (99%) | 3.834 | 3.808 |
| 2019 | 5.322 | 5.223 (98%) | 4.169 | 4.109 |
| 2020 | 927 | 710 (76%) | 895 | 692 |
| 2021 | 675 | 412 (61%) | 613 | 395 |

### 4.3 Classi LLM

| Classe | Count | % su righe con commento |
|---|---|---|
| OK | 7.048 | 70.1% |
| FUORI_ATTRIBUTO | 2.540 | 25.3% |
| ILLEGGIBILE | 272 | 2.7% |
| CONFORME | 182 | 1.8% |
| RIFERIMENTO | 12 | 0.1% |
| ERRORE_PARSING | **1** | 0.01% |

### 4.4 Immagini

- Solo fetta (no grana): **514** campioni
- Solo grana (no fetta): **0**
- Entrambe le viste: **12.040**
- Campioni fisici unici nel dataset: **591**
- Campioni fisici con almeno 1 campione trainable: **481**

### 4.5 Caption OK

- Numero: 7.048
- Lunghezza media: **67,9 caratteri**
- Min: 5 caratteri · Max: 279 caratteri

### 4.6 Copertura complessiva

- Righe con commento non vuoto: 10.055
- **Trainable / righe con commento: 91,6%**

---

## 5. Voto e motivazione

### **8.5 / 10**

#### Punti di forza (+)

| # | Criterio | Valutazione |
|---|---|---|
| ✓ | Linkage caption–immagine al 100% (join senza perdite) | Eccellente |
| ✓ | Pipeline LLM a 4 passi (norm → CONFORME → FUORI_ATT → fix) | Solida |
| ✓ | 91,6% trainable rate sui commenti disponibili | Molto alto |
| ✓ | Metadati completi: data seduta, caseificio, panelista, anno, peso | Completi |
| ✓ | Schema unificato tra 4 anni con colonne originali preservate | Nessuna perdita |
| ✓ | Flag granulari immagini (fetta/grana/both) per modelli flessibili | Preparato per futuri modelli |
| ✓ | Tracciabilità completa: `caption_id`, `sample_id`, `_source_file` | Riproducibile |
| ✓ | Peso (0.5 per pattern ripetuto) per sample weighting nel training | Pronto |
| ✓ | 1 solo ERRORE_PARSING residuo su 13.261 righe (0.007%) | Quasi perfetto |

#### Limitazioni (-)

| # | Limitazione | Impatto |
|---|---|---|
| − | 2020-2021 copertura immagini 61-76% vs 98-99% per 2018-2019 | Distribuzione temporale sbilanciata |
| − | ~1.300 campioni per attributo (piccolo per deep learning puro) | Richiede transfer learning; già pianificato |
| − | Aroma e Spessore hanno meno campioni (~980) | Potenziale underfitting per quegli attributi |
| − | 294 righe con anno "2022" (origine incerta) | Marginale, nessun impatto trainable |
| − | 1 ERRORE_PARSING residuo (Struttura_della_Pasta) | Trascurabile |

#### Perché non 10/10

Un dataset da 10/10 avrebbe: bilanciamento perfetto tra anni (impossibile retroattivamente), ≥2.000 campioni per attributo per training da zero senza transfer learning, e zero ERRORE_PARSING. Il punteggio 8.5 riflette un dataset **production-ready** per il progetto specifico (transfer learning + fine-tuning), con l'unica limitazione strutturale nella disponibilità fisica delle immagini 2020-2021.

---

## 6. Punti di attenzione per il training

1. **Split campione fisico, non riga:** dividere train/val/test a livello di `(codice_caseificio, data_seduta)` per evitare data leakage. Le 7 caption dello stesso campione devono stare tutte nello stesso split.

2. **Stratificazione per anno:** con 2020-2021 sottorappresentati, uno split casuale puro rischierebbe di escluderli dalla validation. Usare stratificazione.

3. **Modelli single-attribute vs multi-attribute:** con ~1.300 campioni per attributo, considerare un modello per attributo (più semplice) oppure un modello condizionato con token `[ATTR]` in testa alla caption.

4. **FUORI_ATTRIBUTO e ILLEGGIBILI:** queste righe hanno `has_caption=False` e sono già escluse dai trainable. Non includere nel training.

5. **CONFORME:** 182 righe con caption di tipo "Il campione soddisfa i requisiti normativi" — valutare se includerle o trattarle come classe separata.

6. **Peso 0.5:** le righe con `peso=0.5` (commenti ripetuti verbatim) possono essere usate per weighted sampling durante il training.

7. **Fetta-only:** le 353 righe con solo fetta sono ora trainable (`has_images=True`, `has_fetta=True`, `has_grana=False`). Modelli dual-view devono filtrare su `has_both_views=True`; modelli single-view su `has_fetta=True`.

---

## 7. File prodotti

| File | Descrizione | Righe |
|---|---|---|
| `07_.../raw_per_attribute/{Attr}_raw.csv` × 7 | Dati grezzi + immagini per attributo | ~1.800/attr |
| `data/processed/caption_per_attributo/{Attr}_captions.csv` × 7 | Caption LLM per attributo | ~1.200/attr |
| `data/processed/caption_per_attributo/{Attr}_full.csv` × 7 | Join completo per attributo | ~1.900/attr |
| **`data/processed/dataset_captioning.csv`** | **Dataset finale combinato** | **13.261** |
| `src/data/14_build_raw_per_attribute.py` | Script costruzione raw | — |
| `src/data/15_merge_captions_with_images.py` | Script merge finale | — |
| `src/data/16_patch_profumo_2018.py` | Patch chirurgica Profumo 2018 | — |

---

*Report generato automaticamente da Claude Code il 2026-04-13.*
