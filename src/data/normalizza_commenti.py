# src/data/normalizza_commenti.py
import json
import re
import logging
from pathlib import Path

logger = logging.getLogger(__name__)

# ── Costanti ──────────────────────────────────────────────────────────────────

MODEL_DEFAULT = "gpt-4o-mini"
BATCH_SIZE_DEFAULT = 20
MAX_RETRY_DEFAULT = 3
ALERT_SCARTATI_PCT = 20

ATTRIBUTI = [
    "Texture",
    "Struttura della Pasta",
    "Colore della Pasta",
    "Spessore della Crosta",
    "Profumo",
    "Sapore",
    "Aroma",
]

ATTRIBUTI_DESCRIZIONI = {
    "Texture": (
        "Valuta le caratteristiche tattili della pasta: compattezza, granulosità, "
        "elasticità e presenza di difetti strutturali come stiratura o scioglievolezza anomala."
    ),
    "Struttura della Pasta": (
        "Valuta l'aspetto visivo della sezione: presenza e dimensione degli occhi, "
        "fratture, distribuzione dell'occhiatura e uniformità della pasta."
    ),
    "Colore della Pasta": (
        "Valuta il colore della pasta: tonalità (da paglierino chiaro a giallo intenso), "
        "uniformità, presenza di alone centrale, macchie o aree di colore anomalo."
    ),
    "Spessore della Crosta": (
        "Valuta lo spessore della crosta esterna in relazione alle attese per la "
        "stagionatura del campione: regolare, sottile, spessa, irregolare."
    ),
    "Profumo": (
        "Valuta le note olfattive del formaggio: intensità, tipicità del Grana Trentino, "
        "complessità aromatica e presenza di note anomale o difetti."
    ),
    "Sapore": (
        "Valuta le caratteristiche gustative: intensità, dolcezza, sapidità, piccantezza, "
        "acidità, amaro e persistenza gustativa in bocca."
    ),
    "Aroma": (
        "Valuta le note aromatiche retronasali: intensità, tipicità del Grana Trentino, "
        "complessità e presenza di note anomale o non caratteristiche."
    ),
}

CLASSI_VALIDE = {"OK", "CONFORME", "FUORI_ATTRIBUTO", "RIFERIMENTO", "ILLEGGIBILE"}


# ── Stub definitions ──────────────────────────────────────────────────────

def prenormalizza_commento(commento, vocabolario):
    raise NotImplementedError

def parse_llm_response(response_text, expected_ids):
    raise NotImplementedError

def genera_baseline(attributo, vocabolario, client, model=MODEL_DEFAULT):
    raise NotImplementedError

def normalizza_batch(batch, attributo, vocabolario, baseline, client, model=MODEL_DEFAULT):
    raise NotImplementedError

def genera_report(risultati, attributo, output_path):
    raise NotImplementedError


# ── carica_vocabolario ────────────────────────────────────────────────────

def carica_vocabolario(attributo: str, vocab_dir: Path) -> dict:
    """Carica il vocabolario JSON validato per l'attributo dato.

    Ritorna il dict del vocabolario.
    Lancia FileNotFoundError se il file non esiste.
    """
    nome_file = attributo.replace(" ", "_") + "_vocabolario.json"
    path = Path(vocab_dir) / nome_file
    if not path.exists():
        raise FileNotFoundError(f"Vocabolario non trovato: {path}")
    with open(path, encoding="utf-8") as f:
        return json.load(f)
