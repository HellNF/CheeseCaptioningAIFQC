# src/models/decoders.py
from __future__ import annotations
import math
import torch
import torch.nn as nn


class LSTMDecoder(nn.Module):
    """LSTM decoder con input visivo come h0. Output: (B, seq_len, vocab_size)."""

    def __init__(
        self,
        vocab_size: int,
        embed_dim: int = 256,
        hidden_size: int = 512,
        pad_id: int = 0,
    ) -> None:
        super().__init__()
        self.embed = nn.Embedding(vocab_size, embed_dim, padding_idx=pad_id)
        self.lstm = nn.LSTM(embed_dim, hidden_size, batch_first=True)
        self.fc = nn.Linear(hidden_size, vocab_size)
        self.hidden_size = hidden_size

    def forward(
        self,
        visual_tokens: torch.Tensor,   # (B, 1, 512)
        captions: torch.Tensor,        # (B, seq_len)
    ) -> torch.Tensor:                 # (B, seq_len, vocab_size)
        # visual_tokens: (B,1,512) → h0/c0: (1,B,512)
        if visual_tokens.size(-1) != self.hidden_size:
            raise ValueError(
                f"visual_tokens last dim {visual_tokens.size(-1)} != hidden_size {self.hidden_size}"
            )
        h0 = visual_tokens.squeeze(1).unsqueeze(0)  # (1, B, 512)
        c0 = torch.zeros_like(h0)
        emb = self.embed(captions)                   # (B, seq_len, embed_dim)
        out, _ = self.lstm(emb, (h0, c0))            # (B, seq_len, hidden_size)
        return self.fc(out)                           # (B, seq_len, vocab_size)


class _SinusoidalPE(nn.Module):
    """Positional encoding sinusoidale."""

    def __init__(self, d_model: int, max_len: int = 512) -> None:
        super().__init__()
        assert d_model % 2 == 0, f"d_model deve essere pari, ricevuto {d_model}"
        pe = torch.zeros(max_len, d_model)
        pos = torch.arange(max_len).unsqueeze(1).float()
        div = torch.exp(torch.arange(0, d_model, 2).float() * (-math.log(10000.0) / d_model))
        pe[:, 0::2] = torch.sin(pos * div)
        pe[:, 1::2] = torch.cos(pos * div)
        self.register_buffer("pe", pe.unsqueeze(0))  # (1, max_len, d_model)

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        return x + self.pe[:, : x.size(1)]


class TransformerDecoder(nn.Module):
    """Transformer decoder con cross-attention sui visual token.
    Output: (B, seq_len, vocab_size).
    """

    def __init__(
        self,
        vocab_size: int,
        n_visual_tokens: int,
        d_model: int = 512,
        n_heads: int = 8,
        n_layers: int = 4,
        ffn_dim: int = 2048,
        pad_id: int = 0,
        dropout: float = 0.1,
    ) -> None:
        super().__init__()
        self.embed = nn.Embedding(vocab_size, d_model, padding_idx=pad_id)
        self.pe = _SinusoidalPE(d_model)
        decoder_layer = nn.TransformerDecoderLayer(
            d_model=d_model,
            nhead=n_heads,
            dim_feedforward=ffn_dim,
            dropout=dropout,
            batch_first=True,
        )
        self.transformer = nn.TransformerDecoder(decoder_layer, num_layers=n_layers)
        self.fc = nn.Linear(d_model, vocab_size)
        self.d_model = d_model

    @staticmethod
    def _causal_mask(seq_len: int, device: torch.device) -> torch.Tensor:
        """Maschera causale (upper-triangular = -inf)."""
        mask = torch.triu(torch.ones(seq_len, seq_len, device=device), diagonal=1)
        return mask.masked_fill(mask.bool(), float("-inf"))

    def forward(
        self,
        visual_tokens: torch.Tensor,   # (B, n_visual_tokens, 512)
        captions: torch.Tensor,        # (B, seq_len)
    ) -> torch.Tensor:                 # (B, seq_len, vocab_size)
        seq_len = captions.size(1)
        tgt_mask = self._causal_mask(seq_len, captions.device)
        emb = self.pe(self.embed(captions))   # (B, seq_len, d_model)
        out = self.transformer(
            tgt=emb,
            memory=visual_tokens,
            tgt_mask=tgt_mask,
        )                                     # (B, seq_len, d_model)
        return self.fc(out)                   # (B, seq_len, vocab_size)
