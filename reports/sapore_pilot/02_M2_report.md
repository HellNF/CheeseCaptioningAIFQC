# M2 — CNN frozen + Transformer (Sapore)

**Data:** 2026-04-30
**GPU:** NVIDIA RTX 4060 Laptop (8 GB VRAM)
**Attributo:** Sapore (train=976, val=234, test=230)
**Loader:** `on_topic_only=True`

## Configurazione

- Encoder: `CNNEncoderGlobal` (ResNet-50 ImageNet, **frozen**) — 1 token visivo
- Decoder: `TransformerDecoder` from-scratch — 6 layers, 8 heads, d_model=512
- Loss: CE label smoothing 0.1
- Decode: nucleus (top_p=0.9, T=0.7)
- AdamW lr=1e-4, cosine, clip=5.0
- Batch 32, max 50 epoche, patience 7

## Metriche test

| Metrica | Valore |
|---|---|
| BLEU-1 | 0.3288 |
| **BLEU-4** | **0.0839** |
| METEOR | 0.2841 |
| ROUGE-L | 0.2416 |
| Caption uniche | 199/230 (87%) |

## Training

| | Valore |
|---|---|
| Best epoch | 6/13 (early stop) |
| Best val_loss | 1.9329 |
| Tempo totale | 12m 55s |

Convergenza rapida: best a epoca 6, da epoca 7 inizia overfitting (val_loss sale 1.93→2.08 mentre train_loss continua a scendere). Early stop scattato a epoca 13. **Pattern opposto a M1** (che invece sottoallenava).

## Confronto con M2 di Struttura

| | Struttura | Sapore | Δ |
|---|---|---|---|
| BLEU-4 | 0.041 | **0.084** | **+105%** |
| METEOR | 0.229 | 0.284 | +24% |
| ROUGE-L | 0.208 | 0.242 | +16% |

Anche M2 raddoppia BLEU-4 sul dataset pulito. Pattern coerente con M1.

## Confronto interno (M1 vs M2 su Sapore)

| | M1 (LSTM) | M2 (Transformer) |
|---|---|---|
| BLEU-4 | **0.092** | 0.084 |
| METEOR | **0.289** | 0.284 |
| ROUGE-L | 0.239 | **0.242** |
| Tempo | 50m 44s | 12m 55s |
| Best ep | 49/50 | 6/13 |

M1 lievemente migliore su BLEU-4/METEOR, M2 su ROUGE-L. **M2 è 4x più veloce** e converge in 1/8 delle epoche → più overfitting-prone su questo dataset piccolo. La differenza assoluta è piccola (~1 punto percentuale).

## Caption esempio (8 sample)

| # | Predizione | Riferimento |
|---|---|---|
| 0 | Il sapore è equilibrato, con una piccantezza eccessiva e una dolcezza delicata. | Ha poco sapore. |
| 5 | Il Grana Trentino DOP presenta una leggera sapidità. | C'è un amaro netto. |
| 10 | Il sapore è caratterizzato da una piccantezza marcata e una sapidità. | Troppo salato. |
| 25 | Il sapore del Grana Trentino DOP è caratterizzato da una nota amara e aciante. | Il Grana Trentino DOP offre un sapore medio, conforme alle aspettative di un formaggio di alta qualità. |
| 50 | Il sapore del Grana Trentino DOP si presenta con una leggera piccantezza e una sapidità marcata. | Generalmente equilibrato. |
| 100 | Il sapore è acido e leggermente piccante. | Il sapore è leggermente saporito e piccante, ma nel complesso equilibrato. |
| 150 | Il sapore è caratterizzato da una piccantezza di umami. | Un po' troppo salato. |
| 200 | Il sapore è caratterizzato da una dolcezza sapidità. | Il sapore è equilibrato con note dolciastre, peccato per il finale amarognolo. |

## Osservazioni

**Cosa funziona:**
- Vocabolario pulito (piccantezza, sapidità, amaro, acido, dolcezza, umami).
- Caption più sintetiche di M1 (LSTM tendeva a frasi lunghe).
- Diversità preservata (199/230 = 87%).

**Cosa non funziona:**
- **Errori grammaticali simili a M1**: #25 "aciante" (parola inventata, non italiano), #150 "piccantezza di umami" (costruzione strana), #200 "dolcezza sapidità" (concatenazione errata, identico bug di M1).
- Generico vs specifico: stesso problema di M1 — il modello produce frasi standardizzate mentre il riferimento è puntuale ("ha poco sapore").
- **Overfitting precoce**: solo 6 epoche utili. Suggerisce che con dataset di 976 campioni un Transformer da 5M params satura velocemente. M1 (LSTM) con ~2M params utilizzati ha gestito meglio.

**Confronto architetturale (M1 vs M2):**
- L'LSTM è più lenta a convergere ma raggiunge valori finali leggermente migliori. Il Transformer è più aggressivo nell'apprendere ma overfitta su questo dataset piccolo.
- Entrambi mostrano **gli stessi errori grammaticali** ("dolcezza sapidità", "aciante" vs "acido e acido"). Suggerisce che il bug è **decoder from-scratch su vocabulary 30k con poco training data**, non specifico dell'architettura.

**Ipotesi per i prossimi:**
- M3 (ViT+Transformer) — encoder migliore potrebbe non aiutare se decoder è il collo di bottiglia.
- Modelli M5* (GePpeTto pretrained) dovrebbero **eliminare gli errori grammaticali** perché GePpeTto ha già un prior linguistico forte.

## Output

- Pesi: `models/m2_cnn_transformer/Sapore/best.pt`
- Predictions: `models/m2_cnn_transformer/Sapore/predictions.csv`
- Log: `models/m2_cnn_transformer/Sapore/log.csv`
