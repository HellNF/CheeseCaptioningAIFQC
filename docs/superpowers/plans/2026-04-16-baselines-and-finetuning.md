# Plan: Add Baseline Evaluations + Fine-tune M1/M2/M3

**Data:** 16 aprile 2026
**Status:** Codice implementato — da eseguire

## Context

We trained 4 captioning models (M1/M2/M3 from scratch, M4 BLIP fine-tuned) with modest results (BLEU-4 ~0.04-0.09). Two problems:

1. **No baselines** — we can't prove the models learned anything beyond repeating common phrases. M1 shows mode collapse, so its high BLEU-1 may be artificial.
2. **M1/M2/M3 decoders trained from scratch** with frozen encoders — unfair comparison vs M4 (fully pretrained). Fine-tuning the encoders could close the gap.

---

## Task 1: Baseline Evaluations (do first, all cheap to compute — under 15 min total)

Four baselines, each answering a different question:

### Baselines

| # | Baseline | GPU? | Time | Question it answers |
|---|----------|------|------|---------------------|
| 1 | **Random caption** | No | instant | Absolute floor — what does chance look like? |
| 2 | **Most-frequent caption** | No | instant | Is the model just memorizing the most common phrase? (critical for M1 mode collapse) |
| 3 | **Frequency-weighted sampling** | No | instant | Can you get decent scores without images, just by sampling common captions? Tests if models actually use visual info |
| 4 | **Nearest-neighbor retrieval** | Yes | ~1-2 min | Does the decoder add value, or could we just copy the caption of the most similar training image? |

### Dropped baselines (and why)

- **Zero-shot BLIP**: BLIP is pretrained on English. Our references are Italian. Zero-shot output would be English text scored against Italian references — meaningless near-zero scores. Not informative.
- **N-gram language model**: with ~600-1000 captions per attribute, bigram statistics are too sparse. Generated text would be incoherent gibberish — an unfairly weak baseline. Replaced with frequency-weighted sampling which uses complete, coherent captions.

### Step 1.1 — ✅ Create `src/models/baselines.py`

Functions:
- `random_baseline(train_df, test_df, attributo, seed=42) -> (preds, refs)`
- `most_frequent_baseline(train_df, test_df, attributo) -> (preds, refs)`
- `frequency_weighted_baseline(train_df, test_df, attributo, seed=42) -> (preds, refs)` — sample complete captions from training set weighted by their frequency (more common captions get picked more often). No images, no generation — just smarter sampling. Tests whether models use visual info or just language priors.
- `retrieval_baseline(train_df, test_df, tokenizer, device) -> (preds, refs)` — frozen ResNet-50 features, cosine similarity to find nearest train image (excluding same sample_id), copy its caption
- `compute_baseline_metrics(preds, refs, predictions_path) -> dict` — reuse the same HuggingFace `evaluate` metric computation pattern from `src/models/metrics.py:full_eval()` (BLEU-1, BLEU-4, METEOR, ROUGE-L)

Important: round-trip captions through `ItalianTokenizer.encode()` then `.decode()` to match the text normalization that model predictions go through.

For the retrieval baseline: use a frozen ResNet-50 (pretrained ImageNet) to extract a 2048-dim feature vector per image (fetta + grana concatenated, same as M1 encoder approach via `CNNEncoderGlobal` from `src/models/encoders.py`). Compute cosine similarity between test and train features. **Critical: exclude training rows with the same `sample_id` as the test row** — otherwise the baseline finds the exact same image (different panelist) and effectively measures inter-annotator agreement, not retrieval quality.

### Step 1.2 — ✅ Create `evaluate_baselines.py` (root)

CLI:
```
python evaluate_baselines.py --attributo Struttura_della_Pasta
python evaluate_baselines.py --attributo all   # all 7 attributes
python evaluate_baselines.py --attributo all --skip-gpu  # skip retrieval baseline
```

Logic:
1. Load CSV + splits.json, filter same way as `GranaTrentinoDataset` (has_caption & has_images & has_both_views, then split IDs, then attributo)
2. Run all 4 baselines per attribute (or 3 if --skip-gpu)
3. Save outputs per baseline to matching directory structure:
   - `models/baseline_random/{attributo}/metrics.json` and `predictions.csv`
   - `models/baseline_most_frequent/{attributo}/metrics.json` and `predictions.csv`
   - `models/baseline_freq_weighted/{attributo}/metrics.json` and `predictions.csv`
   - `models/baseline_retrieval/{attributo}/metrics.json` and `predictions.csv`

Directory structure matches existing convention so `compare_models.py` picks them up automatically.

### Step 1.3 — ✅ Update `reports/compare_models.py`

Add to `MODEL_DIRS` dict:
```python
"Baseline (random)": "baseline_random",
"Baseline (most-frequent)": "baseline_most_frequent",
"Baseline (freq-weighted)": "baseline_freq_weighted",
"Baseline (retrieval)": "baseline_retrieval",
```

No other changes needed — `_load_results()` already reads `metrics.json` or recomputes from `predictions.csv`.

### Files created/modified ✅
- `src/models/baselines.py` — **new** (done)
- `evaluate_baselines.py` — **new** (done)
- `reports/compare_models.py` — 4 baseline + 3 FT model entries added (done)

### ⏳ To run
```bash
# All 7 attributes, including retrieval baseline (needs GPU/CPU for ResNet-50)
python evaluate_baselines.py --attributo all

# Or attribute by attribute
python evaluate_baselines.py --attributo Struttura_della_Pasta

# Without GPU
python evaluate_baselines.py --attributo all --skip-gpu

# Update the comparison report after running
python reports/compare_models.py
```

### Critical checks (after running)
- M1/M2/M3 should beat most-frequent and freq-weighted baselines (otherwise they're not using images)
- M1/M2/M3 should beat retrieval baseline (otherwise decoder adds no value over image lookup)

---

## Task 2: Fine-tune M1/M2/M3 (unfreeze encoders)

### Step 2.1 — ✅ Add unfreezing to `src/models/encoders.py`

For all 3 encoder classes (`CNNEncoderGlobal`, `CNNEncoderSpatial`, `ViTEncoder`):
- Add `self._frozen = True` flag in `__init__`
- Add `unfreeze_encoder()` method that sets all backbone params to `requires_grad = True` and `self._frozen = False`
- In `forward()`: use `torch.no_grad()` only when `self._frozen` (currently hardcoded for M1/M2)
- For M3 (ViTEncoder): `unfreeze_encoder()` unfreezes blocks 0-7 (8-11 already unfrozen)

### Step 2.2 — ✅ Add passthrough in `src/models/models.py`

Add `unfreeze_encoder()` method to `CnnLstm`, `CnnTransformer`, `ViTTransformer` that calls `self.encoder.unfreeze_encoder()`.

### Step 2.3 — ✅ Add `--finetune` flag to `train.py`

New CLI args:
- `--finetune` — unfreeze encoder, use differential LR

Changes:
- Run directory: append `_ft` → `models/m1_cnn_lstm_ft/{attributo}/`
- Call `model.unfreeze_encoder()` before training
- All models get differential LR when fine-tuning (generalize existing M3 pattern): encoder params at `lr * 0.1`, decoder/projection at `lr`
- Fine-tuning defaults: lower LR (1e-4 for M1/M2, 5e-5 for M3), smaller batch size (16 for M1/M2, 8 for M3), cosine scheduler

### Step 2.4 — ✅ Update `reports/compare_models.py`

M1-FT, M2-FT, M3-FT entries already added together with baselines in step 1.3.

### Files modified ✅
- `src/models/encoders.py` — `_frozen` flag, `unfreeze_encoder()`, conditional `torch.no_grad()` (done)
- `src/models/models.py` — `unfreeze_encoder()` passthrough to all 3 models (done)
- `train.py` — `--finetune` flag, `DEFAULTS_FT`, `MODEL_DIR_NAMES_FT`, differential LR, encoder unfreezing, `finetune` in config.json (done)
- `reports/compare_models.py` — 3 FT entries added (done)

### ⏳ To run (start with pilot on Struttura_della_Pasta, then all attributes)
```bash
# Quick smoke test — 5 epochs to verify gradients flow
python train.py --model m1 --attributo Struttura_della_Pasta --finetune --epochs 5

# Full fine-tuning runs (best done on GPU, e.g. Kaggle)
python train.py --model m1 --attributo Struttura_della_Pasta --finetune
python train.py --model m2 --attributo Struttura_della_Pasta --finetune
python train.py --model m3 --attributo Struttura_della_Pasta --finetune

# Then update the comparison report
python reports/compare_models.py
```

### Critical checks (after running)
- Check `models/m1_cnn_lstm_ft/Struttura_della_Pasta/` is created with `best.pt`, `log.csv`
- Verify `config.json` has `"finetune": true`
- Fine-tuned models should beat their frozen counterparts, especially on METEOR

---

## Implementation order

1. ✅ Task 1 code — `src/models/baselines.py`, `evaluate_baselines.py`, `compare_models.py`
2. ✅ Task 2 code — `encoders.py`, `models.py`, `train.py`
3. ⏳ **Run baselines** — `python evaluate_baselines.py --attributo all`
4. ⏳ **Interpret baseline results** — do M1/M2/M3 beat retrieval? If yes, proceed to fine-tuning.
5. ⏳ **Run fine-tuning** (GPU recommended — Kaggle or local if CUDA available):
   - Start with M1 on Struttura_della_Pasta as smoke test
   - Then M2, M3 on same attribute
   - Then expand to all 7 attributes if results are promising
6. ⏳ **Update report** — `python reports/compare_models.py`
