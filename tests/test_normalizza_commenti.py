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


# ── ATTRIBUTI_DESCRIZIONI ──────────────────────────────────────────────────

def test_attributi_descrizioni_ha_tutti_e_sette():
    assert len(ATTRIBUTI) == 7
    for a in ATTRIBUTI:
        assert a in ATTRIBUTI_DESCRIZIONI, f"Descrizione mancante per: {a}"
        assert len(ATTRIBUTI_DESCRIZIONI[a]) > 20, f"Descrizione troppo corta per: {a}"


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
