"""
Kaggle setup: clona il repo, collega il dataset e verifica l'ambiente.

Incolla questo in una cella Kaggle PRIMA di lanciare kaggle_train_all.py.
Prerequisiti:
  - Dataset Kaggle "grana-trentino-captioning" aggiunto al notebook
    (deve contenere le immagini BMP e data/processed/dataset_captioning.csv)
  - GPU abilitata (T4 o P100)
"""
import os
import subprocess
import sys
from pathlib import Path

# ── 1. Setup repo ────────────────────────────────────────────────────────
REPO_URL = "https://github.com/panciut/CheeseCaptioningAIFQC.git"
BRANCH = "feature/per-attribute-captioning"
WORK_DIR = Path("/kaggle/working")
REPO_DIR = WORK_DIR / "CheeseCaptioningAIFQC"

# Dataset Kaggle — adatta il nome se diverso
KAGGLE_INPUT = Path("/kaggle/input/grana-trentino-captioning")

print("=" * 60)
print("  SETUP KAGGLE — Grana Trentino Captioning")
print("=" * 60)

# Clone repo se non esiste
if not REPO_DIR.exists():
    print("\n[1/5] Clonazione repo...")
    subprocess.run(
        ["git", "clone", "-b", BRANCH, REPO_URL, str(REPO_DIR)],
        check=True,
    )
else:
    print("\n[1/5] Repo già presente, aggiornamento...")
    subprocess.run(["git", "-C", str(REPO_DIR), "pull"], check=True)

os.chdir(str(REPO_DIR))
print(f"  Working dir: {os.getcwd()}")

# ── 2. Installa dipendenze ──────────────────────────────────────────────
print("\n[2/5] Installazione dipendenze...")
subprocess.run([
    sys.executable, "-m", "pip", "install", "-q",
    "transformers", "evaluate", "rouge_score", "nltk",
    "sentencepiece", "protobuf",
], check=True)

# ── 3. Collega dati ─────────────────────────────────────────────────────
print("\n[3/5] Collegamento dataset...")

data_processed = REPO_DIR / "data" / "processed"
data_processed.mkdir(parents=True, exist_ok=True)

# Cerca il CSV nel dataset Kaggle
csv_found = False
for candidate in [
    KAGGLE_INPUT / "data" / "processed" / "dataset_captioning.csv",
    KAGGLE_INPUT / "dataset_captioning.csv",
    KAGGLE_INPUT / "processed" / "dataset_captioning.csv",
]:
    if candidate.exists():
        target = data_processed / "dataset_captioning.csv"
        if not target.exists():
            os.symlink(candidate, target)
        print(f"  CSV: {candidate}")
        csv_found = True
        break

if not csv_found:
    print("  ✗ ERRORE: dataset_captioning.csv non trovato!")
    print(f"  Contenuto di {KAGGLE_INPUT}:")
    for p in sorted(KAGGLE_INPUT.rglob("*.csv"))[:10]:
        print(f"    {p}")
    sys.exit(1)

# Collega immagini — cerca la directory con i BMP
img_link = REPO_DIR / "07_captioning risultati grana Trentino"
if not img_link.exists():
    for candidate in [
        KAGGLE_INPUT / "07_captioning risultati grana Trentino",
        KAGGLE_INPUT / "images",
        KAGGLE_INPUT,
    ]:
        if candidate.exists() and list(candidate.rglob("*.bmp"))[:1]:
            os.symlink(candidate, img_link)
            print(f"  Immagini: {candidate}")
            break
    else:
        print("  ⚠ WARN: directory immagini BMP non trovata automaticamente")
        print("  Potrebbe servire creare un symlink manuale")

# ── 4. Verifica GPU ─────────────────────────────────────────────────────
print("\n[4/5] Verifica GPU...")
try:
    import torch
    if torch.cuda.is_available():
        gpu_name = torch.cuda.get_device_name(0)
        gpu_mem = torch.cuda.get_device_properties(0).total_mem / 1e9
        print(f"  ✓ GPU: {gpu_name} ({gpu_mem:.1f} GB)")
    else:
        print("  ⚠ WARN: GPU non disponibile — il training sarà molto lento!")
except ImportError:
    print("  ✗ PyTorch non installato")

# ── 5. Verifica moduli ──────────────────────────────────────────────────
print("\n[5/5] Verifica import...")
try:
    sys.path.insert(0, str(REPO_DIR))
    from src.models.vocabulary import ItalianTokenizer
    from src.models.models import build_model
    print("  ✓ Import OK")

    tok = ItalianTokenizer()
    print(f"  ✓ Tokenizer: vocab_size={len(tok)}")
except Exception as e:
    print(f"  ✗ ERRORE import: {e}")
    sys.exit(1)

# ── Riepilogo ────────────────────────────────────────────────────────────
print("\n" + "=" * 60)
print("  ✓ SETUP COMPLETATO")
print(f"  Repo: {REPO_DIR}")
print(f"  Data: {data_processed}")
print("=" * 60)
print("\nProssimo passo — lancia il training:")
print("  !python scripts/kaggle_train_all.py")
print("\nOppure seleziona modelli specifici:")
print("  !python scripts/kaggle_train_all.py --only m1-ft m5a")
