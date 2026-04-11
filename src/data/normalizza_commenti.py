# src/data/normalizza_commenti.py
import difflib
import json
import re
import logging
import pandas as pd
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
        if "da" in conv:
            pattern = re.compile(re.escape(conv["da"]), re.IGNORECASE)
            testo = pattern.sub(conv["a"], testo)
        elif "pattern_regex" in conv:
            pattern = re.compile(conv["pattern_regex"], re.IGNORECASE)
            testo = pattern.sub(conv["forma_canonica"], testo)
    return testo.strip()


# ── Costanti di formato ────────────────────────────────────────────────────

_USER_MSG_HEADER = (
    "Normalizza i seguenti commenti di panel sensoriale. "
    "Per ciascuno restituisci un oggetto JSON su una riga separata:\n"
    '{"id": N, "classe": "OK|CONFORME|FUORI_ATTRIBUTO|RIFERIMENTO|ILLEGGIBILE", "caption": "..."|null}\n\n'
    "Classi:\n"
    "- OK: commento che esprime QUALSIASI concetto relativo all'attributo, anche breve "
    "(es. 'Intenso', 'Moderata intensità', 'Friabile', 'Gommoso') → caption normalizzata in linguaggio naturale\n"
    "- CONFORME: SOLO espressioni di generica conformità senza informazioni specifiche "
    "('ok','buono','nella media','conforme','nella norma','regolare','normale') "
    "→ espandi con la descrizione baseline\n"
    "- FUORI_ATTRIBUTO: riguarda un attributo diverso → caption in linguaggio naturale "
    "che descrive il commento (non vincolarsi all'attributo corrente)\n"
    "- RIFERIMENTO: rimanda ad altra scheda ('vedi sopra') → caption null\n"
    "- ILLEGGIBILE: incomprensibile o corrotto → caption null\n\n"
    "Commenti:\n"
)

_CONFORME_REPROCESS_HEADER = (
    "Riprocessa i seguenti commenti già classificati come CONFORME.\n"
    "Per ciascuno decidi:\n"
    "- Se contiene un descrittore specifico (colore, intensità, nota sensoriale, "
    "misura, aggettivo tecnico) → classe \"OK\" con caption specifica in italiano "
    "naturale (15-60 parole)\n"
    "- Se è puramente generico senza informazione specifica (\"ok\", \"bello\", "
    "\"positivo\", \"buono\", \"nella media\", \"ottimo\", \"conforme\") → "
    "classe \"CONFORME\" con caption che descriva campione conforme alla norma, "
    "DIVERSA dalla baseline standard (varia la formulazione)\n\n"
    "Formato risposta — una riga JSON per commento:\n"
    "{\"id\": N, \"classe\": \"OK\"|\"CONFORME\", \"caption\": \"...\"}\n\n"
    "Commenti:\n"
)

_FUORI_ATTRIBUTO_SYSTEM = (
    "Sei un assistente che normalizza commenti di panel sensoriale di formaggio.\n"
    "Trasforma il commento grezzo in una frase in italiano standard, chiara e naturale.\n"
    "Non aggiungere informazioni non presenti nel commento originale.\n"
    "Lunghezza: 10-40 parole."
)

_FUORI_ATTRIBUTO_HEADER = (
    "Normalizza i seguenti commenti in linguaggio naturale.\n"
    "Per ciascuno restituisci una riga JSON:\n"
    "{\"id\": N, \"caption\": \"...\"}\n\n"
    "Commenti:\n"
)

_FAITHFUL_MSG_HEADER = (
    "Normalizza i seguenti commenti di panel sensoriale. "
    "Per ciascuno restituisci un oggetto JSON su una riga separata:\n"
    '{"id": N, "classe": "OK|CONFORME|FUORI_ATTRIBUTO|RIFERIMENTO|ILLEGGIBILE", "caption": "..."|null}\n\n'
    "Classi:\n"
    "- OK: commento che esprime QUALSIASI concetto relativo all'attributo → caption normalizzata\n"
    "- CONFORME: SOLO espressioni di generica conformità ('ok','buono','nella media') "
    "→ espandi con la descrizione baseline\n"
    "- FUORI_ATTRIBUTO: riguarda un attributo diverso → caption in linguaggio naturale\n"
    "- RIFERIMENTO: rimanda ad altra scheda → caption null\n"
    "- ILLEGGIBILE: incomprensibile → caption null\n\n"
    "⚠️ REGOLA DI FEDELTÀ — obbligatoria:\n"
    "La caption DEVE rispecchiare fedelmente il commento originale, anche se descrive:\n"
    "- difetti (es. 'troppo salato', 'amaro eccessivo', 'bruciato')\n"
    "- note negative o atipiche\n"
    "- caratteristiche fuori standard\n"
    "NON usare la formulazione standard del campione conforme.\n"
    "NON edulcorare, NON trasformare difetti in pregi.\n\n"
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


def parse_fuori_attributo_response(response_text: str, expected_ids: list[int]) -> list[dict]:
    """Parsa la risposta LLM per riprocessamento FUORI_ATTRIBUTO.

    Ritorna lista di {id, caption} per ogni id atteso.
    Gli id mancanti ottengono caption None.
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
        if "id" not in obj:
            continue
        try:
            id_int = int(obj["id"])
        except (ValueError, TypeError):
            continue
        parsed[id_int] = {"id": id_int, "caption": obj.get("caption")}

    output = []
    for id_ in expected_ids:
        if id_ in parsed:
            output.append(parsed[id_])
        else:
            output.append({"id": id_, "caption": None})
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


def trova_hallucinate(
    df: pd.DataFrame,
    baseline: str,
    min_count: int = 5,
    sim_threshold: float = 0.45,
) -> pd.DataFrame:
    """Individua righe OK con caption probabilmente hallucinate (baseline ripetuta).

    Criteri: caption appare >= min_count volte tra le righe OK
    E (similarità con baseline >= sim_threshold OPPURE count >= 15).

    Ritorna sottoinsieme del DataFrame con le righe sospette.
    """
    ok_rows = df[df["classe"] == "OK"].copy()
    if ok_rows.empty:
        return ok_rows.iloc[0:0]

    counts = ok_rows["caption"].value_counts()
    baseline_lower = baseline.lower()

    sospette: set[str] = set()
    for caption, count in counts.items():
        if count < min_count or not isinstance(caption, str):
            continue
        sim = difflib.SequenceMatcher(None, caption.lower(), baseline_lower).ratio()
        if sim >= sim_threshold or count >= 15:
            sospette.add(caption)

    return ok_rows[ok_rows["caption"].isin(sospette)]


def normalizza_faithful_batch(
    batch: list[dict],
    attributo: str,
    vocabolario: dict,
    baseline: str,
    client,
    model: str = MODEL_DEFAULT,
) -> list[dict]:
    """Ri-normalizza un batch usando un prompt con regola di fedeltà esplicita.

    Identico a normalizza_batch ma usa _FAITHFUL_MSG_HEADER che vieta
    esplicitamente di edulcorare commenti negativi o usare la formulazione baseline.

    batch: lista di {id, commento_prenorm}
    Ritorna lista di {id, classe, caption}.
    """
    if not batch:
        return []
    system_prompt = _build_system_prompt(attributo, vocabolario, baseline)
    commenti_text = "\n".join(
        f'{item["id"]}. "{item["commento_prenorm"]}"' for item in batch
    )
    user_message = _FAITHFUL_MSG_HEADER + commenti_text

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


def riprocessa_conforme_batch(
    batch: list[dict],
    attributo: str,
    vocabolario: dict,
    baseline: str,
    client,
    model: str = MODEL_DEFAULT,
) -> list[dict]:
    """Riprocessa un batch di righe CONFORME via LLM.

    Distingue tra commenti con contenuto specifico (→ classe OK, caption specifica)
    e commenti puramente generici (→ classe CONFORME, caption variata dalla baseline).

    batch: lista di {id, commento_raw}
    Ritorna lista di {id, classe, caption}.
    """
    if not batch:
        return []
    system_prompt = _build_system_prompt(attributo, vocabolario, baseline)
    commenti_text = "\n".join(
        f'{item["id"]}. "{item["commento_raw"]}"' for item in batch
    )
    user_message = _CONFORME_REPROCESS_HEADER + commenti_text

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


def riprocessa_fuori_attributo_batch(
    batch: list[dict],
    client,
    model: str = MODEL_DEFAULT,
) -> list[dict]:
    """Genera caption in linguaggio naturale per un batch di righe FUORI_ATTRIBUTO.

    Non vincola la caption all'attributo di provenienza.
    batch: lista di {id, commento_raw}
    Ritorna lista di {id, caption}.
    """
    if not batch:
        return []
    commenti_text = "\n".join(
        f'{item["id"]}. "{item["commento_raw"]}"' for item in batch
    )
    user_message = _FUORI_ATTRIBUTO_HEADER + commenti_text

    response = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": _FUORI_ATTRIBUTO_SYSTEM},
            {"role": "user", "content": user_message},
        ],
        max_tokens=len(batch) * 60,
        temperature=0.2,
    )
    response_text = response.choices[0].message.content
    expected_ids = [item["id"] for item in batch]
    return parse_fuori_attributo_response(response_text, expected_ids)


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


def carica_baseline(attributo: str, baseline_dir: Path) -> str:
    """Carica la baseline pre-generata per l'attributo.

    Ritorna la stringa baseline.
    Lancia FileNotFoundError se il file non esiste.
    """
    path = Path(baseline_dir) / f"{attributo.replace(' ', '_')}_baseline.json"
    if not path.exists():
        raise FileNotFoundError(f"Baseline non trovata: {path}")
    with open(path, encoding="utf-8") as f:
        return json.load(f)["baseline"]


def carica_commenti(attributo: str, csv_dir: Path) -> list[dict]:
    """Carica e unisce tutti i CSV raw per l'attributo. Filtra righe vuote.

    Ritorna lista di {id, anno, prodotto, panelista, commento_raw}.
    """
    csv_dir = Path(csv_dir)
    pattern_match = attributo.lower().replace(" ", "").replace("_", "")

    file_trovati = [
        f for f in csv_dir.glob("*.csv")
        if pattern_match in f.stem.lower().replace(" ", "").replace("_", "")
    ]
    if not file_trovati:
        return []

    righe = []
    id_counter = 1
    for csv_path in sorted(file_trovati):
        anno_match = re.search(r"(20\d{2})", csv_path.stem)
        anno = anno_match.group(1) if anno_match else "unknown"
        try:
            df = pd.read_csv(csv_path, encoding="utf-8", on_bad_lines="skip")
        except UnicodeDecodeError:
            df = pd.read_csv(csv_path, encoding="latin-1", on_bad_lines="skip")

        if "Commenti" not in df.columns:
            continue
        df = df.dropna(subset=["Commenti"])
        df = df[df["Commenti"].astype(str).str.strip() != ""]

        col_prodotto = "Prodotto" if "Prodotto" in df.columns else ("Prod" if "Prod" in df.columns else None)
        col_panelista = "Panelista" if "Panelista" in df.columns else ("Sogg" if "Sogg" in df.columns else None)

        for _, row in df.iterrows():
            righe.append({
                "id": id_counter,
                "anno": anno,
                "prodotto": str(row[col_prodotto]) if col_prodotto else "",
                "panelista": str(row[col_panelista]) if col_panelista else "",
                "commento_raw": str(row["Commenti"]).strip(),
            })
            id_counter += 1

    return righe
