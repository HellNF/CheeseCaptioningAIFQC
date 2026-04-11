"""Export dei FUORI_ATTRIBUTO candidati falsi negativi per revisione umana.

Produce data/interim/revisione_fuori_attributo.csv con colonne:
  attributo, id, commento_raw, caption, candidato_ok, nuova_classe

La colonna `candidato_ok` è True se il commento contiene keyword pertinenti
all'attributo — usarla come guida per la revisione.
La colonna `nuova_classe` è vuota: il revisore può scrivere OK, CONFORME
o lasciarla vuota per mantenere FUORI_ATTRIBUTO.

Uso:
    python src/data/export_revisione_fuori_attributo.py
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parents[2]))

import pandas as pd

ROOT = Path(__file__).parent.parent.parent
OUTPUT_DIR = ROOT / "data" / "processed" / "caption_per_attributo"
INTERIM_DIR = ROOT / "data" / "interim"

# Keywords che indicano pertinenza per ciascun attributo
KEYWORDS = {
    "Sapore": [
        "piccante", "salato", "amaro", "acido", "dolce", "umami", "sapido",
        "equilibrat", "neutro", "insapore", "persistente", "acre", "bruciante",
        "pungente", "sapore", "gustativo", "retrogusto", "blando", "intenso",
        "armonico", "disarmonico", "fresco", "maturo",
    ],
    "Aroma": [
        "burro", "panna", "lattico", "propionico", "fermentat", "brodo",
        "nocciola", "tostato", "latte", "crema", "frutto", "fiore", "grasso",
        "ossidato", "vaniglia", "caramello", "stantio", "animale", "cotto",
        "acido", "vegetale", "fungo", "muffa",
    ],
    "Profumo": [
        "intenso", "leggero", "forte", "debole", "elegante", "fresco",
        "pungente", "fermentat", "balsamico", "floreale", "fruttato",
        "note", "sentore", "olfatto", "aroma", "odore", "neutro", "complesso",
    ],
}

ATTRIBUTI_TARGET = list(KEYWORDS.keys())


def is_candidato(commento_raw: str, keywords: list[str]) -> bool:
    if not isinstance(commento_raw, str):
        return False
    testo = commento_raw.lower()
    return any(k in testo for k in keywords)


def main():
    righe = []
    for attributo in ATTRIBUTI_TARGET:
        csv_name = f"{attributo.replace(' ', '_')}_captions.csv"
        csv_path = OUTPUT_DIR / csv_name
        if not csv_path.exists():
            print(f"[WARN] {csv_path} non trovato, salto.")
            continue

        df = pd.read_csv(csv_path)
        fuori = df[df["classe"] == "FUORI_ATTRIBUTO"].copy()
        keywords = KEYWORDS[attributo]

        fuori["attributo"] = attributo
        fuori["candidato_ok"] = fuori["commento_raw"].apply(
            lambda x: is_candidato(x, keywords)
        )
        fuori["nuova_classe"] = ""

        righe.append(
            fuori[["attributo", "id", "commento_raw", "caption", "candidato_ok", "nuova_classe"]]
        )
        candidati = fuori["candidato_ok"].sum()
        print(f"{attributo}: {len(fuori)} FUORI, {candidati} candidati falsi negativi")

    if not righe:
        print("Nessun dato trovato.")
        return 1

    export = pd.concat(righe, ignore_index=True)
    # Candidati prima, poi non-candidati; dentro ogni gruppo per attributo
    export = export.sort_values(["attributo", "candidato_ok"], ascending=[True, False])

    INTERIM_DIR.mkdir(parents=True, exist_ok=True)
    out_path = INTERIM_DIR / "revisione_fuori_attributo.csv"
    export.to_csv(out_path, index=False, encoding="utf-8-sig")
    print(f"\nExport: {out_path} ({len(export)} righe)")
    print("Istruzioni: compila 'nuova_classe' con OK, CONFORME, o lascia vuota per FUORI_ATTRIBUTO.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
