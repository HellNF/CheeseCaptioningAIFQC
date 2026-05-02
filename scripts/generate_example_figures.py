"""Genera figure con immagini esempio + predizioni dei top 3 modelli."""
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from PIL import Image
import pandas as pd
import textwrap
from pathlib import Path

OUT = Path('reports/figures/sapore_pilot')
OUT.mkdir(parents=True, exist_ok=True)

# Load predictions for top 3
m3ft = pd.read_csv('models/m3_vit_transformer_ft/Sapore/predictions.csv')
m5c = pd.read_csv('models/m5c_vit_gpt/Sapore/predictions.csv')
m5b = pd.read_csv('models/m5b_cnnspatial_gpt/Sapore/predictions.csv')

# Load full dataset to get image paths for test rows
df_full = pd.read_csv('data/processed/dataset_captioning.csv')
df_sapore = df_full[(df_full['attributo']=='Sapore') & (df_full['has_caption']==True) & (df_full['has_both_views']==True) & (df_full['classe'].isin(['OK','CONFORME']))]

# Get sample_ids in test split order
import json
with open('data/processed/splits.json') as f:
    splits = json.load(f)
test_ids = set(splits['test'])
df_test = df_sapore[df_sapore['sample_id'].isin(test_ids)].reset_index(drop=True)

print(f'Test rows: {len(df_test)} (expected 230)')
print(f'Predictions rows: {len(m3ft)}')

# Select 6 representative examples: 2 hits, 2 partial, 2 misses
selected_ids = [10, 75, 100,  0, 50, 200]
labels = ['Hit', 'Hit', 'Partial', 'Miss', 'Miss', 'Miss']

fig, axes = plt.subplots(2, 3, figsize=(16, 11))
axes = axes.flatten()

for i, (idx, label) in enumerate(zip(selected_ids, labels)):
    if idx >= len(df_test):
        continue
    row = df_test.iloc[idx]
    fetta_path = Path(row['path_fetta_primaria']) if pd.notna(row.get('path_fetta_primaria')) else None
    grana_path = Path(row['path_grana_primaria']) if pd.notna(row.get('path_grana_primaria')) else None

    # Load and show fetta image (or grana if fetta missing)
    img_path = fetta_path
    if img_path and not img_path.is_absolute():
        img_path = Path('.') / img_path
    if img_path and img_path.exists():
        img = Image.open(img_path).convert('RGB')
        axes[i].imshow(img)
    axes[i].axis('off')

    pred_m3ft = m3ft.caption_pred.iloc[idx]
    pred_m5c = m5c.caption_pred.iloc[idx]
    pred_m5b = m5b.caption_pred.iloc[idx]
    ref = m3ft.caption_ref.iloc[idx]

    def _wrap(s, w=58): return '\n'.join(textwrap.wrap(s, width=w))

    title = f'#{idx} - {label}\nREF: "{_wrap(ref, 60)}"'
    caption = (f'M3-FT: "{_wrap(pred_m3ft, 70)}"\n\n'
               f'M5c:   "{_wrap(pred_m5c, 70)}"\n\n'
               f'M5b:   "{_wrap(pred_m5b, 70)}"')

    axes[i].set_title(title, fontsize=9, loc='left', pad=8)
    axes[i].text(0.0, -0.04, caption, transform=axes[i].transAxes,
                 fontsize=8, va='top', family='monospace')

plt.suptitle('Sapore - Test set examples (top 3 models predictions)\nFetta view shown; both fetta+grana fed to encoder', fontsize=12, y=1.00)
plt.tight_layout()
plt.savefig(OUT / '06_examples_top3.png', dpi=110, bbox_inches='tight')
plt.close()
print(f'Saved {OUT / "06_examples_top3.png"}')

# 2x2 esempi più piccoli — 4 casi diversi
fig, axes = plt.subplots(2, 2, figsize=(13, 11))
axes = axes.flatten()
selected_ids = [10, 100, 0, 50]
labels = ['Hit (correct direction)', 'Partial (close lexicon)',
          'Miss (opposite valence)', 'Miss (different focus)']
for i, (idx, label) in enumerate(zip(selected_ids, labels)):
    row = df_test.iloc[idx]
    img_path = Path(row['path_fetta_primaria']) if pd.notna(row.get('path_fetta_primaria')) else None
    if img_path and not img_path.is_absolute():
        img_path = Path('.') / img_path
    if img_path and img_path.exists():
        img = Image.open(img_path).convert('RGB')
        axes[i].imshow(img)
    axes[i].axis('off')
    pred_m3ft = m3ft.caption_pred.iloc[idx]
    pred_m5c = m5c.caption_pred.iloc[idx]
    pred_m5b = m5b.caption_pred.iloc[idx]
    ref = m3ft.caption_ref.iloc[idx]

    def _wrap(s, w=68): return '\n'.join(textwrap.wrap(s, width=w))

    title = f'Test #{idx} - {label}\nREF (it): "{_wrap(ref)}"'
    caption = (f'M3-FT: "{_wrap(pred_m3ft)}"\n'
               f'M5c:   "{_wrap(pred_m5c)}"\n'
               f'M5b:   "{_wrap(pred_m5b)}"')
    axes[i].set_title(title, fontsize=10, loc='left', pad=6)
    axes[i].text(0.0, -0.02, caption, transform=axes[i].transAxes,
                 fontsize=8.5, va='top', family='monospace')

plt.suptitle('Sapore - 4 test examples covering hit/partial/miss spectrum', fontsize=12, y=1.0)
plt.tight_layout()
plt.savefig(OUT / '07_examples_2x2.png', dpi=110, bbox_inches='tight')
plt.close()
print(f'Saved {OUT / "07_examples_2x2.png"}')
