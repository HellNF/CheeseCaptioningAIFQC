import torch
import pytest
from src.models.models import CnnLstm, CnnTransformer, ViTTransformer

B, SEQ_LEN, VOCAB_SIZE = 2, 10, 1000
FETTA = torch.randn(B, 3, 224, 224)
GRANA = torch.randn(B, 3, 224, 224)
CAPTIONS = torch.randint(0, VOCAB_SIZE, (B, SEQ_LEN))


def test_cnn_lstm_forward():
    model = CnnLstm(vocab_size=VOCAB_SIZE, embed_dim=256, hidden_dim=512, frozen_encoder=True)
    logits = model(FETTA, GRANA, CAPTIONS)
    assert logits.shape == (B, SEQ_LEN, VOCAB_SIZE)


def test_cnn_transformer_forward():
    model = CnnTransformer(vocab_size=VOCAB_SIZE, embed_dim=512, frozen_encoder=True)
    logits = model(FETTA, GRANA, CAPTIONS)
    assert logits.shape == (B, SEQ_LEN, VOCAB_SIZE)


def test_vit_transformer_forward():
    model = ViTTransformer(vocab_size=VOCAB_SIZE, embed_dim=512, frozen_encoder=True)
    logits = model(FETTA, GRANA, CAPTIONS)
    assert logits.shape == (B, SEQ_LEN, VOCAB_SIZE)
