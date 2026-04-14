# tests/models/test_metrics.py
import torch
import pytest
from torch.utils.data import DataLoader, TensorDataset
from src.models.vocabulary import ItalianTokenizer
from src.models.models import build_model
from src.models.metrics import generate_caption, quick_eval, full_eval

VOCAB_SIZE = 52000
B, SEQ = 2, 8

@pytest.fixture(scope="module")
def tok():
    return ItalianTokenizer()

@pytest.fixture(scope="module")
def tiny_model(tok):
    return build_model("m1", vocab_size=len(tok), device=torch.device("cpu"))

@pytest.fixture
def tiny_loader(tok):
    fetta = torch.randn(4, 3, 224, 224)
    grana = torch.randn(4, 3, 224, 224)
    caps = torch.randint(1, len(tok), (4, SEQ))
    weights = torch.ones(4)
    ds = TensorDataset(fetta, grana, caps, weights)
    return DataLoader(ds, batch_size=B)

def test_generate_caption_returns_string(tiny_model, tok):
    fetta = torch.randn(1, 3, 224, 224)
    grana = torch.randn(1, 3, 224, 224)
    result = generate_caption(tiny_model, fetta, grana, tok, torch.device("cpu"), max_len=20)
    assert isinstance(result, str)
    assert len(result) >= 0  # può essere vuota se il modello non è addestrato

def test_generate_caption_respects_max_len(tiny_model, tok):
    fetta = torch.randn(1, 3, 224, 224)
    grana = torch.randn(1, 3, 224, 224)
    result = generate_caption(tiny_model, fetta, grana, tok, torch.device("cpu"), max_len=5)
    ids = tok.encode(result, add_special=False)
    assert len(ids) <= 5

def test_quick_eval_returns_float(tiny_model, tok, tiny_loader):
    bleu4 = quick_eval(tiny_model, tiny_loader, tok, torch.device("cpu"))
    assert isinstance(bleu4, float)
    assert 0.0 <= bleu4 <= 1.0

def test_full_eval_returns_all_metrics(tiny_model, tok, tiny_loader, tmp_path):
    results = full_eval(
        tiny_model, tiny_loader, tok, torch.device("cpu"),
        predictions_path=tmp_path / "predictions.csv",
    )
    for key in ["bleu1", "bleu4", "meteor", "rouge_l"]:
        assert key in results, f"{key} mancante in full_eval"
        assert 0.0 <= results[key] <= 1.0

def test_full_eval_saves_predictions(tiny_model, tok, tiny_loader, tmp_path):
    pred_path = tmp_path / "predictions.csv"
    full_eval(tiny_model, tiny_loader, tok, torch.device("cpu"), predictions_path=pred_path)
    assert pred_path.exists()
    import pandas as pd
    df = pd.read_csv(pred_path)
    assert "caption_pred" in df.columns
    assert "caption_ref" in df.columns
    assert len(df) == 4  # 4 campioni nel loader
