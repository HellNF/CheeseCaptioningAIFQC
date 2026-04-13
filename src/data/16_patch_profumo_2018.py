"""
Nome Script: Patch Profumo 2018 — recupera le caption mancanti del file 2018
Scopo: Il run originale di 10_normalizza_commenti.py su Profumo ha processato solo i file
       2019-2021, lasciando fuori le 1083 righe del file Commenti TOT_2018_Profumo.csv.
       Questo script le processa ora in modo chirurgico, SENZA toccare le 395 righe esistenti
       e SENZA rieseguire gli altri attributi.

Strategia:
- Carica il CSV esistente (395 righe) e tutte le righe del sorgente (1478 via carica_commenti)
- Anti-join su (prodotto, panelista, commento_raw, anno) per identificare le 1083 mancanti
- Riassegna id sequenziali continuativi (396 in avanti)
- Pre-normalizzazione deterministica con vocabolario validato
- Carica baseline cached da baseline_descriptions/Profumo_baseline.json (no nuove chiamate LLM per baseline)
- Chiama LLM in batch da 20 per classe + caption (come script 10), con retry e checkpoint
- Appende al CSV esistente, preservando tutti gli id originali

Note:
- Le 1083 nuove righe non passano automaticamente per 11/12/13 (riprocessa CONFORME /
  FUORI_ATTRIBUTO / fix hallucinations). Se necessario, rilanciare questi script
  dopo aver applicato questo patch.

Uso:
    python src/data/16_patch_profumo_2018.py
    python src/data/16_patch_profumo_2018.py --dry-run
    python src/data/16_patch_profumo_2018.py --batch-size 20

Autore: Claude Code
Data: 2026-04-13
"""

import argparse
import json
import logging
import sys
import time
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path(__file__).parents[2]))

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

import openai
import pandas as pd
from dotenv import load_dotenv

load_dotenv()

from src.data.normalizza_commenti import (  # noqa: E402
    BATCH_SIZE_DEFAULT,
    MAX_RETRY_DEFAULT,
    MODEL_DEFAULT,
    carica_baseline,
    carica_commenti,
    carica_vocabolario,
    normalizza_batch,
    prenormalizza_commento,
)

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
logger = logging.getLogger(__name__)

# ── Percorsi ────────────────────────────────────────────────────────────────
ROOT = Path(__file__).parent.parent.parent
CSV_DIR = ROOT / "07_captioning risultati grana Trentino" / "GT commenti liberi" / "csv dataset"
VOCAB_DIR = ROOT / "data" / "interim" / "vocabolari_validati_per_attributo"
BASELINE_DIR = ROOT / "data" / "interim" / "baseline_descriptions"
CAPTIONS_CSV = (
    ROOT / "data" / "processed" / "caption_per_attributo" / "Profumo_captions.csv"
)
PATCH_CHECKPOINT_DIR = (
    ROOT / "data" / "interim" / "normalizzazione_in_corso_patch_profumo_2018"
)

ATTRIBUTO = "Profumo"


# ── Helpers ─────────────────────────────────────────────────────────────────
def _row_key(prodotto: Any, panelista: Any, commento_raw: Any, anno: Any) -> tuple[str, str, str, str]:
    """Chiave univoca per anti-join (allineata a carica_commenti)."""
    return (
        str(prodotto).strip(),
        str(panelista).strip(),
        str(commento_raw).strip(),
        str(anno).strip(),
    )


def _normalizza_con_retry(
    batch_input: list[dict],
    vocabolario: dict,
    baseline: str,
    client,
    model: str,
    max_retry: int,
) -> list[dict]:
    """Wrap di normalizza_batch con retry esponenziale."""
    for tentativo in range(max_retry):
        try:
            return normalizza_batch(batch_input, ATTRIBUTO, vocabolario, baseline, client, model)
        except Exception as exc:
            if tentativo < max_retry - 1:
                attesa = 10 * (2**tentativo)
                logger.warning(
                    "Errore batch (tentativo %d/%d): %s. Attendo %ds.",
                    tentativo + 1,
                    max_retry,
                    exc,
                    attesa,
                )
                time.sleep(attesa)
            else:
                logger.error("Errore batch (tentativo %d/%d): %s", tentativo + 1, max_retry, exc)
    return [{"id": it["id"], "classe": "ERRORE", "caption": None} for it in batch_input]


# ── Main ────────────────────────────────────────────────────────────────────
def main(dry_run: bool, batch_size: int, model: str, max_retry: int) -> int:
    logger.info("=" * 80)
    logger.info("PATCH PROFUMO 2018")
    logger.info("=" * 80)
    logger.info("Attributo:  %s", ATTRIBUTO)
    logger.info("Model:      %s", model)
    logger.info("Batch size: %d", batch_size)
    logger.info("Dry run:    %s", dry_run)

    # 1. Carica CSV esistente
    if not CAPTIONS_CSV.exists():
        logger.error("CSV esistente non trovato: %s", CAPTIONS_CSV)
        return 1
    df_existing = pd.read_csv(CAPTIONS_CSV)
    logger.info("CSV esistente: %d righe (id %d-%d)", len(df_existing),
                int(df_existing["id"].min()), int(df_existing["id"].max()))

    # 2. Carica tutte le righe del sorgente
    all_rows = carica_commenti(ATTRIBUTO, CSV_DIR)
    logger.info("carica_commenti: %d righe totali nel sorgente", len(all_rows))

    # 3. Identifica righe mancanti via anti-join
    existing_keys = {
        _row_key(r["prodotto"], r["panelista"], r["commento_raw"], r["anno"])
        for _, r in df_existing.iterrows()
    }
    missing = [
        r for r in all_rows
        if _row_key(r["prodotto"], r["panelista"], r["commento_raw"], r["anno"])
        not in existing_keys
    ]
    logger.info("Righe mancanti da processare: %d", len(missing))

    if not missing:
        logger.info("Niente da fare: tutte le righe sono già nel CSV.")
        return 0

    # Distribuzione anno delle mancanti (sanity check)
    from collections import Counter
    anni_missing = Counter(str(r["anno"]) for r in missing)
    logger.info("Distribuzione anno righe mancanti: %s", dict(sorted(anni_missing.items())))

    # 4. Riassegna id sequenziali continuativi (preserva quelli esistenti)
    next_id = int(df_existing["id"].max()) + 1
    for offset, r in enumerate(missing):
        r["id"] = next_id + offset
    logger.info("Nuovi id assegnati: %d-%d", next_id, next_id + len(missing) - 1)

    # 5. Carica vocabolario e baseline (cached)
    vocabolario = carica_vocabolario(ATTRIBUTO, VOCAB_DIR)
    n_sinonimi = len(vocabolario.get("sinonimi_diretti", []))
    n_cluster = len(vocabolario.get("cluster", []))
    logger.info("Vocabolario caricato: %d sinonimi, %d cluster", n_sinonimi, n_cluster)

    baseline = carica_baseline(ATTRIBUTO, BASELINE_DIR)
    logger.info("Baseline cached: %s", baseline[:120] + ("..." if len(baseline) > 120 else ""))

    # 6. Pre-normalizzazione deterministica
    for r in missing:
        r["commento_prenorm"] = prenormalizza_commento(r["commento_raw"], vocabolario)

    if dry_run:
        logger.info("")
        logger.info("DRY RUN — esempi di pre-normalizzazione:")
        for r in missing[:5]:
            logger.info("  [id=%d] %r -> %r", r["id"], r["commento_raw"], r["commento_prenorm"])
        logger.info("")
        logger.info("Nessuna chiamata LLM, nessun salvataggio.")
        return 0

    # 7. LLM client + checkpoint dir
    client = openai.OpenAI()
    PATCH_CHECKPOINT_DIR.mkdir(parents=True, exist_ok=True)
    logger.info("Checkpoint dir: %s", PATCH_CHECKPOINT_DIR)

    # 8. Processa in batch, riusando eventuali checkpoint già salvati
    risultati: list[dict] = []
    n_batches = (len(missing) + batch_size - 1) // batch_size
    for bi in range(n_batches):
        chunk = missing[bi * batch_size : (bi + 1) * batch_size]
        checkpoint_path = PATCH_CHECKPOINT_DIR / f"{ATTRIBUTO}_batch_{bi:04d}.json"

        if checkpoint_path.exists():
            with open(checkpoint_path, encoding="utf-8") as f:
                cached = json.load(f)
            risultati.extend(cached)
            logger.debug("Batch %d caricato da checkpoint.", bi)
            continue

        batch_input = [{"id": r["id"], "commento_prenorm": r["commento_prenorm"]} for r in chunk]
        logger.info("Batch %d/%d (%d commenti)", bi + 1, n_batches, len(batch_input))

        out = _normalizza_con_retry(batch_input, vocabolario, baseline, client, model, max_retry)

        # Arricchisci con metadati (commento_raw, prodotto, ecc.)
        meta_by_id = {r["id"]: r for r in chunk}
        for o in out:
            meta = meta_by_id.get(o["id"], {})
            o.update(
                {
                    "commento_raw": meta.get("commento_raw", ""),
                    "commento_prenorm": meta.get("commento_prenorm", ""),
                    "anno": meta.get("anno", ""),
                    "prodotto": meta.get("prodotto", ""),
                    "panelista": meta.get("panelista", ""),
                    "peso": 1.0,
                }
            )

        with open(checkpoint_path, "w", encoding="utf-8") as f:
            json.dump(out, f, ensure_ascii=False)
        risultati.extend(out)

    # 9. Combina con esistente e salva
    new_df = pd.DataFrame(risultati)

    # Allinea colonne con l'esistente
    for col in df_existing.columns:
        if col not in new_df.columns:
            new_df[col] = pd.NA
    new_df = new_df[df_existing.columns.tolist()]

    combined = pd.concat([df_existing, new_df], ignore_index=True)
    combined = combined.sort_values("id").reset_index(drop=True)

    # Backup e salva
    backup_path = CAPTIONS_CSV.with_suffix(".csv.pre_patch.bak")
    if not backup_path.exists():
        df_existing.to_csv(backup_path, index=False, encoding="utf-8")
        logger.info("Backup esistente creato: %s", backup_path.name)

    combined.to_csv(CAPTIONS_CSV, index=False, encoding="utf-8")
    logger.info(
        "Salvato %s: %d righe totali (%d esistenti + %d nuove)",
        CAPTIONS_CSV.name,
        len(combined),
        len(df_existing),
        len(new_df),
    )

    # 10. Report distribuzione classi nuove
    logger.info("")
    logger.info("Distribuzione classi nuove righe:")
    for c, n in new_df["classe"].value_counts(dropna=False).items():
        logger.info("  %s: %d", c, n)

    return 0


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Patch Profumo 2018 mancante.")
    parser.add_argument("--dry-run", action="store_true", help="Solo pre-normalizzazione, no API")
    parser.add_argument("--batch-size", type=int, default=BATCH_SIZE_DEFAULT)
    parser.add_argument("--model", default=MODEL_DEFAULT)
    parser.add_argument("--max-retry", type=int, default=MAX_RETRY_DEFAULT)
    args = parser.parse_args()
    sys.exit(
        main(
            dry_run=args.dry_run,
            batch_size=args.batch_size,
            model=args.model,
            max_retry=args.max_retry,
        )
    )
