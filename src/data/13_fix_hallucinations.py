"""Fase 4d — Correzione caption hallucinate (baseline ripetuta su righe OK).

Rileva righe OK con caption uguale alla baseline o quasi, le riprocessa
con un prompt che impone fedeltà al commento originale.

Uso:
    python src/data/13_fix_hallucinations.py
    python src/data/13_fix_hallucinations.py --attributo Sapore
    python src/data/13_fix_hallucinations.py --dry-run
"""
import argparse
import logging
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parents[2]))

import openai
import pandas as pd
from dotenv import load_dotenv

load_dotenv()

from src.data.normalizza_commenti import (
    ATTRIBUTI,
    carica_vocabolario,
    carica_baseline,
    trova_hallucinate,
    normalizza_faithful_batch,
    MODEL_DEFAULT,
    BATCH_SIZE_DEFAULT,
    MAX_RETRY_DEFAULT,
)

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
logger = logging.getLogger(__name__)

ROOT = Path(__file__).parent.parent.parent
VOCAB_DIR = ROOT / "data" / "interim" / "vocabolari_validati_per_attributo"
BASELINE_DIR = ROOT / "data" / "interim" / "baseline_descriptions"
OUTPUT_DIR = ROOT / "data" / "processed" / "caption_per_attributo"


def _faithful_con_retry(batch, attributo, vocabolario, baseline, client, model, max_retry):
    for tentativo in range(max_retry):
        try:
            return normalizza_faithful_batch(batch, attributo, vocabolario, baseline, client, model)
        except Exception as exc:
            if tentativo < max_retry - 1:
                attesa = 10 * (2 ** tentativo)
                logger.warning(f"Errore (tentativo {tentativo+1}/{max_retry}): {exc}. Attendo {attesa}s.")
                time.sleep(attesa)
            else:
                logger.error(f"Batch fallito dopo {max_retry} tentativi: {exc}")
    return [{"id": item["id"], "classe": "ERRORE", "caption": None} for item in batch]


def processa_attributo(attributo, client, model, batch_size, max_retry, dry_run):
    csv_path = OUTPUT_DIR / f"{attributo.replace(' ', '_')}_captions.csv"
    df = pd.read_csv(csv_path)

    baseline = carica_baseline(attributo, BASELINE_DIR)
    sospette = trova_hallucinate(df, baseline)

    if len(sospette) == 0:
        logger.info(f"[{attributo}] Nessuna caption hallucinata trovata.")
        return

    logger.info(f"[{attributo}] {len(sospette)} righe con caption hallucinata da riprocessare.")

    if dry_run:
        captions_uniche = sospette["caption"].value_counts()
        for cap, n in captions_uniche.head(3).items():
            logger.info(f"  DRY-RUN: x{n} '{cap[:80]}'")
        return

    vocabolario = carica_vocabolario(attributo, VOCAB_DIR)

    # Usa commento_raw per aggirare eventuali prenorm degradati
    batch_list = [
        {"id": row["id"], "commento_prenorm": row["commento_raw"]}
        for _, row in sospette.iterrows()
    ]
    batches = [batch_list[i:i + batch_size] for i in range(0, len(batch_list), batch_size)]

    tutti_risultati = []
    for idx, batch in enumerate(batches):
        logger.info(f"[{attributo}] Batch {idx+1}/{len(batches)}...")
        risultati = _faithful_con_retry(batch, attributo, vocabolario, baseline, client, model, max_retry)
        tutti_risultati.extend(risultati)

    # Aggiorna solo le righe riprocessate
    risultati_map = {r["id"]: r for r in tutti_risultati}
    for idx_row in df.index:
        row_id = df.at[idx_row, "id"]
        if row_id in risultati_map:
            df.at[idx_row, "classe"] = risultati_map[row_id]["classe"]
            df.at[idx_row, "caption"] = risultati_map[row_id]["caption"]
    df.to_csv(csv_path, index=False)

    rimaste_hallucinate = sum(
        1 for r in tutti_risultati
        if isinstance(r.get("caption"), str) and r["caption"] in sospette["caption"].values
    )
    logger.info(
        f"[{attributo}] Riprocessate: {len(sospette)}. "
        f"Ancora uguali alla baseline: {rimaste_hallucinate}. "
        f"Errori: {sum(1 for r in tutti_risultati if r['classe'] == 'ERRORE')}."
    )


def main() -> int:
    parser = argparse.ArgumentParser(description="Fase 4d — Fix caption hallucinate")
    parser.add_argument("--attributo", choices=ATTRIBUTI)
    parser.add_argument("--model", default=MODEL_DEFAULT)
    parser.add_argument("--batch-size", type=int, default=BATCH_SIZE_DEFAULT)
    parser.add_argument("--max-retry", type=int, default=MAX_RETRY_DEFAULT)
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    client = None if args.dry_run else openai.OpenAI()
    attributi = [args.attributo] if args.attributo else ATTRIBUTI

    n_errori = 0
    for attributo in attributi:
        try:
            processa_attributo(attributo, client, args.model, args.batch_size, args.max_retry, args.dry_run)
        except Exception as exc:
            logger.error(f"[{attributo}] Errore fatale: {exc}")
            n_errori += 1

    return 1 if n_errori else 0


if __name__ == "__main__":
    sys.exit(main())
