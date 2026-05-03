"""Genera grafici per il report finale."""
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import json
from pathlib import Path

OUT = Path('reports/figures/sapore_pilot')
OUT.mkdir(parents=True, exist_ok=True)

# === PLOT 1: Matrice 2x2 ===
fig, axes = plt.subplots(1, 2, figsize=(11, 4.5))

sapore_means = {
    'frozen+scratch': 0.0913,
    'frozen+GePpeTto': 0.1008,
    'ft+scratch': 0.1045,
    'ft+GePpeTto': 0.0969,
}
struttura_means = {
    'frozen+scratch': 0.0441,
    'frozen+GePpeTto': 0.0475,
    'ft+scratch': 0.0418,
    'ft+GePpeTto': 0.0427,
}

cells = list(sapore_means.keys())
x = np.arange(len(cells))
w = 0.36

axes[0].bar(x - w/2, [struttura_means[c] for c in cells], w, label='Struttura (47% noise)', color='#cc6677')
axes[0].bar(x + w/2, [sapore_means[c] for c in cells], w, label='Sapore (0.6% noise)', color='#117733')
axes[0].set_xticks(x)
axes[0].set_xticklabels(cells, rotation=15, ha='right')
axes[0].set_ylabel('Mean BLEU-4 (n=3 per cell)')
axes[0].set_title('2x2 cell means: Struttura vs Sapore')
axes[0].legend()
axes[0].grid(axis='y', alpha=0.3)
for i, c in enumerate(cells):
    axes[0].text(i - w/2, struttura_means[c]+0.002, f'{struttura_means[c]:.3f}', ha='center', fontsize=8)
    axes[0].text(i + w/2, sapore_means[c]+0.002, f'{sapore_means[c]:.3f}', ha='center', fontsize=8)

sapore_matrix = np.array([[0.0913, 0.1008], [0.1045, 0.0969]])
im = axes[1].imshow(sapore_matrix, cmap='YlGn', vmin=0.085, vmax=0.110)
axes[1].set_xticks([0, 1])
axes[1].set_yticks([0, 1])
axes[1].set_xticklabels(['Decoder scratch', 'Decoder GePpeTto'])
axes[1].set_yticklabels(['Encoder frozen', 'Encoder fine-tuned'])
axes[1].set_title('Sapore - 2x2 BLEU-4 (winner: ft x scratch)')
for i in range(2):
    for j in range(2):
        axes[1].text(j, i, f'{sapore_matrix[i,j]:.3f}', ha='center', va='center',
                     color='black', fontsize=12, fontweight='bold')
plt.colorbar(im, ax=axes[1], label='BLEU-4', fraction=0.04)

plt.tight_layout()
plt.savefig(OUT / '01_matrice_2x2.png', dpi=120, bbox_inches='tight')
plt.close()
print(f'Saved {OUT / "01_matrice_2x2.png"}')

# === PLOT 2: BLEU-4 vs METEOR ===
sapore_data = {
    'M1': (0.0921, 0.2888, 'frozen-scratch'),
    'M2': (0.0839, 0.2841, 'frozen-scratch'),
    'M3': (0.0980, 0.3073, 'frozen-scratch'),
    'M5a': (0.0903, 0.2744, 'frozen-geppetto'),
    'M5b': (0.1004, 0.2923, 'frozen-geppetto'),
    'M5c': (0.1118, 0.3196, 'frozen-geppetto'),
    'M1-FT': (0.0980, 0.2836, 'ft-scratch'),
    'M2-FT': (0.0983, 0.2976, 'ft-scratch'),
    'M3-FT': (0.1172, 0.3050, 'ft-scratch'),
    'M5a-FT': (0.0924, 0.2960, 'ft-geppetto'),
    'M5b-FT': (0.1001, 0.2945, 'ft-geppetto'),
    'M5c-FT': (0.0981, 0.2945, 'ft-geppetto'),
}
colors = {'frozen-scratch': '#332288', 'frozen-geppetto': '#88ccee',
          'ft-scratch': '#cc6677', 'ft-geppetto': '#ddcc77'}
fig, ax = plt.subplots(figsize=(9, 6))
for name, (b, m, cell) in sapore_data.items():
    ax.scatter(b, m, c=colors[cell], s=110, edgecolor='black', linewidth=0.6, zorder=3)
    offset = (0.0015, 0.001)
    if name == 'M1-FT': offset = (0.0015, -0.003)
    if name == 'M3-FT': offset = (0.0015, -0.003)
    if name == 'M5a': offset = (-0.005, -0.005)
    ax.annotate(name, (b+offset[0], m+offset[1]), fontsize=9)

ax.scatter(0.1172, 0.3050, c='none', edgecolor='red', linewidth=2.5, s=210, zorder=2, label='Top BLEU-4 (M3-FT)')
ax.scatter(0.1118, 0.3196, c='none', edgecolor='gold', linewidth=2.5, s=210, zorder=2, label='Top METEOR (M5c)')

import matplotlib.patches as mpatches
patches = [mpatches.Patch(color=v, label=k) for k,v in colors.items()]
ax.legend(handles=patches + [
    plt.Line2D([], [], color='red', marker='o', markerfacecolor='none', markersize=12, linewidth=0, label='Top BLEU-4'),
    plt.Line2D([], [], color='gold', marker='o', markerfacecolor='none', markersize=12, linewidth=0, label='Top METEOR'),
], loc='lower right', fontsize=9)
ax.set_xlabel('BLEU-4 (test set)')
ax.set_ylabel('METEOR (test set)')
ax.set_title('Sapore - 12 models trade-off: BLEU-4 vs METEOR')
ax.grid(alpha=0.3)
plt.tight_layout()
plt.savefig(OUT / '02_bleu_vs_meteor.png', dpi=120, bbox_inches='tight')
plt.close()
print(f'Saved {OUT / "02_bleu_vs_meteor.png"}')

# === PLOT 3: Loss curves ===
top_models = {
    'M3-FT': 'models/m3_vit_transformer_ft/Sapore/log.csv',
    'M5c': 'models/m5c_vit_gpt/Sapore/log.csv',
    'M5b': 'models/m5b_cnnspatial_gpt/Sapore/log.csv',
    'M3': 'models/m3_vit_transformer/Sapore/log.csv',
    'M1': 'models/m1_cnn_lstm/Sapore/log.csv',
}
fig, axes = plt.subplots(1, 2, figsize=(13, 4.5))
for name, path in top_models.items():
    df = pd.read_csv(path)
    axes[0].plot(df.epoch, df.train_loss, label=name, linewidth=1.5)
    axes[1].plot(df.epoch, df.val_loss, label=name, linewidth=1.5)
axes[0].set_xlabel('Epoch'); axes[0].set_ylabel('Train loss')
axes[0].set_title('Sapore - Train loss (top 5 models)')
axes[0].legend(); axes[0].grid(alpha=0.3)
axes[1].set_xlabel('Epoch'); axes[1].set_ylabel('Val loss')
axes[1].set_title('Sapore - Val loss (top 5 models)')
axes[1].legend(); axes[1].grid(alpha=0.3)
plt.tight_layout()
plt.savefig(OUT / '03_loss_curves.png', dpi=120, bbox_inches='tight')
plt.close()
print(f'Saved {OUT / "03_loss_curves.png"}')

# === PLOT 4: Caption length ===
fig, ax = plt.subplots(figsize=(9, 5))
preds_data = {}
for name, path in top_models.items():
    df = pd.read_csv(path.replace('log.csv', 'predictions.csv'))
    pred_lens = df.caption_pred.str.split().str.len()
    preds_data[name] = pred_lens
ref_lens = pd.read_csv(top_models['M3-FT'].replace('log.csv', 'predictions.csv')).caption_ref.str.split().str.len()

bplot = ax.boxplot([ref_lens] + [preds_data[n] for n in top_models.keys()],
                   labels=['REF'] + list(top_models.keys()), patch_artist=True)
for patch, c in zip(bplot['boxes'], ['#999999', '#cc6677', '#88ccee', '#117733', '#332288', '#ddcc77']):
    patch.set_facecolor(c); patch.set_alpha(0.6)
ax.set_ylabel('Caption length (words)')
ax.set_title('Sapore - Caption length: reference vs top 5 model predictions')
ax.grid(axis='y', alpha=0.3)
ax.axhline(ref_lens.median(), color='gray', linestyle='--', linewidth=0.8, label=f'Ref median = {ref_lens.median():.0f}')
ax.legend()
plt.tight_layout()
plt.savefig(OUT / '04_caption_length.png', dpi=120, bbox_inches='tight')
plt.close()
print(f'Saved {OUT / "04_caption_length.png"}')

# === PLOT 5: Bootstrap CI ===
with open('reports/sapore_pilot/bootstrap_ci.json') as f:
    ci = json.load(f)

fig, axes = plt.subplots(1, 3, figsize=(14, 4.5))
metrics = [('bleu4', 'BLEU-4'), ('meteor', 'METEOR'), ('rouge', 'ROUGE-L')]
model_names = list(ci.keys())
for ax, (mkey, mlabel) in zip(axes, metrics):
    means = [ci[n][mkey][0] for n in model_names]
    lows = [ci[n][mkey][1] for n in model_names]
    highs = [ci[n][mkey][2] for n in model_names]
    err_low = [m - l for m, l in zip(means, lows)]
    err_high = [h - m for h, m in zip(highs, means)]
    y_pos = np.arange(len(model_names))
    ax.errorbar(means, y_pos, xerr=[err_low, err_high], fmt='o', capsize=4, color='#332288', linewidth=1.5)
    ax.set_yticks(y_pos)
    ax.set_yticklabels(model_names)
    ax.set_xlabel(mlabel)
    ax.set_title(f'{mlabel} - bootstrap 95% CI (n=1000)')
    ax.grid(axis='x', alpha=0.3)
    ax.invert_yaxis()
plt.tight_layout()
plt.savefig(OUT / '05_bootstrap_ci.png', dpi=120, bbox_inches='tight')
plt.close()
print(f'Saved {OUT / "05_bootstrap_ci.png"}')

# Stats
print('\n=== Caption length stats (Sapore test) ===')
print(f'REF: mean={ref_lens.mean():.1f}, median={ref_lens.median():.0f}, max={ref_lens.max()}')
for name, pl in preds_data.items():
    print(f'{name}: mean={pl.mean():.1f}, median={pl.median():.0f}, max={pl.max()}')
