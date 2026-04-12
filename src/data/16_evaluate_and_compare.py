# src/data/16_evaluate_and_compare.py
"""
Carica i tre modelli addestrati e genera il report di confronto.

Uso:
  python src/data/16_evaluate_and_compare.py --attributo Texture

Richiede che i checkpoint siano presenti in:
  models/m1_<attributo>/best_model.pt
  models/m2_<attributo>/best_model.pt
  models/m3_<attributo>/best_model.pt
"""
import argparse
import json
from pathlib import Path
import pandas as pd
import torch
from sklearn.model_selection import train_test_split
import torchvision.transforms as T
from PIL import Image

from src.models.vocabulary import ItalianTokenizer
from src.models.models import CnnLstm, CnnTransformer, ViTTransformer
from src.models.metrics import compute_nlg_metrics, generate_caption


EVAL_TRANSFORM = T.Compose([
    T.Resize((224, 224)),
    T.ToTensor(),
    T.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225]),
])

MODEL_CLASSES = {"m1": CnnLstm, "m2": CnnTransformer, "m3": ViTTransformer}


def load_model(model_key: str, attributo: str, tokenizer: ItalianTokenizer, device):
    ModelClass = MODEL_CLASSES[model_key]
    model = ModelClass(vocab_size=tokenizer.vocab_size, frozen_encoder=False)
    ckpt = Path(f"models/{model_key}_{attributo}/best_model.pt")
    model.load_state_dict(torch.load(ckpt, map_location=device, weights_only=True))
    model = model.to(device)
    model.eval()
    return model


def evaluate_model(model, test_df: pd.DataFrame, tokenizer, device) -> dict:
    hyps, refs = [], []
    for _, row in test_df.iterrows():
        fetta = EVAL_TRANSFORM(Image.open(row["fetta_path"]).convert("RGB")).unsqueeze(0)
        grana = EVAL_TRANSFORM(Image.open(row["grana_path"]).convert("RGB")).unsqueeze(0)
        caption = generate_caption(model, fetta, grana, tokenizer, device=str(device))
        hyps.append(caption)
        refs.append(str(row["caption"]))
    return compute_nlg_metrics(hypotheses=hyps, references=refs)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--attributo", default="Texture")
    parser.add_argument("--dataset-csv", default="data/processed/dataset_captioning.csv")
    parser.add_argument("--image-root", default="", help="Prefisso opzionale per i path delle immagini")
    parser.add_argument("--device", default="cpu")
    args = parser.parse_args()

    if args.device == "cuda" and not torch.cuda.is_available():
        print("CUDA non disponibile, uso CPU.")
        args.device = "cpu"
    device = torch.device(args.device)

    df_full = pd.read_csv(args.dataset_csv)
    df = df_full[df_full["attributo"] == args.attributo].reset_index(drop=True)
    if df.empty:
        valid_attrs = sorted(df_full["attributo"].dropna().unique().tolist())
        raise SystemExit(
            f"Nessuna riga trovata per attributo '{args.attributo}'.\n"
            f"Attributi disponibili: {valid_attrs}"
        )

    # applica prefisso immagini se specificato
    if args.image_root:
        root = Path(args.image_root)
        df["fetta_path"] = df["fetta_path"].apply(lambda p: str(root / p))
        df["grana_path"] = df["grana_path"].apply(lambda p: str(root / p))

    # stesso split usato durante il training
    sample_ids = df["sample_id"].unique().tolist()
    _, held_out = train_test_split(sample_ids, test_size=0.15, random_state=42)
    test_ids = held_out[:len(held_out)//2]
    test_df = df[df["sample_id"].isin(test_ids)].reset_index(drop=True)
    print(f"Campioni di test per {args.attributo}: {len(test_df)}")

    tokenizer = ItalianTokenizer()
    results = {}

    for key in ["m1", "m2", "m3"]:
        ckpt = Path(f"models/{key}_{args.attributo}/best_model.pt")
        if not ckpt.exists():
            print(f"Checkpoint non trovato per {key}, skip.")
            continue
        print(f"Valutazione {key}...")
        model = load_model(key, args.attributo, tokenizer, device)
        scores = evaluate_model(model, test_df, tokenizer, device)
        results[key] = scores
        print(f"  {key}: {scores}")

    if not results:
        raise SystemExit(
            "Nessun checkpoint trovato. "
            "Esegui prima il training con 15_train_captioning_model.py per tutti e tre i modelli."
        )

    # genera report markdown
    model_names = {"m1": "CNN+LSTM", "m2": "CNN+Transformer", "m3": "ViT+Transformer"}
    lines = [
        f"# Report Valutazione Modelli — {args.attributo}\n",
        "| Modello | BLEU | METEOR | ROUGE-L |",
        "|---|---|---|---|",
    ]
    for key, scores in results.items():
        lines.append(
            f"| {model_names[key]} | {scores['bleu']:.4f} | {scores['meteor']:.4f} | {scores['rouge_l']:.4f} |"
        )

    report = "\n".join(lines)
    out_path = Path(f"reports/training_results_{args.attributo}.md")
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(report, encoding="utf-8")
    print(f"\nReport salvato in {out_path}")
    print(report)


if __name__ == "__main__":
    main()
