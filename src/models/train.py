import torch
import torch.nn as nn
from torch.utils.data import DataLoader
from pathlib import Path
import pandas as pd
from tqdm import tqdm
from src.models.dataset import GranaTrentinoDataset
from src.models.vocabulary import ItalianTokenizer


def _collate_fn(batch, tokenizer: ItalianTokenizer, max_caption_len: int):
    """
    Collate function per il DataLoader.
    Tokenizza le caption e crea i tensori input/target con teacher forcing.
    """
    fettas, granas, captions = zip(*batch)
    fettas = torch.stack(fettas)
    granas = torch.stack(granas)

    # tokenizza con BOS/EOS + padding
    encoded = tokenizer.batch_encode(
        list(captions),
        max_length=max_caption_len + 1,
        padding=True,
    )
    ids = encoded["input_ids"]  # (B, max_len+1)

    # teacher forcing: input = ids[:, :-1], target = ids[:, 1:]
    caption_input = ids[:, :-1]   # (B, max_len)
    caption_target = ids[:, 1:]   # (B, max_len)

    return fettas, granas, caption_input, caption_target


def train_one_epoch(model, loader, optimizer, criterion, device):
    model.train()
    total_loss = 0.0
    for fetta, grana, cap_in, cap_tgt in loader:
        fetta, grana = fetta.to(device), grana.to(device)
        cap_in, cap_tgt = cap_in.to(device), cap_tgt.to(device)

        optimizer.zero_grad()
        logits = model(fetta, grana, cap_in)        # (B, seq_len, vocab_size)
        B, S, V = logits.shape
        loss = criterion(logits.reshape(B * S, V), cap_tgt.reshape(B * S))
        loss.backward()
        torch.nn.utils.clip_grad_norm_(model.parameters(), max_norm=1.0)
        optimizer.step()
        total_loss += loss.item()
    return total_loss / len(loader)


def evaluate_epoch(model, loader, criterion, device):
    model.eval()
    total_loss = 0.0
    with torch.no_grad():
        for fetta, grana, cap_in, cap_tgt in loader:
            fetta, grana = fetta.to(device), grana.to(device)
            cap_in, cap_tgt = cap_in.to(device), cap_tgt.to(device)
            logits = model(fetta, grana, cap_in)
            B, S, V = logits.shape
            loss = criterion(logits.reshape(B * S, V), cap_tgt.reshape(B * S))
            total_loss += loss.item()
    return total_loss / len(loader)


def train_model(
    model: nn.Module,
    train_df: pd.DataFrame,
    val_df: pd.DataFrame,
    tokenizer: ItalianTokenizer,
    epochs: int = 20,
    batch_size: int = 32,
    lr: float = 1e-4,
    device: str = "cuda",
    checkpoint_dir: Path = Path("models/checkpoints"),
    max_caption_len: int = 64,
) -> dict:
    """
    Addestra il modello e salva il checkpoint migliore (val loss).

    Restituisce dict con history: {'train_loss': [...], 'val_loss': [...]}
    """
    checkpoint_dir = Path(checkpoint_dir)
    checkpoint_dir.mkdir(parents=True, exist_ok=True)
    device = torch.device(device if torch.cuda.is_available() else "cpu")
    model = model.to(device)

    collate = lambda b: _collate_fn(b, tokenizer, max_caption_len)
    train_ds = GranaTrentinoDataset(train_df)
    val_ds = GranaTrentinoDataset(val_df)
    train_loader = DataLoader(train_ds, batch_size=batch_size, shuffle=True,
                              collate_fn=collate, num_workers=0, pin_memory=False)
    val_loader = DataLoader(val_ds, batch_size=batch_size, shuffle=False,
                            collate_fn=collate, num_workers=0, pin_memory=False)

    optimizer = torch.optim.Adam(
        filter(lambda p: p.requires_grad, model.parameters()), lr=lr
    )
    scheduler = torch.optim.lr_scheduler.ReduceLROnPlateau(optimizer, patience=3, factor=0.5)
    criterion = nn.CrossEntropyLoss(ignore_index=tokenizer.pad_id)

    history = {"train_loss": [], "val_loss": []}
    best_val_loss = float("inf")

    for epoch in range(1, epochs + 1):
        train_loss = train_one_epoch(model, train_loader, optimizer, criterion, device)
        val_loss = evaluate_epoch(model, val_loader, criterion, device)
        scheduler.step(val_loss)

        history["train_loss"].append(train_loss)
        history["val_loss"].append(val_loss)
        print(f"Epoch {epoch:03d} | train_loss={train_loss:.4f} | val_loss={val_loss:.4f}")

        if val_loss < best_val_loss:
            best_val_loss = val_loss
            torch.save(model.state_dict(), checkpoint_dir / "best_model.pt")

    return history
