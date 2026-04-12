from __future__ import annotations

import torch
from transformers import AutoTokenizer


class ItalianTokenizer:
    """Wrapper around the GePpeTto (GPT-2-based) tokenizer for Italian text."""

    MODEL_NAME = "LorenzoDeMattei/GePpeTto"

    def __init__(self) -> None:
        self._tokenizer = AutoTokenizer.from_pretrained(self.MODEL_NAME)

        # Ensure required special tokens exist
        special_tokens: dict[str, str] = {}
        if self._tokenizer.pad_token is None:
            special_tokens["pad_token"] = "<PAD>"
        if self._tokenizer.bos_token is None:
            special_tokens["bos_token"] = "<SOS>"
        if self._tokenizer.eos_token is None:
            special_tokens["eos_token"] = "<EOS>"

        if special_tokens:
            self._tokenizer.add_special_tokens(special_tokens)

    # ------------------------------------------------------------------
    # Properties
    # ------------------------------------------------------------------

    @property
    def vocab_size(self) -> int:
        return len(self._tokenizer)

    @property
    def pad_id(self) -> int:
        return self._tokenizer.pad_token_id

    @property
    def bos_id(self) -> int:
        return self._tokenizer.bos_token_id

    @property
    def eos_id(self) -> int:
        return self._tokenizer.eos_token_id

    # ------------------------------------------------------------------
    # Methods
    # ------------------------------------------------------------------

    def encode(self, text: str, add_special_tokens: bool = False) -> list[int]:
        """Encode *text* to a list of token ids.

        If *add_special_tokens* is True, prepend ``bos_id`` and append
        ``eos_id`` to the resulting sequence.
        """
        ids: list[int] = self._tokenizer.encode(text, add_special_tokens=False)
        if add_special_tokens:
            ids = [self.bos_id] + ids + [self.eos_id]
        return ids

    def decode(self, ids: list[int], skip_special_tokens: bool = True) -> str:
        """Decode a list of token ids back to a string."""
        return self._tokenizer.decode(ids, skip_special_tokens=skip_special_tokens)

    def batch_encode(
        self,
        texts: list[str],
        max_length: int = 64,
        padding: bool = True,
    ) -> dict[str, torch.Tensor]:
        """Batch-encode a list of texts.

        Returns a dict with ``input_ids`` and ``attention_mask`` as
        PyTorch tensors.
        """
        return self._tokenizer(
            texts,
            max_length=max_length,
            padding="max_length" if padding else False,
            truncation=True,
            return_tensors="pt",
        )
