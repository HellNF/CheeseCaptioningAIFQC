"""
Script di Debug: Investigazione Bug Profumo 2018
Trova perché l'attributo Profumo per anno 2018 ha 0% copertura nel join
"""

import pandas as pd
from pathlib import Path
import json

PROJECT_ROOT = Path(__file__).parent.parent.parent

print("="*80)
print("DEBUG PROFUMO 2018 - INVESTIGAZIONE BUG")
print("="*80)

# ============================================================================
# STEP 1: Analizza file Profumo 2018
# ============================================================================
print("\n" + "="*80)
print("STEP 1: ANALISI FILE PROFUMO 2018")
print("="*80)

profumo_path = PROJECT_ROOT / "data" / "interim" / "fase_B" / "Commenti TOT_2018_Profumo_fase_B.csv"
print(f"\nCaricamento: {profumo_path}")

df_profumo = pd.read_csv(profumo_path, encoding='utf-8')

print(f"\nRighe totali: {len(df_profumo)}")
print(f"Colonne: {list(df_profumo.columns)}")

print("\n--- Prime 5 righe complete ---")
print(df_profumo.head().to_string())

# Valori unici Prodotto
if 'Prod' in df_profumo.columns:
    print("\n--- Valori unici colonna 'Prod' ---")
    print(df_profumo['Prod'].unique())
    print(f"Totale codici unici: {df_profumo['Prod'].nunique()}")
elif 'Prodotto' in df_profumo.columns:
    print("\n--- Valori unici colonna 'Prodotto' ---")
    print(df_profumo['Prodotto'].unique())
    print(f"Totale codici unici: {df_profumo['Prodotto'].nunique()}")

# Valori unici Seduta
if 'Seduta' in df_profumo.columns:
    print("\n--- Valori unici colonna 'Seduta' ---")
    print(sorted(df_profumo['Seduta'].unique()))
    print(f"Totale sedute uniche: {df_profumo['Seduta'].nunique()}")

# Verifica colonne metadata
print("\n--- Colonne metadata ---")
print(f"Colonna 'anno': {'SÌ' if 'anno' in df_profumo.columns else 'NO'}")
print(f"Colonna 'attributo': {'SÌ' if 'attributo' in df_profumo.columns else 'NO'}")

# Conta commenti validi
# NOTA: Colonna si chiama 'Commenti ' (con spazio!)
comment_col = None
for col in df_profumo.columns:
    if 'commenti' in col.lower():
        comment_col = col
        break

print(f"\nColonna commenti trovata: '{comment_col}' (nota spazio finale!)")

if comment_col:
    commenti_validi = df_profumo[comment_col].notna() & (df_profumo[comment_col].str.strip() != '')
else:
    print("ERRORE: Colonna commenti non trovata!")
    commenti_validi = pd.Series([False] * len(df_profumo))
print(f"\nCommenti validi (non vuoti): {commenti_validi.sum()}")

# ============================================================================
# STEP 2: Analizza mapping caseifici
# ============================================================================
print("\n" + "="*80)
print("STEP 2: ANALISI MAPPING CASEIFICI")
print("="*80)

mapping_path = PROJECT_ROOT / "07_captioning risultati grana Trentino" / "GT commenti liberi" / "codifiche" / "codifica caseifici_codici caseifici.csv"
print(f"\nCaricamento: {mapping_path}")

df_mapping = pd.read_csv(mapping_path, header=None, encoding='utf-8')

print(f"\nRighe totali: {len(df_mapping)}")
print("\n--- Tutte le 24 righe del mapping ---")
print(df_mapping.to_string(index=False, header=False))

# Verifica match con Prod del file Profumo
if 'Prod' in df_profumo.columns:
    prod_profumo = set(df_profumo['Prod'].unique())
    prod_mapping = set(df_mapping[1].str.strip())

    print(f"\n--- Verifica match Prod Profumo vs Mapping ---")
    print(f"Codici Prod nel file Profumo: {len(prod_profumo)}")
    print(f"Codici Prod nel mapping: {len(prod_mapping)}")
    print(f"Codici Profumo NON nel mapping: {prod_profumo - prod_mapping}")
    print(f"Codici Mapping NON in Profumo: {prod_mapping - prod_profumo}")

# ============================================================================
# STEP 3: Analizza date_sedute_2018
# ============================================================================
print("\n" + "="*80)
print("STEP 3: ANALISI DATE SEDUTE 2018")
print("="*80)

excel_path = PROJECT_ROOT / "07_captioning risultati grana Trentino" / "GT commenti liberi" / "Commenti TOT_2018.xlsx"
print(f"\nCaricamento: {excel_path}")

df_date = pd.read_excel(excel_path, sheet_name='date_sedute_2018')

print(f"\nRighe totali: {len(df_date)}")
print("\n--- Tutte le 29 righe Session → Date ---")
print(df_date.to_string(index=False))

# Verifica match con Seduta del file Profumo
if 'Seduta' in df_profumo.columns:
    sedute_profumo = set(df_profumo['Seduta'].unique())
    session_date = set(df_date['Session'].unique())

    print(f"\n--- Verifica match Seduta Profumo vs Session mapping ---")
    print(f"Sedute nel file Profumo: {sorted(sedute_profumo)}")
    print(f"Session nel mapping date: {sorted(session_date)}")
    print(f"Sedute Profumo NON nel mapping: {sedute_profumo - session_date}")
    print(f"Session mapping NON in Profumo: {session_date - sedute_profumo}")

# ============================================================================
# STEP 4: Analizza campioni_completi.csv
# ============================================================================
print("\n" + "="*80)
print("STEP 4: ANALISI CAMPIONI COMPLETI")
print("="*80)

campioni_path = PROJECT_ROOT / "data" / "processed" / "campioni_completi.csv"
print(f"\nCaricamento: {campioni_path}")

df_campioni = pd.read_csv(campioni_path, encoding='utf-8')

# Filtra anno 2018
df_2018 = df_campioni[df_campioni['anno'] == 2018]
print(f"\nCampioni anno 2018: {len(df_2018)}")

print("\n--- Valore commenti_profumo per i primi 5 campioni 2018 ---")
for idx, row in df_2018.head().iterrows():
    commenti_json = row['commenti_profumo']
    commenti_list = json.loads(commenti_json)
    print(f"{row['sample_id']}: {len(commenti_list)} commenti - {commenti_list[:2] if commenti_list else '[]'}")

# Conta campioni con commenti_profumo non vuoto
count_profumo = 0
for _, row in df_2018.iterrows():
    commenti_json = row['commenti_profumo']
    commenti_list = json.loads(commenti_json)
    if commenti_list:
        count_profumo += 1

print(f"\n--- Campioni 2018 con commenti_profumo non vuoto: {count_profumo}/{len(df_2018)} ---")

# ============================================================================
# STEP 5: Simula join manualmente per 3 righe
# ============================================================================
print("\n" + "="*80)
print("STEP 5: SIMULAZIONE JOIN MANUALE (3 RIGHE)")
print("="*80)

# Prendi 3 righe con commenti validi
df_profumo_valid = df_profumo[commenti_validi].head(3)

# Crea mapping dict
mapping_dict = {}
for _, row in df_mapping.iterrows():
    codice_caseificio = str(row[0]).strip().replace('_', '')  # TN_302 → TN302
    codice_prodotto = str(row[1]).strip()  # C0A
    mapping_dict[codice_prodotto] = codice_caseificio

# Crea date dict
date_dict = {}
for _, row in df_date.iterrows():
    session = int(row['Session'])
    date = pd.to_datetime(row['Date']).strftime('%Y-%m-%d')
    date_dict[session] = date

print("\nSimulazione per 3 righe:")

for idx, (_, row) in enumerate(df_profumo_valid.iterrows(), 1):
    print(f"\n--- RIGA {idx} ---")

    # Step 1: Estrai dati
    prod = str(row['Prod']).strip() if 'Prod' in row else None
    seduta = int(row['Seduta']) if 'Seduta' in row and pd.notna(row['Seduta']) else None
    commento = str(row[comment_col]).strip() if pd.notna(row[comment_col]) else ""

    print(f"Prod: {prod}")
    print(f"Seduta: {seduta}")
    print(f"Commento: {commento[:50]}...")

    # Step 2: Prod → codice_caseificio
    codice_caseificio = mapping_dict.get(prod)
    print(f"→ Codice caseificio (da mapping): {codice_caseificio}")

    if not codice_caseificio:
        print("❌ ERRORE: Codice prodotto non trovato nel mapping!")
        continue

    # Step 3: Seduta → data_seduta
    data_seduta = date_dict.get(seduta)
    print(f"→ Data seduta (da date_2018): {data_seduta}")

    if not data_seduta:
        print("❌ ERRORE: Numero seduta non trovato nel mapping date!")
        continue

    # Step 4: Costruisci sample_id
    sample_id = f"{codice_caseificio}_{data_seduta}"
    print(f"→ Sample ID atteso: {sample_id}")

    # Step 5: Verifica se esiste in campioni_completi
    sample_exists = sample_id in df_campioni['sample_id'].values
    print(f"→ Esiste in campioni_completi.csv: {'SÌ ✅' if sample_exists else 'NO ❌'}")

    if sample_exists:
        # Mostra i commenti_profumo per questo campione
        row_campione = df_campioni[df_campioni['sample_id'] == sample_id].iloc[0]
        commenti_json = row_campione['commenti_profumo']
        commenti_list = json.loads(commenti_json)
        print(f"→ Commenti profumo in campioni_completi: {len(commenti_list)} commenti")
        if commenti_list:
            print(f"   Esempi: {commenti_list[:2]}")
    else:
        print("❌ PERCHÉ NON ESISTE:")
        # Verifica se esiste con codice diverso
        matching_date = df_campioni[df_campioni['data_seduta'] == data_seduta]
        if len(matching_date) > 0:
            print(f"   - Campioni con stessa data ({data_seduta}):")
            for _, mc in matching_date.iterrows():
                print(f"     • {mc['sample_id']} (anno={mc['anno']})")
        else:
            print(f"   - Nessun campione con data {data_seduta}")

        # Verifica se esiste con stesso caseificio
        matching_cas = df_campioni[df_campioni['codice_caseificio'] == codice_caseificio]
        if len(matching_cas) > 0:
            print(f"   - Campioni con stesso caseificio ({codice_caseificio}): {len(matching_cas)}")
        else:
            print(f"   - Nessun campione con caseificio {codice_caseificio}")

# ============================================================================
# SALVA OUTPUT
# ============================================================================
print("\n" + "="*80)
print("DEBUG COMPLETATO")
print("="*80)

# Salva in file log
log_path = PROJECT_ROOT / "logs" / "debug_profumo_2018.txt"
print(f"\n[OUTPUT salvato in: {log_path}]")
