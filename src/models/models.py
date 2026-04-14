# src/models/models.py
from __future__ import annotations
import torch
import torch.nn as nn

from src.models.encoders import CNNEncoderGlobal, CNNEncoderSpatial, ViTEncoder
from src.models.decoders import LSTMDecoder, TransformerDecoder


class CnnLstm(nn.Module):
    """M1: CNN encoder globale + LSTM decoder."""

    def __init__(self, vocab_size: int) -> None:
        super().__init__()
        self.encoder = CNNEncoderGlobal()
        self.decoder = LSTMDecoder(vocab_size=vocab_size)

    def forward(
        self,
        fetta: torch.Tensor,
        grana: torch.Tensor,
        captions: torch.Tensor,
    ) -> torch.Tensor:
        visual = self.encoder(fetta, grana)         # (B, 1, 512)
        return self.decoder(visual, captions)        # (B, seq, vocab)


class CnnTransformer(nn.Module):
    """M2: CNN encoder spaziale + Transformer decoder."""

    def __init__(self, vocab_size: int) -> None:
        super().__init__()
        self.encoder = CNNEncoderSpatial()
        self.decoder = TransformerDecoder(vocab_size=vocab_size, n_visual_tokens=98)

    def forward(
        self,
        fetta: torch.Tensor,
        grana: torch.Tensor,
        captions: torch.Tensor,
    ) -> torch.Tensor:
        visual = self.encoder(fetta, grana)         # (B, 98, 512)
        return self.decoder(visual, captions)        # (B, seq, vocab)


class ViTTransformer(nn.Module):
    """M3: ViT encoder + Transformer decoder."""

    def __init__(self, vocab_size: int) -> None:
        super().__init__()
        self.encoder = ViTEncoder()
        self.decoder = TransformerDecoder(vocab_size=vocab_size, n_visual_tokens=392)

    def forward(
        self,
        fetta: torch.Tensor,
        grana: torch.Tensor,
        captions: torch.Tensor,
    ) -> torch.Tensor:
        visual = self.encoder(fetta, grana)         # (B, 392, 512)
        return self.decoder(visual, captions)        # (B, seq, vocab)


def build_model(
    model_name: str,
    vocab_size: int,
    device: torch.device,
) -> nn.Module:
    """Factory: crea il modello richiesto e lo sposta sul device."""
    mapping = {
        "m1": CnnLstm,
        "m2": CnnTransformer,
        "m3": ViTTransformer,
    }
    if model_name not in mapping:
        raise ValueError(f"Modello sconosciuto: {model_name!r}. Scegli tra {list(mapping)}")
    return mapping[model_name](vocab_size=vocab_size).to(device)
