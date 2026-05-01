# Cumulativo 1 — Encoder frozen × Decoder from-scratch (Sapore)

**Data:** 2026-04-30 (aggiornato post M3 re-run)
**Modelli inclusi:** M1, M2, M3 (3/12 completati)
**Cella 2×2:** [Encoder frozen, Decoder from-scratch]

## Tabella metriche

| Modello | Architettura | BLEU-1 | BLEU-4 | METEOR | ROUGE-L | Best ep | Tempo | Uniche |
|---|---|---|---|---|---|---|---|---|
| M1 | CNN(g) + LSTM | 0.329 | 0.092 | 0.289 | 0.239 | 49/50 | 50m | 89% |
| M2 | CNN(g) + Transformer | 0.329 | 0.084 | 0.284 | 0.242 | 6/13 | 13m | 87% |
| **M3** | ViT + Transformer | 0.315 | **0.098** | **0.307** | **0.249** | 8/13 | 21m | 85% |
| **Media** | — | **0.324** | **0.091** | **0.293** | **0.243** | — | — | 87% |

## Cella 2×2 vs Struttura

|  | Struttura (vecchio pilot) | Sapore (questo) | Δ |
|---|---|---|---|
| BLEU-4 medio | 0.044 | **0.091** | **+107%** |
| METEOR medio | 0.229 | 0.293 | +28% |
| ROUGE-L medio | 0.209 | 0.243 | +16% |

Conferma robusta del pattern: la cella `frozen × scratch` **più che raddoppia BLEU-4** sul dataset pulito. Il pattern emerso con tutti e 3 i modelli è coerente.

## Pattern osservati nel gruppo

### 1. Mode collapse risolto
Tutti e 3 i modelli producono 85-89% di caption uniche. Il fix `label smoothing 0.1 + nucleus sampling (top_p=0.9, T=0.7)` continua a funzionare anche su Sapore.

### 2. Vocabolario tecnico appreso
Tutti i modelli usano correttamente il lessico sensoriale del Grana: piccantezza, sapidità, umami, amaro, acido, dolce, salato, pungente, equilibrato, marcata, leggera. Nessuna parola random fuori dominio.

### 3. Errori grammaticali isolati ma sistematici
- M1: "acido e acido" (ripetizione)
- M2: "aciante" (parola inventata), "dolcezza sapidità" (concatenazione)
- M3: "sapidità marcata e [...] sapidità marcata" (ripetizione frammento), frase troncata

Tutti e 3 hanno qualche errore. Suggerisce che è un problema di **decoder from-scratch su vocabulary 30k con poco training data**, non architettura-specifico.

### 4. Direzionalità semantica incerta
Tutti tendono a produrre caption "positive/equilibrate" anche quando il riferimento è negativo o iperbolico:
- Ref "ha poco sapore" → pred "leggera piccantezza" / "sapidità marcata"
- Ref "troppo salato" → pred "leggermente amaro" / "amaro e piccantezza"

Il modello ha imparato il **template sintattico medio del dataset** ("Il sapore è X, con Y") ma fatica ad associare specifici stimoli visivi a giudizi netti.

### 5. Tempo training variabile
M1 (50m, no early stop), M2 (13m, early stop ep 13), M3 (21m, early stop ep 13). LSTM converge lentamente; Transformer overfitta velocemente.

## Confronto interno: chi vince?

- **BLEU-4**: M3 (0.098) > M1 (0.092) > M2 (0.084)
- **METEOR**: M3 (0.307) > M1 (0.289) > M2 (0.284)
- **ROUGE-L**: M3 (0.249) > M2 (0.242) > M1 (0.239)

**M3 è il vincitore del gruppo** su tutte e 3 le metriche, dopo il re-run con best.pt valido. Il ViT (timm vit_small) cattura informazione visiva migliore della CNN globale (ResNet-50) per questo dataset.

**Implicazione**: a differenza di Struttura (dove i 3 modelli erano quasi indistinguibili), su Sapore il choice di encoder fa la differenza. ViT > CNNGlobal.

## Ipotesi per il prossimo gruppo (frozen × GePpeTto, M5a/M5b/M5c)

Già completato M5a:
- M5a (CNN+GePpeTto): BLEU-4=0.090, METEOR=0.274, ROUGE-L=0.231, val_loss=1.542

**M5a è leggermente sotto M3** su BLEU-4 (0.090 vs 0.098) e METEOR (0.274 vs 0.307) **nonostante val_loss molto più bassa** (1.54 vs 1.97). Pattern interessante:

1. GePpeTto migliora la **fluenza linguistica** (val_loss = log-perplexity → 25% inferiore).
2. GePpeTto **non migliora l'accuracy semantica** (BLEU-4 e METEOR simili o leggermente sotto).
3. METEOR di M3 (0.307) è il migliore visto finora — **encoder ViT > decoder GePpeTto** in termini di qualità test.

Se questo pattern regge anche per M5b e M5c, la conclusione sarà: **per dataset piccolo (1000 samples), il decoder pre-trained non aggiunge valore** rispetto a un decoder from-scratch ben architettato; **l'encoder visivo è quello che fa la differenza**.

## Stato pilot

Completati: 3/12 + M5a (4 modelli totali). Tempo totale finora: ~105m (escluso il crash + restart M3).

Prossimi: M5b (CNNSpatial+GePpeTto) → M5c (ViT+GePpeTto) → cumulativo_2.
