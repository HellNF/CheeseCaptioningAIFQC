# Design: Revisione Umana Vocabolari per Attributo

**Data:** 2026-04-10  
**Branch:** `feature/per-attribute-captioning`  
**Fase pipeline:** Fase 3 — Revisione umana vocabolari  
**Stato:** APPROVATO

---

## 1. Contesto

Fase 1 (Script 08) e Fase 2 (NotebookLM) sono complete per tutti e 7 gli attributi.  
Le bozze dei vocabolari sono in `data/interim/vocabolari_bozza_per_attributo/`, una per attributo,  
e contengono: inventario termini, cluster semantici, normalizzazioni anomalie, dubbi aperti.

Questa Fase 3 produce i 7 JSON validati in `data/interim/vocabolari_validati_per_attributo/`  
che alimenteranno lo Script 09 (normalizzazione commenti).

---

## 2. Componenti

### 2a — Documenti di revisione (7 file Markdown)

**Posizione:** `data/interim/vocabolari_revisione_umana/{Attributo}_revisione.md`  
**Generati da:** Claude (leggendo i `_vocabolario_nblm.md` + `_statistiche.md`)

Ogni file contiene sezioni con **blocchi `yaml` inline editabili** — sia le proposte  
pre-compilate da Claude che i dubbi aperti usano la stessa struttura, così il revisore  
può correggere qualsiasi scelta, non solo i dubbi.

#### Struttura del documento

```
## META
```yaml
attributo: "Texture"
versione: "1.0"
stato: "DA_RIVEDERE"   # cambia in APPROVATO quando hai finito
```

## TERMINI TECNICI INVARIABILI
Lista in un unico blocco yaml — modificabile se necessario.

## CLUSTER SEMANTICI
Un blocco yaml per cluster, pre-compilato da Claude con le proposte NBLM validate.

## SINONIMI / ABBREVIAZIONI / TYPO
Un blocco yaml per voce, pre-compilato.

## CONVERSIONI QUANTITATIVE
Solo per Spessore della Crosta — range mm → etichetta qualitativa.

## DUBBI — RICHIEDE DECISIONE UMANA
Un blocco yaml per dubbio con campo `scelta: ""` da compilare.
I dubbi con scelta vuota bloccano la generazione del JSON.

## NOTE LIBERE
Campo testo libero per osservazioni aggiuntive.
```

#### Formato blocchi per tipo

**Cluster semantico (pre-compilato, editabile):**
```markdown
### Cluster: cristalli_tirosina
> Frequenza stimata: 315 | Termini NBLM: cristalli, microcristalli, tirosina, perle…

```yaml
forma_canonica: cristalli
varianti: [microcristalli, tirosina, perle, gnocchetti duri, scagliette, schioccante, scricchiola]
frequenza_stimata: 315
note: ""
```
```

**Sinonimo / abbreviazione / typo (pre-compilato, editabile):**
```markdown
### Sinonimo: sol. → solubile
```yaml
da: "sol."
a: solubile
tipo: abbreviazione   # sinonimo | abbreviazione | dialetto | typo
note: ""
```
```

**Dubbio aperto (da compilare):**
```markdown
### DUBBIO: "alleabile"
> Q_09, seduta 17/2019 — "Alleabile". Parola inesistente.
> Opzione A → `malleabile` (struttura plastica)
> Opzione B → `allappante` (astringenza)

```yaml
scelta: ""   # scrivi A, B, oppure una forma_canonica custom
note: ""
```
```

---

### 2b — Script di compilazione

**File:** `src/data/09a_compila_vocabolari.py`  
**Eseguito:** manualmente dopo aver compilato i documenti di revisione  
**Input:** `data/interim/vocabolari_revisione_umana/*.md`  
**Output:** `data/interim/vocabolari_validati_per_attributo/{Attributo}_vocabolario.json`  
**Report:** `data/interim/vocabolari_revisione_umana/revisione_status.md`

#### Comportamento

- Parsa tutti i blocchi ` ```yaml ``` ` di ogni `_revisione.md` con `yaml.safe_load`
- Identifica il tipo di blocco dal titolo della sezione (`### Cluster:`, `### Sinonimo:`, `### DUBBIO:`)
- Per dubbi con `scelta: ""` → stampa warning e include nel JSON sotto `dubbi_non_risolti`
- Genera il JSON nel formato standard definito in `pipeline_per_attributo.md §FASE3`
- Stampa un report finale: attributi completi vs attributi con dubbi aperti

#### JSON output (formato esistente, invariato)

```json
{
  "attributo": "Texture",
  "versione": "1.0",
  "data_validazione": "YYYY-MM-DD",
  "validato_da": "",
  "note_generali": "",
  "termini_tecnici_invariabili": ["cristalli", "tirosina", ...],
  "cluster": [
    {
      "nome_cluster": "cristalli_tirosina",
      "forma_canonica": "cristalli",
      "varianti": ["microcristalli", "perle", ...],
      "frequenza_stimata": 315
    }
  ],
  "sinonimi_diretti": [
    {"da": "sol.", "a": "solubile", "tipo": "abbreviazione"}
  ],
  "conversioni_quantitative": [],
  "dubbi_non_risolti": []
}
```

---

## 3. Struttura cartelle

```
data/interim/
  vocabolari_bozza_per_attributo/        ← INPUT (già esistente, generato da Fase 2)
  vocabolari_revisione_umana/            ← NUOVO
    Aroma_revisione.md
    Colore_della_Pasta_revisione.md
    Profumo_revisione.md
    Sapore_revisione.md
    Spessore_della_Crosta_revisione.md
    Struttura_della_Pasta_revisione.md
    Texture_revisione.md
    revisione_status.md                  ← generato da script 09a
  vocabolari_validati_per_attributo/     ← OUTPUT (generato da script 09a)
    Aroma_vocabolario.json
    ...

src/data/
  09a_compila_vocabolari.py              ← NUOVO
```

---

## 4. Workflow operativo

1. Claude genera i 7 `_revisione.md` (leggendo le bozze NBLM)
2. Revisore umano apre ogni file, corregge i blocchi pre-compilati se necessario, compila i dubbi
3. Revisore cambia `stato: "DA_RIVEDERE"` → `stato: "APPROVATO"` per ogni attributo completato
4. Esegue `python src/data/09a_compila_vocabolari.py`
5. Lo script genera i JSON e `revisione_status.md`
6. Se ci sono dubbi aperti → risolverli e rieseguire; i JSON sono idempotenti

---

## 5. Decisioni architetturali

| Decisione | Scelta | Motivazione |
|---|---|---|
| Formato review doc | Markdown + blocchi yaml inline | Contestuale, leggibile, parsabile |
| Sezioni pre-compilate editabili | Sì — stessa struttura yaml dei dubbi | Revisore ha controllo completo |
| Dubbi bloccanti | No — generano `dubbi_non_risolti` nel JSON | Non blocca il progresso, segnala solo |
| Script separato (09a) | Sì — non fuso con 09 | Responsabilità singola; 09 consuma solo JSON già validati |
| Formato JSON output | Invariato rispetto a `pipeline_per_attributo.md` | Compatibilità con Script 09 già pianificato |
