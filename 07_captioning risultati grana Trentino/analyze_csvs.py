import pandas as pd
import csv
import os

BASE = r"c:\Users\nicol\Desktop\CheeseCaptioningAIFQC\07_captioning risultati grana Trentino"

# Build the full list of (subdirectory, filename) pairs
files = []

# Directory 1: GT commenti liberi/csv dataset/
dir1 = os.path.join(BASE, "GT commenti liberi", "csv dataset")
for f in sorted(os.listdir(dir1)):
    if f.endswith(".csv"):
        files.append((dir1, f))

# Directory 2: GT commenti liberi/codifiche/
dir2 = os.path.join(BASE, "GT commenti liberi", "codifiche")
codifiche_csvs = [
    "codifica caseifici_codici caseifici.csv",
    "Risultati_2019-21_Medie Giuria2019_Q.csv",
    "Risultati_2019-21_Medie Giuria2021_Q.csv",
    "Risultati_2019-21_Medie Giuria2020_Q .csv",
]
for f in codifiche_csvs:
    files.append((dir2, f))

# Directory 3: validation_reports/
dir3 = os.path.join(BASE, "validation_reports")
files.append((dir3, "session_validation_report.csv"))


def detect_delimiter(filepath):
    """Detect the delimiter of a CSV file by sniffing the first few lines."""
    with open(filepath, "r", encoding="utf-8", errors="replace") as fh:
        sample = fh.read(8192)
    try:
        dialect = csv.Sniffer().sniff(sample, delimiters=",;\t|")
        return dialect.delimiter
    except csv.Error:
        return ","


def analyze_csv(directory, filename):
    filepath = os.path.join(directory, filename)
    rel_dir = os.path.relpath(directory, BASE)

    print("=" * 100)
    print(f"FILE: {filename}")
    print(f"DIR:  {rel_dir}")
    print(f"PATH: {filepath}")
    print("-" * 100)

    if not os.path.isfile(filepath):
        print("  *** FILE NOT FOUND ***\n")
        return

    delim = detect_delimiter(filepath)
    delim_name = {",": "comma", ";": "semicolon", "\t": "tab", "|": "pipe"}.get(delim, repr(delim))

    df = None
    for enc in ["utf-8", "latin-1", "cp1252"]:
        try:
            df = pd.read_csv(filepath, sep=delim, encoding=enc, on_bad_lines="warn")
            break
        except Exception:
            continue

    if df is None:
        print("  *** COULD NOT READ FILE ***\n")
        return

    print(f"DELIMITER: '{delim}' ({delim_name})")
    print(f"SHAPE:     {df.shape[0]} rows x {df.shape[1]} columns")
    print()
    print(f"COLUMNS ({df.shape[1]}):")
    for i, col in enumerate(df.columns):
        dtype = df[col].dtype
        non_null = df[col].notna().sum()
        print(f"  [{i}] {col!r:50s}  dtype={str(dtype):10s}  non-null={non_null}/{df.shape[0]}")
    print()
    print("FIRST 3 ROWS:")
    pd.set_option("display.max_columns", None)
    pd.set_option("display.width", 200)
    pd.set_option("display.max_colwidth", 60)
    print(df.head(3).to_string(index=True))
    print()


print(f"TOTAL FILES TO ANALYZE: {len(files)}")
print()

for directory, filename in files:
    analyze_csv(directory, filename)

print("=" * 100)
print("ANALYSIS COMPLETE")
