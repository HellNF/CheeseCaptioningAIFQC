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


# ── Implementazioni ───────────────────────────────────────────────────────

def prenormalizza_commento(commento: str, vocabolario: dict) -> str:
    """Applica sostituzioni da vocabolario (sinonimi, typo, abbreviazioni,
    conversioni quantitative) al testo grezzo.

    Ritorna il testo pre-normalizzato.
    """
    testo = commento
    for rule in vocabolario.get("sinonimi_diretti", []):
        pattern = re.compile(re.escape(rule["da"]), re.IGNORECASE)
        testo = pattern.sub(rule["a"], testo)
    for conv in vocabolario.get("conversioni_quantitative", []):
        pattern = re.compile(re.escape(conv["da"]), re.IGNORECASE)
        testo = pattern.sub(conv["a"], testo)
    return testo.strip()


# ── Stub rimanenti ────────────────────────────────────────────────────────

def parse_llm_response(response_text: str, expected_ids: list[int]) -> list[dict]:
    """Parsa la risposta LLM in formato jsonlines.

    Ritorna lista di {id, classe, caption} per ogni id atteso.
    Gli id mancanti o con classe invalida ottengono classe ERRORE_PARSING.
    """
    parsed: dict[int, dict] = {}
    for line in response_text.strip().split("\n"):
        line = line.strip()
        if not line:
            continue
        try:
            obj = json.loads(line)
        except json.JSONDecodeError:
            continue
        if "id" not in obj or "classe" not in obj:
            continue
        # Fix 1: Coerce id to int, skip line if coercion fails
        try:
            id_int = int(obj["id"])
        except (ValueError, TypeError):
            continue
        if obj["classe"] not in CLASSI_VALIDE:
            obj["classe"] = "ERRORE_PARSING"
            obj["caption"] = None
        # Fix 2: Project output to only {id, classe, caption} keys
        parsed[id_int] = {"id": id_int, "classe": obj["classe"], "caption": obj.get("caption")}

    output = []
    for id_ in expected_ids:
        if id_ in parsed:
            output.append(parsed[id_])
        else:
            output.append({"id": id_, "classe": "ERRORE_PARSING", "caption": None})
    return output


def genera_baseline(attributo: str, vocabolario: dict, client, model: str = MODEL_DEFAULT) -> str:
    """Genera via LLM la descrizione di un campione conforme alla norma per l'attributo.

    Ritorna la stringa baseline (15-40 parole).
    """
    desc = ATTRIBUTI_DESCRIZIONI.get(attributo, "")
    termini = ", ".join(vocabolario.get("termini_tecnici_invariabili", []))
    forme_canoniche = ", ".join(
        c["forma_canonica"] for c in vocabolario.get("cluster", [])
    )
    prompt = (
        f"Sei un esperto di valutazione sensoriale del Grana Trentino DOP.\n"
        f"Scrivi UNA frase in italiano standard che descriva un campione di formaggio "
        f"con caratteristiche conformi alla norma per l'attributo '{attributo}'.\n"
        f"Definizione attributo: {desc}\n"
        f"Termini tecnici del vocabolario da usare: {termini or forme_canoniche}\n"
        f"Lunghezza: 15-40 parole. Rispondi con la sola frase, senza prefissi o spiegazioni."
    )
    response = client.chat.completions.create(
        model=model,
        messages=[{"role": "user", "content": prompt}],
        max_tokens=120,
        temperature=0.3,
    )
    return response.choices[0].message.content.strip()


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
