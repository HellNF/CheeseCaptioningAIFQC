import torch
import torch.nn as nn
from src.models.encoders import CNNEncoderGlobal, CNNEncoderSpatial, ViTEncoder
from src.models.decoders import LSTMDecoder, TransformerDecoder


class CnnLstm(nn.Module):
    """
    M1 — CNN + LSTM (Show and Tell).
    Encoder: ResNet-50 globale (una feature per immagine).
    Fusione FETTA+GRANA: concatenazione → proiezione lineare.
    Decoder: LSTM, feature visiva come hidden state iniziale.
    """

    def __init__(
        self,
        vocab_size: int,
        embed_dim: int = 256,
        hidden_dim: int = 512,
        frozen_encoder: bool = True,
    ):
        super().__init__()
        self.encoder = CNNEncoderGlobal(embed_dim=hidden_dim, frozen=frozen_encoder)
        # fusione: concat(fetta, grana) → proiezione a hidden_dim
        self.fusion = nn.Linear(hidden_dim * 2, hidden_dim)
        self.decoder = LSTMDecoder(vocab_size=vocab_size, embed_dim=embed_dim, hidden_dim=hidden_dim)

    def forward(
        self,
        fetta: torch.Tensor,
        grana: torch.Tensor,
        captions: torch.Tensor,
    ) -> torch.Tensor:
        """
        Args:
            fetta, grana: (B, 3, 224, 224)
            captions: (B, seq_len)
        Returns:
            logits: (B, seq_len, vocab_size)
        """
        f_feat = self.encoder(fetta)                         # (B, hidden_dim)
        g_feat = self.encoder(grana)                         # (B, hidden_dim)
        visual = self.fusion(torch.cat([f_feat, g_feat], dim=1))  # (B, hidden_dim)
        return self.decoder(visual, captions)


class CnnTransformer(nn.Module):
    """
    M2 — CNN + Transformer Decoder.
    Encoder: ResNet-50 spaziale (49 visual tokens per immagine).
    Fusione FETTA+GRANA: concatenazione → 98 visual tokens.
    Decoder: Transformer con cross-attention sui 98 tokens.
    """

    def __init__(
        self,
        vocab_size: int,
        embed_dim: int = 512,
        n_heads: int = 8,
        n_layers: int = 4,
        frozen_encoder: bool = True,
    ):
        super().__init__()
        self.encoder = CNNEncoderSpatial(embed_dim=embed_dim, frozen=frozen_encoder)
        self.decoder = TransformerDecoder(
            vocab_size=vocab_size,
            embed_dim=embed_dim,
            n_heads=n_heads,
            n_layers=n_layers,
        )

    def forward(
        self,
        fetta: torch.Tensor,
        grana: torch.Tensor,
        captions: torch.Tensor,
    ) -> torch.Tensor:
        f_tokens = self.encoder(fetta)                                  # (B, 49, D)
        g_tokens = self.encoder(grana)                                  # (B, 49, D)
        visual_tokens = torch.cat([f_tokens, g_tokens], dim=1)         # (B, 98, D)
        return self.decoder(visual_tokens, captions)


class ViTTransformer(nn.Module):
    """
    M3 — ViT + Transformer Decoder (CPTR-like).
    Encoder: ViT-B/16 (196 patch tokens per immagine).
    Fusione FETTA+GRANA: concatenazione → 392 visual tokens.
    Decoder: Transformer con cross-attention sui 392 patch tokens.
    """

    def __init__(
        self,
        vocab_size: int,
        embed_dim: int = 512,
        n_heads: int = 8,
        n_layers: int = 4,
        frozen_encoder: bool = True,
        trainable_vit_layers: int = 4,
    ):
        super().__init__()
        self.encoder = ViTEncoder(
            embed_dim=embed_dim,
            frozen=frozen_encoder,
            trainable_layers=trainable_vit_layers,
        )
        self.decoder = TransformerDecoder(
            vocab_size=vocab_size,
            embed_dim=embed_dim,
            n_heads=n_heads,
            n_layers=n_layers,
        )

    def forward(
        self,
        fetta: torch.Tensor,
        grana: torch.Tensor,
        captions: torch.Tensor,
    ) -> torch.Tensor:
        f_tokens = self.encoder(fetta)                                  # (B, 196, D)
        g_tokens = self.encoder(grana)                                  # (B, 196, D)
        visual_tokens = torch.cat([f_tokens, g_tokens], dim=1)         # (B, 392, D)
        return self.decoder(visual_tokens, captions)
