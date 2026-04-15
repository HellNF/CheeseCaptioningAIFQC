"""
CLI per training dei modelli encoder-decoder Grana Trentino.

Esempi:
  python train.py --model m1 --attributo Texture
  python train.py --model m2 --attributo all --epochs 50
  python train.py --model m1 --attributo Texture --resume
  python train.py --model m1 --attributo Texture --eval-only
"""
from __future__ import annotations
import argparse
import json
import sys
from pathlib import Path

import sys as _sys

import torch
from torch.nn.utils.rnn import pad_sequence
from torch.utils.data import DataLoader

# num_workers > 0 richiede funzioni picklable; su Windows (spawn) le closure locali
# non funzionano, quindi usiamo 0 worker e lasciamo al DataLoader il caricamento nel processo principale.
_NUM_WORKERS = 0 if _sys.platform == "win32" else 2

PROJECT_ROOT = Path(__file__).parent

sys.path.insert(0, str(PROJECT_ROOT))

from src.models.vocabulary import ItalianTokenizer
from src.models.dataset import GranaTrentinoDataset, build_splits
from src.models.models import build_model
from src.models.train import train_model
from src.models.metrics import full_eval

DATASET_CSV = PROJECT_ROOT / "data" / "processed" / "dataset_captioning.csv"
SPLITS_JSON = PROJECT_ROOT / "data" / "processed" / "splits.json"
MODELS_DIR = PROJECT_ROOT / "models"

DEFAULTS = {
    "m1": dict(epochs=50, batch_size=32, lr=3e-4, patience=7, scheduler="steplr"),
    "m2": dict(epochs=50, batch_size=32, lr=3e-4, patience=7, scheduler="steplr"),
    "m3": dict(epochs=30, batch_size=16, lr=1e-4, patience=5, scheduler="cosine"),
}
MODEL_DIR_NAMES = {"m1": "m1_cnn_lstm", "m2": "m2_cnn_transformer", "m3": "m3_vit_transformer"}


def parse_args():
    p = argparse.ArgumentParser(description="Training image captioning Grana Trentino")
    p.add_argument("--model", required=True, choices=["m1", "m2", "m3"])
    p.add_argument("--attributo", required=True,
                   help="Nome attributo (es. Texture) o 'all' per modello globale")
    p.add_argument("--epochs", type=int, default=None)
    p.add_argument("--batch-size", type=int, default=None)
    p.add_argument("--lr", type=float, default=None)
    p.add_argument("--beam-size", type=int, default=3)
    p.add_argument("--seed", type=int, default=42)
    p.add_argument("--resume", action="store_true")
    p.add_argument("--include-fetta-only", action="store_true")
    p.add_argument("--eval-only", action="store_true")
    return p.parse_args()


class _CollateFn:
    """Collate picklable (compatibile con multiprocessing spawn su Windows)."""

    def __init__(self, pad_id: int) -> None:
        self.pad_id = pad_id

    def __call__(self, batch):
        fette = torch.stack([b["fetta"] for b in batch])
        grana = torch.stack([b["grana"] for b in batch])
        caps = pad_sequence(
            [b["caption"] for b in batch], batch_first=True,
            padding_value=self.pad_id,
        )
        weights = torch.tensor([b["weight"] for b in batch], dtype=torch.float)
        return fette, grana, caps, weights


def make_loader(
    split: str,
    tokenizer: ItalianTokenizer,
    attributo: str | None,
    batch_size: int,
    require_both_views: bool,
) -> DataLoader:
    ds = GranaTrentinoDataset(
        csv_path=DATASET_CSV,
        tokenizer=tokenizer,
        splits_path=SPLITS_JSON,
        attributo=attributo,
        split=split,
        require_both_views=require_both_views,
    )
    return DataLoader(
        ds, batch_size=batch_size, shuffle=(split == "train"),
        collate_fn=_CollateFn(tokenizer.PAD_ID),
        num_workers=_NUM_WORKERS, pin_memory=True,
    )


def main():
    args = parse_args()
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    print(f"Device: {device}")

    # Genera splits se non esiste
    if not SPLITS_JSON.exists():
        print("Generazione splits.json...")
        build_splits(DATASET_CSV, seed=args.seed, out_path=SPLITS_JSON)

    # Risolvi attributo
    attributo = None if args.attributo == "all" else args.attributo
    attr_dir = "global" if attributo is None else attributo

    # Iperparametri
    defaults = DEFAULTS[args.model]
    epochs = args.epochs or defaults["epochs"]
    batch_size = args.batch_size or defaults["batch_size"]
    lr = args.lr or defaults["lr"]

    # Run directory
    run_dir = MODELS_DIR / MODEL_DIR_NAMES[args.model] / attr_dir

    # Tokenizer
    print("Caricamento tokenizer...")
    tokenizer = ItalianTokenizer()

    # Modello
    if args.eval_only:
        best_pt = run_dir / "best.pt"
        if not best_pt.exists():
            print(f"ERRORE: {best_pt} non trovato. Esegui prima il training.")
            sys.exit(1)

    print(f"Costruzione modello {args.model.upper()}...")
    model = build_model(args.model, vocab_size=len(tokenizer), device=device)

    if args.eval_only:
        state = torch.load(run_dir / "best.pt", map_location="cpu", weights_only=True)
        model.load_state_dict(state["model_state"])
        model.to(device)
        print("Valutazione su test set...")
        test_loader = make_loader("test", tokenizer, attributo, batch_size,
                                  require_both_views=not args.include_fetta_only)
        results = full_eval(model, test_loader, tokenizer, device,
                            predictions_path=run_dir / "predictions.csv",
                            beam_size=args.beam_size)
        print("Test set results:")
        for k, v in results.items():
            print(f"  {k}: {v:.4f}")
        return

    # Controlla sovrascrittura
    if (run_dir / "best.pt").exists() and not args.resume:
        answer = input(f"Esiste già un training in {run_dir}. Sovrascrivere? [s/N] ")
        if answer.lower() not in ("s", "si", "y", "yes"):
            print("Annullato.")
            sys.exit(0)

    # Loaders
    require_both = not args.include_fetta_only
    train_loader = make_loader("train", tokenizer, attributo, batch_size, require_both)
    val_loader = make_loader("val", tokenizer, attributo, batch_size, require_both)
    print(f"Train: {len(train_loader.dataset)} campioni | Val: {len(val_loader.dataset)} campioni")

    # Optimizer e scheduler
    if args.model == "m3":
        vit_params = [p for n, p in model.named_parameters()
                      if p.requires_grad and "encoder.vit" in n]
        other_params = [p for n, p in model.named_parameters()
                        if p.requires_grad and "encoder.vit" not in n]
        optimizer = torch.optim.AdamW([
            {"params": vit_params, "lr": lr * 0.1},
            {"params": other_params, "lr": lr},
        ])
        scheduler = torch.optim.lr_scheduler.CosineAnnealingLR(optimizer, T_max=epochs)
    else:
        optimizer = torch.optim.Adam(model.parameters(), lr=lr)
        scheduler = torch.optim.lr_scheduler.StepLR(optimizer, step_size=10, gamma=0.5)

    config = dict(
        model=args.model, attributo=attr_dir, epochs=epochs,
        batch_size=batch_size, lr=lr, seed=args.seed,
        beam_size=args.beam_size, early_stopping_patience=defaults["patience"],
        include_fetta_only=args.include_fetta_only,
    )

    # Training
    train_model(
        model=model,
        train_loader=train_loader,
        val_loader=val_loader,
        optimizer=optimizer,
        scheduler=scheduler,
        tokenizer=tokenizer,
        device=device,
        run_dir=run_dir,
        config=config,
        resume=args.resume,
    )

    # Valutazione finale su test set
    print("\nValutazione finale su test set con best.pt...")
    from src.models.train import load_checkpoint
    load_checkpoint(run_dir / "best.pt", model, optimizer)
    test_loader = make_loader("test", tokenizer, attributo, batch_size, require_both)
    results = full_eval(model, test_loader, tokenizer, device,
                        predictions_path=run_dir / "predictions.csv",
                        beam_size=args.beam_size)
    print("Test set results:")
    for k, v in results.items():
        print(f"  {k}: {v:.4f}")


if __name__ == "__main__":
    main()
