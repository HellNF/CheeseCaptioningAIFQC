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

def test_parse_id_duplicato_ultimo_vince():
    response_text = (
        '{"id": 1, "classe": "OK", "caption": "prima"}\n'
        '{"id": 1, "classe": "CONFORME", "caption": "seconda"}\n'
    )
    risultati = parse_llm_response(response_text, expected_ids=[1])
    assert len(risultati) == 1
    assert risultati[0]["caption"] == "seconda"  # last wins
