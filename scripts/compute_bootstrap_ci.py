"""Bootstrap 95% CI for top-5 Sapore models, n=1000."""
import json
import numpy as np
import pandas as pd
import evaluate as hf_evaluate
from pathlib import Path

bleu = hf_evaluate.load('bleu')
meteor = hf_evaluate.load('meteor')
rouge = hf_evaluate.load('rouge')

models = {
    'M3-FT': 'models/m3_vit_transformer_ft/Sapore/predictions.csv',
    'M5c':   'models/m5c_vit_gpt/Sapore/predictions.csv',
    'M5b-FT':'models/m5b_cnnspatial_gpt_ft/Sapore/predictions.csv',
    'M5b':   'models/m5b_cnnspatial_gpt/Sapore/predictions.csv',
    'M3':    'models/m3_vit_transformer/Sapore/predictions.csv',
}

N_BOOT = 1000
SEED = 42
rng = np.random.default_rng(SEED)
out = {}

for name, path in models.items():
    df = pd.read_csv(path)
    preds = df['caption_pred'].fillna('').tolist()
    refs = df['caption_ref'].fillna('').tolist()
    n = len(preds)
    bl4, mt, rg = [], [], []
    for _ in range(N_BOOT):
        idx = rng.integers(0, n, size=n)
        p = [preds[i] for i in idx]
        r = [[refs[i]] for i in idx]
        try:
            bl4.append(bleu.compute(predictions=p, references=r)['bleu'])
        except Exception:
            bl4.append(0.0)
        mt.append(meteor.compute(predictions=p, references=[refs[i] for i in idx])['meteor'])
        rg.append(rouge.compute(predictions=p, references=[refs[i] for i in idx])['rougeL'])
    def ci(arr):
        a = np.array(arr)
        return [float(a.mean()), float(np.percentile(a, 2.5)), float(np.percentile(a, 97.5))]
    out[name] = {'bleu4': ci(bl4), 'meteor': ci(mt), 'rouge': ci(rg)}
    print(f'{name}: BLEU-4 {out[name]["bleu4"]} METEOR {out[name]["meteor"]}')

Path('reports/sapore_pilot/bootstrap_ci.json').write_text(json.dumps(out, indent=2))
print('Saved bootstrap_ci.json with n=1000')
