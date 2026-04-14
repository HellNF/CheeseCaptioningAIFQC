# tests/models/test_models.py
import torch
import pytest
from src.models.models import CnnLstm, CnnTransformer, ViTTransformer, build_model

B, SEQ, VOCAB = 2, 8, 52000

@pytest.fixture(scope="module")
def dummy():
    fetta = torch.randn(B, 3, 224, 224)
    grana = torch.randn(B, 3, 224, 224)
    captions = torch.randint(0, VOCAB, (B, SEQ))
    return fetta, grana, captions

def test_cnn_lstm_forward(dummy):
    fetta, grana, caps = dummy
    model = CnnLstm(vocab_size=VOCAB)
    out = model(fetta, grana, caps)
    assert out.shape == (B, SEQ, VOCAB)

def test_cnn_transformer_forward(dummy):
    fetta, grana, caps = dummy
    model = CnnTransformer(vocab_size=VOCAB)
    out = model(fetta, grana, caps)
    assert out.shape == (B, SEQ, VOCAB)

def test_vit_transformer_forward(dummy):
    fetta, grana, caps = dummy
    model = ViTTransformer(vocab_size=VOCAB)
    out = model(fetta, grana, caps)
    assert out.shape == (B, SEQ, VOCAB)

def test_build_model_m1(dummy):
    fetta, grana, caps = dummy
    model = build_model("m1", vocab_size=VOCAB, device=torch.device("cpu"))
    out = model(fetta, grana, caps)
    assert out.shape == (B, SEQ, VOCAB)

def test_build_model_m2(dummy):
    fetta, grana, caps = dummy
    model = build_model("m2", vocab_size=VOCAB, device=torch.device("cpu"))
    out = model(fetta, grana, caps)
    assert out.shape == (B, SEQ, VOCAB)

def test_build_model_m3(dummy):
    fetta, grana, caps = dummy
    model = build_model("m3", vocab_size=VOCAB, device=torch.device("cpu"))
    out = model(fetta, grana, caps)
    assert out.shape == (B, SEQ, VOCAB)

def test_build_model_invalid():
    with pytest.raises(ValueError, match="Modello sconosciuto"):
        build_model("m99", vocab_size=VOCAB, device=torch.device("cpu"))
