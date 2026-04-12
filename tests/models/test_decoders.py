import torch
import pytest
from src.models.decoders import LSTMDecoder, TransformerDecoder

VOCAB_SIZE = 1000
EMBED_DIM = 512
B = 2
SEQ_LEN = 10

def test_lstm_decoder_output_shape():
    dec = LSTMDecoder(vocab_size=VOCAB_SIZE, embed_dim=256, hidden_dim=EMBED_DIM)
    visual_feat = torch.randn(B, EMBED_DIM)   # feature globale da CNN (M1)
    captions = torch.randint(0, VOCAB_SIZE, (B, SEQ_LEN))
    logits = dec(visual_feat, captions)
    # output: (B, SEQ_LEN, VOCAB_SIZE)
    assert logits.shape == (B, SEQ_LEN, VOCAB_SIZE)

def test_transformer_decoder_output_shape():
    dec = TransformerDecoder(vocab_size=VOCAB_SIZE, embed_dim=EMBED_DIM,
                              n_heads=8, n_layers=4, ffn_dim=2048)
    visual_tokens = torch.randn(B, 49, EMBED_DIM)   # feature spaziali da CNN (M2)
    captions = torch.randint(0, VOCAB_SIZE, (B, SEQ_LEN))
    logits = dec(visual_tokens, captions)
    # output: (B, SEQ_LEN, VOCAB_SIZE)
    assert logits.shape == (B, SEQ_LEN, VOCAB_SIZE)

def test_transformer_decoder_with_vit_tokens():
    dec = TransformerDecoder(vocab_size=VOCAB_SIZE, embed_dim=EMBED_DIM,
                              n_heads=8, n_layers=4, ffn_dim=2048)
    visual_tokens = torch.randn(B, 196, EMBED_DIM)   # patch tokens da ViT (M3)
    captions = torch.randint(0, VOCAB_SIZE, (B, SEQ_LEN))
    logits = dec(visual_tokens, captions)
    assert logits.shape == (B, SEQ_LEN, VOCAB_SIZE)
