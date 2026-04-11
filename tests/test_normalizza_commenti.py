# tests/test_normalizza_commenti.py
import json
import pytest
from pathlib import Path
from unittest.mock import MagicMock

from src.data.normalizza_commenti import (
    ATTRIBUTI,
    ATTRIBUTI_DESCRIZIONI,
    carica_vocabolario,
    carica_baseline,
    carica_commenti,
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


# ── carica_baseline ────────────────────────────────────────────────────────

def test_carica_baseline_ritorna_stringa(tmp_path):
    (tmp_path / "Texture_baseline.json").write_text(
        json.dumps({"attributo": "Texture", "baseline": "Testo baseline di prova."}),
        encoding="utf-8"
    )
    risultato = carica_baseline("Texture", tmp_path)
    assert risultato == "Testo baseline di prova."

def test_carica_baseline_nome_con_spazi(tmp_path):
    (tmp_path / "Struttura_della_Pasta_baseline.json").write_text(
        json.dumps({"attributo": "Struttura della Pasta", "baseline": "Baseline testo."}),
        encoding="utf-8"
    )
    risultato = carica_baseline("Struttura della Pasta", tmp_path)
    assert risultato == "Baseline testo."

def test_carica_baseline_file_mancante(tmp_path):
    with pytest.raises(FileNotFoundError):
        carica_baseline("Attributo_Inesistente", tmp_path)


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

def test_prenorm_applica_pattern_regex():
    vocab_con_regex = {
        "attributo": "Spessore della Crosta",
        "sinonimi_diretti": [],
        "conversioni_quantitative": [
            {"pattern_regex": r"\d+\s*mm", "forma_canonica": "spessore misurato", "range_min_mm": 0, "range_max_mm": 999},
        ],
        "cluster": [],
        "termini_tecnici_invariabili": [],
    }
    risultato = prenormalizza_commento("crosta di 15mm omogenea", vocab_con_regex)
    assert "spessore misurato" in risultato
    assert "15mm" not in risultato


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


# ── genera_baseline ────────────────────────────────────────────────────────

def _mock_client(content: str):
    """Helper: crea un client OpenAI mock che ritorna content."""
    client = MagicMock()
    client.chat.completions.create.return_value = MagicMock(
        choices=[MagicMock(message=MagicMock(content=content))]
    )
    return client

VOCAB_FIXTURE_WITH_TERMS = {
    **VOCAB_FIXTURE,
    "termini_tecnici_invariabili": ["compattezza", "granulosità"],
}

def test_genera_baseline_include_termini_vocabolario():
    client = _mock_client("Baseline con termini.")
    genera_baseline("Texture", VOCAB_FIXTURE_WITH_TERMS, client)
    messages = client.chat.completions.create.call_args.kwargs["messages"]
    prompt_text = str(messages)
    assert "compattezza" in prompt_text

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
    messages = client.chat.completions.create.call_args.kwargs["messages"]
    prompt_text = str(messages)
    assert "Texture" in prompt_text


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
    normalizza_batch(BATCH_FIXTURE, "Texture", VOCAB_FIXTURE_WITH_TERMS, "Baseline.", client)
    messages = client.chat.completions.create.call_args.kwargs["messages"]
    system_content = str(messages)
    assert "Texture" in system_content
    assert "Baseline." in system_content
    assert "compattezza" in system_content  # vocabulary term from VOCAB_FIXTURE_WITH_TERMS

def test_normalizza_batch_classi_corrette():
    client = _mock_client(LLM_BATCH_RESPONSE)
    risultati = normalizza_batch(
        BATCH_FIXTURE, "Texture", VOCAB_FIXTURE, "Baseline.", client
    )
    classi = {r["id"]: r["classe"] for r in risultati}
    assert classi[1] == "OK"
    assert classi[2] == "CONFORME"
    assert classi[3] == "RIFERIMENTO"


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


# ── carica_commenti ────────────────────────────────────────────────────────

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
    assert "panelista" in primo
    assert "id" in primo
    assert primo["anno"] == "2019"
    assert primo["panelista"] == "Q_02"

def test_carica_commenti_nessun_file(tmp_path):
    commenti = carica_commenti("Texture", tmp_path)
    assert commenti == []


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
    assert len(commenti) == 4  # 5 righe dati - 1 vuota = 4

    # Pre-normalizzazione
    for c in commenti:
        c["commento_prenorm"] = prenormalizza_commento(c["commento_raw"], vocab)
    assert all("commento_prenorm" in c for c in commenti)

    # Mock LLM response
    llm_response = "\n".join([
        f'{{"id": {c["id"]}, "classe": "OK", "caption": "Caption per commento {c["id"]}."}}'
        for c in commenti
    ])
    client = _mock_client(llm_response)
    baseline = "La texture risulta nella norma."

    # Normalizza batch
    batch_input = [{"id": c["id"], "commento_prenorm": c["commento_prenorm"]} for c in commenti]
    risultati = normalizza_batch(batch_input, "Texture", vocab, baseline, client)
    assert len(risultati) == 4
    assert all(r["classe"] == "OK" for r in risultati)

    # Report
    report_path = tmp_path / "report.md"
    for r, c in zip(risultati, commenti):
        r["commento_raw"] = c["commento_raw"]
    genera_report(risultati, "Texture", report_path)
    assert report_path.exists()
    content = report_path.read_text(encoding="utf-8")
    assert "Texture" in content
    assert "4" in content
