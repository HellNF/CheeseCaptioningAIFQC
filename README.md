# Grana Trentino Image Captioning

Progetto di image captioning per formaggio Grana Trentino usando encoder-decoder models.

## Setup Ambiente

### 1. Crea Virtual Environment

```bash
python -m venv .venv
source .venv/bin/activate  # Linux/Mac
# oppure
.venv\Scripts\activate  # Windows
```

### 2. Installa Dipendenze

```bash
pip install -r requirements.txt
```

### 3. Verifica Installazione

```bash
python -c "import torch; print(torch.__version__)"
```

## Struttura Progetto

```
├── docs/                  # Documentazione e contesto
├── data/                  # Dati (raw, interim, processed)
├── src/                   # Codice sorgente
├── notebooks/             # Jupyter notebooks per esplorazioni
├── reports/               # Report progressivi
└── models_trained/        # Modelli addestrati
```

## Workflow

### 1. Data Validation & Quality (COMPLETATO ✅)

```bash
# Valida che CSV → immagini siano collegabili (supporto 2018-2022)
cd utils
python validate_sessions.py --pattern "Commenti"
# Output: 12905/13261 righe valide (97.3% successo)

# Analizza risultati validazione
python analyze_validation_report.py
# Output: breakdown dettagliato errori per tipo/anno/file
```

**Scripts disponibili:**
- `utils/validate_sessions.py` - Valida CSV→immagini (2018-2022, match su data)
- `utils/analyze_validation_report.py` - Analizza validation report con stats dettagliate
- `utils/standardize_folder_names.py` - Standardizza nomi cartelle (già eseguito, 89 cartelle OK)

### 2. Exploratory Data Analysis

```bash
# Analisi esplorativa completa (genera report + 12 grafici)
cd src/data
python 01_exploratory_analysis.py
# Output: reports/01_analisi_esplorativa.md + reports/figures/*.png
```

### 3. Data Preprocessing (TODO)

- Pulizia testo commenti
- Preprocessing immagini
- Creazione dataset finale (solo campioni completi)

### 4. Model Training (TODO)

- Training 3 modelli: CLIP, BLIP, ViT+GPT2
- Evaluation con metriche standard

## Validation Results (Aggiornato 2026-02-11)

- **Righe valide**: 12905/13261 (**97.3% successo!**)
- **Errori totali**: 362 (2.7%)
  - sessione_inesistente: 191 (52.8% - date con dati ma senza foto, LEGITTIMO)
  - missing_prodotto: 102 (28.2% - campo Prodotto vuoto nei CSV)
  - asset_mancante: 67 (18.5% - file immagini specifici mancanti)
- **Date uniche senza immagini**: Solo 7 su ~120 date totali
- **Anni coperti**: 2018-2022 completi

## Note

- I dati originali sono in `07_captioning risultati grana Trentino/`
- Validation report aggiornato: `validation_reports/session_validation_report.csv`
- Report esplorativa: `reports/01_analisi_esplorativa.md`

```

---

## **STEP 7: File `requirements.txt`**

Crea questo file con le dipendenze base:
```

# Core

numpy>=1.21.0
pandas>=1.3.0
matplotlib>=3.4.0
seaborn>=0.11.0

# Image Processing

opencv-python>=4.5.0
Pillow>=8.3.0

# NLP

nltk>=3.6.0
spacy>=3.1.0

# ML/DL

torch>=1.9.0
torchvision>=0.10.0
transformers>=4.10.0

# Utilities

tqdm>=4.62.0
scikit-learn>=0.24.0
openpyxl>=3.0.0 # Per leggere Excel

# Evaluation

pycocoevalcap>=1.2

# Logging e Debugging

tensorboard>=2.6.0
