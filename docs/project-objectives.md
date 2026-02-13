# Obiettivi del Progetto

## Task Principale
Sviluppare un sistema di image captioning per formaggio Grana Trentino che generi descrizioni testuali dalle immagini.

## Fase 1: Pre-processing (OBBLIGATORIO)
1. **Pulizia testo commenti panelisti:**
   - Sostituire descrizioni quantitative con qualitative
   - Riformulare frasi dialettali in italiano standard
   - Espandere commenti telegrafici in frasi complete
   - Ridurre sinonimi (creare vocabolario controllato)

2. **Pulizia immagini:**
   - Rimuovere spot colorati (rosso/blu) usati per marcare lati forma
   - Normalizzare dimensioni/qualità

## Fase 2: Modeling
Implementare e confrontare 3 metodi encoder-decoder **concettualmente diversi**:
- Metodo 1: [da scegliere]
- Metodo 2: [da scegliere]  
- Metodo 3: [da scegliere]

## Vincoli
- Accuratezza nella Fase 1 è critica (impatta qualità modelli)
- I 3 metodi devono essere molto diversi tra loro concettualmente