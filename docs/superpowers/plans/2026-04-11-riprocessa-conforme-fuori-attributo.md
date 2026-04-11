# Riprocessamento CONFORME e FUORI_ATTRIBUTO — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Aggiungere a `normalizza_commenti.py` le funzioni per riprocessare righe CONFORME (con distinzione specifico/generico) e FUORI_ATTRIBUTO (generazione caption), e creare i due script pipeline.

**Architecture:** Seguire il pattern esistente — funzioni pure testabili in `normalizza_commenti.py`, script pipeline in `src/data/`. Due nuovi script: `11_riprocessa_conforme.py` e `12_riprocessa_fuori_attributo.py`. Aggiornamento di `_USER_MSG_HEADER` per generare caption anche per FUORI_ATTRIBUTO.

**Tech Stack:** Python 3.11, openai>=1.0.0, pandas, python-dotenv, pytest

---

## File Map

| Azione | File | Responsabilità |
|--------|------|----------------|
| Modify | `src/data/normalizza_commenti.py` | Aggiunge 5 simboli: `carica_baseline`, `parse_fuori_attributo_response`, `riprocessa_conforme_batch`, `riprocessa_fuori_attributo_batch`, costanti prompt; aggiorna `_USER_MSG_HEADER` |
| Modify | `tests/test_normalizza_commenti.py` | Aggiunge test per i 4 nuovi simboli |
| Create | `src/data/11_riprocessa_conforme.py` | Script pipeline CONFORME |
| Create | `src/data/12_riprocessa_fuori_attributo.py` | Script pipeline FUORI_ATTRIBUTO |

---

## Task 1: `carica_baseline` — test e implementazione

**Files:**
- Modify: `src/data/normalizza_commenti.py`
- Modify: `tests/test_normalizza_commenti.py`

- [ ] **Step 1.1: Scrivi il test fallente**

In `tests/test_normalizza_commenti.py`, aggiungi dopo i test di `carica_vocabolario`:

```python
# ── carica_baseline ────────────────────────────────────────────────────────

from src.data.normalizza_commenti import carica_baseline

def test_carica_baseline_ritorna_stringa(tmp_path):
    import json
    (tmp_path / "Texture_baseline.json").write_text(
        json.dumps({"attributo": "Texture", "baseline": "Testo baseline di prova."}),
        encoding="utf-8"
    )
    risultato = carica_baseline("Texture", tmp_path)
    assert risultato == "Testo baseline di prova."

def test_carica_baseline_file_mancante(tmp_path):
    with pytest.raises(FileNotFoundError):
        carica_baseline("Attributo_Inesistente", tmp_path)
```

- [ ] **Step 1.2: Verifica che i test fallano**

```bash
pytest tests/test_normalizza_commenti.py::test_carica_baseline_ritorna_stringa tests/test_normalizza_commenti.py::test_carica_baseline_file_mancante -v
```
Atteso: `ImportError` o `FAILED` — `carica_baseline` non esiste ancora.

- [ ] **Step 1.3: Implementa `carica_baseline` in `normalizza_commenti.py`**

Aggiungi dopo `carica_vocabolario`:

```python
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
```

Aggiungi `carica_baseline` agli import nel file di test (riga 7):
```python
from src.data.normalizza_commenti import (
    ...
    carica_baseline,
)
```

- [ ] **Step 1.4: Verifica che i test passino**

```bash
pytest tests/test_normalizza_commenti.py::test_carica_baseline_ritorna_stringa tests/test_normalizza_commenti.py::test_carica_baseline_file_mancante -v
```
Atteso: `2 passed`

- [ ] **Step 1.5: Commit**

```bash
git add src/data/normalizza_commenti.py tests/test_normalizza_commenti.py
git commit -m "feat: add carica_baseline function with tests"
```

---

## Task 2: `parse_fuori_attributo_response` — test e implementazione

**Files:**
- Modify: `src/data/normalizza_commenti.py`
- Modify: `tests/test_normalizza_commenti.py`

- [ ] **Step 2.1: Scrivi il test fallente**

In `tests/test_normalizza_commenti.py`, aggiungi dopo i test di `parse_llm_response`:

```python
# ── parse_fuori_attributo_response ─────────────────────────────────────────

from src.data.normalizza_commenti import parse_fuori_attributo_response

def test_parse_fuori_attributo_risposta_completa():
    response_text = (
        '{"id": 1, "caption": "Il campione ha un odore di burro."}\n'
        '{"id": 2, "caption": "Note di panna cotta."}\n'
    )
    risultati = parse_fuori_attributo_response(response_text, expected_ids=[1, 2])
    assert len(risultati) == 2
    assert risultati[0] == {"id": 1, "caption": "Il campione ha un odore di burro."}
    assert risultati[1] == {"id": 2, "caption": "Note di panna cotta."}

def test_parse_fuori_attributo_id_mancante():
    response_text = '{"id": 1, "caption": "Testo."}'
    risultati = parse_fuori_attributo_response(response_text, expected_ids=[1, 2])
    assert len(risultati) == 2
    assert risultati[1] == {"id": 2, "caption": None}

def test_parse_fuori_attributo_json_malformato():
    response_text = 'non json\n{"id": 1, "caption": "Testo."}'
    risultati = parse_fuori_attributo_response(response_text, expected_ids=[1])
    assert risultati[0]["caption"] == "Testo."

def test_parse_fuori_attributo_risposta_vuota():
    risultati = parse_fuori_attributo_response("", expected_ids=[1])
    assert risultati[0] == {"id": 1, "caption": None}
```

- [ ] **Step 2.2: Verifica che i test fallano**

```bash
pytest tests/test_normalizza_commenti.py -k "fuori_attributo_response" -v
```
Atteso: `ImportError` o `FAILED`.

- [ ] **Step 2.3: Implementa `parse_fuori_attributo_response` in `normalizza_commenti.py`**

Aggiungi dopo `parse_llm_response`:

```python
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
```

Aggiungi `parse_fuori_attributo_response` agli import nel test.

- [ ] **Step 2.4: Verifica che i test passino**

```bash
pytest tests/test_normalizza_commenti.py -k "fuori_attributo_response" -v
```
Atteso: `4 passed`

- [ ] **Step 2.5: Commit**

```bash
git add src/data/normalizza_commenti.py tests/test_normalizza_commenti.py
git commit -m "feat: add parse_fuori_attributo_response with tests"
```

---

## Task 3: Costanti prompt e `_USER_MSG_HEADER` aggiornato

**Files:**
- Modify: `src/data/normalizza_commenti.py`

Nessun test diretto (le costanti sono testate indirettamente dai test delle funzioni che le usano).

- [ ] **Step 3.1: Aggiungi le tre costanti prompt in `normalizza_commenti.py`**

Sostituisci il blocco `_USER_MSG_HEADER` esistente (riga 85-97) con:

```python
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
```

- [ ] **Step 3.2: Verifica che i test esistenti passino ancora**

```bash
pytest tests/test_normalizza_commenti.py -v
```
Atteso: tutti i test precedenti `passed` (le costanti cambiate non rompono i test che mockano il client).

- [ ] **Step 3.3: Commit**

```bash
git add src/data/normalizza_commenti.py
git commit -m "feat: update FUORI_ATTRIBUTO prompt to generate captions, add reprocess prompt constants"
```

---

## Task 4: `riprocessa_conforme_batch` — test e implementazione

**Files:**
- Modify: `src/data/normalizza_commenti.py`
- Modify: `tests/test_normalizza_commenti.py`

- [ ] **Step 4.1: Scrivi il test fallente**

In `tests/test_normalizza_commenti.py`, aggiungi dopo i test di `normalizza_batch`:

```python
# ── riprocessa_conforme_batch ──────────────────────────────────────────────

from src.data.normalizza_commenti import riprocessa_conforme_batch

BATCH_CONFORME_FIXTURE = [
    {"id": 10, "commento_raw": "Paglierino"},
    {"id": 11, "commento_raw": "ok"},
]

LLM_CONFORME_RESPONSE = (
    '{"id": 10, "classe": "OK", "caption": "Il campione presenta una pasta di colore paglierino."}\n'
    '{"id": 11, "classe": "CONFORME", "caption": "Il campione presenta caratteristiche visive conformi alla norma, con colore uniforme e omogeneo."}\n'
)

def test_riprocessa_conforme_ritorna_risultati_per_tutti():
    client = _mock_client(LLM_CONFORME_RESPONSE)
    risultati = riprocessa_conforme_batch(
        BATCH_CONFORME_FIXTURE, "Colore della Pasta", VOCAB_FIXTURE, "Baseline.", client
    )
    assert len(risultati) == 2

def test_riprocessa_conforme_classi_ok_e_conforme():
    client = _mock_client(LLM_CONFORME_RESPONSE)
    risultati = riprocessa_conforme_batch(
        BATCH_CONFORME_FIXTURE, "Colore della Pasta", VOCAB_FIXTURE, "Baseline.", client
    )
    classi = {r["id"]: r["classe"] for r in risultati}
    assert classi[10] == "OK"
    assert classi[11] == "CONFORME"

def test_riprocessa_conforme_include_baseline_nel_prompt():
    client = _mock_client(LLM_CONFORME_RESPONSE)
    riprocessa_conforme_batch(
        BATCH_CONFORME_FIXTURE, "Colore della Pasta", VOCAB_FIXTURE, "Baseline specifica.", client
    )
    messages = client.chat.completions.create.call_args.kwargs["messages"]
    assert "Baseline specifica." in str(messages)

def test_riprocessa_conforme_batch_vuoto():
    client = _mock_client("")
    risultati = riprocessa_conforme_batch([], "Texture", VOCAB_FIXTURE, "Baseline.", client)
    assert risultati == []
    client.chat.completions.create.assert_not_called()
```

- [ ] **Step 4.2: Verifica che i test fallano**

```bash
pytest tests/test_normalizza_commenti.py -k "riprocessa_conforme" -v
```
Atteso: `ImportError` o `FAILED`.

- [ ] **Step 4.3: Implementa `riprocessa_conforme_batch` in `normalizza_commenti.py`**

Aggiungi dopo `normalizza_batch`:

```python
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
```

Aggiungi `riprocessa_conforme_batch` agli import nel test.

- [ ] **Step 4.4: Verifica che i test passino**

```bash
pytest tests/test_normalizza_commenti.py -k "riprocessa_conforme" -v
```
Atteso: `4 passed`

- [ ] **Step 4.5: Commit**

```bash
git add src/data/normalizza_commenti.py tests/test_normalizza_commenti.py
git commit -m "feat: add riprocessa_conforme_batch with tests"
```

---

## Task 5: `riprocessa_fuori_attributo_batch` — test e implementazione

**Files:**
- Modify: `src/data/normalizza_commenti.py`
- Modify: `tests/test_normalizza_commenti.py`

- [ ] **Step 5.1: Scrivi il test fallente**

In `tests/test_normalizza_commenti.py`, aggiungi:

```python
# ── riprocessa_fuori_attributo_batch ──────────────────────────────────────

from src.data.normalizza_commenti import riprocessa_fuori_attributo_batch

BATCH_FUORI_FIXTURE = [
    {"id": 20, "commento_raw": "burro e panna"},
    {"id": 21, "commento_raw": "carne lessa"},
]

LLM_FUORI_RESPONSE = (
    '{"id": 20, "caption": "Il campione presenta note di burro e panna."}\n'
    '{"id": 21, "caption": "Sentori di carne lessa."}\n'
)

def test_riprocessa_fuori_attributo_ritorna_caption():
    client = _mock_client(LLM_FUORI_RESPONSE)
    risultati = riprocessa_fuori_attributo_batch(BATCH_FUORI_FIXTURE, client)
    assert len(risultati) == 2
    assert risultati[0] == {"id": 20, "caption": "Il campione presenta note di burro e panna."}
    assert risultati[1] == {"id": 21, "caption": "Sentori di carne lessa."}

def test_riprocessa_fuori_attributo_no_system_caseario():
    """Verifica che il prompt non contenga il contesto di attributo specifico."""
    client = _mock_client(LLM_FUORI_RESPONSE)
    riprocessa_fuori_attributo_batch(BATCH_FUORI_FIXTURE, client)
    messages = client.chat.completions.create.call_args.kwargs["messages"]
    system_content = messages[0]["content"]
    assert "ATTRIBUTO CORRENTE" not in system_content
    assert "VOCABOLARIO" not in system_content

def test_riprocessa_fuori_attributo_batch_vuoto():
    client = _mock_client("")
    risultati = riprocessa_fuori_attributo_batch([], client)
    assert risultati == []
    client.chat.completions.create.assert_not_called()
```

- [ ] **Step 5.2: Verifica che i test fallano**

```bash
pytest tests/test_normalizza_commenti.py -k "riprocessa_fuori_attributo" -v
```
Atteso: `ImportError` o `FAILED`.

- [ ] **Step 5.3: Implementa `riprocessa_fuori_attributo_batch` in `normalizza_commenti.py`**

Aggiungi dopo `riprocessa_conforme_batch`:

```python
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
```

Aggiungi `riprocessa_fuori_attributo_batch` agli import nel test.

- [ ] **Step 5.4: Verifica che i test passino**

```bash
pytest tests/test_normalizza_commenti.py -k "riprocessa_fuori_attributo" -v
```
Atteso: `3 passed`

- [ ] **Step 5.5: Verifica intera suite**

```bash
pytest tests/test_normalizza_commenti.py -v
```
Atteso: tutti i test `passed` (nessuna regressione).

- [ ] **Step 5.6: Commit**

```bash
git add src/data/normalizza_commenti.py tests/test_normalizza_commenti.py
git commit -m "feat: add riprocessa_fuori_attributo_batch with tests"
```

---

## Task 6: Script `11_riprocessa_conforme.py`

**Files:**
- Create: `src/data/11_riprocessa_conforme.py`

- [ ] **Step 6.1: Crea il file**

```python
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
    variati = sum(1 for r in tutti_risultati if r["classe"] == "CONFORME")
    logger.info(f"[{attributo}] Promossi OK: {promossi}, CONFORME variati: {variati}")

    REPORTS_DIR.mkdir(parents=True, exist_ok=True)
    report_path = REPORTS_DIR / f"riprocessa_conforme_{attributo.replace(' ', '_')}.md"
    lines = [
        f"# Report riprocessamento CONFORME — {attributo}",
        "",
        f"- Righe riprocessate: {len(conforme_rows)}",
        f"- Promosse a OK: {promossi}",
        f"- CONFORME con caption variata: {variati}",
        f"- Errori: {len(conforme_rows) - promossi - variati}",
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

    for attributo in attributi:
        try:
            processa_attributo(attributo, client, args.model, args.batch_size, args.max_retry, args.dry_run)
        except Exception as exc:
            logger.error(f"[{attributo}] Errore fatale: {exc}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
```

- [ ] **Step 6.2: Verifica dry-run**

```bash
python src/data/11_riprocessa_conforme.py --dry-run --attributo Texture
```
Atteso: log con `DRY-RUN` e i primi 3 commenti CONFORME di Texture stampati.

- [ ] **Step 6.3: Commit**

```bash
git add src/data/11_riprocessa_conforme.py
git commit -m "feat: add 11_riprocessa_conforme.py pipeline script"
```

---

## Task 7: Script `12_riprocessa_fuori_attributo.py`

**Files:**
- Create: `src/data/12_riprocessa_fuori_attributo.py`

- [ ] **Step 7.1: Crea il file**

```python
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
    logger.info(f"[{attributo}] Caption generate: {con_caption}/{len(fuori_rows)}")

    REPORTS_DIR.mkdir(parents=True, exist_ok=True)
    report_path = REPORTS_DIR / f"riprocessa_fuori_attributo_{attributo.replace(' ', '_')}.md"
    lines = [
        f"# Report riprocessamento FUORI_ATTRIBUTO — {attributo}",
        "",
        f"- Righe processate: {len(fuori_rows)}",
        f"- Caption generate: {con_caption}",
        f"- Senza caption (errori): {len(fuori_rows) - con_caption}",
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

    for attributo in attributi:
        try:
            processa_attributo(attributo, client, args.model, args.batch_size, args.max_retry, args.dry_run)
        except Exception as exc:
            logger.error(f"[{attributo}] Errore fatale: {exc}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
```

- [ ] **Step 7.2: Verifica dry-run**

```bash
python src/data/12_riprocessa_fuori_attributo.py --dry-run --attributo Aroma
```
Atteso: log con `DRY-RUN` e i primi 3 commenti FUORI_ATTRIBUTO di Aroma.

- [ ] **Step 7.3: Verifica suite test completa**

```bash
pytest tests/test_normalizza_commenti.py -v
```
Atteso: tutti i test `passed`.

- [ ] **Step 7.4: Commit finale**

```bash
git add src/data/12_riprocessa_fuori_attributo.py
git commit -m "feat: add 12_riprocessa_fuori_attributo.py pipeline script"
```
