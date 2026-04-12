import torch
import pytest
import pandas as pd
from PIL import Image
from src.models.train import train_model
from src.models.models import CnnLstm
from src.models.vocabulary import ItalianTokenizer

@pytest.fixture(scope="module")
def tok():
    return ItalianTokenizer()

def test_train_model_runs_without_error(tmp_path, tok):
    # crea 4 immagini fittizie
    for name in ["f1.bmp", "g1.bmp", "f2.bmp", "g2.bmp"]:
        Image.new("RGB", (224, 224)).save(tmp_path / name)

    df = pd.DataFrame([
        {"fetta_path": str(tmp_path / "f1.bmp"), "grana_path": str(tmp_path / "g1.bmp"),
         "attributo": "Texture", "caption": "Il campione è granuloso."},
        {"fetta_path": str(tmp_path / "f2.bmp"), "grana_path": str(tmp_path / "g2.bmp"),
         "attributo": "Texture", "caption": "Pasta compatta e solubile."},
    ])

    model = CnnLstm(vocab_size=tok.vocab_size, embed_dim=64, hidden_dim=128, frozen_encoder=True)
    history = train_model(
        model=model,
        train_df=df,
        val_df=df,
        tokenizer=tok,
        epochs=1,
        batch_size=2,
        lr=1e-3,
        device="cpu",
        checkpoint_dir=tmp_path / "checkpoints",
        max_caption_len=20,
    )
    assert "train_loss" in history
    assert len(history["train_loss"]) == 1
