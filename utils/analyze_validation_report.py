"""
Analisi completa del validation report con statistiche dettagliate.

Dopo l'aggiornamento del validation script (supporto 2018-2022, match su data),
questo script analizza il nuovo report per identificare:
- Distribuzione errori per tipo
- Breakdown per anno e file CSV
- Date specifiche senza immagini
- Suggerimenti per azioni correttive

Output: stampa report console + opzionale CSV riassuntivo
"""
import pandas as pd
from pathlib import Path
from collections import Counter
from typing import Dict, List

# Percorsi
PROJECT_ROOT = Path(__file__).resolve().parents[1]
VALIDATION_CSV = PROJECT_ROOT / "07_captioning risultati grana Trentino" / "validation_reports" / "session_validation_report.csv"
OUTPUT_DIR = PROJECT_ROOT / "reports"

def load_validation_report() -> pd.DataFrame:
    """Carica il validation report."""
    if not VALIDATION_CSV.exists():
        raise FileNotFoundError(f"Validation report non trovato: {VALIDATION_CSV}")

    df = pd.read_csv(VALIDATION_CSV, encoding='utf-8')
    print(f"OK Caricato validation report: {len(df)} issue trovate\n")
    return df

def analyze_by_type(df: pd.DataFrame) -> Dict[str, int]:
    """Analizza la distribuzione per tipo di errore."""
    print("=" * 70)
    print("ANALISI PER TIPO DI ERRORE")
    print("=" * 70)

    type_counts = df['issue_type'].value_counts().to_dict()
    total = len(df)

    for issue_type, count in sorted(type_counts.items(), key=lambda x: -x[1]):
        pct = (count / total * 100) if total > 0 else 0
        print(f"  {issue_type:25s}: {count:4d} ({pct:5.1f}%)")

    print()
    return type_counts

def analyze_by_year(df: pd.DataFrame) -> Dict[str, Dict[str, int]]:
    """Analizza la distribuzione per anno."""
    print("=" * 70)
    print("ANALISI PER ANNO")
    print("=" * 70)

    # Estrai anno dalla data seduta
    df['anno'] = pd.to_datetime(df['data_seduta'], errors='coerce').dt.year

    results = {}
    for anno in sorted(df['anno'].dropna().unique()):
        anno_int = int(anno)
        df_anno = df[df['anno'] == anno]

        print(f"\n{anno_int}:")
        print(f"  Totale errori: {len(df_anno)}")

        # Breakdown per tipo
        type_counts = df_anno['issue_type'].value_counts()
        for issue_type, count in type_counts.items():
            print(f"    - {issue_type}: {count}")

        results[str(anno_int)] = type_counts.to_dict()

    print()
    return results

def analyze_by_file(df: pd.DataFrame) -> Dict[str, int]:
    """Analizza la distribuzione per file CSV."""
    print("=" * 70)
    print("ANALISI PER FILE CSV (top 15)")
    print("=" * 70)

    file_counts = df['csv_file'].value_counts()

    for csv_file, count in file_counts.head(15).items():
        print(f"  {csv_file:50s}: {count:3d} issue")

    if len(file_counts) > 15:
        print(f"  ... e altri {len(file_counts) - 15} file")

    print()
    return file_counts.to_dict()

def analyze_missing_sessions(df: pd.DataFrame) -> List[str]:
    """Analizza le date senza immagini (sessione_inesistente)."""
    print("=" * 70)
    print("DATE SENZA IMMAGINI (sessione_inesistente)")
    print("=" * 70)

    missing = df[df['issue_type'] == 'sessione_inesistente'].copy()

    if len(missing) == 0:
        print("  Nessuna sessione mancante!\n")
        return []

    print(f"  Totale: {len(missing)} righe CSV senza cartella immagini\n")

    # Date uniche senza immagini
    date_mancanti = missing['data_seduta'].unique()
    print(f"  Date uniche senza immagini: {len(date_mancanti)}\n")

    # Mostra prime 20 date
    print("  Prime 20 date senza immagini:")
    for i, data in enumerate(sorted(date_mancanti)[:20], 1):
        count = (missing['data_seduta'] == data).sum()
        print(f"    {i:2d}. {data}: {count} righe CSV")

    if len(date_mancanti) > 20:
        print(f"    ... e altre {len(date_mancanti) - 20} date")

    print()
    return list(date_mancanti)

def analyze_missing_assets(df: pd.DataFrame):
    """Analizza i file immagini mancanti specifici (asset_mancante)."""
    print("=" * 70)
    print("FILE IMMAGINI MANCANTI (asset_mancante)")
    print("=" * 70)

    missing_assets = df[df['issue_type'] == 'asset_mancante'].copy()

    if len(missing_assets) == 0:
        print("  Nessun file immagine mancante!\n")
        return

    print(f"  Totale: {len(missing_assets)} righe con file immagine mancante\n")

    # Breakdown per caseificio
    print("  Top 10 caseifici con file mancanti:")
    caseifici = missing_assets['caseificio'].value_counts()
    for caseificio, count in caseifici.head(10).items():
        print(f"    {caseificio}: {count}")

    print()

def analyze_missing_prodotto(df: pd.DataFrame):
    """Analizza i prodotti mancanti nei CSV."""
    print("=" * 70)
    print("PRODOTTI MANCANTI NEI CSV (missing_prodotto)")
    print("=" * 70)

    missing_prod = df[df['issue_type'] == 'missing_prodotto'].copy()

    if len(missing_prod) == 0:
        print("  Nessun prodotto mancante!\n")
        return

    print(f"  Totale: {len(missing_prod)} righe con campo Prodotto vuoto\n")

    # Breakdown per file
    print("  File con più prodotti mancanti:")
    files = missing_prod['csv_file'].value_counts()
    for csv_file, count in files.head(10).items():
        print(f"    {csv_file}: {count}")

    print()

def generate_summary(df: pd.DataFrame):
    """Genera sommario finale con raccomandazioni."""
    print("=" * 70)
    print("SOMMARIO E RACCOMANDAZIONI")
    print("=" * 70)

    total = len(df)

    type_counts = df['issue_type'].value_counts().to_dict()

    sessione_inesistente = type_counts.get('sessione_inesistente', 0)
    asset_mancante = type_counts.get('asset_mancante', 0)
    missing_prodotto = type_counts.get('missing_prodotto', 0)

    print(f"\nSTATS Totale issue: {total}")
    print(f"  - Sessioni senza immagini: {sessione_inesistente} (date realmente senza foto)")
    print(f"  - File immagini specifici mancanti: {asset_mancante}")
    print(f"  - Prodotti mancanti nei CSV: {missing_prodotto}")

    print("\nRACCOMANDAZIONI Raccomandazioni:")

    if sessione_inesistente > 0:
        print(f"\n  1. Sessioni senza immagini ({sessione_inesistente} errori):")
        print(f"     -> Sono date con dati sensoriali ma senza foto")
        print(f"     -> NORMALE: alcune sedute erano solo valutazioni sensoriali")
        print(f"     -> Azione: escludere queste date dal dataset finale")

    if asset_mancante > 0:
        print(f"\n  2. File immagini mancanti ({asset_mancante} errori):")
        print(f"     -> File immagini specifici non trovati nelle cartelle")
        print(f"     -> Azione: verificare se i file esistono con nomi diversi")
        print(f"     -> Oppure: escludere questi campioni dal dataset")

    if missing_prodotto > 0:
        print(f"\n  3. Prodotti mancanti ({missing_prodotto} errori):")
        print(f"     -> Campo 'Prodotto' vuoto nei CSV")
        print(f"     -> Azione: correggere i CSV o escludere queste righe")

    print()

def main():
    """Main function."""
    print("\n" + "=" * 70)
    print("ANALISI VALIDATION REPORT - DATASET GRANA TRENTINO")
    print("=" * 70)
    print()

    # Carica report
    df = load_validation_report()

    # Analisi
    analyze_by_type(df)
    analyze_by_year(df)
    analyze_by_file(df)
    analyze_missing_sessions(df)
    analyze_missing_assets(df)
    analyze_missing_prodotto(df)
    generate_summary(df)

    print("=" * 70)
    print("Analisi completata!")
    print("=" * 70)

if __name__ == "__main__":
    main()
