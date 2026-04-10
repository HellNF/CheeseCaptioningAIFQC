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


# ── Costanti di formato ────────────────────────────────────────────────────

_USER_MSG_HEADER = (
    "Normalizza i seguenti commenti di panel sensoriale. "
    "Per ciascuno restituisci un oggetto JSON su una riga separata:\n"
    '{"id": N, "classe": "OK|CONFORME|FUORI_ATTRIBUTO|RIFERIMENTO|ILLEGGIBILE", "caption": "..."|null}\n\n'
    "Classi:\n"
    "- OK: commento con contenuto specifico → caption normalizzata in linguaggio naturale\n"
    "- CONFORME: breve/generico che esprime conformità ('ok','buono','nella media') "
    "→ espandi con la descrizione baseline\n"
    "- FUORI_ATTRIBUTO: riguarda un attributo diverso → caption null\n"
    "- RIFERIMENTO: rimanda ad altra scheda ('vedi sopra') → caption null\n"
    "- ILLEGGIBILE: incomprensibile o corrotto → caption null\n\n"
    "Commenti:\n"
)


# ── Implementazioni ───────────────────────────────────────────────────────

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


def _build_system_prompt(attributo: str, vocabolario: dict, baseline: str) -> str:
    """Costruisce il system prompt per la normalizzazione LLM."""
    desc = ATTRIBUTI_DESCRIZIONI.get(attributo, "")
    termini = ", ".join(vocabolario.get("termini_tecnici_invariabili", []))
    cluster_lines = "\n".join(
        f"  - {c['forma_canonica']}: {', '.join(c.get('varianti', []))}"
        for c in vocabolario.get("cluster", [])
    ) or "  (nessuno)"
    sinonimi_lines = "\n".join(
        f"  - '{s['da']}' → '{s['a']}'"
        for s in vocabolario.get("sinonimi_diretti", [])
    ) or "  (nessuno)"

    return (
        "[CONTESTO CASEARIO]\n"
        "Il Grana Trentino è un formaggio DOP a pasta dura stagionato prodotto in Trentino.\n"
        "Le valutazioni provengono da un panel sensoriale esperto che valuta campioni di formaggio.\n"
        "Queste caption saranno usate per addestrare modelli encoder-decoder di image captioning.\n"
        "Il linguaggio deve essere tecnico ma naturale, in italiano standard. "
        "Lunghezza target: 15-60 parole.\n\n"
        f"[ATTRIBUTO CORRENTE]\n"
        f"Attributo: {attributo}\n"
        f"Definizione: {desc}\n"
        f"Descrizione baseline (campione conforme): {baseline}\n\n"
        f"[VOCABOLARIO VALIDATO]\n"
        f"Termini tecnici: {termini or '(vedi cluster)'}\n"
        f"Cluster semantici:\n{cluster_lines}\n"
        f"Normalizzazioni (sinonimi/typo/abbreviazioni):\n{sinonimi_lines}"
    )


def normalizza_batch(
    batch: list[dict],
    attributo: str,
    vocabolario: dict,
    baseline: str,
    client,
    model: str = MODEL_DEFAULT,
) -> list[dict]:
    """Normalizza un batch di commenti pre-normalizzati via LLM.

    batch: lista di {id, commento_prenorm}
    Ritorna lista di {id, classe, caption}.
    """
    if not batch:
        return []
    system_prompt = _build_system_prompt(attributo, vocabolario, baseline)
    commenti_text = "\n".join(
        f'{item["id"]}. "{item["commento_prenorm"]}"' for item in batch
    )
    user_message = _USER_MSG_HEADER + commenti_text

    response = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_message},
        ],
        max_tokens=len(batch) * 80,
        temperature=0.2,
    )
    response_text = response.choices[0].message.content
    expected_ids = [item["id"] for item in batch]
    return parse_llm_response(response_text, expected_ids)


def genera_report(risultati: list[dict], attributo: str, output_path: Path) -> None:
    """Genera report Markdown con statistiche di normalizzazione.

    output_path: percorso completo del file .md da creare.
    """
    import random

    totale = len(risultati)
    conteggi: dict[str, int] = {}
    for r in risultati:
        conteggi[r["classe"]] = conteggi.get(r["classe"], 0) + 1

    caption_prodotte = conteggi.get("OK", 0) + conteggi.get("CONFORME", 0)
    scartati = totale - caption_prodotte
    pct_scartati = (scartati / totale * 100) if totale > 0 else 0

    lines = [
        f"# Report normalizzazione — {attributo}",
        "",
        "## Statistiche",
        "",
        f"- Commenti processati: {totale}",
        f"- Caption prodotte: {caption_prodotte}",
        f"- Scartati: {scartati} ({pct_scartati:.1f}%)",
        "",
        "## Distribuzione classi",
        "",
        "| Classe | Conteggio | % |",
        "|--------|-----------|---|",
    ]
    for classe in ["OK", "CONFORME", "FUORI_ATTRIBUTO", "RIFERIMENTO", "ILLEGGIBILE", "ERRORE_PARSING", "ERRORE"]:
        n = conteggi.get(classe, 0)
        if n > 0:
            lines.append(f"| {classe} | {n} | {n/totale*100:.1f}% |")

    if pct_scartati > ALERT_SCARTATI_PCT:
        lines += [
            "",
            f"> **ATTENZIONE:** percentuale scartati ({pct_scartati:.1f}%) superiore alla soglia ({ALERT_SCARTATI_PCT}%).",
        ]

    campione = [r for r in risultati if r.get("caption")]
    campione = random.sample(campione, min(10, len(campione)))
    lines += ["", "## Esempi before/after (campione casuale)", ""]
    for r in campione:
        lines.append(f"- **Raw:** `{r.get('commento_raw', '')}` → **Caption:** {r['caption']}")

    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text("\n".join(lines), encoding="utf-8")


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
