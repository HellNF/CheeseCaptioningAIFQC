"""
Nome Script: [DESCRIZIONE BREVE]
Scopo: [COSA FA]
Input: [COSA PRENDE]
Output: [COSA PRODUCE]

Autore: [TUO NOME]
Data: [DATA]
"""

import logging
from pathlib import Path
from typing import List, Dict, Any
import pandas as pd

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/script_name.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Costanti
PROJECT_ROOT = Path(__file__).parent.parent
DATA_DIR = PROJECT_ROOT / "07_captioning risultati grana Trentino"
OUTPUT_DIR = PROJECT_ROOT / "data" / "processed"

def main():
    """Funzione principale dello script."""
    logger.info("Inizio elaborazione")
    
    try:
        # Il tuo codice qui
        pass
        
    except Exception as e:
        logger.error(f"Errore durante elaborazione: {e}", exc_info=True)
        raise
    
    logger.info("Elaborazione completata")

if __name__ == "__main__":
    main()


# **Quando usarlo:** Ogni volta che Claude o Copilot ti crea un nuovo script, chiedigli di basarlo su questo template.

# ---

# ## **STEP 4: Creare Struttura Cartelle Standard**

# Crea queste cartelle nel tuo progetto:
# ```
# grana-captioning/
# ├── .vscode/              # ✅ Già creata
# ├── .github/              # ✅ Appena creata
# ├── docs/                 # ✅ Già creata
# ├── templates/            # ✅ Appena creata
# ├── data/                 # 👉 CREA QUESTA
# │   ├── raw/              # Link simbolico ai dati originali
# │   ├── interim/          # Dati intermedi (versione A pulizia)
# │   ├── processed/        # Dati finali (versione B pulizia)
# │   └── metadata/         # Info su campioni, mapping, ecc.
# ├── src/                  # 👉 CREA QUESTA
# │   ├── data/
# │   ├── preprocessing/
# │   ├── models/
# │   └── evaluation/
# ├── notebooks/            # 👉 CREA QUESTA (per esplorazioni)
# ├── logs/                 # 👉 CREA QUESTA
# ├── reports/              # 👉 CREA QUESTA (report progressivi)
# └── models_trained/       # 👉 CREA QUESTA (modelli salvati)