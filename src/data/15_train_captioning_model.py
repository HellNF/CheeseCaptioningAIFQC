"""
Script per addestrare un modello di image captioning.

Uso:
  python src/data/15_train_captioning_model.py \\
      --model m1 \\
      --attributo Texture \\
      --epochs 20 \\
      --batch-size 16 \\
      --lr 1e-4 \\
      --device cuda

Modelli disponibili: m1 (CNN+LSTM), m2 (CNN+Transformer), m3 (ViT+Transformer)
"""
import argparse
import json
from pathlib import Path
import pandas as pd
import torch
from sklearn.model_selection import train_test_split

from src.models.vocabulary import ItalianTokenizer
from src.models.models import CnnLstm, CnnTransformer, ViTTransformer
from src.models.train import train_model
from src.models.metrics import compute_nlg_metrics, generate_caption
from src.models.dataset import GranaTrentinoDataset
import torchvision.transforms as T


MODEL_CLASSES = {
    "m1": CnnLstm,
    "m2": CnnTransformer,
    "m3": ViTTransformer,
}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--model",     choices=["m1", "m2", "m3"], required=True)
    parser.add_argument("--attributo", default="Texture")
    parser.add_argument("--dataset-csv", default="data/processed/dataset_captioning.csv")
    parser.add_argument("--epochs",    type=int, default=20)
    parser.add_argument("--batch-size",type=int, default=16)
    parser.add_argument("--lr",        type=float, default=1e-4)
    parser.add_argument("--device",    default="cuda")
    parser.add_argument("--max-len",   type=int, default=64)
    parser.add_argument("--image-root", default=None,
                        help="Root directory to prepend to fetta_path/grana_path (default: none)")
    args = parser.parse_args()

    print(f"Caricamento dataset: {args.dataset_csv}")
    df_full = pd.read_csv(args.dataset_csv)
    df = df_full[df_full["attributo"] == args.attributo].reset_index(drop=True)
    print(f"Righe per {args.attributo}: {len(df)}")
    if df.empty:
        valid_attrs = sorted(df_full["attributo"].dropna().unique().tolist())
        raise SystemExit(
            f"Nessuna riga trovata per attributo '{args.attributo}'.\n"
            f"Attributi disponibili: {valid_attrs}"
        )

    # prepend image root if provided
    if args.image_root:
        root = Path(args.image_root)
        df["fetta_path"] = df["fetta_path"].apply(lambda p: str(root / p))
        df["grana_path"] = df["grana_path"].apply(lambda p: str(root / p))

    # split per sample_id (nessun campione in train E val)
    sample_ids = df["sample_id"].unique().tolist()
    train_ids, val_ids = train_test_split(sample_ids, test_size=0.15, random_state=42)
    test_ids = val_ids[:len(val_ids)//2]
    val_ids  = val_ids[len(val_ids)//2:]

    train_df = df[df["sample_id"].isin(train_ids)].reset_index(drop=True)
    val_df   = df[df["sample_id"].isin(val_ids)].reset_index(drop=True)
    test_df  = df[df["sample_id"].isin(test_ids)].reset_index(drop=True)
    print(f"Train: {len(train_df)} | Val: {len(val_df)} | Test: {len(test_df)}")

    tokenizer = ItalianTokenizer()
    print(f"Vocabolario: {tokenizer.vocab_size} token")

    ModelClass = MODEL_CLASSES[args.model]
    model = ModelClass(vocab_size=tokenizer.vocab_size, frozen_encoder=True)

    checkpoint_dir = Path(f"models/{args.model}_{args.attributo}")
    history = train_model(
        model=model,
        train_df=train_df,
        val_df=val_df,
        tokenizer=tokenizer,
        epochs=args.epochs,
        batch_size=args.batch_size,
        lr=args.lr,
        device=args.device,
        checkpoint_dir=checkpoint_dir,
        max_caption_len=args.max_len,
    )

    # salva history
    with open(checkpoint_dir / "history.json", "w") as f:
        json.dump(history, f, indent=2)

    print(f"\nTraining completato. Checkpoint in: {checkpoint_dir}")
    print(f"Best val_loss: {min(history['val_loss']):.4f}")


if __name__ == "__main__":
    main()
