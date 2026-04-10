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
    """Estrae il termine dal header 'DUBBIO: "termine"'."""
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
            vocab["validato_da"] = data.get("validato_da", "")

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
            scelta_raw = data.get("scelta", "")
            scelta = "" if scelta_raw is None else str(scelta_raw).strip()
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
