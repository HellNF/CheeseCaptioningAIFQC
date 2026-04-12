import pytest
from src.models.metrics import compute_nlg_metrics

def test_perfect_prediction():
    refs = ["Il campione è granuloso e solubile."]
    hyps = ["Il campione è granuloso e solubile."]
    scores = compute_nlg_metrics(hypotheses=hyps, references=refs)
    assert scores["bleu"] > 0.99
    assert scores["rouge_l"] > 0.99

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
