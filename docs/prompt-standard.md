# Prompt Standard per Claude/Copilot

## Inizio Sessione

```
@workspace Leggi docs/CONTESTO_COMPLETO_PROGETTO.md e confermami
che hai capito il progetto prima di procedere.
```

## Analisi Esplorativa

```
Crea uno script Python che analizza [FILE/DATASET] e produce:
1. Statistiche descrittive
2. Distribuzioni variabili chiave
3. Report markdown in reports/
4. Grafici in reports/figures/

Usa il template in templates/script_template.py
Salva come src/data/analyze_[nome].py
```

## Pulizia Dati

```
Scrivi una funzione che pulisce i commenti seguendo queste regole:
[LISTA REGOLE SPECIFICHE]

La funzione deve:
- Accettare DataFrame in input
- Loggare ogni trasformazione
- Generare report prima/dopo
- Gestire encoding \xa0
```

## Code Review

```
#file:src/data/script.py
Rivedi questo codice per:
1. Gestione errori robusta
2. Performance su ~3000 campioni
3. Documentazione completa
4. Conformità a .github/copilot-instructions.md
```

## Debugging

```
#file:src/data/script.py:45-67
Questo blocco genera [ERRORE].
Contesto: [SPIEGA PROBLEMA]
Come gestirlo considerando che [VINCOLI]?
```

```

---

## **STEP 9: Come Usare Tutto Questo**

### **Quando inizi una nuova sessione con Claude:**

1. Apri VS Code
2. Apri la cartella progetto
3. Apri la chat di Claude
4. Scrivi:
```

@workspace Leggi docs/CONTESTO_COMPLETO_PROGETTO.md e confermami
che sei pronto a lavorare sul progetto Grana Trentino.

```

Claude leggerà automaticamente anche `project-overview.md` (grazie a `claude.contextFiles` in settings.json).

### **Quando chiedi codice a Claude:**

**Per script nuovi:**
```

Crea uno script basato su templates/script_template.py che fa [TASK].
Salva come src/[categoria]/[nome].py

```

**Per modifiche:**
```

#file:src/data/loader.py
Aggiungi gestione encoding UTF-8 e logging dettagliato
