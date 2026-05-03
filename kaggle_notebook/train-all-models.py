#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Kaggle Kernel: Train all 12 models for Grana Trentino captioning (Sapore pilot).
v8: 2x2 factorial complete (6 frozen + 6 fine-tuned), default attribute=Sapore.
"""
import json
import os
import subprocess
import sys
import shutil
import traceback
from pathlib import Path

print("=" * 70)
print("  SETUP - Grana Trentino - All Models Training")
print("=" * 70)
sys.stdout.flush()

WORK_DIR = Path("/kaggle/working")

# ---- Find dataset ----
KAGGLE_INPUT = None
inp = Path("/kaggle/input")
for d in inp.iterdir():
    if (d / "images").exists() or (d / "data").exists():
        KAGGLE_INPUT = d
        break
    if KAGGLE_INPUT is None:
        KAGGLE_INPUT = d

# Check nested structure (datasets/owner/name)
if KAGGLE_INPUT and not (KAGGLE_INPUT / "data").exists() and not (KAGGLE_INPUT / "images").exists():
    for sub in KAGGLE_INPUT.rglob("data"):
        if (sub / "processed").exists():
            KAGGLE_INPUT = sub.parent
            break

print(f"Dataset: {KAGGLE_INPUT}")
if KAGGLE_INPUT and KAGGLE_INPUT.exists():
    for item in sorted(KAGGLE_INPUT.iterdir()):
        print(f"  {'DIR ' if item.is_dir() else 'FILE'} {item.name}")
sys.stdout.flush()

# ---- Check GPU ----
print("\nGPU check...")
sys.stdout.flush()
import torch
device = "cpu"
use_gpu = False
gpu_name = "none"

if torch.cuda.is_available():
    gpu_name = torch.cuda.get_device_name(0)
    cap = torch.cuda.get_device_capability(0)
    sm = cap[0] * 10 + cap[1]
    print(f"  GPU: {gpu_name} (sm_{sm})")

    if sm >= 70:
        # T4 (sm_75), V100 (sm_70), A100 (sm_80) etc. - compatible
        try:
            t = torch.tensor([1.0], device="cuda")
            _ = t + t
            device = "cuda"
            use_gpu = True
            print(f"  CUDA test: OK - using GPU!")
        except Exception as e:
            print(f"  CUDA test FAILED: {e}")
            print(f"  Falling back to CPU")
    else:
        # P100 (sm_60) - incompatible with modern PyTorch
        print(f"  sm_{sm} < sm_70: incompatible with this PyTorch version")
        print(f"  Falling back to CPU")
else:
    print("  No GPU detected")

if not use_gpu:
    print("\n" + "!" * 70)
    print("  NO COMPATIBLE GPU - ABORTING")
    print("  Got P100 (sm_60) or no GPU. Need T4 (sm_75) or newer.")
    print("  Re-run the kernel to get a different GPU assignment.")
    print("!" * 70)
    sys.exit(1)

print(f"  Device: {device}")
sys.stdout.flush()

# ---- Clone repo ----
REPO_URL = "https://github.com/HellNF/CheeseCaptioningAIFQC.git"
BRANCH = "feature/per-attribute-captioning"
REPO_DIR = WORK_DIR / "repo"

print(f"\nCloning repo (branch: {BRANCH})...")
sys.stdout.flush()
if not REPO_DIR.exists():
    subprocess.run(
        ["git", "clone", "-b", BRANCH, "--depth", "1", REPO_URL, str(REPO_DIR)],
        check=True, timeout=120,
    )
    print("  OK")
else:
    print("  Already exists")

os.chdir(str(REPO_DIR))
sys.path.insert(0, str(REPO_DIR))
sys.stdout.flush()

# ---- Install deps ----
print("\nInstalling deps...")
sys.stdout.flush()
subprocess.run([
    sys.executable, "-m", "pip", "install", "-q",
    "transformers", "evaluate", "rouge_score", "nltk",
    "sentencepiece", "protobuf",
], check=True, timeout=300)
print("  OK")
sys.stdout.flush()

# ---- Link dataset (FORCE Kaggle CSV over repo CSV) ----
print("\nLinking dataset...")
sys.stdout.flush()

data_dir = REPO_DIR / "data" / "processed"
data_dir.mkdir(parents=True, exist_ok=True)

for fname in ["dataset_captioning.csv", "splits.json"]:
    dst = data_dir / fname
    if dst.exists() or dst.is_symlink():
        dst.unlink()
    src = None
    if KAGGLE_INPUT:
        for c in [KAGGLE_INPUT / "data" / "processed" / fname, KAGGLE_INPUT / fname]:
            if c.exists():
                src = c
                break
        if src is None:
            found = list(KAGGLE_INPUT.rglob(fname))
            if found:
                src = found[0]
    if src:
        shutil.copy2(src, dst)
        print(f"  {fname}: OK (from {src})")
    else:
        print(f"  {fname}: NOT FOUND")
sys.stdout.flush()

# Link images
img_dst = REPO_DIR / "images"
if not img_dst.exists() and KAGGLE_INPUT:
    img_src = KAGGLE_INPUT / "images"
    if not img_src.exists():
        found = list(KAGGLE_INPUT.rglob("*.jpg"))[:1]
        if found:
            img_src = found[0].parent
    if img_src and img_src.exists():
        os.symlink(img_src, img_dst)
        n = len(list(img_src.glob("*.jpg")))
        print(f"  images/: {n} JPG files")
sys.stdout.flush()

# ---- Verify ----
print("\nVerification...")
sys.stdout.flush()
import pandas as pd
from PIL import Image
df = pd.read_csv(data_dir / "dataset_captioning.csv")
sample = df["path_fetta_primaria"].dropna().iloc[0]
full = REPO_DIR / sample
print(f"  CSV: {len(df)} rows")
print(f"  Sample: {sample}")
print(f"  Exists: {full.exists()}")
if full.exists():
    img = Image.open(full)
    print(f"  Image: {img.size}")
else:
    print("  FATAL: images not accessible!")
    sys.exit(1)
sys.stdout.flush()

from src.models.vocabulary import ItalianTokenizer
tok = ItalianTokenizer()
print(f"  Tokenizer: vocab={len(tok)}")
sys.stdout.flush()

ATTRIBUTO = "Sapore"
# CHUNK: "frozen" = M1/M2/M3/M5a/M5b/M5c (6 frozen models)
#        "ft"     = M1-FT/M2-FT/M3-FT/M5a-FT/M5b-FT/M5c-FT (6 fine-tuned models)
#        "all"    = tutti i 12 (richiede >20GB storage, può fallire per disk full)
CHUNK = "m5c-only"

CHUNK_MODELS = {
    "frozen":   ["m1", "m2", "m3", "m5a", "m5b", "m5c"],
    "ft":       ["m1-ft", "m2-ft", "m3-ft", "m5a-ft", "m5b-ft", "m5c-ft"],
    "m5c-only": ["m5c"],
}

print(f"\n{'=' * 70}")
print(f"  SETUP OK")
print(f"  GPU: {gpu_name} -> device={device}")
print(f"  Attributo: {ATTRIBUTO} | Chunk: {CHUNK}")
print(f"{'=' * 70}\n")
sys.stdout.flush()

# ---- Train via kaggle_train_all.py ----
train_script = REPO_DIR / "scripts" / "kaggle_train_all.py"

cmd = [sys.executable, str(train_script), "--attributo", ATTRIBUTO, "--beam-size", "3"]
if CHUNK in CHUNK_MODELS:
    cmd.extend(["--only"] + CHUNK_MODELS[CHUNK])

print(f"Command: {' '.join(cmd)}")
sys.stdout.flush()

train_env = {**os.environ, "PYTHONUNBUFFERED": "1", "PYTHONUTF8": "1"}

result = subprocess.run(
    cmd, cwd=str(REPO_DIR),
    env=train_env,
    check=False, timeout=36000,  # 10 hours max
)
print(f"\nTraining exit code: {result.returncode}")
sys.stdout.flush()

# ---- Copy results to /kaggle/working for download ----
# /kaggle/working/ è l'output ufficiale del kernel — qui serve copiare TUTTO
# quello che vogliamo poter scaricare a fine run (csv + json + best.pt).
print("\nSaving results to /kaggle/working/results/...")
models_dir = REPO_DIR / "models"
output_dir = WORK_DIR / "results"
total_pt = 0
total_pt_mb = 0
if models_dir.exists():
    for md in models_dir.iterdir():
        if md.is_dir():
            for ad in md.iterdir():
                if ad.is_dir():
                    dst = output_dir / md.name / ad.name
                    dst.mkdir(parents=True, exist_ok=True)
                    for f in ad.iterdir():
                        if f.suffix in (".csv", ".json", ".txt"):
                            shutil.copy2(f, dst / f.name)
                            print(f"  {md.name}/{ad.name}/{f.name}")
                        elif f.name == "best.pt":
                            try:
                                shutil.copy2(f, dst / f.name)
                                size_mb = f.stat().st_size / 1024**2
                                total_pt += 1
                                total_pt_mb += size_mb
                                print(f"  {md.name}/{ad.name}/{f.name} ({size_mb:.0f} MB)")
                            except OSError as e:
                                print(f"  WARN: {f.name}: {e}")
print(f"\nCheckpoint salvati: {total_pt} (totale {total_pt_mb:.0f} MB)")

# ---- Push checkpoint come Kaggle dataset (backup permanente) ----
# Un dataset per chunk per evitare collisioni e perdite parziali
DATASET_ID = f"marcopanciera/{ATTRIBUTO.lower()}-pilot-{CHUNK.replace('_','-')}-checkpoints"
print(f"\nPush dei pesi come Kaggle dataset: {DATASET_ID}")
sys.stdout.flush()

ds_dir = WORK_DIR / "dataset_upload"
if output_dir.exists():
    if ds_dir.exists():
        shutil.rmtree(ds_dir)
    shutil.copytree(output_dir, ds_dir)

    # Metadata per Kaggle dataset
    metadata = {
        "title": f"{ATTRIBUTO} pilot checkpoints",
        "id": DATASET_ID,
        "licenses": [{"name": "CC0-1.0"}],
    }
    with open(ds_dir / "dataset-metadata.json", "w") as f:
        json.dump(metadata, f, indent=2)

    # Crea o aggiorna
    try:
        # Tenta create; se esiste, fa version
        cr = subprocess.run(
            ["kaggle", "datasets", "create", "-p", str(ds_dir), "--dir-mode", "zip"],
            capture_output=True, text=True, timeout=1800,
        )
        if cr.returncode != 0 and "already exists" in (cr.stderr + cr.stdout).lower():
            cr = subprocess.run(
                ["kaggle", "datasets", "version", "-p", str(ds_dir),
                 "-m", f"Auto-upload {ATTRIBUTO} pilot", "--dir-mode", "zip"],
                capture_output=True, text=True, timeout=1800,
            )
        print(cr.stdout[-500:] if cr.stdout else "")
        print(cr.stderr[-500:] if cr.stderr else "")
    except Exception as e:
        print(f"WARN dataset push fallito: {e}")

# Copy report (path dinamico: reports/{attributo_lower}_pilot/kaggle_training_report.md)
report_src = REPO_DIR / "reports" / f"{ATTRIBUTO.lower()}_pilot" / "kaggle_training_report.md"
if report_src.exists():
    shutil.copy2(report_src, WORK_DIR / "kaggle_training_report.md")
    print(f"\n  Report: kaggle_training_report.md (from {report_src})")
else:
    # fallback path legacy
    legacy = REPO_DIR / "reports" / "kaggle_training_report.md"
    if legacy.exists():
        shutil.copy2(legacy, WORK_DIR / "kaggle_training_report.md")
        print(f"\n  Report: kaggle_training_report.md (legacy path)")

print("\n=== DONE ===")
