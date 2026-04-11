# src/data/12_riprocessa_fuori_attributo.py
"""Fase 4c — Generazione caption per righe FUORI_ATTRIBUTO.

Uso:
    python src/data/12_riprocessa_fuori_attributo.py
    python src/data/12_riprocessa_fuori_attributo.py --attributo Aroma
    python src/data/12_riprocessa_fuori_attributo.py --dry-run
"""
import argparse
import json
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
    riprocessa_fuori_attributo_batch,
    MODEL_DEFAULT,
    BATCH_SIZE_DEFAULT,
    MAX_RETRY_DEFAULT,
)

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
logger = logging.getLogger(__name__)

ROOT = Path(__file__).parent.parent.parent
OUTPUT_DIR = ROOT / "data" / "processed" / "caption_per_attributo"
CHECKPOINT_DIR = ROOT / "data" / "interim" / "riprocessa_fuori_attributo_in_corso"
REPORTS_DIR = ROOT / "reports"


def _fuori_con_retry(batch, client, model, max_retry):
    for tentativo in range(max_retry):
        try:
            return riprocessa_fuori_attributo_batch(batch, client, model)
        except Exception as exc:
            if tentativo < max_retry - 1:
                attesa = 10 * (2 ** tentativo)
                logger.warning(f"Errore (tentativo {tentativo+1}/{max_retry}): {exc}. Attendo {attesa}s.")
                time.sleep(attesa)
            else:
                logger.warning(f"Errore (tentativo {tentativo+1}/{max_retry}): {exc}.")
    logger.error(f"Batch fallito dopo {max_retry} tentativi.")
    return [{"id": item["id"], "caption": None} for item in batch]


def processa_attributo(attributo, client, model, batch_size, max_retry, dry_run):
    csv_path = OUTPUT_DIR / f"{attributo.replace(' ', '_')}_captions.csv"
    df = pd.read_csv(csv_path)

    fuori_rows = df[(df["classe"] == "FUORI_ATTRIBUTO") & (df["caption"].isna())].copy()
    if len(fuori_rows) == 0:
        logger.info(f"[{attributo}] Nessun FUORI_ATTRIBUTO senza caption.")
        return

    logger.info(f"[{attributo}] {len(fuori_rows)} FUORI_ATTRIBUTO da processare.")

    if dry_run:
        for _, row in fuori_rows.head(3).iterrows():
            logger.info(f"  DRY-RUN: [{row['id']}] {row['commento_raw']}")
        return

    CHECKPOINT_DIR.mkdir(parents=True, exist_ok=True)

    batch_list = fuori_rows[["id", "commento_raw"]].to_dict("records")
    batches = [batch_list[i:i + batch_size] for i in range(0, len(batch_list), batch_size)]

    tutti_risultati = []
    for idx, batch in enumerate(batches):
        ckpt = CHECKPOINT_DIR / f"{attributo.replace(' ', '_')}_batch_{idx:04d}.json"
        if ckpt.exists():
            with open(ckpt, encoding="utf-8") as f:
                tutti_risultati.extend(json.load(f))
            logger.info(f"[{attributo}] Batch {idx+1}/{len(batches)} da checkpoint.")
            continue
        risultati = _fuori_con_retry(batch, client, model, max_retry)
        tutti_risultati.extend(risultati)
        with open(ckpt, "w", encoding="utf-8") as f:
            json.dump(risultati, f, ensure_ascii=False)
        logger.info(f"[{attributo}] Batch {idx+1}/{len(batches)} completato.")

    # Aggiorna solo la colonna caption (classe invariata)
    risultati_map = {r["id"]: r["caption"] for r in tutti_risultati}
    for idx_row in df.index:
        row_id = df.at[idx_row, "id"]
        if row_id in risultati_map and risultati_map[row_id] is not None:
            df.at[idx_row, "caption"] = risultati_map[row_id]
    df.to_csv(csv_path, index=False)

    con_caption = sum(1 for r in tutti_risultati if r["caption"] is not None)
    senza_caption = len(fuori_rows) - con_caption
    logger.info(f"[{attributo}] Caption generate: {con_caption}/{len(fuori_rows)}")

    REPORTS_DIR.mkdir(parents=True, exist_ok=True)
    report_path = REPORTS_DIR / f"riprocessa_fuori_attributo_{attributo.replace(' ', '_')}.md"
    lines = [
        f"# Report riprocessamento FUORI_ATTRIBUTO — {attributo}",
        "",
        f"- Righe processate: {len(fuori_rows)}",
        f"- Caption generate: {con_caption}",
        f"- Senza caption (errori): {senza_caption}",
    ]
    report_path.write_text("\n".join(lines), encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description="Fase 4c — Caption per FUORI_ATTRIBUTO")
    parser.add_argument("--attributo", choices=ATTRIBUTI, help="Processa solo questo attributo")
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
