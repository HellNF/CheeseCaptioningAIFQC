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
