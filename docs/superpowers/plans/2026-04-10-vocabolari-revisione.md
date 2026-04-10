# Vocabolari Revisione — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Creare 7 documenti di revisione umana pre-compilati (`_revisione.md`) e lo script `09a_compila_vocabolari.py` che li converte in JSON validati.

**Architecture:** I documenti di revisione sono Markdown con blocchi `yaml` inline editabili — sia le scelte pre-compilate che i dubbi. Lo script parsa i blocchi yaml per header-section e costruisce il JSON finale nel formato richiesto da Script 09. I dubbi con `scelta: ""` finiscono in `dubbi_non_risolti` nel JSON senza bloccare la generazione.

**Tech Stack:** Python 3.x, PyYAML (già installato), pytest, stdlib only (re, pathlib, json, datetime)

---

## File Structure

```
data/interim/vocabolari_revisione_umana/    ← NEW (già creata)
  Aroma_revisione.md
  Colore_della_Pasta_revisione.md
  Profumo_revisione.md
  Sapore_revisione.md
  Spessore_della_Crosta_revisione.md
  Struttura_della_Pasta_revisione.md
  Texture_revisione.md
  revisione_status.md                       ← generato da 09a

data/interim/vocabolari_validati_per_attributo/  ← NEW (già creata)
  {Attributo}_vocabolario.json              ← generato da 09a (7 file)

src/data/
  09a_compila_vocabolari.py                 ← NEW

tests/
  test_09a_compila_vocabolari.py            ← NEW
  fixtures/
    Texture_revisione_fixture.md            ← NEW (fixture minimale per test)
```

---

## Formato documento di revisione (riferimento per tutti i task)

Ogni `_revisione.md` ha questa struttura con blocchi yaml inline editabili:

```markdown
## META
```yaml
attributo: "NomeAttributo"
versione: "1.0"
stato: "DA_RIVEDERE"
note_generali: ""
```

## TERMINI TECNICI INVARIABILI
```yaml
termini: [termine1, termine2, ...]
```

## CLUSTER SEMANTICI

### Cluster: nome_concetto
> Frequenza stimata: N | Varianti NBLM: …

```yaml
forma_canonica: termine_standard
varianti: [variante1, variante2]
frequenza_stimata: N
note: ""
```

## SINONIMI / ABBREVIAZIONI / TYPO

### Sinonimo: da → a
```yaml
da: "termine_originale"
a: "forma_canonica"
tipo: sinonimo   # sinonimo | abbreviazione | typo | dialetto
note: ""
```

## CONVERSIONI QUANTITATIVE
*(solo Spessore della Crosta)*

### Conversione: pattern_mm → etichetta
```yaml
pattern_regex: "\\d+\\s*mm"
range_min_mm: 0
range_max_mm: 7
forma_canonica: "molto sottile"
note: ""
```

## DUBBI — RICHIEDE DECISIONE UMANA

### DUBBIO: "termine_ambiguo"
> Contesto: panelista X, seduta Y/anno — "frase originale"
> Opzione A → `forma_A` (motivazione)
> Opzione B → `forma_B` (motivazione)

```yaml
scelta: ""   # scrivi A, B, o forma_canonica custom
option_a: forma_A
option_b: forma_B
note: ""
```

## NOTE LIBERE
```yaml
note: ""
```
```

**Regole di parsing per lo script:**
- Header `## META` → legge `attributo`, `stato`, `note_generali`
- Header `## TERMINI TECNICI INVARIABILI` → lista `termini`
- Header `### Cluster: *` → blocco cluster con `forma_canonica`, `varianti`, `frequenza_stimata`
- Header `### Sinonimo: *` o `### Abbreviazione: *` o `### Typo: *` o `### Dialetto: *` → blocco sinonimo
- Header `### Conversione: *` → blocco conversione_quantitativa
- Header `### DUBBIO: *` → blocco dubbio; se `scelta: ""` → `dubbi_non_risolti`; se `scelta: A` → usa `option_a`; se `scelta: B` → usa `option_b`; se scelta è testo custom → usa direttamente come `a`

---

## Task 1: Setup — `__init__.py`, `conftest.py`, fixture

**Files:**
- Create: `src/__init__.py` (vuoto)
- Create: `src/data/__init__.py` (vuoto)
- Create: `tests/__init__.py` (vuoto)
- Create: `tests/conftest.py`
- Create: `tests/fixtures/Texture_revisione_fixture.md`
- Create: `tests/fixtures/Texture_vocabolario_expected.json`

- [ ] **Step 1: Crea `__init__.py` per abilitare import del package**

```bash
touch src/__init__.py src/data/__init__.py tests/__init__.py
```

- [ ] **Step 2: Crea `tests/conftest.py` per aggiungere root al sys.path**

Crea `tests/conftest.py`:

```python
import sys
from pathlib import Path

# Aggiunge root del progetto al path così i test trovano src.data.*
sys.path.insert(0, str(Path(__file__).parents[1]))
```

- [ ] **Step 3: Crea directory tests/fixtures**

```bash
mkdir -p tests/fixtures
```

- [ ] **Step 2: Crea la fixture minimale del documento di revisione**

Crea `tests/fixtures/Texture_revisione_fixture.md`:

```markdown
## META
```yaml
attributo: "Texture"
versione: "1.0"
stato: "APPROVATO"
note_generali: ""
```

## TERMINI TECNICI INVARIABILI
```yaml
termini: [cristalli, tirosina, solubile, solubilità, friabile, friabilità, compatto, compattezza, cedevole, grana, nostrano, stirata, scalzo, scalzi, piatti, piatto, sottocrosta, angoli, spigoli, microocchiatura, occhiatura, insilato]
```

## CLUSTER SEMANTICI

### Cluster: cristalli_tirosina
> Frequenza stimata: 315 | Varianti NBLM: cristalli, microcristalli, tirosina, perle…

```yaml
forma_canonica: cristalli
varianti: [microcristalli, tirosina, perle, gnocchetti duri, scagliette, schioccante, scricchiola]
frequenza_stimata: 315
note: ""
```

### Cluster: morbidezza
> Frequenza stimata: 152

```yaml
forma_canonica: morbido
varianti: [molle, tenero, molliccio]
frequenza_stimata: 152
note: ""
```

## SINONIMI / ABBREVIAZIONI / TYPO

### Abbreviazione: sol. → solubile
```yaml
da: "sol."
a: solubile
tipo: abbreviazione
note: ""
```

### Typo: granuolo → granuloso
```yaml
da: granuolo
a: granuloso
tipo: typo
note: ""
```

## DUBBI — RICHIEDE DECISIONE UMANA

### DUBBIO: "alleabile"
> Contesto: Q_09, seduta 17/2019 — "Alleabile". Parola inesistente.
> Opzione A → `malleabile` (struttura plastica)
> Opzione B → `allappante` (astringenza)

```yaml
scelta: "A"
option_a: malleabile
option_b: allappante
note: ""
```

### DUBBIO: "patatoso"
> Contesto: TG_35 e TG_24, sedute 7-8/2020
> Opzione A → `pastoso`
> Opzione B → `farinoso`

```yaml
scelta: ""
option_a: pastoso
option_b: farinoso
note: ""
```

## NOTE LIBERE
```yaml
note: ""
```
```

- [ ] **Step 3: Crea il JSON atteso per la fixture**

Crea `tests/fixtures/Texture_vocabolario_expected.json`:

```json
{
  "attributo": "Texture",
  "versione": "1.0",
  "validato_da": "",
  "note_generali": "",
  "termini_tecnici_invariabili": [
    "cristalli", "tirosina", "solubile", "solubilità", "friabile", "friabilità",
    "compatto", "compattezza", "cedevole", "grana", "nostrano", "stirata",
    "scalzo", "scalzi", "piatti", "piatto", "sottocrosta", "angoli", "spigoli",
    "microocchiatura", "occhiatura", "insilato"
  ],
  "cluster": [
    {
      "nome_cluster": "cristalli_tirosina",
      "forma_canonica": "cristalli",
      "varianti": ["microcristalli", "tirosina", "perle", "gnocchetti duri", "scagliette", "schioccante", "scricchiola"],
      "frequenza_stimata": 315
    },
    {
      "nome_cluster": "morbidezza",
      "forma_canonica": "morbido",
      "varianti": ["molle", "tenero", "molliccio"],
      "frequenza_stimata": 152
    }
  ],
  "sinonimi_diretti": [
    {"da": "sol.", "a": "solubile", "tipo": "abbreviazione"},
    {"da": "granuolo", "a": "granuloso", "tipo": "typo"},
    {"da": "alleabile", "a": "malleabile", "tipo": "dubbio_risolto"}
  ],
  "conversioni_quantitative": [],
  "dubbi_non_risolti": [
    {"termine": "patatoso", "option_a": "pastoso", "option_b": "farinoso", "scelta": "", "note": ""}
  ]
}
```

- [ ] **Step 4: Commit**

```bash
git add tests/fixtures/
git commit -m "test: add fixtures for 09a_compila_vocabolari"
```

---

## Task 2: Test per `extract_blocks`

**Files:**
- Create: `tests/test_09a_compila_vocabolari.py`

- [ ] **Step 1: Scrivi i test failing**

Crea `tests/test_09a_compila_vocabolari.py`:

```python
import json
import pytest
from pathlib import Path
from src.data.compila_vocabolari import extract_blocks, build_vocabolario, compile_all

FIXTURES = Path("tests/fixtures")


# ── extract_blocks ────────────────────────────────────────────────────────────

def test_extract_blocks_returns_cluster():
    md = """
## CLUSTER SEMANTICI

### Cluster: friabilità
> Test

```yaml
forma_canonica: friabile
varianti: [friabilità, frantuma, sbriciola]
frequenza_stimata: 151
note: ""
```
"""
    blocks = extract_blocks(md)
    assert len(blocks) == 1
    b = blocks[0]
    assert b["section"] == "CLUSTER SEMANTICI"
    assert b["header"] == "Cluster: friabilità"
    assert b["data"]["forma_canonica"] == "friabile"
    assert b["data"]["varianti"] == ["friabilità", "frantuma", "sbriciola"]


def test_extract_blocks_returns_sinonimo():
    md = """
## SINONIMI / ABBREVIAZIONI / TYPO

### Abbreviazione: sol. → solubile
```yaml
da: "sol."
a: solubile
tipo: abbreviazione
note: ""
```
"""
    blocks = extract_blocks(md)
    assert len(blocks) == 1
    assert blocks[0]["header"] == "Abbreviazione: sol. → solubile"
    assert blocks[0]["data"]["da"] == "sol."
    assert blocks[0]["data"]["tipo"] == "abbreviazione"


def test_extract_blocks_returns_multiple_blocks():
    md = """
## META
```yaml
attributo: "Texture"
stato: "APPROVATO"
note_generali: ""
```

## TERMINI TECNICI INVARIABILI
```yaml
termini: [cristalli, tirosina]
```
"""
    blocks = extract_blocks(md)
    assert len(blocks) == 2
    assert blocks[0]["section"] == "META"
    assert blocks[1]["section"] == "TERMINI TECNICI INVARIABILI"


def test_extract_blocks_skips_malformed_yaml():
    md = """
## CLUSTER SEMANTICI

### Cluster: test
```yaml
forma_canonica: [unclosed
```
"""
    blocks = extract_blocks(md)
    assert blocks == []


# ── build_vocabolario ─────────────────────────────────────────────────────────

def test_build_vocabolario_open_doubt_goes_to_dubbi():
    blocks = [
        {"section": "META", "header": "META",
         "data": {"attributo": "Texture", "stato": "APPROVATO", "note_generali": ""}},
        {"section": "TERMINI TECNICI INVARIABILI", "header": "TERMINI TECNICI INVARIABILI",
         "data": {"termini": ["cristalli"]}},
        {"section": "DUBBI — RICHIEDE DECISIONE UMANA", "header": 'DUBBIO: "patatoso"',
         "data": {"scelta": "", "option_a": "pastoso", "option_b": "farinoso", "note": ""}},
    ]
    vocab = build_vocabolario(blocks, "Texture")
    assert len(vocab["dubbi_non_risolti"]) == 1
    assert vocab["dubbi_non_risolti"][0]["termine"] == "patatoso"
    assert len(vocab["sinonimi_diretti"]) == 0


def test_build_vocabolario_doubt_A_resolves_to_option_a():
    blocks = [
        {"section": "META", "header": "META",
         "data": {"attributo": "Texture", "stato": "APPROVATO", "note_generali": ""}},
        {"section": "DUBBI — RICHIEDE DECISIONE UMANA", "header": 'DUBBIO: "alleabile"',
         "data": {"scelta": "A", "option_a": "malleabile", "option_b": "allappante", "note": ""}},
    ]
    vocab = build_vocabolario(blocks, "Texture")
    assert len(vocab["dubbi_non_risolti"]) == 0
    assert {"da": "alleabile", "a": "malleabile", "tipo": "dubbio_risolto"} in vocab["sinonimi_diretti"]


def test_build_vocabolario_doubt_B_resolves_to_option_b():
    blocks = [
        {"section": "META", "header": "META",
         "data": {"attributo": "Texture", "stato": "APPROVATO", "note_generali": ""}},
        {"section": "DUBBI — RICHIEDE DECISIONE UMANA", "header": 'DUBBIO: "alleabile"',
         "data": {"scelta": "B", "option_a": "malleabile", "option_b": "allappante", "note": ""}},
    ]
    vocab = build_vocabolario(blocks, "Texture")
    assert {"da": "alleabile", "a": "allappante", "tipo": "dubbio_risolto"} in vocab["sinonimi_diretti"]


def test_build_vocabolario_doubt_custom_scelta():
    blocks = [
        {"section": "META", "header": "META",
         "data": {"attributo": "Texture", "stato": "APPROVATO", "note_generali": ""}},
        {"section": "DUBBI — RICHIEDE DECISIONE UMANA", "header": 'DUBBIO: "immagiabile"',
         "data": {"scelta": "immangiabile", "option_a": "immangiabile", "option_b": "immasticabile", "note": ""}},
    ]
    vocab = build_vocabolario(blocks, "Texture")
    assert {"da": "immagiabile", "a": "immangiabile", "tipo": "dubbio_risolto"} in vocab["sinonimi_diretti"]


def test_build_vocabolario_clusters_mapped_correctly():
    blocks = [
        {"section": "META", "header": "META",
         "data": {"attributo": "Texture", "stato": "APPROVATO", "note_generali": ""}},
        {"section": "CLUSTER SEMANTICI", "header": "Cluster: morbidezza",
         "data": {"forma_canonica": "morbido", "varianti": ["molle", "tenero"], "frequenza_stimata": 152, "note": ""}},
    ]
    vocab = build_vocabolario(blocks, "Texture")
    assert vocab["cluster"] == [
        {"nome_cluster": "morbidezza", "forma_canonica": "morbido",
         "varianti": ["molle", "tenero"], "frequenza_stimata": 152}
    ]


# ── compile_all (integration) ─────────────────────────────────────────────────

def test_compile_all_from_fixture(tmp_path):
    import shutil
    shutil.copy(FIXTURES / "Texture_revisione_fixture.md",
                tmp_path / "Texture_revisione.md")
    output_dir = tmp_path / "output"
    output_dir.mkdir()

    result = compile_all(tmp_path, output_dir)

    assert result["Texture"]["status"] == "open_doubts"  # patatoso è aperto
    json_path = output_dir / "Texture_vocabolario.json"
    assert json_path.exists()
    vocab = json.loads(json_path.read_text(encoding="utf-8"))
    assert vocab["attributo"] == "Texture"
    assert len(vocab["cluster"]) == 2
    assert len(vocab["dubbi_non_risolti"]) == 1
    # alleabile risolto → in sinonimi
    assert any(s["da"] == "alleabile" for s in vocab["sinonimi_diretti"])
```

- [ ] **Step 2: Esegui i test e verifica che falliscano**

```bash
.venv/Scripts/python -m pytest tests/test_09a_compila_vocabolari.py -v 2>&1 | head -30
```

Atteso: `ModuleNotFoundError: No module named 'src.data.compila_vocabolari'`

---

## Task 3: Implementa `src/data/compila_vocabolari.py`

**Files:**
- Create: `src/data/compila_vocabolari.py`

- [ ] **Step 1: Implementa il modulo**

Crea `src/data/compila_vocabolari.py`:

```python
"""
Compila i documenti di revisione umana (_revisione.md) in JSON vocabolario validato.

Usage:
    python src/data/09a_compila_vocabolari.py
    python src/data/09a_compila_vocabolari.py --dry-run
"""
from __future__ import annotations

import re
import json
import yaml
from pathlib import Path
from datetime import date
from typing import Any

REVISIONE_DIR = Path("data/interim/vocabolari_revisione_umana")
OUTPUT_DIR = Path("data/interim/vocabolari_validati_per_attributo")


# ── Parser ────────────────────────────────────────────────────────────────────

def extract_blocks(md_text: str) -> list[dict]:
    """
    Estrae tutti i blocchi ```yaml``` dal Markdown con il loro contesto.

    Ritorna lista di dict:
      {"section": str, "header": str, "data": dict}

    - section: titolo del ## corrente (es. "CLUSTER SEMANTICI")
    - header:  titolo del ### corrente o uguale a section se blocco di sezione diretta
    - data:    dict parsato dal blocco yaml
    """
    blocks: list[dict] = []
    current_section = ""
    current_header = ""

    # Splitta per righe mantenendo i numeri di riga
    lines = md_text.splitlines()
    in_yaml = False
    yaml_lines: list[str] = []

    for line in lines:
        if line.startswith("## ") and not in_yaml:
            current_section = line.lstrip("# ").strip()
            current_header = current_section
            continue
        if line.startswith("### ") and not in_yaml:
            current_header = line.lstrip("# ").strip()
            continue
        if line.strip() == "```yaml" and not in_yaml:
            in_yaml = True
            yaml_lines = []
            continue
        if line.strip() == "```" and in_yaml:
            in_yaml = False
            raw = "\n".join(yaml_lines)
            try:
                data = yaml.safe_load(raw)
                if isinstance(data, dict):
                    blocks.append({
                        "section": current_section,
                        "header": current_header,
                        "data": data,
                    })
            except yaml.YAMLError:
                pass  # blocco malformato, ignorato
            yaml_lines = []
            continue
        if in_yaml:
            yaml_lines.append(line)

    return blocks


def _extract_dubbio_termine(header: str) -> str:
    """Estrae il termine dal header '### DUBBIO: "termine"'."""
    match = re.match(r'DUBBIO:\s*["\']?(.+?)["\']?\s*$', header, re.IGNORECASE)
    return match.group(1).strip() if match else header


def build_vocabolario(blocks: list[dict], attributo: str) -> dict:
    """Costruisce il dizionario JSON dal set di blocchi parsati."""
    vocab: dict[str, Any] = {
        "attributo": attributo.replace("_", " "),
        "versione": "1.0",
        "data_validazione": str(date.today()),
        "validato_da": "",
        "note_generali": "",
        "termini_tecnici_invariabili": [],
        "cluster": [],
        "sinonimi_diretti": [],
        "conversioni_quantitative": [],
        "dubbi_non_risolti": [],
    }

    for block in blocks:
        section = block["section"]
        header = block["header"]
        data = block["data"]

        if section == "META":
            vocab["note_generali"] = data.get("note_generali", "")

        elif section == "TERMINI TECNICI INVARIABILI":
            vocab["termini_tecnici_invariabili"] = data.get("termini", [])

        elif section == "CLUSTER SEMANTICI":
            nome = header.replace("Cluster:", "").strip().lower().replace(" ", "_").replace("/", "_")
            vocab["cluster"].append({
                "nome_cluster": nome,
                "forma_canonica": data.get("forma_canonica", ""),
                "varianti": data.get("varianti", []),
                "frequenza_stimata": data.get("frequenza_stimata", 0),
            })

        elif section in ("SINONIMI / ABBREVIAZIONI / TYPO",
                         "SINONIMI / ABBREVIAZIONI / TYPO / DIALETTALISMI"):
            vocab["sinonimi_diretti"].append({
                "da": data.get("da", ""),
                "a": data.get("a", ""),
                "tipo": data.get("tipo", "sinonimo"),
            })

        elif section == "CONVERSIONI QUANTITATIVE":
            entry = {k: v for k, v in data.items() if k != "note"}
            vocab["conversioni_quantitative"].append(entry)

        elif "DUBBI" in section.upper():
            termine = _extract_dubbio_termine(header)
            scelta = str(data.get("scelta", "")).strip()
            option_a = data.get("option_a", "")
            option_b = data.get("option_b", "")

            if not scelta:
                vocab["dubbi_non_risolti"].append({
                    "termine": termine,
                    "option_a": option_a,
                    "option_b": option_b,
                    "scelta": "",
                    "note": data.get("note", ""),
                })
            else:
                if scelta.upper() == "A":
                    resolved = option_a
                elif scelta.upper() == "B":
                    resolved = option_b
                else:
                    resolved = scelta  # valore custom

                vocab["sinonimi_diretti"].append({
                    "da": termine,
                    "a": resolved,
                    "tipo": "dubbio_risolto",
                })

    return vocab


# ── Compilazione file ─────────────────────────────────────────────────────────

def compile_file(md_path: Path, output_dir: Path) -> dict:
    """
    Compila un singolo _revisione.md → JSON.

    Ritorna {"status": "ok" | "open_doubts" | "not_approved", "n_doubts": int}
    """
    text = md_path.read_text(encoding="utf-8")
    blocks = extract_blocks(text)

    # Ricava attributo dal nome file: Texture_revisione.md → Texture
    attributo = md_path.stem.replace("_revisione", "")

    # Controlla stato
    meta_blocks = [b for b in blocks if b["section"] == "META"]
    stato = ""
    if meta_blocks:
        stato = str(meta_blocks[0]["data"].get("stato", "")).strip()

    vocab = build_vocabolario(blocks, attributo)

    output_path = output_dir / f"{attributo}_vocabolario.json"
    output_dir.mkdir(parents=True, exist_ok=True)
    output_path.write_text(
        json.dumps(vocab, ensure_ascii=False, indent=2),
        encoding="utf-8"
    )

    n_doubts = len(vocab["dubbi_non_risolti"])
    if stato != "APPROVATO":
        status = "not_approved"
    elif n_doubts > 0:
        status = "open_doubts"
    else:
        status = "ok"

    return {"status": status, "n_doubts": n_doubts, "path": str(output_path)}


def compile_all(revisione_dir: Path, output_dir: Path) -> dict[str, dict]:
    """Compila tutti i _revisione.md trovati. Ritorna report per attributo."""
    results: dict[str, dict] = {}
    for md_path in sorted(revisione_dir.glob("*_revisione.md")):
        attributo = md_path.stem.replace("_revisione", "")
        results[attributo] = compile_file(md_path, output_dir)
    return results
```

- [ ] **Step 2: Esegui i test**

```bash
.venv/Scripts/python -m pytest tests/test_09a_compila_vocabolari.py -v
```

Atteso: tutti i test PASS (eccetto `test_compile_all_from_fixture` che dipende dalla fixture — verificare separatamente).

- [ ] **Step 3: Commit**

```bash
git add src/data/compila_vocabolari.py tests/test_09a_compila_vocabolari.py tests/fixtures/
git commit -m "feat: add compila_vocabolari module with TDD"
```

---

## Task 4: Script CLI `09a_compila_vocabolari.py`

**Files:**
- Create: `src/data/09a_compila_vocabolari.py`

- [ ] **Step 1: Crea lo script entry-point**

Crea `src/data/09a_compila_vocabolari.py`:

```python
#!/usr/bin/env python
"""
Script 09a — Compilazione vocabolari validati per attributo.

Legge i documenti di revisione umana in:
  data/interim/vocabolari_revisione_umana/

Genera i JSON vocabolario in:
  data/interim/vocabolari_validati_per_attributo/

Genera il report:
  data/interim/vocabolari_revisione_umana/revisione_status.md

Usage:
    python src/data/09a_compila_vocabolari.py
    python src/data/09a_compila_vocabolari.py --dry-run
"""
import sys
import argparse
from pathlib import Path
from datetime import date

# Aggiunge root del progetto al path per import del modulo
sys.path.insert(0, str(Path(__file__).parents[2]))
from src.data.compila_vocabolari import compile_all, REVISIONE_DIR, OUTPUT_DIR


def build_status_report(results: dict) -> str:
    lines = [
        f"# Revisione Status — {date.today()}",
        "",
        "| Attributo | Stato | Dubbi aperti | JSON generato |",
        "|---|---|---|---|",
    ]
    for attributo, info in sorted(results.items()):
        status_emoji = {
            "ok": "✅",
            "open_doubts": "⚠️",
            "not_approved": "🔴",
        }.get(info["status"], "❓")
        lines.append(
            f"| {attributo.replace('_', ' ')} "
            f"| {status_emoji} {info['status']} "
            f"| {info['n_doubts']} "
            f"| `{Path(info['path']).name}` |"
        )
    lines.append("")
    n_ok = sum(1 for r in results.values() if r["status"] == "ok")
    n_open = sum(1 for r in results.values() if r["status"] == "open_doubts")
    n_not = sum(1 for r in results.values() if r["status"] == "not_approved")
    lines.append(f"**Totale:** {len(results)} attributi — "
                 f"{n_ok} completi, {n_open} con dubbi aperti, {n_not} non approvati")
    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(description="Compila vocabolari revisione → JSON")
    parser.add_argument("--dry-run", action="store_true",
                        help="Mostra cosa farebbe senza scrivere file")
    parser.add_argument("--revisione-dir", type=Path, default=REVISIONE_DIR)
    parser.add_argument("--output-dir", type=Path, default=OUTPUT_DIR)
    args = parser.parse_args()

    if not args.revisione_dir.exists():
        print(f"❌ Directory non trovata: {args.revisione_dir}")
        sys.exit(1)

    files = list(args.revisione_dir.glob("*_revisione.md"))
    if not files:
        print(f"⚠️  Nessun file *_revisione.md trovato in {args.revisione_dir}")
        sys.exit(0)

    print(f"📂 Trovati {len(files)} file da compilare...")

    if args.dry_run:
        print("🔍 Dry-run: nessun file scritto.")
        for f in sorted(files):
            print(f"  - {f.name}")
        return

    results = compile_all(args.revisione_dir, args.output_dir)

    # Salva report
    report = build_status_report(results)
    report_path = args.revisione_dir / "revisione_status.md"
    report_path.write_text(report, encoding="utf-8")

    # Stampa riepilogo
    print("\n" + report)
    print(f"\n📊 Report salvato in: {report_path}")
    print(f"📁 JSON generati in:  {args.output_dir}")

    # Exit code 1 se ci sono dubbi aperti o non approvati
    if any(r["status"] != "ok" for r in results.values()):
        sys.exit(1)


if __name__ == "__main__":
    main()
```

- [ ] **Step 2: Verifica dry-run (senza file revisione creati)**

```bash
.venv/Scripts/python src/data/09a_compila_vocabolari.py --dry-run
```

Atteso: `⚠️  Nessun file *_revisione.md trovato in data/interim/vocabolari_revisione_umana`

- [ ] **Step 3: Commit**

```bash
git add src/data/09a_compila_vocabolari.py
git commit -m "feat: add 09a_compila_vocabolari CLI script"
```

---

## Task 5: Genera `Texture_revisione.md`

**Files:**
- Create: `data/interim/vocabolari_revisione_umana/Texture_revisione.md`

Fonte: `data/interim/vocabolari_bozza_per_attributo/Texture_vocabolario_nblm.md` (letto per intero).

- [ ] **Step 1: Crea il documento**

Crea `data/interim/vocabolari_revisione_umana/Texture_revisione.md` con il seguente contenuto:

```markdown
# Revisione Vocabolario — Texture
**Fonte:** Texture_vocabolario_nblm.md | **Generato:** 2026-04-10 | **Stato:** DA_RIVEDERE

## META
```yaml
attributo: "Texture"
versione: "1.0"
stato: "DA_RIVEDERE"
note_generali: ""
```

## TERMINI TECNICI INVARIABILI
```yaml
termini: [cristalli, tirosina, solubile, solubilità, friabile, friabilità, compatto, compattezza, cedevole, grana, nostrano, stirata, scalzo, scalzi, piatti, piatto, sottocrosta, angoli, spigoli, microocchiatura, occhiatura, insilato]
```

## CLUSTER SEMANTICI

### Cluster: cristalli_tirosina
> Frequenza stimata: 315 | Varianti NBLM: cristalli, microcristalli, tirosina, perle, gnocchetti duri, scagliette, schioccante, scricchiola

```yaml
forma_canonica: cristalli
varianti: [microcristalli, tirosina, perle, gnocchetti duri, scagliette, schioccante, scricchiola]
frequenza_stimata: 315
note: ""
```

### Cluster: solubilità
> Frequenza stimata: 255 | Varianti NBLM: solubile, solubilità, sol., solub., si scioglie, fondente, si liquefa, liquescente

```yaml
forma_canonica: solubile
varianti: [solubilità, "si scioglie", fondente, "si liquefa", liquescente]
frequenza_stimata: 255
note: "sol. e solub. sono normalizzati nella sezione abbreviazioni"
```

### Cluster: asciutto
> Frequenza stimata: 202 | Varianti NBLM: asciutto, secco, disidratata, asciuga le fauci, secchezza

```yaml
forma_canonica: asciutto
varianti: [secco, disidratata, "asciuga le fauci", secchezza, asciutta]
frequenza_stimata: 202
note: ""
```

### Cluster: friabilità
> Frequenza stimata: 151 | Varianti NBLM: friabile, friabilità, frantuma, sbriciola, franabile

```yaml
forma_canonica: friabile
varianti: [friabilità, frantuma, sbriciola, franabile]
frequenza_stimata: 151
note: "friabile e friabilità sono termini tecnici invariabili"
```

### Cluster: morbidezza
> Frequenza stimata: 152 | Varianti NBLM: morbido, molle, tenero, molliccio

```yaml
forma_canonica: morbido
varianti: [molle, tenero, molliccio]
frequenza_stimata: 152
note: ""
```

### Cluster: pastosità
> Frequenza stimata: 124 | Varianti NBLM: pastoso, pastosità, patatoso, pongo, crema

```yaml
forma_canonica: pastoso
varianti: [pastosità, pongo, crema]
frequenza_stimata: 124
note: "patatoso è un dubbio — vedere sezione DUBBI"
```

### Cluster: granulosità
> Frequenza stimata: 100 | Varianti NBLM: grana, granuloso, granulosità, granuli, granuolo

```yaml
forma_canonica: granuloso
varianti: [granulosità, granuli]
frequenza_stimata: 100
note: "grana è termine tecnico invariabile e non va incluso nelle varianti"
```

### Cluster: umidità
> Frequenza stimata: 80 | Varianti NBLM: umido, umidità, unidita

```yaml
forma_canonica: umido
varianti: [umidità, umida, unidita]
frequenza_stimata: 80
note: ""
```

### Cluster: compattezza
> Frequenza stimata: 80 | Varianti NBLM: compatto, compattezza

```yaml
forma_canonica: compatto
varianti: [compattezza]
frequenza_stimata: 80
note: "compatto e compattezza sono termini tecnici invariabili"
```

### Cluster: struttura_microstruttura
> Frequenza stimata: 60 | Varianti NBLM: struttura, microstruttura

```yaml
forma_canonica: struttura
varianti: [microstruttura]
frequenza_stimata: 60
note: ""
```

### Cluster: cedevolezza
> Frequenza stimata: 40 | Varianti NBLM: cedevole, cedevolezza

```yaml
forma_canonica: cedevole
varianti: [cedevolezza]
frequenza_stimata: 40
note: "cedevole è termine tecnico invariabile"
```

### Cluster: sabbioso_farinoso
> Frequenza stimata: 60 | Varianti NBLM: sabbioso, sabbiosità, sabbietta, farinoso, sensazione di farina, polveroso, residuo in bocca

```yaml
forma_canonica: sabbioso
varianti: [sabbiosità, sabbietta, farinoso, "sensazione di farina", polveroso, "residuo in bocca", farinosità]
frequenza_stimata: 60
note: ""
```

### Cluster: adesività
> Frequenza stimata: 52 | Varianti NBLM: adesivo, adesività, impasta, incolla la bocca, colloso

```yaml
forma_canonica: adesivo
varianti: [adesività, impasta, "incolla la bocca", colloso]
frequenza_stimata: 52
note: ""
```

### Cluster: plasticità_elasticità
> Frequenza stimata: 29 | Varianti NBLM: gommoso, elastico, plastico, indeformabile, deformabile, malleabile

```yaml
forma_canonica: plastico
varianti: [gommoso, elastico, indeformabile, deformabile]
frequenza_stimata: 29
note: "malleabile è gestito come dubbio per 'alleabile'"
```

### Cluster: astringenza
> Frequenza stimata: 28 | Varianti NBLM: astringente, allappante, ingozza, ingrossa, lega la bocca, legato, faticoso

```yaml
forma_canonica: astringente
varianti: [allappante, "lega la bocca", legato]
frequenza_stimata: 28
note: "ingozza e ingrossa sono gestiti come dubbio; faticoso come dubbio"
```

### Cluster: durezza
> Frequenza stimata: 20 | Varianti NBLM: duro, durezza

```yaml
forma_canonica: duro
varianti: [durezza]
frequenza_stimata: 20
note: ""
```

### Cluster: maturazione_insufficiente
> Frequenza stimata: 6 | Varianti NBLM: immaturo, giovane, non pronto, fresco

```yaml
forma_canonica: giovane
varianti: [immaturo, "non pronto", fresco]
frequenza_stimata: 6
note: "solo nel senso di maturazione insufficiente, non come gusto"
```

### Cluster: scarsa_coesione
> Frequenza stimata: 3 | Varianti NBLM: si spappola, si sfalda

```yaml
forma_canonica: "si sfalda"
varianti: ["si spappola"]
frequenza_stimata: 3
note: ""
```

### Cluster: percezione_lipidica
> Frequenza stimata: 3 | Varianti NBLM: burroso, unto, untuosità

```yaml
forma_canonica: burroso
varianti: [unto, untuosità]
frequenza_stimata: 3
note: ""
```

### Cluster: comparazione_formaggi
> Frequenza stimata: 11 | Varianti NBLM: nostrano, pasta stirata, struttura stirata tipo Sbrinz, emmental, asiago

```yaml
forma_canonica: nostrano
varianti: ["pasta stirata", "struttura stirata", emmental, asiago, sbrinz]
frequenza_stimata: 11
note: "nostrano e stirata sono termini tecnici invariabili"
```

## SINONIMI / ABBREVIAZIONI / TYPO

### Abbreviazione: sol. → solubile
```yaml
da: "sol."
a: solubile
tipo: abbreviazione
note: ""
```

### Abbreviazione: solub. → solubile
```yaml
da: "solub."
a: solubile
tipo: abbreviazione
note: ""
```

### Abbreviazione: cris. → cristalli
```yaml
da: "cris."
a: cristalli
tipo: abbreviazione
note: ""
```

### Abbreviazione: crist. → cristalli
```yaml
da: "crist."
a: cristalli
tipo: abbreviazione
note: ""
```

### Abbreviazione: legg. → leggermente
```yaml
da: "legg."
a: leggermente
tipo: abbreviazione
note: ""
```

### Dialetto: a gogo → molti
```yaml
da: "a gogo"
a: molti
tipo: dialetto
note: "es. 'cristalli a gogo'"
```

### Dialetto: pongo → pastoso
```yaml
da: pongo
a: pastoso
tipo: dialetto
note: "es. 'sembra di mangiare pongo'"
```

### Dialetto: scrocchiarelli → cristalli
```yaml
da: scrocchiarelli
a: cristalli
tipo: dialetto
note: "onomatopea per cristalli che scrocchiano sotto i denti"
```

### Typo: granuolo → granuloso
```yaml
da: granuolo
a: granuloso
tipo: typo
note: ""
```

### Typo: unidita → umidità
```yaml
da: unidita
a: umidità
tipo: typo
note: ""
```

### Typo: aciutto → asciutto
```yaml
da: aciutto
a: asciutto
tipo: typo
note: ""
```

### Typo: firabile → friabile
```yaml
da: firabile
a: friabile
tipo: typo
note: ""
```

### Typo: rfiabile → friabile
```yaml
da: rfiabile
a: friabile
tipo: typo
note: ""
```

### Typo: identi → i denti
```yaml
da: identi
a: "i denti"
tipo: typo
note: "errore di spaziatura: 'sotto identi'"
```

### Sinonimo: un po- → un po'
```yaml
da: "un po-"
a: "un po'"
tipo: typo
note: "trattino al posto dell'apostrofo"
```

### Sinonimo: gestire mediocre → texture mediocre
```yaml
da: "gestire mediocre"
a: "texture mediocre"
tipo: typo
note: "probabile errore speech-to-text o battitura"
```

## DUBBI — RICHIEDE DECISIONE UMANA

### DUBBIO: "alleabile"
> Contesto: Q_09, seduta 17/2019 — "Alleabile". Parola inesistente in italiano.
> Opzione A → `malleabile` (campo semantico struttura plastica, stesso panelista usa "deformabile")
> Opzione B → `allappante` (astringenza in bocca)

```yaml
scelta: ""   # A o B
option_a: malleabile
option_b: allappante
note: ""
```

### DUBBIO: "ingrossa un pochetto"
> Contesto: TG_04, campione C0M seduta 16/2020
> Opzione A → `ingozza` (difficoltà di deglutizione, stesso panelista usa sistematicamente "ingozza")
> Opzione B → `impasta` (aumento di volume in bocca)

```yaml
scelta: ""   # A o B
option_a: ingozza
option_b: impasta
note: ""
```

### DUBBIO: "gestire mediocre"
> Contesto: TG_19, seduta 8/2021 campione C0A — "Gestire mediocre"
> Opzione A → `texture mediocre` (errore speech-to-text "Texture" → "Gestire")
> Opzione B → `difficile da masticare` (la gestione del bolo)

```yaml
scelta: ""   # A o B
option_a: "texture mediocre"
option_b: "difficile da masticare"
note: ""
```

### DUBBIO: "perle"
> Contesto: TG_04, TG_14, TG_19 — "perle di tirosina" descritte come fastidiose e distinte dai cristalli
> Opzione A → normalizza in `cristalli` (accorpa al termine tecnico)
> Opzione B → mantieni `perle` come descrittore di difetto (agglomerati anomali, duri, non piacevoli)

```yaml
scelta: ""   # A o B
option_a: cristalli
option_b: perle
note: ""
```

### DUBBIO: "patatoso"
> Contesto: TG_35 e TG_24, sedute 7-8/2020
> Opzione A → `pastoso` (pasta cedevole, umida, come patata lessa schiacciata)
> Opzione B → `farinoso` (amido asciutto della patata cruda)

```yaml
scelta: ""   # A o B
option_a: pastoso
option_b: farinoso
note: ""
```

### DUBBIO: "faticoso?"
> Contesto: TG_24, seduta 20/2021 — "Leggermente poco solubile e faticoso?"
> Opzione A → `duro` (faticoso al primo morso)
> Opzione B → `astringente` (faticoso da deglutire, abbinato a scarsa solubilità)

```yaml
scelta: ""   # A o B
option_a: duro
option_b: astringente
note: ""
```

### DUBBIO: "immagiabile"
> Contesto: Q_02, seduta 9/2019 campione C0F — "Difficile da giudicare perché immagiabile"
> Opzione A → `immangiabile` (giudizio edonico negativo totale)
> Opzione B → `immasticabile` (difetto puramente meccanico)

```yaml
scelta: ""   # A o B
option_a: immangiabile
option_b: immasticabile
note: ""
```

### DUBBIO: "(1)" numero isolato nel testo
> Contesto: Q_09, seduta 21/2018 — "morbido poco granuloso no cristalli (1)"
> Opzione A → annotazione intensità (punteggio 1 = assente per cristalli)
> Opzione B → riferimento alla porzione degustata

```yaml
scelta: ""   # A o B — se A, ignorare il numero; se B, ignorare il numero
option_a: "ignora"
option_b: "ignora"
note: "in entrambi i casi il numero va rimosso dal testo normalizzato"
```

### DUBBIO: "farino"
> Contesto: TG_13, seduta 19/2018 — "asciutto, farino e poco solubile"
> Opzione A → `farinoso` (troncamento)
> Opzione B → nessuna correzione, già assegnabile al cluster sabbioso_farinoso

```yaml
scelta: ""   # A o B
option_a: farinoso
option_b: farinoso
note: "in entrambi i casi la forma canonica è farinoso"
```

## NOTE LIBERE
```yaml
note: ""
```
```

- [ ] **Step 2: Verifica formato yaml leggendo con script**

```bash
.venv/Scripts/python -c "
from src.data.compila_vocabolari import extract_blocks
from pathlib import Path
text = Path('data/interim/vocabolari_revisione_umana/Texture_revisione.md').read_text(encoding='utf-8')
blocks = extract_blocks(text)
print(f'Estratti {len(blocks)} blocchi')
clusters = [b for b in blocks if 'Cluster:' in b['header']]
print(f'  Cluster: {len(clusters)}')
dubbi = [b for b in blocks if 'DUBBIO' in b['section']]
print(f'  Dubbi: {len(dubbi)}')
"
```

Atteso output:
```
Estratti 35 blocchi
  Cluster: 19
  Dubbi: 9
```

- [ ] **Step 3: Commit**

```bash
git add data/interim/vocabolari_revisione_umana/Texture_revisione.md
git commit -m "docs: add Texture_revisione.md pre-filled review document"
```

---

## Task 6: Genera i restanti 6 documenti di revisione

**Files:**
- Create: `data/interim/vocabolari_revisione_umana/Aroma_revisione.md`
- Create: `data/interim/vocabolari_revisione_umana/Colore_della_Pasta_revisione.md`
- Create: `data/interim/vocabolari_revisione_umana/Profumo_revisione.md`
- Create: `data/interim/vocabolari_revisione_umana/Sapore_revisione.md`
- Create: `data/interim/vocabolari_revisione_umana/Spessore_della_Crosta_revisione.md`
- Create: `data/interim/vocabolari_revisione_umana/Struttura_della_Pasta_revisione.md`

Per ogni attributo, leggi il file sorgente corrispondente e crea il documento di revisione seguendo esattamente il formato di `Texture_revisione.md`.

**Regole di trasformazione da NBLM → revisione.md:**

1. **META**: usa sempre `stato: "DA_RIVEDERE"` con `note_generali: ""`
2. **TERMINI TECNICI**: copia la lista da `{Attributo}_vocabolario_TEMPLATE.json` campo `termini_tecnici_invariabili`
3. **CLUSTER**: dalla sezione `## Query 2` del file NBLM → per ogni `**Cluster: X**` crea un `### Cluster: nome_snake_case` con i campi `forma_canonica`, `varianti`, `frequenza_stimata` (stima numerica, non testo come "Alta")
4. **SINONIMI**: dalla sezione `## Query 3` → righe con tipo 1 (abbreviazioni), 2 (dialettalismi), 3 (typo) → un blocco yaml per voce con `da`, `a`, `tipo`
5. **CONVERSIONI QUANTITATIVE** (solo Spessore della Crosta): dalla sezione `## Query 3` o soglie → range mm con `pattern_regex`, `range_min_mm`, `range_max_mm`, `forma_canonica`
6. **DUBBI**: dalla sezione `## Query 4` → un blocco per ogni `**DUBBIO N:**` con `scelta: ""`, `option_a`, `option_b` dalle opzioni A/B del NBLM

**Per ogni file:**

- [ ] **Aroma**: leggi `Aroma_vocabolario_nblm.md` completo → crea `Aroma_revisione.md`
- [ ] **Colore della Pasta**: leggi `Colore_della_Pasta_vocabolario_nblm.md` completo → crea `Colore_della_Pasta_revisione.md`
- [ ] **Profumo**: leggi `Profumo_vocabolario_nblm.md` completo → crea `Profumo_revisione.md`
- [ ] **Sapore**: leggi `Sapore_vocabolario_nblm.md` completo → crea `Sapore_revisione.md`
- [ ] **Spessore della Crosta**: leggi `Spessore_della_Crosta_vocabolario_nblm.md` completo → crea `Spessore_della_Crosta_revisione.md` (includi sezione CONVERSIONI QUANTITATIVE con i range mm)
- [ ] **Struttura della Pasta**: leggi `Struttura_della_Pasta_vocabolario_nblm.md` completo → crea `Struttura_della_Pasta_revisione.md`

- [ ] **Verifica tutti e 6 con extract_blocks**

```bash
.venv/Scripts/python -c "
from src.data.compila_vocabolari import extract_blocks
from pathlib import Path
revisione_dir = Path('data/interim/vocabolari_revisione_umana')
for f in sorted(revisione_dir.glob('*_revisione.md')):
    text = f.read_text(encoding='utf-8')
    blocks = extract_blocks(text)
    clusters = len([b for b in blocks if 'Cluster:' in b['header']])
    dubbi = len([b for b in blocks if 'DUBBIO' in b['section']])
    print(f'{f.stem}: {len(blocks)} blocchi totali, {clusters} cluster, {dubbi} dubbi')
"
```

Atteso: nessun errore di parsing, ogni file produce almeno 5 blocchi.

- [ ] **Commit**

```bash
git add data/interim/vocabolari_revisione_umana/
git commit -m "docs: add pre-filled review documents for all 7 attributes"
```

---

## Task 7: Test integrazione e run finale

- [ ] **Step 1: Esegui tutti i test**

```bash
.venv/Scripts/python -m pytest tests/ -v
```

Atteso: tutti PASS.

- [ ] **Step 2: Esegui script su tutti i documenti**

```bash
.venv/Scripts/python src/data/09a_compila_vocabolari.py
```

Atteso: genera 7 JSON + `revisione_status.md`. Exit code 1 perché ci sono dubbi aperti (normale — i dubbi vanno compilati dal revisore umano).

- [ ] **Step 3: Verifica che i JSON siano validi**

```bash
.venv/Scripts/python -c "
import json
from pathlib import Path
for f in sorted(Path('data/interim/vocabolari_validati_per_attributo').glob('*.json')):
    v = json.loads(f.read_text(encoding='utf-8'))
    print(f\"{f.stem}: {len(v['cluster'])} cluster, {len(v['sinonimi_diretti'])} sinonimi, {len(v['dubbi_non_risolti'])} dubbi aperti\")
"
```

- [ ] **Step 4: Commit finale**

```bash
git add data/interim/vocabolari_validati_per_attributo/ data/interim/vocabolari_revisione_umana/revisione_status.md
git commit -m "feat: generate initial vocabulary JSONs (Fase 3 bootstrap complete)"
```
