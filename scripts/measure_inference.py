"""Misura latenza, VRAM, params per i top 3 modelli."""
import torch
import time
from pathlib import Path
import sys

sys.path.insert(0, '.')
from src.models.models import build_model
from src.models.vocabulary import ItalianTokenizer
from src.models.metrics import generate_caption

models_to_test = [
    ('M1', 'm1', False, 'models/m1_cnn_lstm/Sapore/best.pt'),
    ('M3', 'm3', False, 'models/m3_vit_transformer/Sapore/best.pt'),
    ('M3-FT', 'm3', True, 'models/m3_vit_transformer_ft/Sapore/best.pt'),
    ('M5c', 'm5c', False, 'models/m5c_vit_gpt/Sapore/best.pt'),
    ('M5c-FT', 'm5c', True, 'models/m5c_vit_gpt_ft/Sapore/best.pt'),
]

device = torch.device('cuda')
tok = ItalianTokenizer()

print('Model | params total | params trainable | best.pt size MB | VRAM MB | Latency ms')
print('-' * 85)

for name, flag, ft, ckpt in models_to_test:
    torch.cuda.empty_cache()
    torch.cuda.reset_peak_memory_stats()

    # Build model
    model = build_model(flag, vocab_size=len(tok), device=device)
    if ft:
        model.unfreeze_encoder()
    state = torch.load(ckpt, map_location=device, weights_only=True)
    sd = state.get('model_state_dict') or state.get('state_dict') or state
    if isinstance(sd, dict) and any(k.startswith('module.') for k in sd):
        sd = {k.replace('module.', ''): v for k, v in sd.items()}
    try:
        model.load_state_dict(sd, strict=False)
    except Exception as e:
        print(f'{name}: load error {e}')
        continue
    model.eval()

    # Params
    p_total = sum(p.numel() for p in model.parameters()) / 1e6
    p_train = sum(p.numel() for p in model.parameters() if p.requires_grad) / 1e6

    # Disk
    disk_mb = Path(ckpt).stat().st_size / 1024**2

    # Dummy input
    fetta = torch.randn(1, 3, 224, 224, device=device)
    grana = torch.randn(1, 3, 224, 224, device=device)

    # Warmup
    with torch.no_grad():
        for _ in range(3):
            _ = generate_caption(model, fetta, grana, tok, device=device, max_len=30, strategy='nucleus', top_p=0.9, temperature=0.7)

    # Measure latency: 10 runs
    torch.cuda.synchronize()
    t0 = time.perf_counter()
    for _ in range(10):
        with torch.no_grad():
            _ = generate_caption(model, fetta, grana, tok, device=device, max_len=30, strategy='nucleus', top_p=0.9, temperature=0.7)
    torch.cuda.synchronize()
    dt = (time.perf_counter() - t0) / 10 * 1000  # ms per inference

    # VRAM peak
    vram_peak = torch.cuda.max_memory_allocated() / 1024**2

    print(f'{name:8s} | {p_total:7.1f} M | {p_train:7.1f} M | {disk_mb:6.0f} | {vram_peak:6.0f} | {dt:7.1f}')

    del model
    torch.cuda.empty_cache()
