# tests/models/test_train.py
import json
import csv
import torch
import pytest
from pathlib import Path
from torch.utils.data import DataLoader, TensorDataset

from src.models.models import build_model
from src.models.train import train_one_epoch, evaluate_epoch, train_model, load_checkpoint

VOCAB = 100
B, SEQ = 4, 6

def _make_loader(n=8):
    """DataLoader sintetico: batch di (fetta, grana, caption, weight)."""
    fetta = torch.randn(n, 3, 224, 224)
    grana = torch.randn(n, 3, 224, 224)
    caps = torch.randint(1, VOCAB, (n, SEQ))
    weights = torch.ones(n)
    ds = TensorDataset(fetta, grana, caps, weights)
    return DataLoader(ds, batch_size=B)

@pytest.fixture
def m1_model():
    return build_model("m1", vocab_size=VOCAB, device=torch.device("cpu"))

def test_train_one_epoch_returns_float(m1_model):
    loader = _make_loader()
    opt = torch.optim.Adam(m1_model.parameters(), lr=1e-3)
    loss = train_one_epoch(m1_model, loader, opt, pad_id=0, device=torch.device("cpu"))
    assert isinstance(loss, float)
    assert loss > 0

def test_evaluate_epoch_returns_dict(m1_model):
    loader = _make_loader()
    result = evaluate_epoch(m1_model, loader, pad_id=0, device=torch.device("cpu"))
    assert "val_loss" in result
    assert isinstance(result["val_loss"], float)

def test_checkpoint_save_load(tmp_path, m1_model):
    run_dir = tmp_path / "m1" / "Texture"
    opt = torch.optim.Adam(m1_model.parameters())
    # Salva
    from src.models.train import save_checkpoint
    save_checkpoint(m1_model, opt, epoch=3, val_loss=1.23, run_dir=run_dir, is_best=True)
    assert (run_dir / "last.pt").exists()
    assert (run_dir / "best.pt").exists()
    # Carica
    loaded_model = build_model("m1", vocab_size=VOCAB, device=torch.device("cpu"))
    loaded_opt = torch.optim.Adam(loaded_model.parameters())
    epoch, val_loss = load_checkpoint(run_dir / "last.pt", loaded_model, loaded_opt)
    assert epoch == 3
    assert abs(val_loss - 1.23) < 1e-6

def test_log_csv_written(tmp_path, m1_model):
    run_dir = tmp_path / "m1" / "Texture"
    run_dir.mkdir(parents=True)
    from src.models.train import append_log
    append_log(run_dir, epoch=1, train_loss=2.0, val_loss=1.8, bleu4=0.1, elapsed=10.0)
    append_log(run_dir, epoch=2, train_loss=1.5, val_loss=1.3, bleu4=0.2, elapsed=11.0)
    log_path = run_dir / "log.csv"
    assert log_path.exists()
    with open(log_path) as f:
        rows = list(csv.DictReader(f))
    assert len(rows) == 2
    assert rows[0]["epoch"] == "1"
    assert float(rows[1]["bleu4"]) == pytest.approx(0.2)
