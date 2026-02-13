# Contesto Completo Progetto: Grana Trentino Image Captioning

## 1. OBIETTIVO FINALE

Sviluppare un sistema di image captioning per formaggio Grana Trentino che genera descrizioni testuali complete a partire da immagini.

**Deliverable:**
- Report dettagliato e progressivo (anche in forma grezza durante sviluppo)
- 3 modelli di captioning implementati e confrontati
- Documentazione metodologia completa di pulizia dataset
- Contenuti dettagliati più importanti della forma

**Scopo Captioning:**
- Input: Coppia di immagini (FETTA + GRANA) dello stesso campione
- Output: Una caption testuale completa che descrive tutti gli 8 attributi sensoriali
- La caption deve coprire sia qualità visive che sensoriali (profumo, sapore, texture, struttura, colore, ecc.)
- Deve includere anche caratteristiche negative/difetti se presenti

---

## 2. STRUTTURA DATI

### 2.1 Immagini BMP
- **Totale:** 2.745 immagini
- **Periodo:** 2018-2022 (4 annate)
- **Organizzazione:** Cartelle per data di esaminazione

**Tipi di immagine:**
- **FETTA (1.285 img):** Taglio netto, sezione uniforme
- **GRANA (1.360 img):** Spaccatura, sezione non uniforme, mostra texture

**Naming Convention (evolve nel tempo):**
```
P{posizione}{lato}_{codice}_{vista}.bmp
P{posizione}{lato}_TN{codice}_{vista}.bmp
P{posizione}{LATO}_TN{codice}_{id}_{VISTA}.bmp
P{posizione}_TN{codice}_{id}_{VISTA}_{replica}.bmp
```

**Componenti chiave:**
- `{lato}` = a/b oppure A/B → lato sinistro/destro della forma
- `TN{codice}` = codice caseificio (300-338)
- `{vista}` = FETTA o GRANA
- `{id}` = numero identificativo forma (3 cifre)

**Spot colorati:** Presenti nelle immagini per marcare lati, sempre ESTERNI al campione (non sovrapposti)

### 2.2 Dati Tabulari

**Chiave Univoca Campione:**
```
Codice Caseificio + Data Seduta = Campione Fisico Unico
```
Stesso codice TN302 in date diverse = campioni DIVERSI (nuova produzione)

**File Commenti (Excel/CSV):**
- 4 file Excel principali (2018, 2019, 2020, 2021)
- Schema DIVERSO tra 2018 e anni successivi:
  - **2018:** 5 colonne con punteggi numerici individuali + commenti
  - **2019-2021:** 7 colonne solo commenti (no punteggi diretti)

**File Codifiche:**
- `codifica caseifici.csv`: Mapping codici caseificio (TN_302 → C0A → A)
- `Risultati_2019-21.xlsx`: Punteggi medi aggregati giuria per anno

**Multi-Panelista:**
- Ogni campione valutato da N panelisti diversi
- Codici tipo: TG_19, Q_10, oppure Sogg 1, Sogg 2 (2018)
- Tutti panelisti hanno uguale affidabilità (nessuna gerarchia)

### 2.3 Attributi Sensoriali (8 totali)

| Attributo | Categoria | Note |
|---|---|---|
| Spessore della Crosta | Visivo | |
| Struttura della Pasta | Visivo | |
| Colore della Pasta | Visivo | |
| Aspetto Esteriore | Visivo | Solo in risultati aggregati |
| Profumo | Olfattivo | |
| Sapore | Gustativo | |
| Aroma | Gustativo/Olfattivo | Retronasale |
| Texture | Tattile | Introdotto dal 2021 |

**IMPORTANTE:** Non c'è distinzione nei commenti tra FETTA e GRANA. Diverse caratteristiche vengono osservate su entrambe le viste, ma i commenti non specificano quale immagine.

---

## 3. WORKFLOW PROGETTO

### Fase 1: Analisi Esplorativa (PRIORITÀ MASSIMA)
**Obiettivo:** Capire i dati prima di decidere strategie

**Analisi da condurre:**
1. **Statistiche punteggi numerici:**
   - Distribuzione per attributo
   - Correlazioni tra attributi
   - Varianza inter-panelista

2. **Analisi testuale:**
   - Frequenza termini per attributo
   - Correlazione punteggio numerico ↔ termini usati (es. punteggio 8-10 → "intenso", 1-3 → "delicato")
   - Identificazione pattern telegrafici (abbreviazioni comuni)
   - Rilevamento termini dialettali trentini
   - Mappatura sinonimi

3. **Analisi associazioni:**
   - Join immagini ↔ commenti (tramite codice + data)
   - Verifica completezza dati
   - Identificazione sample con dati mancanti

4. **Analisi immagini:**
   - Dimensioni/risoluzioni BMP
   - Presenza/posizione spot colorati
   - Qualità immagini per anno

**Output:** Report esplorativo dettagliato che guiderà le decisioni successive

### Fase 2: Definizione Regole Pulizia
**Basate su analisi Fase 1:**

1. **Vocabolario Controllato:**
   - Mappare punteggi numerici → termini qualitativi standard
   - Ridurre sinonimi a termine canonico
   - Definire scale qualitative (debole/moderato/intenso, ecc.)

2. **Regole Normalizzazione:**
   - Espansione abbreviazioni (cr. → crosta, sp. → spessore)
   - Traduzione dialetto → italiano standard
   - Riformulazione telegrafese → frasi complete

3. **Strategia Aggregazione Multi-Panelista:**
   - Tradurre commenti individuali in linguaggio standardizzato
   - Verificare sovrapposizione concetti
   - Gestire pareri discordanti (da definire post-analisi)
   - Interpretare commenti generici ("ok", "normale") usando punteggi numerici

### Fase 3: Pulizia Dataset
**Due livelli:**
- **Versione A (intermedia):** Pulizia minima
  - "cr. un po sp." → "crosta un po' spessa"
  - Espansione abbreviazioni, correzione typo
  
- **Versione B (finale):** Rielaborazione completa
  - "crosta un po' spessa" → "La crosta presenta uno spessore moderatamente elevato"
  - Frasi complete ed eleganti

**Preservazione:**
- Mantenere informazioni negative/difetti
- Documentare tutte le trasformazioni

### Fase 4: Pre-processing Immagini
1. Analisi dimensioni (normalizzazione se necessaria)
2. Rimozione spot colorati esterni (se impattano modelli)
3. Quality check visivo
4. Organizzazione FETTA+GRANA per campione

### Fase 5: Creazione Dataset Finale
- Join immagini ↔ commenti puliti
- Formato: [FETTA_path, GRANA_path] → [caption_aggregata]
- Split train/validation/test (da definire)

### Fase 6: Modeling
**3 modelli encoder-decoder concettualmente DIVERSI**
(Specifiche da definire post-analisi)

**Input:** 2 immagini (FETTA + GRANA)
**Output:** 1 caption testuale completa (8 attributi)

**Considerazioni:**
- Primo progetto captioning → serve spiegazione architetture
- Necessità documentazione dettagliata scelte

### Fase 7: Evaluation
**Metriche automatiche:**
- BLEU
- METEOR
- CIDEr
- Altre standard nel campo

**Confronto:** I 3 modelli valutati con stesse metriche

### Fase 8: Report Finale
- Stilato PROGRESSIVAMENTE durante tutto il progetto
- Forma non importante, contenuti dettagliati SÌ
- Documentare decisioni, risultati, lesson learned

---

## 4. VINCOLI E REQUISITI TECNICI

### 4.1 Problemi Noti da Gestire

**Qualità Dati (9 issue documentate):**
1. **Encoding:** File 2021 contengono `\xa0` (non-breaking space)
2. **Formato decimali:** 2018 usa virgola italiana "7,48" come stringa
3. **Schema variabile:** 2018 = 5 colonne, 2019-2021 = 7 colonne
4. **Colonne extra:** Foglio Profumo 2020 ha 8a colonna non documentata
5. **Capitalizzazione:** Nomi attributi inconsistenti (crosta/Crosta)
6. **Missing header:** `codifica caseifici.xlsx` senza intestazione
7. **Ordine colonne:** Varia tra 2019/2020/2021 nei risultati aggregati
8. **Formati date:** DD-MM-YYYY vs YYYY-MM-DD
9. **Missing data:** 1.454 issue nel validation report (principalmente `missing_prodotto`)

### 4.2 Stack Tecnologico
- **Linguaggio:** Python 3.8+
- **ML Frameworks:** PyTorch o TensorFlow (da scegliere)
- **Preprocessing:**
  - pandas (dati tabulari)
  - opencv/PIL (immagini)
  - nltk/spacy (testo)
- **Metriche:** nlg-eval o pycocoevalcap

### 4.3 Vincoli Progetto
- **Tempo:** Limitato ma non deadline critica
- **Risorse computazionali:** [Da specificare se limitazioni GPU]
- **Esperienza:** Prima volta con captioning → necessario approccio didattico

---

## 5. DECISIONI CHIAVE

### Confermate:
✅ Caption singola per coppia FETTA+GRANA (non dataset separati)  
✅ Caption copre tutti 8 attributi in frase completa  
✅ Aggregazione multi-panelista in caption consenso  
✅ Preservare caratteristiche negative  
✅ Punteggi numerici per creare vocabolario controllato  
✅ Report progressivo durante progetto  
✅ Valutazione solo automatica (no valutazione umana)

### Da Definire Post-Analisi:
⏳ Strategia aggregazione commenti discordanti  
⏳ Mapping preciso punteggi → termini qualitativi  
⏳ Architetture 3 modelli  
⏳ Split train/val/test  
⏳ Dimensioni/normalizzazione immagini  
⏳ Necessità rimozione spot colorati

---

## 6. FILE DI RIFERIMENTO

**Documentazione:**
- `docs/project-overview.md` → Analisi dettagliata struttura dati originale
- `docs/CONTESTO_COMPLETO_PROGETTO.md` → Questo file (contesto progetto)
- `docs/regole-pulizia-testo.md` → Da riempire durante Fase 2

**Dati Chiave:**
- `07_captioning risultati grana Trentino/TrentinGrana/` → Immagini BMP (2745)
- `07_captioning risultati grana Trentino/GT commenti liberi/` → Excel commenti
- `07_captioning risultati grana Trentino/GT commenti liberi/codifiche/` → Mapping + punteggi aggregati
- `07_captioning risultati grana Trentino/validation_reports/` → Issue qualità dati

---

## 7. NOTE PER LLM

**Livello Utente:**
- Prima esperienza con image captioning
- Prima esperienza con LLM per progetti ML
- Necessità spiegazioni architetture e best practices

**Approach Richiesto:**
1. **Fase esplorativa prima di decisioni:** Non assumere soluzioni, analizzare dati reali
2. **Documentazione progressiva:** Ogni script deve produrre report/log
3. **Spiegazioni tecniche:** Accompagnare codice con commenti didattici
4. **Validazione frequente:** Checkpoint e verifiche intermedie
5. **Flessibilità:** Decisioni basate su evidenze dall'analisi

**Priorità:**
1️⃣ Analisi esplorativa completa  
2️⃣ Qualità pulizia dati (impatta tutto il resto)  
3️⃣ Documentazione progressiva  
4️⃣ Confronto modelli robusto

---

## 8. PROSSIMI STEP IMMEDIATI

**Step 1:** Analisi esplorativa dataset
- Script conteggio righe/colonne per file
- Statistiche distribuzioni punteggi
- Frequenza termini nei commenti
- Verifica encoding e missing data

**Step 2:** Join immagini-commenti
- Mappare codici caseificio
- Associare data seduta
- Verificare completezza

**Step 3:** Definire regole pulizia
- Basate su correlazioni punteggi-termini
- Vocabolario controllato
- Pattern normalizzazione

---

**Ultimo aggiornamento:** [Data corrente]
**Versione documento:** 1.0
```

---

## **Istruzioni per l'uso:**

Salva questo file come `docs/CONTESTO_COMPLETO_PROGETTO.md` nella tua cartella di progetto.

**Quando inizi una nuova sessione con Claude:**
```
@workspace Leggi docs/CONTESTO_COMPLETO_PROGETTO.md per avere 
il contesto completo del progetto. Confermami che l'hai letto 
e sei pronto a lavorare sulla Fase 1 (analisi esplorativa).