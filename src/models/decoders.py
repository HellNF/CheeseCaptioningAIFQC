import math
import torch
import torch.nn as nn


class LSTMDecoder(nn.Module):
    """
    Decoder LSTM per M1 (CNN+LSTM, nessuna attention).

    L'immagine viene iniettata come hidden state iniziale dell'LSTM.
    Ad ogni step riceve l'embedding della parola precedente.
    """

    def __init__(self, vocab_size: int, embed_dim: int = 256, hidden_dim: int = 512, visual_dim: int = None):
        super().__init__()
        visual_dim = visual_dim or hidden_dim
        self.embedding = nn.Embedding(vocab_size, embed_dim)
        self.lstm = nn.LSTM(embed_dim, hidden_dim, batch_first=True)
        self.fc_out = nn.Linear(hidden_dim, vocab_size)
        # proiezione: feature visiva → hidden state iniziale LSTM
        self.visual_to_hidden = nn.Linear(visual_dim, hidden_dim)
        self.visual_to_cell = nn.Linear(visual_dim, hidden_dim)

    def forward(
        self,
        visual_feat: torch.Tensor,
        captions: torch.Tensor,
    ) -> torch.Tensor:
        """
        Args:
            visual_feat: (B, visual_dim) — vettore globale dalla CNN
            captions:    (B, seq_len) — indici parole (teacher forcing)
        Returns:
            logits: (B, seq_len, vocab_size)
        """
        h0 = self.visual_to_hidden(visual_feat).unsqueeze(0)   # (1, B, H)
        c0 = self.visual_to_cell(visual_feat).unsqueeze(0)     # (1, B, H)
        embeds = self.embedding(captions)                       # (B, seq_len, E)
        out, _ = self.lstm(embeds, (h0, c0))                   # (B, seq_len, H)
        return self.fc_out(out)                                 # (B, seq_len, V)


class TransformerDecoder(nn.Module):
    """
    Decoder Transformer per M2 (CNN+Transformer) e M3 (ViT+Transformer).

    Usa nn.TransformerDecoder di PyTorch: self-attention sulle parole +
    cross-attention sui visual tokens. Funziona con qualsiasi numero di
    visual tokens (49 per CNN spaziale, 196/392 per ViT).
    """

    def __init__(
        self,
        vocab_size: int,
        embed_dim: int = 512,
        n_heads: int = 8,
        n_layers: int = 4,
        ffn_dim: int = 2048,
        max_len: int = 128,
        dropout: float = 0.1,
    ):
        super().__init__()
        self.embed_dim = embed_dim
        self.embedding = nn.Embedding(vocab_size, embed_dim)
        self.pos_encoding = _PositionalEncoding(embed_dim, max_len, dropout)

        decoder_layer = nn.TransformerDecoderLayer(
            d_model=embed_dim,
            nhead=n_heads,
            dim_feedforward=ffn_dim,
            dropout=dropout,
            batch_first=True,
        )
        self.transformer_decoder = nn.TransformerDecoder(decoder_layer, num_layers=n_layers)
        self.fc_out = nn.Linear(embed_dim, vocab_size)

    def forward(
        self,
        visual_tokens: torch.Tensor,
        captions: torch.Tensor,
    ) -> torch.Tensor:
        """
        Args:
            visual_tokens: (B, n_visual, embed_dim) — da CNN spaziale o ViT
            captions:      (B, seq_len) — indici parole (teacher forcing)
        Returns:
            logits: (B, seq_len, vocab_size)
        """
        seq_len = captions.size(1)
        # causal mask: impedisce di vedere parole future
        causal_mask = nn.Transformer.generate_square_subsequent_mask(
            seq_len, device=captions.device
        )
        embeds = self.pos_encoding(
            self.embedding(captions) * math.sqrt(self.embed_dim)
        )  # (B, seq_len, embed_dim)

        out = self.transformer_decoder(
            tgt=embeds,
            memory=visual_tokens,
            tgt_mask=causal_mask,
        )  # (B, seq_len, embed_dim)
        return self.fc_out(out)  # (B, seq_len, vocab_size)


class _PositionalEncoding(nn.Module):
    def __init__(self, embed_dim: int, max_len: int, dropout: float):
        super().__init__()
        self.dropout = nn.Dropout(dropout)
        pe = torch.zeros(max_len, embed_dim)
        pos = torch.arange(max_len).unsqueeze(1)
        div = torch.exp(torch.arange(0, embed_dim, 2) * (-math.log(10000.0) / embed_dim))
        pe[:, 0::2] = torch.sin(pos * div)
        pe[:, 1::2] = torch.cos(pos * div)
        self.register_buffer("pe", pe.unsqueeze(0))  # (1, max_len, embed_dim)

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        x = x + self.pe[:, : x.size(1)]
        return self.dropout(x)
