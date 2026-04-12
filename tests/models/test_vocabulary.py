import pytest
from src.models.vocabulary import ItalianTokenizer


@pytest.fixture(scope="module")
def tok():
    return ItalianTokenizer()


def test_vocab_size(tok):
    assert tok.vocab_size > 10_000


def test_encode_decode_roundtrip(tok):
    text = "La pasta ha una struttura granulosa e compatta."
    ids = tok.encode(text)
    decoded = tok.decode(ids)
    assert "granulosa" in decoded


def test_special_tokens_exist(tok):
    assert tok.pad_id is not None
    assert tok.eos_id is not None
    assert tok.bos_id is not None


def test_encode_adds_bos_eos(tok):
    text = "La crosta è sottile."
    ids = tok.encode(text, add_special_tokens=True)
    assert ids[0] == tok.bos_id
    assert ids[-1] == tok.eos_id
