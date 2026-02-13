import pandas as pd
import glob
import os

# cartella dove si trovano i file .xlsx
cartella = "07_captioning risultati grana Trentino\GT commenti liberi\codifiche"

# cerca tutti i file .xlsx
file_excel = glob.glob(os.path.join(cartella, "*.xlsx"))

for file in file_excel:
    # ricava il nome base del file senza estensione
    nome_base = os.path.splitext(os.path.basename(file))[0]

    # carica il file Excel
    excel = pd.ExcelFile(file)

    for sheet in excel.sheet_names:
        df = pd.read_excel(excel, sheet_name=sheet)

        # nome del csv: nomefile_nomefoglio.csv
        nome_csv = f"{nome_base}_{sheet}.csv"

        # salva nella stessa cartella
        df.to_csv(os.path.join(cartella, nome_csv), index=False)

    print(f"Convertito: {file}")
