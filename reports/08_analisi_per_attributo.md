# Report Analisi Per-Attributo + NotebookLM

**Data elaborazione:** 2026-04-09 21:17:16

---

## Attributi processati

Spessore della Crosta

## Notebook NotebookLM creati

| Attributo | Notebook ID |
|-----------|------------|
| Aroma | `8721a403-3952-439f-948b-e75f553ee673` |
| Profumo | `caf696ac-d6ba-4edc-a365-757fe5744d5e` |
| Sapore | `d911d865-fed6-40e0-8a4d-7efc631991c1` |
| Texture | `266cde9d-883b-4eba-833f-853158140f7a` |
| Struttura della Pasta | `ce6c1c95-1505-4804-895a-c8f4d43f6fad` |
| Colore della Pasta | `9a5189f4-0ad6-4b99-8be4-5c23cc264590` |
| Spessore della Crosta | `bb7dbaaf-6496-4560-8c0d-7a77b1e1bd7b` |

## Output generati

### Fase 1 — Analisi statistica
```
data/interim/analisi_statistica_per_attributo/
  {Attributo}_statistiche.md          ← distribuzione, top termini, soglie quantitative
  {Attributo}_contesto_notebooklm.md  ← caricato come prima sorgente su NotebookLM
```

### Fase 2 — Vocabolario bozza NotebookLM
```
data/interim/vocabolari_bozza_per_attributo/
  {Attributo}_vocabolario_nblm.md     ← risposte alle 4 query (da revisionare)
  {Attributo}_vocabolario_TEMPLATE.json ← template vuoto per la revisione umana
  notebook_ids.json                     ← IDs notebook per riferimento futuro
```

## Passo successivo (manuale)

1. Per ogni attributo, apri `{Attributo}_vocabolario_nblm.md`
2. Leggi le 4 sezioni (inventario, cluster, anomalie, dubbi)
3. Compila `{Attributo}_vocabolario_TEMPLATE.json` con le decisioni finali
4. Rinomina il file compilato: `{Attributo}_vocabolario.json`
5. Sposta in: `data/interim/vocabolari_validati_per_attributo/`
6. Quando tutti i vocabolari sono validati → esegui script 09
