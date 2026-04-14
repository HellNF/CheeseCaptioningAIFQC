import torch
import pytest
from src.models.encoders import CNNEncoderGlobal, CNNEncoderSpatial, ViTEncoder

B = 2  # batch size per test

@pytest.fixture(scope="module")
def dummy_images():
    """Coppia di immagini sintetiche 224×224 RGB."""
    fetta = torch.randn(B, 3, 224, 224)
    grana = torch.randn(B, 3, 224, 224)
    return fetta, grana

def test_cnn_global_output_shape(dummy_images):
    fetta, grana = dummy_images
    enc = CNNEncoderGlobal()
    out = enc(fetta, grana)
    assert out.shape == (B, 1, 512), f"Atteso (B,1,512), ottenuto {out.shape}"

def test_cnn_global_trainable_params(dummy_images):
    enc = CNNEncoderGlobal()
    trainable = [p for p in enc.parameters() if p.requires_grad]
    frozen = [p for p in enc.parameters() if not p.requires_grad]
    assert len(trainable) > 0
    assert len(frozen) > 0

def test_cnn_spatial_output_shape(dummy_images):
    fetta, grana = dummy_images
    enc = CNNEncoderSpatial()
    out = enc(fetta, grana)
    assert out.shape == (B, 98, 512), f"Atteso (B,98,512), ottenuto {out.shape}"

def test_vit_output_shape(dummy_images):
    fetta, grana = dummy_images
    enc = ViTEncoder()
    out = enc(fetta, grana)
    assert out.shape == (B, 392, 512), f"Atteso (B,392,512), ottenuto {out.shape}"

def test_vit_partial_freeze():
    enc = ViTEncoder()
    trainable_names = [n for n, p in enc.named_parameters() if p.requires_grad]
    assert any("blocks.11" in n for n in trainable_names)
    assert any("blocks.8" in n for n in trainable_names)

def test_encoders_d_model():
    for enc_cls in [CNNEncoderGlobal, CNNEncoderSpatial, ViTEncoder]:
        enc = enc_cls()
        assert enc.d_model == 512

def test_encoders_n_visual_tokens():
    assert CNNEncoderGlobal().n_visual_tokens == 1
    assert CNNEncoderSpatial().n_visual_tokens == 98
    assert ViTEncoder().n_visual_tokens == 392
