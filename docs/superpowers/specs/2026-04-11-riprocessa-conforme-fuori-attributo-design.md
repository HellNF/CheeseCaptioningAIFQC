# Design — Riprocessamento CONFORME e FUORI_ATTRIBUTO

**Data**: 2026-04-11
**Autore**: panciut
**Stato**: approvato

## Contesto

Dopo la Fase 4 (normalizzazione commenti via LLM), i CSV in
`data/processed/caption_per_attributo/` presentano due categorie di righe
che richiedono un trattamento migliorato:

- **699 CONFORME** distribuiti sui 7 attributi: il LLM ha assegnato a tutti
  la stessa stringa baseline, ma molti contengono descrittori specifici
  ("Paglierino", "Compatto", "Grana grossa") che meritano caption proprie.
- **2910 FUORI_ATTRIBUTO** con `caption = null`: alcuni sono falsi negativi
  (commenti pertinenti classificati erroneamente), ma anche i veri
  fuori-attributo devono avere una caption per consentire la revisione umana.

## Obiettivi

1. **Script 11** — Riprocessare i CONFORME distinguendo tra:
   - Commento con contenuto specifico → `classe = OK`, caption specifica
   - Commento puramente generico → `classe = CONFORME`, caption **variata**
     sulla baseline (non stringa identica)

2. **Script 12** — Generare caption per tutti i FUORI_ATTRIBUTO, mantenendo
   `classe = FUORI_ATTRIBUTO`. La caption descrive il commento in linguaggio
   naturale senza vincolarsi all'attributo di provenienza. Il training li
   esclude per default; la revisione umana può includerli rimuovendo il filtro.

3. **Aggiornamento `normalizza_commenti.py`** — Modificare il prompt base
   affinché le future run generino caption anche per FUORI_ATTRIBUTO
   (non più `caption = null`).

## Architettura

```
src/data/
  normalizza_commenti.py        ← aggiornato: FUORI_ATTRIBUTO genera caption
  11_riprocessa_conforme.py     ← nuovo script
  12_riprocessa_fuori_attributo.py ← nuovo script

data/processed/caption_per_attributo/
  <Attributo>_captions.csv      ← aggiornato in-place da entrambi gli script

data/interim/
  riprocessa_conforme_in_corso/ ← checkpoint script 11
  riprocessa_fuori_attributo_in_corso/ ← checkpoint script 12

reports/
  riprocessa_conforme_<Attributo>.md
  riprocessa_fuori_attributo_<Attributo>.md
```

## Script 11 — `11_riprocessa_conforme.py`

### Input
CSV esistenti in `data/processed/caption_per_attributo/`, righe con
`classe == CONFORME`.

### Prompt LLM

**System prompt**: identico a quello di `normalizza_commenti.py` per
l'attributo corrente (contesto caseario + vocabolario + baseline).

**User message** (per batch):

```
Riprocessa i seguenti commenti già classificati come CONFORME.
Per ciascuno decidi:
- Se contiene un descrittore specifico (colore, intensità, nota sensoriale,
  misura, aggettivo tecnico) → classe "OK" con caption specifica in italiano
  naturale (15-60 parole)
- Se è puramente generico senza informazione specifica ("ok", "bello",
  "positivo", "buono", "nella media") → classe "CONFORME" con una caption
  che descriva un campione conforme alla norma, DIVERSA dalla baseline
  standard (varia la formulazione)

Formato risposta — una riga JSON per commento:
{"id": N, "classe": "OK"|"CONFORME", "caption": "..."}
```

### Output
- Righe promosse a OK: `classe = OK`, caption specifica
- Righe che restano CONFORME: `classe = CONFORME`, caption variata
- CSV aggiornato in-place
- Report: `reports/riprocessa_conforme_<Attributo>.md`
  con conteggio OK recuperati, CONFORME con caption variata

### Argparse
```
--attributo   Processa solo questo attributo
--model       Modello LLM (default: gpt-4o-mini)
--batch-size  Commenti per batch (default: 20)
--dry-run     Non chiama API, stampa cosa processerebbe
```

### Checkpoint
Un file JSON per batch in `data/interim/riprocessa_conforme_in_corso/`
con naming `<Attributo>_batch_NNNN.json`. Lo script rileva i batch già
completati e li salta.

---

## Script 12 — `12_riprocessa_fuori_attributo.py`

### Input
CSV esistenti in `data/processed/caption_per_attributo/`, righe con
`classe == FUORI_ATTRIBUTO` e `caption` nulla.

### Prompt LLM

**System prompt** minimale (senza vincolo di attributo):

```
Sei un assistente che normalizza commenti di panel sensoriale.
Il tuo compito è trasformare il commento grezzo in una frase in italiano
standard, chiara e naturale. Non aggiungere informazioni non presenti.
Lunghezza: 10-40 parole.
```

**User message** (per batch):

```
Normalizza i seguenti commenti in linguaggio naturale.
Per ciascuno restituisci una riga JSON:
{"id": N, "caption": "..."}

Commenti:
N. "testo grezzo"
```

### Output
- `classe` invariata (`FUORI_ATTRIBUTO`)
- `caption` popolata con la normalizzazione in linguaggio naturale
- CSV aggiornato in-place
- Report: `reports/riprocessa_fuori_attributo_<Attributo>.md`

### Argparse
```
--attributo   Processa solo questo attributo
--model       Modello LLM (default: gpt-4o-mini)
--batch-size  Commenti per batch (default: 20)
--dry-run     Non chiama API, stampa cosa processerebbe
```

### Checkpoint
`data/interim/riprocessa_fuori_attributo_in_corso/<Attributo>_batch_NNNN.json`

---

## Aggiornamento `normalizza_commenti.py`

Modificare `_USER_MSG_HEADER` per cambiare il comportamento di
`FUORI_ATTRIBUTO`: invece di `caption null`, il LLM genera una caption
generica che descrive il commento. La classe resta `FUORI_ATTRIBUTO`.

```python
"- FUORI_ATTRIBUTO: riguarda un attributo diverso → caption in linguaggio "
"naturale che descrive il commento (non vincolarsi all'attributo corrente)\n"
```

Questo garantisce che le future run di `10_normalizza_commenti.py`
producano caption complete per tutte le classi.

---

## Utilizzo al training

Il CSV unificato per il training applica il seguente filtro di default:

```python
df_train = df[df['classe'].isin(['OK', 'CONFORME'])]
```

Per includere i FUORI_ATTRIBUTO nella revisione umana o nel training:

```python
df_train = df[df['caption'].notna()]
```

---

## Costo stimato API

| Script | Righe | Costo stimato |
|--------|-------|---------------|
| 11 (CONFORME) | 699 | ~$0.02 |
| 12 (FUORI_ATTRIBUTO) | 2910 | ~$0.08 |
| **Totale** | **3609** | **~$0.10** |

---

## Testing

- Test unitari per i nuovi prompt (parse risposta, gestione ERRORE_PARSING)
- Test di integrazione su campione ridotto (10 righe per attributo)
- Verifica che i CSV abbiano lo stesso schema dopo l'aggiornamento
- Verifica che nessuna riga OK/CONFORME esistente venga modificata
  (gli script toccano solo le righe target)
