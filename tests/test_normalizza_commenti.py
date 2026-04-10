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
