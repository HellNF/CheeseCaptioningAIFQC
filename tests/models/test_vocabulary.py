import pytest
from src.models.vocabulary import ItalianTokenizer, ATTRIBUTI

@pytest.fixture(scope="module")
def tok():
    return ItalianTokenizer()

def test_special_token_ids_are_distinct(tok):
    ids = [tok.SOS_ID, tok.EOS_ID, tok.PAD_ID]
    assert len(set(ids)) == 3

def test_attr_tokens_exist(tok):
    for attr in ATTRIBUTI:
        assert f"[{attr}]" in tok.ATTR_TOKENS, f"[{attr}] mancante"

def test_encode_adds_sos_eos(tok):
    ids = tok.encode("il campione è granuloso", add_special=True)
    assert ids[0] == tok.SOS_ID
    assert ids[-1] == tok.EOS_ID

def test_encode_no_special(tok):
    ids = tok.encode("il campione è granuloso", add_special=False)
    assert ids[0] != tok.SOS_ID
    assert ids[-1] != tok.EOS_ID

def test_decode_skips_special(tok):
    ids = tok.encode("pasta compatta", add_special=True)
    text = tok.decode(ids, skip_special=True)
    assert "<SOS>" not in text
    assert "<EOS>" not in text
    assert "pasta" in text.lower()

def test_decode_roundtrip(tok):
    original = "pasta compatta e granulosa"
    ids = tok.encode(original, add_special=False)
    decoded = tok.decode(ids, skip_special=False)
    assert "pasta" in decoded.lower()
    assert "granulosa" in decoded.lower()

def test_vocab_size_is_large(tok):
    # GePpeTto uses a 30k BPE vocab (not 50k as GPT-2 English);
    # after adding 10 special tokens the total is ~30010.
    assert len(tok) > 30_000

def test_decode_strips_attr_tokens(tok):
    attr_id = tok.ATTR_TOKENS["[Sapore]"]
    ids = [tok.SOS_ID, attr_id] + tok.encode("pasta compatta", add_special=False) + [tok.EOS_ID]
    text = tok.decode(ids, skip_special=True)
    assert "[Sapore]" not in text
    assert "pasta" in text.lower()
