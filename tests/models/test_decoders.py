# tests/models/test_decoders.py
import torch
import pytest
from src.models.decoders import LSTMDecoder, TransformerDecoder

B, SEQ, VOCAB = 2, 10, 52000

@pytest.fixture
def lstm_dec():
    return LSTMDecoder(vocab_size=VOCAB)

@pytest.fixture
def transformer_dec():
    return TransformerDecoder(vocab_size=VOCAB, n_visual_tokens=98)

def test_lstm_output_shape(lstm_dec):
    visual = torch.randn(B, 1, 512)
    captions = torch.randint(0, VOCAB, (B, SEQ))
    out = lstm_dec(visual, captions)
    assert out.shape == (B, SEQ, VOCAB)

def test_transformer_output_shape(transformer_dec):
    visual = torch.randn(B, 98, 512)
    captions = torch.randint(0, VOCAB, (B, SEQ))
    out = transformer_dec(visual, captions)
    assert out.shape == (B, SEQ, VOCAB)

def test_transformer_with_vit_tokens():
    dec = TransformerDecoder(vocab_size=VOCAB, n_visual_tokens=392)
    visual = torch.randn(B, 392, 512)
    captions = torch.randint(0, VOCAB, (B, SEQ))
    out = dec(visual, captions)
    assert out.shape == (B, SEQ, VOCAB)

def test_lstm_causal_property(lstm_dec):
    """Output al passo t non dipende dai token oltre t (LSTM è già causale)."""
    lstm_dec.eval()
    visual = torch.randn(1, 1, 512)
    cap1 = torch.randint(0, VOCAB, (1, SEQ))
    cap2 = cap1.clone()
    cap2[0, SEQ // 2:] = 0  # modifica la seconda metà
    with torch.no_grad():
        out1 = lstm_dec(visual, cap1)
        out2 = lstm_dec(visual, cap2)
    # Le prime SEQ//2 posizioni devono essere identiche
    assert torch.allclose(out1[0, : SEQ // 2], out2[0, : SEQ // 2], atol=1e-5)

def test_transformer_causal_mask(transformer_dec):
    """Il Transformer usa causal mask: output a posizione t non vede token t+1."""
    transformer_dec.eval()
    visual = torch.randn(1, 98, 512)
    cap1 = torch.randint(0, VOCAB, (1, SEQ))
    cap2 = cap1.clone()
    cap2[0, SEQ // 2:] = 0
    with torch.no_grad():
        out1 = transformer_dec(visual, cap1)
        out2 = transformer_dec(visual, cap2)
    assert torch.allclose(out1[0, : SEQ // 2], out2[0, : SEQ // 2], atol=1e-5)
