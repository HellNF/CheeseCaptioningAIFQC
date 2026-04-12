import torch
import pytest

B = 2
IMG = torch.randn(B, 3, 224, 224)


def test_cnn_global_output_shape():
    from src.models.encoders import CNNEncoderGlobal

    model = CNNEncoderGlobal(embed_dim=512, frozen=True)
    model.eval()
    with torch.no_grad():
        out = model(IMG)
    assert out.shape == (B, 512), f"Expected ({B}, 512), got {out.shape}"


def test_cnn_spatial_output_shape():
    from src.models.encoders import CNNEncoderSpatial

    model = CNNEncoderSpatial(embed_dim=512, frozen=True)
    model.eval()
    with torch.no_grad():
        out = model(IMG)
    assert out.shape == (B, 49, 512), f"Expected ({B}, 49, 512), got {out.shape}"


def test_vit_output_shape():
    from src.models.encoders import ViTEncoder

    model = ViTEncoder(embed_dim=512, frozen=True, trainable_layers=4)
    model.eval()
    with torch.no_grad():
        out = model(IMG)
    assert out.shape == (B, 196, 512), f"Expected ({B}, 196, 512), got {out.shape}"
