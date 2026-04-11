# src/data/11_riprocessa_conforme.py
"""Fase 4b — Riprocessamento righe CONFORME per attributo.

Uso:
    python src/data/11_riprocessa_conforme.py
    python src/data/11_riprocessa_conforme.py --attributo Texture
    python src/data/11_riprocessa_conforme.py --dry-run
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
    carica_vocabolario,
    carica_baseline,
    riprocessa_conforme_batch,
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
CHECKPOINT_DIR = ROOT / "data" / "interim" / "riprocessa_conforme_in_corso"
REPORTS_DIR = ROOT / "reports"


def _conforme_con_retry(batch, attributo, vocabolario, baseline, client, model, max_retry):
    for tentativo in range(max_retry):
        try:
            return riprocessa_conforme_batch(batch, attributo, vocabolario, baseline, client, model)
        except Exception as exc:
            if tentativo < max_retry - 1:
                attesa = 10 * (2 ** tentativo)
                logger.warning(f"Errore (tentativo {tentativo+1}/{max_retry}): {exc}. Attendo {attesa}s.")
                time.sleep(attesa)
            else:
                logger.warning(f"Errore (tentativo {tentativo+1}/{max_retry}): {exc}.")
    logger.error(f"Batch fallito dopo {max_retry} tentativi. Marcato come ERRORE.")
    return [{"id": item["id"], "classe": "ERRORE", "caption": None} for item in batch]


def processa_attributo(attributo, client, model, batch_size, max_retry, dry_run):
    csv_path = OUTPUT_DIR / f"{attributo.replace(' ', '_')}_captions.csv"
    df = pd.read_csv(csv_path)

    conforme_rows = df[df["classe"] == "CONFORME"].copy()
    if len(conforme_rows) == 0:
        logger.info(f"[{attributo}] Nessun CONFORME da riprocessare.")
        return

    logger.info(f"[{attributo}] {len(conforme_rows)} CONFORME da riprocessare.")

    if dry_run:
        for _, row in conforme_rows.head(3).iterrows():
            logger.info(f"  DRY-RUN: [{row['id']}] {row['commento_raw']}")
        return

    vocabolario = carica_vocabolario(attributo, VOCAB_DIR)
    baseline = carica_baseline(attributo, BASELINE_DIR)
    CHECKPOINT_DIR.mkdir(parents=True, exist_ok=True)

    batch_list = conforme_rows[["id", "commento_raw"]].to_dict("records")
    batches = [batch_list[i:i + batch_size] for i in range(0, len(batch_list), batch_size)]

    tutti_risultati = []
    for idx, batch in enumerate(batches):
        ckpt = CHECKPOINT_DIR / f"{attributo.replace(' ', '_')}_batch_{idx:04d}.json"
        if ckpt.exists():
            with open(ckpt, encoding="utf-8") as f:
                tutti_risultati.extend(json.load(f))
            logger.info(f"[{attributo}] Batch {idx+1}/{len(batches)} da checkpoint.")
            continue
        risultati = _conforme_con_retry(batch, attributo, vocabolario, baseline, client, model, max_retry)
        tutti_risultati.extend(risultati)
        with open(ckpt, "w", encoding="utf-8") as f:
            json.dump(risultati, f, ensure_ascii=False)
        logger.info(f"[{attributo}] Batch {idx+1}/{len(batches)} completato.")

    # Aggiorna CSV in-place
    risultati_map = {r["id"]: r for r in tutti_risultati}
    for idx_row in df.index:
        row_id = df.at[idx_row, "id"]
        if row_id in risultati_map:
            df.at[idx_row, "classe"] = risultati_map[row_id]["classe"]
            df.at[idx_row, "caption"] = risultati_map[row_id]["caption"]
    df.to_csv(csv_path, index=False)

    promossi = sum(1 for r in tutti_risultati if r["classe"] == "OK")
    errori = sum(1 for r in tutti_risultati if r["classe"] == "ERRORE")
    rimasti_conforme = len(tutti_risultati) - promossi - errori
    logger.info(f"[{attributo}] Promossi OK: {promossi}, CONFORME con caption variata: {rimasti_conforme}")

    REPORTS_DIR.mkdir(parents=True, exist_ok=True)
    report_path = REPORTS_DIR / f"riprocessa_conforme_{attributo.replace(' ', '_')}.md"
    lines = [
        f"# Report riprocessamento CONFORME — {attributo}",
        "",
        f"- Righe riprocessate: {len(conforme_rows)}",
        f"- Promosse a OK: {promossi}",
        f"- CONFORME con caption variata: {rimasti_conforme}",
        f"- Errori: {errori}",
    ]
    report_path.write_text("\n".join(lines), encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description="Fase 4b — Riprocessamento CONFORME")
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
