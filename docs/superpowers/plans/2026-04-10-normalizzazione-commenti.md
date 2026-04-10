# Normalizzazione Commenti per Attributo — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Trasformare i ~10.005 commenti raw del panel sensoriale in caption in linguaggio naturale italiano, raggruppate per attributo, pronte per il training di modelli encoder-decoder di image captioning.

**Architecture:** Approccio ibrido in due step: (1) pre-normalizzazione programmatica via vocabolari JSON validati, (2) riscrittura LLM (GPT-4o-mini) in batch da 20 con checkpoint incrementale. Step 0 genera una `descrizione_baseline` per attributo usata per espandere commenti di conformità generica ("ok", "buono").

**Tech Stack:** Python 3.10+, OpenAI Python SDK (`openai>=1.0.0`), pandas, pytest, pathlib, json, re

---

## File Map

| File | Azione | Responsabilità |
|------|--------|----------------|
| `src/data/normalizza_commenti.py` | Create | Modulo core: costanti, caricamento vocabolari, pre-normalizzazione, parsing LLM, generazione report |
| `src/data/10_normalizza_commenti.py` | Create | Pipeline script: argparse, loop su attributi, batch+retry, checkpoint, CSV output |
| `tests/test_normalizza_commenti.py` | Create | Test unit e integration per il modulo core |
| `tests/fixtures/Texture_commenti_fixture.csv` | Create | CSV fixture minimale (5 righe, schema 2019) |
| `tests/fixtures/Texture_llm_response_fixture.txt` | Create | Risposta LLM simulata (jsonlines) |
| `requirements.txt` | Modify | Aggiunge `openai>=1.0.0` |

---

## Task 1: Aggiungere dipendenza openai

**Files:**
- Modify: `requirements.txt`

- [ ] **Step 1: Aggiungi openai a requirements.txt**

Apri `requirements.txt` e aggiungi dopo `openpyxl`:

```
openai>=1.0.0
```

- [ ] **Step 2: Installa la dipendenza**

```bash
pip install openai>=1.0.0
```

Output atteso: `Successfully installed openai-...`

- [ ] **Step 3: Commit**

```bash
git add requirements.txt
git commit -m "chore: add openai dependency for comment normalization"
```

---

## Task 2: Modulo core — skeleton, ATTRIBUTI_DESCRIZIONI, carica_vocabolario()

**Files:**
- Create: `src/data/normalizza_commenti.py`
- Create: `tests/test_normalizza_commenti.py`

- [ ] **Step 1: Crea il file di test vuoto**

```python
# tests/test_normalizza_commenti.py
import json
import pytest
from pathlib import Path
from unittest.mock import MagicMock

from src.data.normalizza_commenti import (
    ATTRIBUTI,
    ATTRIBUTI_DESCRIZIONI,
    carica_vocabolario,
    prenormalizza_commento,
    parse_llm_response,
    genera_baseline,
    normalizza_batch,
    genera_report,
)

FIXTURES = Path("tests/fixtures")
VOCAB_DIR = Path("data/interim/vocabolari_validati_per_attributo")
```

- [ ] **Step 2: Scrivi il test per ATTRIBUTI_DESCRIZIONI**

Aggiungi a `tests/test_normalizza_commenti.py`:

```python
# ── ATTRIBUTI_DESCRIZIONI ──────────────────────────────────────────────────

def test_attributi_descrizioni_ha_tutti_e_sette():
    assert len(ATTRIBUTI) == 7
    for a in ATTRIBUTI:
        assert a in ATTRIBUTI_DESCRIZIONI, f"Descrizione mancante per: {a}"
        assert len(ATTRIBUTI_DESCRIZIONI[a]) > 20, f"Descrizione troppo corta per: {a}"
```

- [ ] **Step 3: Esegui il test per verificare che fallisca**

```bash
pytest tests/test_normalizza_commenti.py::test_attributi_descrizioni_ha_tutti_e_sette -v
```

Atteso: `FAILED` — `ModuleNotFoundError` o `ImportError`

- [ ] **Step 4: Crea il modulo con lo skeleton**

```python
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
```

- [ ] **Step 5: Esegui il test per verificare che passi**

```bash
pytest tests/test_normalizza_commenti.py::test_attributi_descrizioni_ha_tutti_e_sette -v
```

Atteso: `PASSED`

- [ ] **Step 6: Scrivi il test per carica_vocabolario()**

Aggiungi a `tests/test_normalizza_commenti.py`:

```python
# ── carica_vocabolario ─────────────────────────────────────────────────────

def test_carica_vocabolario_texture():
    vocab = carica_vocabolario("Texture", VOCAB_DIR)
    assert vocab["attributo"] == "Texture"
    assert "sinonimi_diretti" in vocab
    assert "cluster" in vocab
    assert isinstance(vocab["sinonimi_diretti"], list)

def test_carica_vocabolario_nome_con_spazi():
    vocab = carica_vocabolario("Struttura della Pasta", VOCAB_DIR)
    assert vocab["attributo"] == "Struttura della Pasta"

def test_carica_vocabolario_file_mancante(tmp_path):
    with pytest.raises(FileNotFoundError):
        carica_vocabolario("Attributo_Inesistente", tmp_path)
```

- [ ] **Step 7: Implementa carica_vocabolario()**

Aggiungi a `src/data/normalizza_commenti.py`:

```python
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
```

- [ ] **Step 8: Esegui i test**

```bash
pytest tests/test_normalizza_commenti.py::test_carica_vocabolario_texture \
       tests/test_normalizza_commenti.py::test_carica_vocabolario_nome_con_spazi \
       tests/test_normalizza_commenti.py::test_carica_vocabolario_file_mancante -v
```

Atteso: tutti `PASSED`

- [ ] **Step 9: Commit**

```bash
git add src/data/normalizza_commenti.py tests/test_normalizza_commenti.py
git commit -m "feat: add normalizza_commenti module skeleton with ATTRIBUTI_DESCRIZIONI and carica_vocabolario"
```

---

## Task 3: prenormalizza_commento() — Step 1 programmatico

**Files:**
- Modify: `src/data/normalizza_commenti.py`
- Modify: `tests/test_normalizza_commenti.py`

- [ ] **Step 1: Scrivi i test per prenormalizza_commento()**

Aggiungi a `tests/test_normalizza_commenti.py`:

```python
# ── prenormalizza_commento ─────────────────────────────────────────────────

VOCAB_FIXTURE = {
    "attributo": "Texture",
    "sinonimi_diretti": [
        {"da": "gran.", "a": "grana", "tipo": "abbreviazione"},
        {"da": "compata", "a": "compatta", "tipo": "typo"},
        {"da": "elasticita", "a": "elasticità", "tipo": "typo"},
    ],
    "conversioni_quantitative": [
        {"da": "7/10", "a": "nella norma"},
        {"da": "9/10", "a": "elevata"},
    ],
    "cluster": [],
    "termini_tecnici_invariabili": [],
}

def test_prenorm_applica_sinonimo_abbreviazione():
    risultato = prenormalizza_commento("pasta con gran. tipica", VOCAB_FIXTURE)
    assert "grana" in risultato
    assert "gran." not in risultato

def test_prenorm_corregge_typo():
    risultato = prenormalizza_commento("pasta compata e omogenea", VOCAB_FIXTURE)
    assert "compatta" in risultato
    assert "compata" not in risultato

def test_prenorm_case_insensitive():
    risultato = prenormalizza_commento("COMPATA fine", VOCAB_FIXTURE)
    assert "compatta" in risultato.lower()

def test_prenorm_applica_conversione_quantitativa():
    risultato = prenormalizza_commento("elasticita 7/10", VOCAB_FIXTURE)
    assert "nella norma" in risultato
    assert "7/10" not in risultato

def test_prenorm_commento_vuoto():
    assert prenormalizza_commento("", VOCAB_FIXTURE) == ""

def test_prenorm_nessuna_regola_applicabile():
    assert prenormalizza_commento("buona pasta", VOCAB_FIXTURE) == "buona pasta"
```

- [ ] **Step 2: Esegui i test per verificare che falliscano**

```bash
pytest tests/test_normalizza_commenti.py -k "prenorm" -v
```

Atteso: tutti `FAILED` — `ImportError: cannot import name 'prenormalizza_commento'`

- [ ] **Step 3: Implementa prenormalizza_commento()**

Aggiungi a `src/data/normalizza_commenti.py`:

```python
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
```

- [ ] **Step 4: Esegui i test**

```bash
pytest tests/test_normalizza_commenti.py -k "prenorm" -v
```

Atteso: tutti `PASSED`

- [ ] **Step 5: Commit**

```bash
git add src/data/normalizza_commenti.py tests/test_normalizza_commenti.py
git commit -m "feat: add prenormalizza_commento with synonym and quantitative rules"
```

---

## Task 4: parse_llm_response() — parsing jsonlines

**Files:**
- Modify: `src/data/normalizza_commenti.py`
- Modify: `tests/test_normalizza_commenti.py`
- Create: `tests/fixtures/Texture_llm_response_fixture.txt`

- [ ] **Step 1: Crea la fixture della risposta LLM**

Crea `tests/fixtures/Texture_llm_response_fixture.txt`:

```
{"id": 1, "classe": "OK", "caption": "La texture risulta compatta con grana regolare."}
{"id": 2, "classe": "CONFORME", "caption": "La texture è nella norma, tipica del Grana Trentino."}
{"id": 3, "classe": "RIFERIMENTO", "caption": null}
{"id": 4, "classe": "FUORI_ATTRIBUTO", "caption": null}
{"id": 5, "classe": "ILLEGGIBILE", "caption": null}
```

- [ ] **Step 2: Scrivi i test per parse_llm_response()**

Aggiungi a `tests/test_normalizza_commenti.py`:

```python
# ── parse_llm_response ─────────────────────────────────────────────────────

def test_parse_risposta_completa():
    response_text = (FIXTURES / "Texture_llm_response_fixture.txt").read_text(encoding="utf-8")
    risultati = parse_llm_response(response_text, expected_ids=[1, 2, 3, 4, 5])
    assert len(risultati) == 5
    assert risultati[0] == {"id": 1, "classe": "OK", "caption": "La texture risulta compatta con grana regolare."}
    assert risultati[2] == {"id": 3, "classe": "RIFERIMENTO", "caption": None}

def test_parse_classe_invalida_diventa_errore():
    response_text = '{"id": 1, "classe": "INVENTATA", "caption": "testo"}'
    risultati = parse_llm_response(response_text, expected_ids=[1])
    assert risultati[0]["classe"] == "ERRORE_PARSING"

def test_parse_id_mancante_viene_aggiunto():
    response_text = '{"id": 1, "classe": "OK", "caption": "testo"}'
    risultati = parse_llm_response(response_text, expected_ids=[1, 2])
    assert len(risultati) == 2
    assert risultati[1] == {"id": 2, "classe": "ERRORE_PARSING", "caption": None}

def test_parse_json_malformato_viene_saltato():
    response_text = 'non è json\n{"id": 1, "classe": "OK", "caption": "testo"}'
    risultati = parse_llm_response(response_text, expected_ids=[1])
    assert risultati[0]["classe"] == "OK"

def test_parse_risposta_vuota():
    risultati = parse_llm_response("", expected_ids=[1, 2])
    assert all(r["classe"] == "ERRORE_PARSING" for r in risultati)
```

- [ ] **Step 3: Esegui i test per verificare che falliscano**

```bash
pytest tests/test_normalizza_commenti.py -k "parse" -v
```

Atteso: tutti `FAILED`

- [ ] **Step 4: Implementa parse_llm_response()**

Aggiungi a `src/data/normalizza_commenti.py`:

```python
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
        if obj["classe"] not in CLASSI_VALIDE:
            obj["classe"] = "ERRORE_PARSING"
            obj["caption"] = None
        parsed[obj["id"]] = obj

    output = []
    for id_ in expected_ids:
        if id_ in parsed:
            output.append(parsed[id_])
        else:
            output.append({"id": id_, "classe": "ERRORE_PARSING", "caption": None})
    return output
```

- [ ] **Step 5: Esegui i test**

```bash
pytest tests/test_normalizza_commenti.py -k "parse" -v
```

Atteso: tutti `PASSED`

- [ ] **Step 6: Commit**

```bash
git add src/data/normalizza_commenti.py tests/test_normalizza_commenti.py \
        tests/fixtures/Texture_llm_response_fixture.txt
git commit -m "feat: add parse_llm_response with jsonlines parsing and error handling"
```

---

## Task 5: genera_baseline() — Step 0 (con mock)

**Files:**
- Modify: `src/data/normalizza_commenti.py`
- Modify: `tests/test_normalizza_commenti.py`

- [ ] **Step 1: Scrivi i test per genera_baseline()**

Aggiungi a `tests/test_normalizza_commenti.py`:

```python
# ── genera_baseline ────────────────────────────────────────────────────────

def _mock_client(content: str):
    """Helper: crea un client OpenAI mock che ritorna content."""
    client = MagicMock()
    client.chat.completions.create.return_value = MagicMock(
        choices=[MagicMock(message=MagicMock(content=content))]
    )
    return client

def test_genera_baseline_ritorna_stringa():
    client = _mock_client("La texture risulta nella norma, compatta e omogenea.")
    baseline = genera_baseline("Texture", VOCAB_FIXTURE, client)
    assert isinstance(baseline, str)
    assert len(baseline) > 10

def test_genera_baseline_chiama_api_una_volta():
    client = _mock_client("Testo baseline.")
    genera_baseline("Texture", VOCAB_FIXTURE, client)
    client.chat.completions.create.assert_called_once()

def test_genera_baseline_passa_attributo_nel_prompt():
    client = _mock_client("Baseline.")
    genera_baseline("Texture", VOCAB_FIXTURE, client)
    call_kwargs = client.chat.completions.create.call_args
    messages = call_kwargs[1]["messages"] if "messages" in call_kwargs[1] else call_kwargs[0][0]
    prompt_text = str(messages)
    assert "Texture" in prompt_text
```

- [ ] **Step 2: Esegui i test per verificare che falliscano**

```bash
pytest tests/test_normalizza_commenti.py -k "baseline" -v
```

Atteso: tutti `FAILED`

- [ ] **Step 3: Implementa genera_baseline()**

Aggiungi a `src/data/normalizza_commenti.py`:

```python
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
```

- [ ] **Step 4: Esegui i test**

```bash
pytest tests/test_normalizza_commenti.py -k "baseline" -v
```

Atteso: tutti `PASSED`

- [ ] **Step 5: Commit**

```bash
git add src/data/normalizza_commenti.py tests/test_normalizza_commenti.py
git commit -m "feat: add genera_baseline with LLM call and vocabulary context"
```

---

## Task 6: normalizza_batch() — Step 2 LLM singolo batch (con mock)

**Files:**
- Modify: `src/data/normalizza_commenti.py`
- Modify: `tests/test_normalizza_commenti.py`

- [ ] **Step 1: Scrivi i test per normalizza_batch()**

Aggiungi a `tests/test_normalizza_commenti.py`:

```python
# ── normalizza_batch ───────────────────────────────────────────────────────

BATCH_FIXTURE = [
    {"id": 1, "commento_prenorm": "pasta compatta con grana regolare"},
    {"id": 2, "commento_prenorm": "ok"},
    {"id": 3, "commento_prenorm": "vedi sopra"},
]

LLM_BATCH_RESPONSE = (
    '{"id": 1, "classe": "OK", "caption": "La texture è compatta con grana regolare."}\n'
    '{"id": 2, "classe": "CONFORME", "caption": "La texture risulta nella norma."}\n'
    '{"id": 3, "classe": "RIFERIMENTO", "caption": null}\n'
)

def test_normalizza_batch_ritorna_risultati_per_tutti():
    client = _mock_client(LLM_BATCH_RESPONSE)
    risultati = normalizza_batch(
        BATCH_FIXTURE, "Texture", VOCAB_FIXTURE, "Baseline testo.", client
    )
    assert len(risultati) == 3

def test_normalizza_batch_chiama_api_una_volta():
    client = _mock_client(LLM_BATCH_RESPONSE)
    normalizza_batch(BATCH_FIXTURE, "Texture", VOCAB_FIXTURE, "Baseline.", client)
    client.chat.completions.create.assert_called_once()

def test_normalizza_batch_include_vocabolario_nel_prompt():
    client = _mock_client(LLM_BATCH_RESPONSE)
    normalizza_batch(BATCH_FIXTURE, "Texture", VOCAB_FIXTURE, "Baseline.", client)
    call_kwargs = client.chat.completions.create.call_args
    messages = call_kwargs[1].get("messages", call_kwargs[0][0] if call_kwargs[0] else [])
    system_content = str(messages)
    assert "Texture" in system_content
    assert "Baseline." in system_content

def test_normalizza_batch_classi_corrette():
    client = _mock_client(LLM_BATCH_RESPONSE)
    risultati = normalizza_batch(
        BATCH_FIXTURE, "Texture", VOCAB_FIXTURE, "Baseline.", client
    )
    classi = {r["id"]: r["classe"] for r in risultati}
    assert classi[1] == "OK"
    assert classi[2] == "CONFORME"
    assert classi[3] == "RIFERIMENTO"
```

- [ ] **Step 2: Esegui i test per verificare che falliscano**

```bash
pytest tests/test_normalizza_commenti.py -k "normalizza_batch" -v
```

Atteso: tutti `FAILED`

- [ ] **Step 3: Implementa la funzione helper _build_system_prompt() e normalizza_batch()**

Aggiungi a `src/data/normalizza_commenti.py`:

```python
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
```

- [ ] **Step 4: Esegui i test**

```bash
pytest tests/test_normalizza_commenti.py -k "normalizza_batch" -v
```

Atteso: tutti `PASSED`

- [ ] **Step 5: Commit**

```bash
git add src/data/normalizza_commenti.py tests/test_normalizza_commenti.py
git commit -m "feat: add normalizza_batch with system prompt and LLM call"
```

---

## Task 7: genera_report()

**Files:**
- Modify: `src/data/normalizza_commenti.py`
- Modify: `tests/test_normalizza_commenti.py`

- [ ] **Step 1: Scrivi il test per genera_report()**

Aggiungi a `tests/test_normalizza_commenti.py`:

```python
# ── genera_report ──────────────────────────────────────────────────────────

RISULTATI_FIXTURE = [
    {"id": 1, "classe": "OK",            "caption": "Caption A.", "commento_raw": "pasta compatta"},
    {"id": 2, "classe": "CONFORME",      "caption": "Caption B.", "commento_raw": "ok"},
    {"id": 3, "classe": "RIFERIMENTO",   "caption": None,         "commento_raw": "vedi sopra"},
    {"id": 4, "classe": "OK",            "caption": "Caption C.", "commento_raw": "grana fine"},
    {"id": 5, "classe": "FUORI_ATTRIBUTO","caption": None,        "commento_raw": "crosta spessa"},
]

def test_genera_report_crea_file(tmp_path):
    genera_report(RISULTATI_FIXTURE, "Texture", tmp_path / "report.md")
    assert (tmp_path / "report.md").exists()

def test_genera_report_contiene_statistiche(tmp_path):
    genera_report(RISULTATI_FIXTURE, "Texture", tmp_path / "report.md")
    content = (tmp_path / "report.md").read_text(encoding="utf-8")
    assert "Texture" in content
    assert "OK" in content
    assert "CONFORME" in content
    assert "3" in content   # 3 caption prodotte (OK + CONFORME)

def test_genera_report_alert_se_scartati_elevati(tmp_path):
    molti_scartati = [
        {"id": i, "classe": "ILLEGGIBILE", "caption": None, "commento_raw": f"x{i}"}
        for i in range(9)
    ] + [{"id": 10, "classe": "OK", "caption": "Caption.", "commento_raw": "testo"}]
    genera_report(molti_scartati, "Aroma", tmp_path / "report.md")
    content = (tmp_path / "report.md").read_text(encoding="utf-8")
    assert "ATTENZIONE" in content or "attenzione" in content.lower()
```

- [ ] **Step 2: Esegui i test per verificare che falliscano**

```bash
pytest tests/test_normalizza_commenti.py -k "report" -v
```

Atteso: tutti `FAILED`

- [ ] **Step 3: Implementa genera_report()**

Aggiungi a `src/data/normalizza_commenti.py`:

```python
def genera_report(risultati: list[dict], attributo: str, output_path: Path) -> None:
    """Genera report Markdown con statistiche di normalizzazione.

    output_path: percorso completo del file .md da creare.
    """
    import random

    totale = len(risultati)
    conteggi = {}
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
```

- [ ] **Step 4: Esegui i test**

```bash
pytest tests/test_normalizza_commenti.py -k "report" -v
```

Atteso: tutti `PASSED`

- [ ] **Step 5: Esegui tutti i test del modulo**

```bash
pytest tests/test_normalizza_commenti.py -v
```

Atteso: tutti `PASSED`

- [ ] **Step 6: Commit**

```bash
git add src/data/normalizza_commenti.py tests/test_normalizza_commenti.py
git commit -m "feat: add genera_report with class distribution and before/after examples"
```

---

## Task 8: Fixture CSV e carica_commenti()

**Files:**
- Modify: `src/data/normalizza_commenti.py`
- Modify: `tests/test_normalizza_commenti.py`
- Create: `tests/fixtures/Texture_commenti_fixture.csv`

- [ ] **Step 1: Crea la fixture CSV**

Crea `tests/fixtures/Texture_commenti_fixture.csv` con contenuto:

```
Data Seduta di valutazione,N° Seduta,Bimestre di Valutazione,Data Produzione,Panelista,Prodotto,Commenti
2019-09-04,1,I,2017-12-01,Q_02,C0A,pasta compatta con gran. regolare
2019-09-04,1,I,2017-12-01,Q_09,C0B,ok
2019-09-04,1,I,2017-12-01,TG_20,C0C,vedi sopra
2019-09-04,1,I,2017-12-01,Q_05,C0D,
2019-09-04,1,I,2017-12-01,TG_26,C0E,elastica e granulosa con lieve scioglievolezza
```

- [ ] **Step 2: Scrivi il test per carica_commenti()**

Aggiungi a `tests/test_normalizza_commenti.py`:

```python
# ── carica_commenti ────────────────────────────────────────────────────────

from src.data.normalizza_commenti import carica_commenti

def test_carica_commenti_filtra_vuoti(tmp_path):
    import shutil
    shutil.copy(FIXTURES / "Texture_commenti_fixture.csv",
                tmp_path / "Commenti_2019_Texture.csv")
    commenti = carica_commenti("Texture", tmp_path)
    assert len(commenti) == 4  # 5 righe dati - 1 vuota = 4 non vuote (incluso "vedi sopra")
    testi = [c["commento_raw"] for c in commenti]
    assert "" not in testi

def test_carica_commenti_include_metadati(tmp_path):
    import shutil
    shutil.copy(FIXTURES / "Texture_commenti_fixture.csv",
                tmp_path / "Commenti_2019_Texture.csv")
    commenti = carica_commenti("Texture", tmp_path)
    primo = commenti[0]
    assert "commento_raw" in primo
    assert "prodotto" in primo
    assert "anno" in primo

def test_carica_commenti_nessun_file(tmp_path):
    commenti = carica_commenti("Texture", tmp_path)
    assert commenti == []
```

- [ ] **Step 3: Esegui i test per verificare che falliscano**

```bash
pytest tests/test_normalizza_commenti.py -k "carica_commenti" -v
```

Atteso: tutti `FAILED`

- [ ] **Step 4: Aggiungi import pandas e implementa carica_commenti()**

Aggiungi `import pandas as pd` in cima a `src/data/normalizza_commenti.py` (dopo gli import esistenti), poi aggiungi la funzione:

```python
def carica_commenti(attributo: str, csv_dir: Path) -> list[dict]:
    """Carica e unisce tutti i CSV raw per l'attributo. Filtra righe vuote.

    Ritorna lista di {id, anno, prodotto, panelista, commento_raw}.
    """
    csv_dir = Path(csv_dir)
    attributo_tag = attributo.replace(" ", "_")
    pattern_match = attributo.lower().replace(" ", "")

    file_trovati = [
        f for f in csv_dir.glob("*.csv")
        if pattern_match in f.stem.lower().replace(" ", "").replace("_", "")
    ]
    if not file_trovati:
        return []

    righe = []
    id_counter = 1
    for csv_path in sorted(file_trovati):
        # Estrai anno dal nome file (cerca 4 cifre consecutive)
        anno_match = re.search(r"(20\d{2})", csv_path.stem)
        anno = anno_match.group(1) if anno_match else "unknown"
        try:
            df = pd.read_csv(csv_path, encoding="utf-8", on_bad_lines="skip")
        except Exception:
            df = pd.read_csv(csv_path, encoding="latin-1", on_bad_lines="skip")

        # Colonna commenti: sempre l'ultima colonna "Commenti"
        if "Commenti" not in df.columns:
            continue
        df = df.dropna(subset=["Commenti"])
        df = df[df["Commenti"].astype(str).str.strip() != ""]

        # Colonna prodotto: "Prodotto" (2019-2021) o "Prod" (2018)
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
```

- [ ] **Step 5: Esegui i test**

```bash
pytest tests/test_normalizza_commenti.py -k "carica_commenti" -v
```

Atteso: tutti `PASSED`

- [ ] **Step 6: Aggiorna import in tests/test_normalizza_commenti.py**

Rimuovi la riga `from src.data.normalizza_commenti import carica_commenti` aggiunta localmente al task e aggiungila all'import block in cima al file (insieme agli altri import):

```python
from src.data.normalizza_commenti import (
    ATTRIBUTI,
    ATTRIBUTI_DESCRIZIONI,
    carica_vocabolario,
    carica_commenti,
    prenormalizza_commento,
    parse_llm_response,
    genera_baseline,
    normalizza_batch,
    genera_report,
)
```

- [ ] **Step 7: Esegui tutti i test**

```bash
pytest tests/test_normalizza_commenti.py -v
```

Atteso: tutti `PASSED`

- [ ] **Step 8: Commit**

```bash
git add src/data/normalizza_commenti.py tests/test_normalizza_commenti.py \
        tests/fixtures/Texture_commenti_fixture.csv
git commit -m "feat: add carica_commenti with multi-schema CSV loading and empty filtering"
```

---

## Task 9: Pipeline script 10_normalizza_commenti.py

**Files:**
- Create: `src/data/10_normalizza_commenti.py`

- [ ] **Step 1: Crea lo script pipeline**

```python
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

import openai

from normalizza_commenti import (
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
```

- [ ] **Step 2: Testa lo script in dry-run (non chiama API)**

```bash
cd C:/Users/panci/vsworkspace/CheeseCaptioningAIFQC
python src/data/10_normalizza_commenti.py --dry-run --attributo Texture
```

Atteso: output con 3 esempi di pre-normalizzazione per Texture, nessuna chiamata API.

- [ ] **Step 3: Commit**

```bash
git add src/data/10_normalizza_commenti.py
git commit -m "feat: add pipeline script 10_normalizza_commenti with argparse, checkpoint, retry"
```

---

## Task 10: Test end-to-end con API mock

**Files:**
- Modify: `tests/test_normalizza_commenti.py`

- [ ] **Step 1: Scrivi il test end-to-end**

Aggiungi a `tests/test_normalizza_commenti.py`:

```python
# ── End-to-end integration ─────────────────────────────────────────────────

import shutil

def test_pipeline_completa_da_fixture(tmp_path):
    """Testa la pipeline end-to-end con CSV fixture e API mock."""
    # Setup: copia fixture CSV nella tmp_path
    csv_dir = tmp_path / "csv"
    csv_dir.mkdir()
    shutil.copy(FIXTURES / "Texture_commenti_fixture.csv",
                csv_dir / "Commenti_2019_Texture.csv")

    vocab = carica_vocabolario("Texture", VOCAB_DIR)

    # Carica commenti
    commenti = carica_commenti("Texture", csv_dir)
    assert len(commenti) == 4  # 5 righe dati - 1 vuota = 4 ("vedi sopra" non è filtrato qui, lo classifica l'LLM)

    # Pre-normalizzazione
    for c in commenti:
        c["commento_prenorm"] = prenormalizza_commento(c["commento_raw"], vocab)
    assert all("commento_prenorm" in c for c in commenti)

    # Mock LLM response
    llm_response = "\n".join([
        f'{{"id": {c["id"]}, "classe": "OK", "caption": "Caption per commento {c[\"id\"]}."}}' 
        for c in commenti
    ])
    client = _mock_client(llm_response)
    baseline = "La texture risulta nella norma."

    # Normalizza batch
    batch_input = [{"id": c["id"], "commento_prenorm": c["commento_prenorm"]} for c in commenti]
    risultati = normalizza_batch(batch_input, "Texture", vocab, baseline, client)
    assert len(risultati) == 3
    assert all(r["classe"] == "OK" for r in risultati)

    # Report
    report_path = tmp_path / "report.md"
    for r, c in zip(risultati, commenti):
        r["commento_raw"] = c["commento_raw"]
    genera_report(risultati, "Texture", report_path)
    assert report_path.exists()
    content = report_path.read_text(encoding="utf-8")
    assert "Texture" in content
    assert "3" in content
```

- [ ] **Step 2: Esegui il test**

```bash
pytest tests/test_normalizza_commenti.py::test_pipeline_completa_da_fixture -v
```

Atteso: `PASSED`

- [ ] **Step 3: Esegui la suite completa**

```bash
pytest tests/test_normalizza_commenti.py -v
```

Atteso: tutti `PASSED`

- [ ] **Step 4: Commit finale**

```bash
git add tests/test_normalizza_commenti.py
git commit -m "test: add end-to-end integration test for normalizzazione pipeline"
```

---

## Pilot run (dopo Task 9)

Prima di processare tutti i 10.005 commenti, esegui il pilot su Texture:

```bash
export OPENAI_API_KEY="sk-..."
python src/data/10_normalizza_commenti.py --attributo Texture --batch-size 5 --model gpt-4o-mini
```

Verifica manualmente `reports/normalizzazione_Texture.md`. Se la qualità è soddisfacente:

```bash
python src/data/10_normalizza_commenti.py --model gpt-4o-mini
```

Questo processa tutti e 7 gli attributi (~$0.50 totali).
