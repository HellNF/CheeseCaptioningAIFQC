# src/data/10_normalizza_commenti.py
"""Fase 4 — Normalizzazione commenti per attributo.

Uso:
    python src/data/10_normalizza_commenti.py
    python src/data/10_normalizza_commenti.py --attributo Texture
    python src/data/10_normalizza_commenti.py --model gpt-4o --batch-size 10
    python src/data/10_normalizza_commenti.py --dry-run
"""
import argparse
import json
import logging
import sys
import time
from pathlib import Path

# Aggiunge root del progetto al path per import del modulo
sys.path.insert(0, str(Path(__file__).parents[2]))

import openai

from src.data.normalizza_commenti import (
    ATTRIBUTI,
    carica_vocabolario,
    carica_commenti,
    prenormalizza_commento,
    genera_baseline,
    normalizza_batch,
    genera_report,
    MODEL_DEFAULT,
    BATCH_SIZE_DEFAULT,
    MAX_RETRY_DEFAULT,
)

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
logger = logging.getLogger(__name__)

# ── Percorsi ──────────────────────────────────────────────────────────────────

ROOT = Path(__file__).parent.parent.parent
CSV_DIR = ROOT / "07_captioning risultati grana Trentino" / "GT commenti liberi" / "csv dataset"
VOCAB_DIR = ROOT / "data" / "interim" / "vocabolari_validati_per_attributo"
BASELINE_DIR = ROOT / "data" / "interim" / "baseline_descriptions"
CHECKPOINT_DIR = ROOT / "data" / "interim" / "normalizzazione_in_corso"
OUTPUT_DIR = ROOT / "data" / "processed" / "caption_per_attributo"
REPORTS_DIR = ROOT / "reports"


# ── Retry wrapper ─────────────────────────────────────────────────────────────

def _normalizza_con_retry(
    batch: list[dict],
    attributo: str,
    vocabolario: dict,
    baseline: str,
    client,
    model: str,
    max_retry: int,
) -> list[dict]:
    """Chiama normalizza_batch con retry esponenziale. In caso di errore persistente,
    marca i commenti del batch come ERRORE."""
    for tentativo in range(max_retry):
        try:
            return normalizza_batch(batch, attributo, vocabolario, baseline, client, model)
        except Exception as exc:
            attesa = 2 ** tentativo
            logger.warning(f"Errore batch (tentativo {tentativo+1}/{max_retry}): {exc}. Attendo {attesa}s.")
            time.sleep(attesa)
    logger.error(f"Batch fallito dopo {max_retry} tentativi. Marcato come ERRORE.")
    return [{"id": item["id"], "classe": "ERRORE", "caption": None} for item in batch]


# ── Baseline ──────────────────────────────────────────────────────────────────

def _carica_o_genera_baseline(attributo: str, vocabolario: dict, client, model: str) -> str:
    """Carica la baseline da file se esiste, altrimenti la genera via LLM e la salva."""
    BASELINE_DIR.mkdir(parents=True, exist_ok=True)
    path = BASELINE_DIR / f"{attributo.replace(' ', '_')}_baseline.json"
    if path.exists():
        with open(path, encoding="utf-8") as f:
            return json.load(f)["baseline"]
    logger.info(f"[{attributo}] Generazione baseline...")
    baseline = genera_baseline(attributo, vocabolario, client, model)
    with open(path, "w", encoding="utf-8") as f:
        json.dump({"attributo": attributo, "baseline": baseline}, f, ensure_ascii=False, indent=2)
    logger.info(f"[{attributo}] Baseline: {baseline}")
    return baseline


# ── Salvataggio CSV ───────────────────────────────────────────────────────────

def _salva_csv(risultati: list[dict], attributo: str) -> None:
    import pandas as pd
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    path = OUTPUT_DIR / f"{attributo.replace(' ', '_')}_captions.csv"
    df = pd.DataFrame(risultati)
    df.to_csv(path, index=False, encoding="utf-8")
    logger.info(f"[{attributo}] CSV salvato: {path} ({len(df)} righe)")


# ── Pipeline per un attributo ─────────────────────────────────────────────────

def processa_attributo(
    attributo: str,
    client,
    model: str,
    batch_size: int,
    max_retry: int,
    dry_run: bool,
) -> dict:
    """Esegue la pipeline completa per un singolo attributo.

    Ritorna statistiche: {attributo, totale, caption_prodotte, scartati}.
    """
    logger.info(f"=== {attributo} ===")

    vocabolario = carica_vocabolario(attributo, VOCAB_DIR)
    commenti = carica_commenti(attributo, CSV_DIR)
    logger.info(f"[{attributo}] Commenti non vuoti: {len(commenti)}")

    if not commenti:
        logger.warning(f"[{attributo}] Nessun commento trovato. Salto.")
        return {"attributo": attributo, "totale": 0, "caption_prodotte": 0, "scartati": 0}

    # Step 1: pre-normalizzazione programmatica
    for c in commenti:
        c["commento_prenorm"] = prenormalizza_commento(c["commento_raw"], vocabolario)

    if dry_run:
        logger.info(f"[{attributo}] DRY RUN — mostro 3 esempi pre-normalizzazione:")
        for c in commenti[:3]:
            logger.info(f"  Raw: {c['commento_raw']!r} → Pre: {c['commento_prenorm']!r}")
        return {"attributo": attributo, "totale": len(commenti), "caption_prodotte": 0, "scartati": 0}

    # Step 0: baseline
    baseline = _carica_o_genera_baseline(attributo, vocabolario, client, model)

    # Step 2: LLM in batch con checkpoint
    CHECKPOINT_DIR.mkdir(parents=True, exist_ok=True)
    tutti_risultati = []

    for i in range(0, len(commenti), batch_size):
        batch_idx = i // batch_size
        checkpoint_path = CHECKPOINT_DIR / f"{attributo.replace(' ', '_')}_batch_{batch_idx:04d}.json"

        if checkpoint_path.exists():
            with open(checkpoint_path, encoding="utf-8") as f:
                salvati = json.load(f)
            tutti_risultati.extend(salvati)
            logger.debug(f"[{attributo}] Batch {batch_idx} caricato da checkpoint.")
            continue

        batch_commenti = commenti[i : i + batch_size]
        batch_input = [{"id": c["id"], "commento_prenorm": c["commento_prenorm"]} for c in batch_commenti]
        risultati_batch = _normalizza_con_retry(batch_input, attributo, vocabolario, baseline, client, model, max_retry)

        # Arricchisci con metadati raw
        meta_by_id = {c["id"]: c for c in batch_commenti}
        for r in risultati_batch:
            meta = meta_by_id.get(r["id"], {})
            r.update({
                "commento_raw": meta.get("commento_raw", ""),
                "commento_prenorm": meta.get("commento_prenorm", ""),
                "anno": meta.get("anno", ""),
                "prodotto": meta.get("prodotto", ""),
                "panelista": meta.get("panelista", ""),
            })

        with open(checkpoint_path, "w", encoding="utf-8") as f:
            json.dump(risultati_batch, f, ensure_ascii=False)

        tutti_risultati.extend(risultati_batch)
        logger.info(f"[{attributo}] Batch {batch_idx+1}/{(len(commenti)-1)//batch_size+1} completato.")

    # Output
    _salva_csv(tutti_risultati, attributo)
    report_path = REPORTS_DIR / f"normalizzazione_{attributo.replace(' ', '_')}.md"
    genera_report(tutti_risultati, attributo, report_path)

    caption_prodotte = sum(1 for r in tutti_risultati if r["classe"] in ("OK", "CONFORME"))
    scartati = len(tutti_risultati) - caption_prodotte
    logger.info(f"[{attributo}] Caption prodotte: {caption_prodotte} / {len(tutti_risultati)}")

    return {
        "attributo": attributo,
        "totale": len(tutti_risultati),
        "caption_prodotte": caption_prodotte,
        "scartati": scartati,
    }


# ── Main ──────────────────────────────────────────────────────────────────────

def main() -> int:
    parser = argparse.ArgumentParser(description="Fase 4 — Normalizzazione commenti per attributo")
    parser.add_argument("--attributo", choices=ATTRIBUTI, help="Processa solo questo attributo")
    parser.add_argument("--model", default=MODEL_DEFAULT, help=f"Modello LLM (default: {MODEL_DEFAULT})")
    parser.add_argument("--batch-size", type=int, default=BATCH_SIZE_DEFAULT, help="Commenti per batch")
    parser.add_argument("--max-retry", type=int, default=MAX_RETRY_DEFAULT, help="Retry su errore API")
    parser.add_argument("--dry-run", action="store_true", help="Non chiama l'API, mostra solo pre-normalizzazione")
    args = parser.parse_args()

    client = None if args.dry_run else openai.OpenAI()
    attributi_da_processare = [args.attributo] if args.attributo else ATTRIBUTI

    riepilogo = []
    for attributo in attributi_da_processare:
        try:
            stats = processa_attributo(attributo, client, args.model, args.batch_size, args.max_retry, args.dry_run)
            riepilogo.append(stats)
        except Exception as exc:
            logger.error(f"[{attributo}] Errore: {exc}")
            riepilogo.append({"attributo": attributo, "errore": str(exc)})

    print("\n=== RIEPILOGO ===")
    for s in riepilogo:
        if "errore" in s:
            print(f"  {s['attributo']}: ERRORE — {s['errore']}")
        else:
            print(f"  {s['attributo']}: {s['caption_prodotte']}/{s['totale']} caption prodotte")

    errori = [s for s in riepilogo if "errore" in s]
    return 1 if errori else 0


if __name__ == "__main__":
    sys.exit(main())
