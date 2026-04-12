"""
Metriche NLG per valutare le caption generate.
Usa la libreria `evaluate` di HuggingFace (più stabile su Windows di pycocoevalcap).

Metriche calcolate:
  - BLEU (corpus-level, sacrebleu)
  - METEOR
  - ROUGE-L
"""
import evaluate as hf_evaluate
import torch

# lazy loading per evitare download al import
_BLEU = None
_METEOR = None
_ROUGE = None


def _get_metrics():
    global _BLEU, _METEOR, _ROUGE
    if _BLEU is None:
        _BLEU   = hf_evaluate.load("sacrebleu")
        _METEOR = hf_evaluate.load("meteor")
        _ROUGE  = hf_evaluate.load("rouge")
    return _BLEU, _METEOR, _ROUGE


def compute_nlg_metrics(
    hypotheses: list[str],
    references: list[str],
) -> dict[str, float]:
    """
    Calcola BLEU, METEOR e ROUGE-L tra ipotesi e riferimenti.

    Args:
        hypotheses: lista di caption generate dal modello
        references:  lista di caption di riferimento (ground truth)
    Returns:
        dict con chiavi 'bleu', 'meteor', 'rouge_l'
    """
    bleu_m, meteor_m, rouge_m = _get_metrics()

    # sacrebleu vuole references come lista di liste
    bleu_score = bleu_m.compute(
        predictions=hypotheses,
        references=[[r] for r in references],
    )["score"] / 100.0  # normalizza da 0-100 a 0-1

    meteor_score = meteor_m.compute(
        predictions=hypotheses,
        references=references,
    )["meteor"]

    rouge_score = rouge_m.compute(
        predictions=hypotheses,
        references=references,
    )["rougeL"]

    return {
        "bleu":    round(bleu_score, 4),
        "meteor":  round(meteor_score, 4),
        "rouge_l": round(rouge_score, 4),
    }


def generate_caption(
    model,
    fetta: torch.Tensor,
    grana: torch.Tensor,
    tokenizer,
    max_len: int = 64,
    device: str = "cpu",
) -> str:
    """
    Genera una caption per una coppia di immagini usando greedy decoding.

    Args:
        model: CnnLstm / CnnTransformer / ViTTransformer
        fetta, grana: tensori (1, 3, 224, 224) già normalizzati
        tokenizer: ItalianTokenizer
        max_len: lunghezza massima caption generata
        device: 'cpu' o 'cuda'
    Returns:
        stringa caption generata (può essere troncata a max_len token se EOS non viene predetto)
    """
    model.eval()
    device = torch.device(device)
    model = model.to(device)
    fetta = fetta.to(device)
    grana = grana.to(device)

    generated = [tokenizer.bos_id]

    with torch.no_grad():
        for _ in range(max_len):
            cap_tensor = torch.tensor([generated], device=device)   # (1, t)
            logits = model(fetta, grana, cap_tensor)                 # (1, t, V)
            next_id = logits[0, -1].argmax().item()
            generated.append(next_id)
            if next_id == tokenizer.eos_id:
                break

    return tokenizer.decode(generated[1:])  # escludi BOS
