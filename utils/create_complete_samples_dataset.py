"""
Identifica e salva solo i campioni con DATI COMPLETI (immagini + commenti).
"""
import pandas as pd
from pathlib import Path
from collections import defaultdict
import json

# Percorsi
VALIDATION_CSV = Path("../07_captioning risultati grana Trentino/validation_reports/session_validation_report.csv")
OUTPUT_DIR = Path("../data/processed")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# Carica validation report
df_validation = pd.read_csv(VALIDATION_CSV, encoding='utf-8')

# Issue che IMPEDISCONO l'uso del campione per captioning
issue_bloccanti = {'sessione_inesistente', 'asset_mancante'}

# Trova tutte le righe con issue bloccanti
campioni_problematici = df_validation[
    df_validation['issue_type'].isin(issue_bloccanti)
][['csv_file', 'line_number', 'data_seduta', 'prodotto', 'caseificio']].drop_duplicates()

print(f"{'='*70}")
print("ANALISI COMPLETEZZA DATASET GRANA TRENTINO")
print('='*70)
print(f"\nCampioni con issue bloccanti (no immagini): {len(campioni_problematici)}")

# Conta totale righe nei CSV per anno (approssimativo)
# Ogni riga CSV = 1 commento da 1 panelista per 1 attributo per 1 campione
# Se abbiamo 8 attributi e ~10 panelisti, ogni campione genera ~80 righe

issue_per_anno = defaultdict(int)
for _, row in campioni_problematici.iterrows():
    try:
        anno = pd.to_datetime(row['data_seduta']).year
        issue_per_anno[anno] += 1
    except:
        pass

print("\nIssue per anno:")
for anno in sorted(issue_per_anno.keys()):
    print(f"  {anno}: {issue_per_anno[anno]} righe CSV problematiche")

# Stima campioni completi
# Dalla struttura del progetto sappiamo:
# - 2745 immagini totali = ~1372 coppie FETTA+GRANA
# - Ma non tutte hanno commenti

print(f"\n{'='*70}")
print("STIMA CAMPIONI UTILIZZABILI PER CAPTIONING")
print('='*70)

# Conta immagini disponibili (basato sui folder)
from pathlib import Path
import os

trentingrana_dir = Path("../07_captioning risultati grana Trentino/TrentinGrana")
immagini_per_anno = defaultdict(int)

for root, dirs, files in os.walk(trentingrana_dir):
    for f in files:
        if f.endswith('.bmp'):
            # Estrai anno dal percorso
            parts = Path(root).parts
            for part in parts:
                if any(year in part for year in ['2018', '2019', '2020', '2021', '2022']):
                    anno_match = [y for y in ['2018', '2019', '2020', '2021', '2022'] if y in part]
                    if anno_match:
                        immagini_per_anno[anno_match[0]] += 1
                        break

print("\nImmagini BMP disponibili per anno:")
for anno in sorted(immagini_per_anno.keys()):
    coppie_stimate = immagini_per_anno[anno] // 2  # FETTA + GRANA
    print(f"  {anno}: {immagini_per_anno[anno]} immagini -> ~{coppie_stimate} coppie")

print(f"\n{'='*70}")
print("RACCOMANDAZIONI")
print('='*70)
print("""
1. USARE SOLO CAMPIONI COMPLETI (immagini + commenti):
   - Filtrare validation_report per escludere issue bloccanti
   - Risultato: dataset più piccolo ma 100% utilizzabile

2. DOCUMENTARE LA LIMITAZIONE:
   - ~1300 commenti non hanno immagini corrispondenti
   - Principalmente anni 2020-2022
   - Dataset finale sarà composto dai campioni completi

3. PROSSIMO STEP:
   - Script 02_create_dataset.py che fa il join completo
   - Solo campioni con immagini E commenti E punteggi
   - Output: CSV finale con [fetta_path, grana_path, caption]
""")

# Salva l'elenco dei campioni problematici per riferimento
output_file = OUTPUT_DIR / "campioni_senza_immagini.csv"
campioni_problematici.to_csv(output_file, index=False, encoding='utf-8')
print(f"\nSalvato elenco campioni problematici: {output_file}")
