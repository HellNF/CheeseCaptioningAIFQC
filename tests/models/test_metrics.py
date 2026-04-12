import pytest
from src.models.metrics import compute_nlg_metrics

def test_perfect_prediction():
    refs = ["Il campione è granuloso e solubile."]
    hyps = ["Il campione è granuloso e solubile."]
    scores = compute_nlg_metrics(hypotheses=hyps, references=refs)
    assert scores["bleu"] > 0.99
    assert scores["rouge_l"] > 0.99
    assert scores["meteor"] > 0.99

def test_empty_overlap():
    refs = ["Il campione è granuloso."]
    hyps = ["Pasta molto compatta e friabile."]
    scores = compute_nlg_metrics(hypotheses=hyps, references=refs)
    assert scores["bleu"] < 0.3

def test_returns_all_metrics(tmp_path):
    refs = ["Testo di riferimento per il test."]
    hyps = ["Testo di test per riferimento."]
    scores = compute_nlg_metrics(hypotheses=hyps, references=refs)
    assert set(["bleu", "meteor", "rouge_l"]).issubset(scores.keys())

def test_generate_caption_returns_string():
    import torch
    from PIL import Image
    from src.models.models import CnnLstm
    from src.models.vocabulary import ItalianTokenizer
    from src.models.metrics import generate_caption
    from src.models.dataset import DEFAULT_TRANSFORM

    tok = ItalianTokenizer()
    model = CnnLstm(vocab_size=tok.vocab_size, embed_dim=64, hidden_dim=128, frozen_encoder=True)

    # crea immagini fittizie già trasformate
    img = Image.new("RGB", (224, 224))
    tensor = DEFAULT_TRANSFORM(img).unsqueeze(0)   # (1, 3, 224, 224)

    caption = generate_caption(
        model=model,
        fetta=tensor,
        grana=tensor,
        tokenizer=tok,
        max_len=10,
        device="cpu",
    )
    assert isinstance(caption, str)
    assert len(caption) > 0
