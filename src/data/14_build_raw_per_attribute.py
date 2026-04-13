"""
Nome Script: Build Raw Per Attribute - Unione commenti grezzi per attributo con path immagini
Scopo: Creare un CSV per attributo che unisce i dati grezzi di tutti gli anni (2018-2021),
       mantenendo l'unione delle colonne originali e aggiungendo le path alle immagini BMP.
Input:
    - 07_captioning risultati grana Trentino/GT commenti liberi/csv dataset/*.csv
    - 07_captioning risultati grana Trentino/GT commenti liberi/codifiche/codifica caseifici_codici caseifici.csv
    - data/processed/campioni_completi.csv (per le path immagini)
Output:
    - 07_captioning risultati grana Trentino/GT commenti liberi/raw_per_attribute/{Attributo}_raw.csv

Note sulla progettazione:
- Rinomina Sogg -> Panelista e Prod -> Prodotto per uniformare lo schema tra anni.
- Le colonne specifiche di un singolo anno (es. punteggio numerico 2018, N° Seduta, Bimestre)
  vengono mantenute come union con celle vuote dove non presenti: nessun dato originale perso.
- Per ogni riga vengono aggiunte 4 colonne con le path immagini dal campione fisico
  corrispondente (coppia caseificio + data_seduta):
    * path_fetta_primaria   (immagine primaria singola)
    * path_grana_primaria   (immagine primaria singola)
    * paths_fetta_tutti     (JSON array di tutte le fette disponibili per il campione)
    * paths_grana_tutti     (JSON array di tutte le grane disponibili per il campione)
- Flag booleano has_images per segnalare righe orfane senza corrispondenza immagine.

Autore: Claude Code
Data: 2026-04-13
"""

import logging
import re
import sys
from pathlib import Path
from typing import Any

import pandas as pd

# ── Setup encoding per stdout su Windows ────────────────────────────────────
try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(message)s",
)
logger = logging.getLogger(__name__)

# ── Percorsi ────────────────────────────────────────────────────────────────
PROJECT_ROOT = Path(__file__).parent.parent.parent
RAW_BASE = PROJECT_ROOT / "07_captioning risultati grana Trentino" / "GT commenti liberi"
CSV_DIR = RAW_BASE / "csv dataset"
CODIFICHE_DIR = RAW_BASE / "codifiche"
CAMPIONI_CSV = PROJECT_ROOT / "data" / "processed" / "campioni_completi.csv"
OUTPUT_DIR = RAW_BASE / "raw_per_attribute"

# ── Attributi supportati (nome file output) ─────────────────────────────────
# La chiave è il nome che userò nel file di output;
# il valore è il target normalizzato per il matching con i nomi file sorgenti.
ATTRIBUTI = {
    "Aroma": "aroma",
    "Profumo": "profumo",
    "Sapore": "sapore",
    "Texture": "texture",
    "Struttura_della_Pasta": "strutturadellapasta",
    "Colore_della_Pasta": "coloredellapasta",
    "Spessore_della_Crosta": "spessoredellacrosta",
}


# ── Loader: codifica caseifici ──────────────────────────────────────────────
def load_codifica_caseifici() -> dict[str, str]:
    """Carica il mapping codice_prodotto -> codice_caseificio.

    Il file non ha header. Schema: TN_302 | C0A | A | (extra)
    Restituisce: {'C0A': 'TN302', 'C0B': 'TN304', ...}
    """
    path = CODIFICHE_DIR / "codifica caseifici_codici caseifici.csv"
    if not path.exists():
        raise FileNotFoundError(f"Codifica caseifici non trovata: {path}")

    df = pd.read_csv(path, header=None, encoding="utf-8")
    mapping: dict[str, str] = {}
    for _, row in df.iterrows():
        caseificio_raw = str(row[0]).strip()
        prodotto_raw = str(row[1]).strip()
        if not caseificio_raw or caseificio_raw.lower() == "nan":
            continue
        if not prodotto_raw or prodotto_raw.lower() == "nan":
            continue
        codice_caseificio = caseificio_raw.replace("_", "")
        mapping[prodotto_raw] = codice_caseificio

    logger.info("Codifica caseifici caricata: %d voci", len(mapping))
    return mapping


# ── Loader: campioni_completi come indice immagini ──────────────────────────
def load_campioni_lookup() -> dict[tuple[str, str], dict[str, Any]]:
    """Carica campioni_completi.csv come lookup: (codice_caseificio, data_seduta) -> path images."""
    if not CAMPIONI_CSV.exists():
        raise FileNotFoundError(f"campioni_completi non trovato: {CAMPIONI_CSV}")

    df = pd.read_csv(CAMPIONI_CSV)
    logger.info("campioni_completi caricato: %d righe", len(df))

    lookup: dict[tuple[str, str], dict[str, Any]] = {}
    for _, row in df.iterrows():
        key = (str(row["codice_caseificio"]).strip(), str(row["data_seduta"]).strip())
        lookup[key] = {
            "path_fetta_primaria": row.get("path_fetta_primaria"),
            "path_grana_primaria": row.get("path_grana_primaria"),
            "paths_fetta_tutti": row.get("paths_fetta_tutti"),
            "paths_grana_tutti": row.get("paths_grana_tutti"),
        }
    return lookup


# ── Discovery dei file sorgenti per attributo ──────────────────────────────
_ATTR_PART_PATTERNS = [
    # "Commenti TOT_2018_Aroma" → Aroma
    re.compile(r"^Commenti\s+TOT_\d{4}_(?P<attr>.+)$"),
    # "Commenti liberi_QTG_2019_Aroma" → Aroma
    # "Commenti liberi_TEST_2021_Aroma" → Aroma
    re.compile(r"^Commenti\s+liberi_(?:QTG|TEST)_\d{4}_(?P<attr>.+)$"),
]


def _extract_attr_from_filename(stem: str) -> str | None:
    """Estrae la porzione 'attributo' dal nome file stem, None se non riconosciuto."""
    for pat in _ATTR_PART_PATTERNS:
        m = pat.match(stem)
        if m:
            return m.group("attr")
    return None


def _normalize_attr_name(name: str) -> str:
    """Normalizza nome attributo per il matching (lowercase, no spazi/underscore)."""
    return name.lower().replace(" ", "").replace("_", "")


def find_source_files(target_normalized: str) -> list[Path]:
    """Trova tutti i file sorgente per un attributo (target_normalized già normalizzato)."""
    files: list[Path] = []
    for f in sorted(CSV_DIR.glob("*.csv")):
        if "date_sedute" in f.stem:
            continue
        attr_part = _extract_attr_from_filename(f.stem)
        if attr_part is None:
            continue
        if _normalize_attr_name(attr_part) == target_normalized:
            files.append(f)
    return files


# ── Loader: singolo CSV sorgente ────────────────────────────────────────────
def load_source_csv(path: Path) -> pd.DataFrame:
    """Legge un CSV sorgente gestendo l'encoding. Normalizza spazi nei nomi colonna."""
    try:
        df = pd.read_csv(path, encoding="utf-8", on_bad_lines="skip")
    except UnicodeDecodeError:
        df = pd.read_csv(path, encoding="latin-1", on_bad_lines="skip")
    df.columns = df.columns.str.strip()
    return df


def normalize_column_names(df: pd.DataFrame) -> pd.DataFrame:
    """Rinomina Sogg->Panelista e Prod->Prodotto (solo se presenti)."""
    rename_map: dict[str, str] = {}
    if "Sogg" in df.columns:
        rename_map["Sogg"] = "Panelista"
    if "Prod" in df.columns:
        rename_map["Prod"] = "Prodotto"
    if rename_map:
        df = df.rename(columns=rename_map)
    return df


# ── Processing per attributo ────────────────────────────────────────────────
def process_attributo(
    attr_output_name: str,
    attr_target: str,
    codifica: dict[str, str],
    img_lookup: dict[tuple[str, str], dict[str, Any]],
) -> pd.DataFrame | None:
    """Elabora un singolo attributo: carica, unisce, aggiunge colonne derivate e immagini."""
    files = find_source_files(attr_target)
    if not files:
        logger.warning("Nessun file sorgente trovato per %s", attr_output_name)
        return None

    logger.info("[%s] file sorgenti:", attr_output_name)
    frames = []
    for f in files:
        df = load_source_csv(f)
        df = normalize_column_names(df)
        df["_source_file"] = f.name
        logger.info("  - %s  (%d righe, %d colonne)", f.name, len(df), len(df.columns))
        frames.append(df)

    merged = pd.concat(frames, ignore_index=True, sort=False)

    # Colonna derivata: codice_caseificio da Prodotto via codifica
    if "Prodotto" in merged.columns:
        merged["codice_caseificio"] = (
            merged["Prodotto"].astype(str).str.strip().map(codifica)
        )
    else:
        merged["codice_caseificio"] = None

    # Colonna derivata: anno dall'estrazione del year da Data Seduta di valutazione
    if "Data Seduta di valutazione" in merged.columns:
        merged["anno"] = pd.to_datetime(
            merged["Data Seduta di valutazione"], errors="coerce"
        ).dt.year.astype("Int64")
    else:
        merged["anno"] = pd.NA

    # Join con immagini su (codice_caseificio, Data Seduta di valutazione)
    def _lookup(row: pd.Series) -> pd.Series:
        cas = row.get("codice_caseificio")
        data = row.get("Data Seduta di valutazione")
        if pd.isna(cas) or pd.isna(data):
            return pd.Series(
                {
                    "path_fetta_primaria": None,
                    "path_grana_primaria": None,
                    "paths_fetta_tutti": None,
                    "paths_grana_tutti": None,
                }
            )
        key = (str(cas).strip(), str(data).strip())
        hit = img_lookup.get(key)
        if hit is None:
            return pd.Series(
                {
                    "path_fetta_primaria": None,
                    "path_grana_primaria": None,
                    "paths_fetta_tutti": None,
                    "paths_grana_tutti": None,
                }
            )
        return pd.Series(hit)

    img_cols = merged.apply(_lookup, axis=1)
    for col in [
        "path_fetta_primaria",
        "path_grana_primaria",
        "paths_fetta_tutti",
        "paths_grana_tutti",
    ]:
        merged[col] = img_cols[col]

    # Flag granulari per disponibilità immagini
    merged["has_fetta"] = merged["path_fetta_primaria"].notna()
    merged["has_grana"] = merged["path_grana_primaria"].notna()
    # has_images = almeno una vista disponibile (fetta-only è accettabile per training)
    merged["has_images"] = merged["has_fetta"] | merged["has_grana"]
    # has_both_views utile per modelli dual-view che richiedono entrambe
    merged["has_both_views"] = merged["has_fetta"] & merged["has_grana"]

    return merged


# ── Main ────────────────────────────────────────────────────────────────────
def main() -> None:
    logger.info("=" * 80)
    logger.info("BUILD RAW PER ATTRIBUTE")
    logger.info("=" * 80)

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    logger.info("Output directory: %s", OUTPUT_DIR)

    codifica = load_codifica_caseifici()
    img_lookup = load_campioni_lookup()

    summary_rows: list[dict[str, Any]] = []

    for attr_name, attr_target in ATTRIBUTI.items():
        logger.info("")
        df = process_attributo(attr_name, attr_target, codifica, img_lookup)
        if df is None:
            continue

        out_path = OUTPUT_DIR / f"{attr_name}_raw.csv"
        df.to_csv(out_path, index=False, encoding="utf-8")

        total = len(df)
        with_imgs = int(df["has_images"].sum())
        with_commento = int(df["Commenti"].notna().sum()) if "Commenti" in df.columns else 0
        orphan = total - with_imgs

        logger.info(
            "[%s] salvato %s — %d righe totali, %d con immagini (%.1f%%), %d orfane",
            attr_name,
            out_path.name,
            total,
            with_imgs,
            100 * with_imgs / total if total else 0,
            orphan,
        )
        summary_rows.append(
            {
                "attributo": attr_name,
                "righe_totali": total,
                "righe_con_commento": with_commento,
                "righe_con_immagini": with_imgs,
                "righe_orfane": orphan,
                "match_pct": round(100 * with_imgs / total, 1) if total else 0.0,
            }
        )

    logger.info("")
    logger.info("=" * 80)
    logger.info("SOMMARIO")
    logger.info("=" * 80)
    summary_df = pd.DataFrame(summary_rows)
    logger.info("\n%s", summary_df.to_string(index=False))
    logger.info("")
    logger.info(
        "Totale: %d righe, %d con immagini (%.1f%%)",
        summary_df["righe_totali"].sum(),
        summary_df["righe_con_immagini"].sum(),
        100
        * summary_df["righe_con_immagini"].sum()
        / summary_df["righe_totali"].sum()
        if summary_df["righe_totali"].sum()
        else 0,
    )


if __name__ == "__main__":
    main()
