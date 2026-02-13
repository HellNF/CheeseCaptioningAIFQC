# Vincoli Tecnici

## Dati
- 2.745 immagini BMP (formato pesante)
- Commenti in italiano, con dialetto trentino
- 4 annate con schemi dati DIVERSI (vedi project-overview.md sezione 7)

## Problemi Noti da Gestire
1. Encoding: file 2021 hanno caratteri \xa0 (non-breaking space)
2. Decimali: formato italiano "7,48" vs float
3. Schema variabile: 2018 ha 5 colonne, 2019-2021 hanno 7 colonne
4. Missing data: 1.454 issue nel validation report

## Linguaggio
- Python 3.8+
- Librerie ML: PyTorch o TensorFlow
- Preprocessing: pandas, opencv, PIL

## Output Richiesti
- Dataset pulito e normalizzato
- Report pre/post cleaning
- 3 modelli addestrati
- Comparison paper con metriche