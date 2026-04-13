"""
Nome Script: Merge Captions with Images - Unione finale caption + immagini per training
Scopo: Unire i CSV raw_per_attribute (con Data Seduta, path immagini, e tutti i metadata grezzi)
       con caption_per_attributo (classe, caption, peso dalla normalizzazione LLM).
       Produce il dataset finale arricchito per training del captioning.

Input:
    - 07_captioning risultati grana Trentino/GT commenti liberi/raw_per_attribute/{Attr}_raw.csv
    - data/processed/caption_per_attributo/{Attr}_captions.csv

Output:
    - data/processed/caption_per_attributo/{Attr}_full.csv   (uno per attributo, raw + LLM + images)
    - data/processed/dataset_captioning.csv                  (combinato, tutti gli attributi,
                                                              solo righe con caption e immagini)

Strategia di join:
- Chiavi di join: (prodotto, panelista, commento_raw_stripped, dataset_year)
- dataset_year è estratto dal nome del file sorgente (non dalla data seduta),
  perché il file "Commenti TOT_2018_*.csv" contiene anche sedute di gennaio-aprile 2019
  (le date reali vanno da agosto 2018 ad aprile 2019).
- cumcount() gestisce le chiavi duplicate (stesso panelista + stesso commento in sedute
  diverse): il primo duplicato raw è abbinato al primo caption duplicato, e così via.
  L'output LLM dipende solo dal testo del commento, quindi l'assegnazione è equivalente.

Determinismo:
- Pre-normalizzazione (vocabolario → commento_prenorm): deterministica
- Chiamate LLM (classe, caption): non deterministiche, ma già eseguite e cached nei CSV
- Il join pandas qui è puramente deterministico, zero chiamate API

Autore: Claude Code
Data: 2026-04-13
"""

import logging
import re
import sys
from pathlib import Path

import pandas as pd

# ── Setup encoding stdout Windows ───────────────────────────────────────────
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
RAW_DIR = (
    PROJECT_ROOT
    / "07_captioning risultati grana Trentino"
    / "GT commenti liberi"
    / "raw_per_attribute"
)
CAP_DIR = PROJECT_ROOT / "data" / "processed" / "caption_per_attributo"
OUT_DIR = CAP_DIR  # stesso folder; output con suffisso _full
DATASET_OUT = PROJECT_ROOT / "data" / "processed" / "dataset_captioning.csv"

ATTRIBUTI = [
    "Aroma",
    "Profumo",
    "Sapore",
    "Texture",
    "Struttura_della_Pasta",
    "Colore_della_Pasta",
    "Spessore_della_Crosta",
]

# ── Helpers ─────────────────────────────────────────────────────────────────
_YEAR_RE = re.compile(r"20\d{2}")


def extract_dataset_year(source_filename: str) -> str | None:
    """Estrae l'anno dal nome del file sorgente (es. 'Commenti TOT_2018_Aroma.csv' -> '2018')."""
    if not isinstance(source_filename, str):
        return None
    m = _YEAR_RE.search(source_filename)
    return m.group(0) if m else None


def _norm_str(series: pd.Series) -> pd.Series:
    """Cast a stringa e strip, preservando NaN."""
    return series.astype(str).where(series.notna(), None).str.strip()


def load_raw(attr: str) -> pd.DataFrame:
    path = RAW_DIR / f"{attr}_raw.csv"
    df = pd.read_csv(path)
    logger.info("  raw  %s: %d righe, %d colonne", attr, len(df), len(df.columns))
    return df


def load_captions(attr: str) -> pd.DataFrame:
    path = CAP_DIR / f"{attr}_captions.csv"
    df = pd.read_csv(path)
    logger.info("  cap  %s: %d righe, %d colonne", attr, len(df), len(df.columns))
    return df


def build_join_keys(
    raw: pd.DataFrame, cap: pd.DataFrame
) -> tuple[pd.DataFrame, pd.DataFrame, list[str]]:
    """Prepara le colonne chiave per il join, aggiungendo _dup per gestire duplicati.

    Ritorna (raw_augmented, cap_augmented, lista_chiavi_join).
    """
    raw = raw.copy()
    cap = cap.copy()

    # Chiavi derivate per raw
    raw["_k_prodotto"] = _norm_str(raw["Prodotto"])
    raw["_k_panelista"] = _norm_str(raw["Panelista"])
    raw["_k_commento"] = _norm_str(raw["Commenti"])
    raw["_k_dataset_year"] = raw["_source_file"].apply(extract_dataset_year)

    # Chiavi derivate per cap
    cap["_k_prodotto"] = _norm_str(cap["prodotto"])
    cap["_k_panelista"] = _norm_str(cap["panelista"])
    cap["_k_commento"] = _norm_str(cap["commento_raw"])
    cap["_k_dataset_year"] = cap["anno"].astype("Int64").astype(str)

    keys = ["_k_prodotto", "_k_panelista", "_k_commento", "_k_dataset_year"]

    # cumcount per gestire duplicati (stesso commento più volte nello stesso anno)
    raw["_k_dup"] = raw.groupby(keys).cumcount()
    cap["_k_dup"] = cap.groupby(keys).cumcount()
    keys_full = keys + ["_k_dup"]

    return raw, cap, keys_full


def merge_one_attribute(attr: str) -> pd.DataFrame | None:
    """Esegue join raw + cap per un singolo attributo e restituisce il df arricchito."""
    logger.info("[%s]", attr)
    try:
        raw = load_raw(attr)
        cap = load_captions(attr)
    except FileNotFoundError as e:
        logger.warning("  File non trovato per %s: %s", attr, e)
        return None

    raw, cap, keys_full = build_join_keys(raw, cap)

    # Colonne della caption che vogliamo portare nel risultato
    cap_cols_to_bring = ["id", "classe", "caption", "commento_prenorm", "peso"]

    merged = raw.merge(
        cap[keys_full + cap_cols_to_bring],
        on=keys_full,
        how="left",
        suffixes=("", "_cap"),
    )

    # Rimuovi le colonne ausiliarie di join dal risultato
    merged = merged.drop(columns=keys_full)

    # Rinomina la colonna id per chiarezza
    merged = merged.rename(columns={"id": "caption_id"})

    # Aggiungi attributo (utile per il dataset combinato)
    merged.insert(0, "attributo", attr)

    # Sample id per traceability
    merged["sample_id"] = merged.apply(
        lambda r: (
            f"{r['codice_caseificio']}_{r['Data Seduta di valutazione']}"
            if pd.notna(r.get("codice_caseificio"))
            and pd.notna(r.get("Data Seduta di valutazione"))
            else None
        ),
        axis=1,
    )

    # Flag derivati
    merged["has_caption"] = merged["caption"].notna()

    # Report
    tot = len(merged)
    has_img = int(merged["has_images"].sum())
    has_cap = int(merged["has_caption"].sum())
    has_both = int((merged["has_images"] & merged["has_caption"]).sum())
    logger.info(
        "  MERGE %s: %d totali, %d con immagini, %d con caption, %d trainable",
        attr,
        tot,
        has_img,
        has_cap,
        has_both,
    )

    return merged


def reorder_columns(df: pd.DataFrame) -> pd.DataFrame:
    """Mette le colonne principali all'inizio per leggibilità."""
    preferred = [
        "attributo",
        "sample_id",
        "caption_id",
        "codice_caseificio",
        "Prodotto",
        "Panelista",
        "Data Seduta di valutazione",
        "anno",
        "classe",
        "caption",
        "commento_prenorm",
        "Commenti",
        "peso",
        "has_caption",
        "has_images",
        "has_fetta",
        "has_grana",
        "has_both_views",
        "path_fetta_primaria",
        "path_grana_primaria",
        "paths_fetta_tutti",
        "paths_grana_tutti",
    ]
    existing_preferred = [c for c in preferred if c in df.columns]
    remaining = [c for c in df.columns if c not in existing_preferred]
    return df[existing_preferred + remaining]


def main() -> None:
    logger.info("=" * 80)
    logger.info("MERGE CAPTIONS WITH IMAGES")
    logger.info("=" * 80)
    logger.info("Raw dir: %s", RAW_DIR)
    logger.info("Caption dir: %s", CAP_DIR)
    logger.info("")

    all_frames: list[pd.DataFrame] = []
    summary_rows: list[dict] = []

    for attr in ATTRIBUTI:
        merged = merge_one_attribute(attr)
        if merged is None:
            continue

        merged = reorder_columns(merged)

        # Salva file per attributo
        out_path = OUT_DIR / f"{attr}_full.csv"
        merged.to_csv(out_path, index=False, encoding="utf-8")
        logger.info("  salvato %s", out_path.name)

        all_frames.append(merged)

        commento_non_vuoto = merged["Commenti"].notna() & (
            merged["Commenti"].astype(str).str.strip() != ""
        )
        summary_rows.append(
            {
                "attributo": attr,
                "righe_totali": len(merged),
                "con_commento": int(commento_non_vuoto.sum()),
                "con_caption": int(merged["has_caption"].sum()),
                "con_immagini": int(merged["has_images"].sum()),
                "trainable": int(
                    (merged["has_caption"] & merged["has_images"]).sum()
                ),
            }
        )
        logger.info("")

    # Dataset combinato
    if all_frames:
        combined = pd.concat(all_frames, ignore_index=True, sort=False)
        combined.to_csv(DATASET_OUT, index=False, encoding="utf-8")
        logger.info("Dataset combinato salvato: %s (%d righe)", DATASET_OUT, len(combined))

        trainable = combined[combined["has_caption"] & combined["has_images"]]
        logger.info("  trainable (has_caption & has_images): %d", len(trainable))

    # Sommario
    logger.info("")
    logger.info("=" * 80)
    logger.info("SOMMARIO")
    logger.info("=" * 80)
    summary_df = pd.DataFrame(summary_rows)
    logger.info("\n%s", summary_df.to_string(index=False))
    if not summary_df.empty:
        logger.info("")
        logger.info(
            "TOT: %d righe, %d con caption, %d con immagini, %d trainable",
            summary_df["righe_totali"].sum(),
            summary_df["con_caption"].sum(),
            summary_df["con_immagini"].sum(),
            summary_df["trainable"].sum(),
        )


if __name__ == "__main__":
    main()
