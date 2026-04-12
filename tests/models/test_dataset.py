"""Tests for build_caption_index() — TDD written before implementation."""
import pytest
import pandas as pd
from pathlib import Path

from src.models.dataset import build_caption_index


# ---------------------------------------------------------------------------
# Fixture: minimal fake data in tmp directories
# ---------------------------------------------------------------------------

@pytest.fixture()
def tmp_data(tmp_path: Path) -> dict:
    """Creates minimal fake CSVs and returns their paths."""
    # --- caption_per_attributo dir ---
    captions_dir = tmp_path / "caption_per_attributo"
    captions_dir.mkdir()

    texture_captions = pd.DataFrame(
        {
            "id": [1, 2, 3, 4],
            "classe": ["OK", "OK", "FUORI_ATTRIBUTO", "ILLEGGIBILE"],
            "caption": [
                "Granulosa e compatta.",
                "Struttura fine e omogenea.",
                None,          # FUORI_ATTRIBUTO — should be excluded
                "",            # ILLEGGIBILE — should be excluded
            ],
            "commento_raw": ["gr.", "fine", "fuori", "ill."],
            "commento_prenorm": ["gr.", "fine", "fuori", "ill."],
            "anno": [2019, 2020, 2019, 2020],
            "prodotto": ["C0A", "C0B", "C0A", "C0B"],
            "panelista": ["P1", "P2", "P3", "P4"],
            "peso": [1.0, 1.0, 1.0, 1.0],
        }
    )
    texture_captions.to_csv(captions_dir / "Texture_captions.csv", index=False)

    # --- codifica caseifici (CSV, no header) ---
    codifica_path = tmp_path / "codifica.csv"
    codifica_df = pd.DataFrame(
        {
            0: ["TN_302", "TN_304"],   # codice TN con underscore
            1: ["C0A", "C0B"],          # codice anonimato (prodotto)
            2: ["A", "B"],
        }
    )
    codifica_df.to_csv(codifica_path, index=False, header=False)

    # --- campioni_completi ---
    campioni_path = tmp_path / "campioni_completi.csv"
    campioni_df = pd.DataFrame(
        {
            "sample_id": ["TN302_2019-12-11", "TN304_2020-09-30"],
            "codice_caseificio": ["TN302", "TN304"],
            "data_seduta": ["2019-12-11", "2020-09-30"],
            "anno": [2019, 2020],
            "path_fetta_primaria": [
                "data/images/fetta_TN302_2019.bmp",
                "data/images/fetta_TN304_2020.bmp",
            ],
            "path_grana_primaria": [
                "data/images/grana_TN302_2019.bmp",
                "data/images/grana_TN304_2020.bmp",
            ],
            "n_immagini_fetta": [2, 2],
            "n_immagini_grana": [2, 2],
        }
    )
    campioni_df.to_csv(campioni_path, index=False)

    return {
        "captions_dir": captions_dir,
        "codifica_csv": codifica_path,
        "campioni_csv": campioni_path,
    }


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------

def test_build_caption_index_columns(tmp_data):
    """Output DataFrame must contain the required columns."""
    result = build_caption_index(
        captions_dir=tmp_data["captions_dir"],
        campioni_csv=tmp_data["campioni_csv"],
        codifica_csv=tmp_data["codifica_csv"],
    )
    required_cols = {"fetta_path", "grana_path", "attributo", "caption", "sample_id", "anno"}
    assert required_cols.issubset(set(result.columns)), (
        f"Missing columns: {required_cols - set(result.columns)}"
    )


def test_build_caption_index_filters_non_ok(tmp_data):
    """Rows with null or empty caption must be excluded."""
    result = build_caption_index(
        captions_dir=tmp_data["captions_dir"],
        campioni_csv=tmp_data["campioni_csv"],
        codifica_csv=tmp_data["codifica_csv"],
    )
    # Original data: rows 1,2 valid; rows 3,4 must be dropped
    assert len(result) == 2, f"Expected 2 rows, got {len(result)}"
    for cap in result["caption"]:
        assert cap and cap.strip(), f"Found empty/null caption: {cap!r}"


def test_build_caption_index_has_image_paths(tmp_data):
    """fetta_path and grana_path must not be empty."""
    result = build_caption_index(
        captions_dir=tmp_data["captions_dir"],
        campioni_csv=tmp_data["campioni_csv"],
        codifica_csv=tmp_data["codifica_csv"],
    )
    assert len(result) > 0, "Result is empty"
    for col in ("fetta_path", "grana_path"):
        assert result[col].notna().all(), f"Found NaN in {col}"
        assert (result[col] != "").all(), f"Found empty string in {col}"


def test_build_caption_index_attributo_name(tmp_data):
    """attributo column must be derived from the filename stem (before '_captions')."""
    result = build_caption_index(
        captions_dir=tmp_data["captions_dir"],
        campioni_csv=tmp_data["campioni_csv"],
        codifica_csv=tmp_data["codifica_csv"],
    )
    assert set(result["attributo"]) == {"Texture"}


def test_build_caption_index_deduplicates_date(tmp_path):
    """When multiple sedute exist for same (caseificio, anno), the first date is kept."""
    captions_dir = tmp_path / "caps"
    captions_dir.mkdir()

    caps_df = pd.DataFrame(
        {
            "id": [1],
            "classe": ["OK"],
            "caption": ["Bella struttura."],
            "commento_raw": ["bella"],
            "commento_prenorm": ["bella"],
            "anno": [2019],
            "prodotto": ["C0A"],
            "panelista": ["P1"],
            "peso": [1.0],
        }
    )
    caps_df.to_csv(captions_dir / "Texture_captions.csv", index=False)

    codifica_path = tmp_path / "codifica.csv"
    pd.DataFrame({0: ["TN_302"], 1: ["C0A"], 2: ["A"]}).to_csv(
        codifica_path, index=False, header=False
    )

    # Two sedute for same caseificio+anno
    campioni_path = tmp_path / "campioni.csv"
    pd.DataFrame(
        {
            "sample_id": ["TN302_2019-06-01", "TN302_2019-12-11"],
            "codice_caseificio": ["TN302", "TN302"],
            "data_seduta": ["2019-06-01", "2019-12-11"],
            "anno": [2019, 2019],
            "path_fetta_primaria": ["fetta_jun.bmp", "fetta_dec.bmp"],
            "path_grana_primaria": ["grana_jun.bmp", "grana_dec.bmp"],
            "n_immagini_fetta": [2, 2],
            "n_immagini_grana": [2, 2],
        }
    ).to_csv(campioni_path, index=False)

    result = build_caption_index(
        captions_dir=captions_dir,
        campioni_csv=campioni_path,
        codifica_csv=codifica_path,
    )
    assert len(result) == 1
    # The first date (earliest) should be selected
    assert result.iloc[0]["fetta_path"] == "fetta_jun.bmp"
