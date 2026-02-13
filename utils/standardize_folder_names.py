"""
Standardizza i nomi delle cartelle immagini a formato uniforme.

FORMATO TARGET: YYYY-MM-DD_Seduta_NN
Esempio: 2020-12-18_Seduta_16

Questo risolve il problema delle 1331 "sessione_inesistente" causato
da nomenclatura inconsistente tra CSV e cartelle immagini.
"""

import re
import logging
from pathlib import Path
from datetime import datetime
from typing import Optional, Tuple
import sys

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(levelname)s: %(message)s',
    handlers=[
        logging.FileHandler('standardize_folders.log', mode='w', encoding='utf-8'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

TRENTINGRANA_DIR = Path("../07_captioning risultati grana Trentino/TrentinGrana")


def parse_folder_name(nome_cartella: str) -> Optional[Tuple[datetime, Optional[int]]]:
    """Estrae data e numero seduta (se presente) da qualsiasi formato corrente.

    Pattern supportati:
    - 16°Seduta_18-12-2020
    - 30-10-2019_9°Seduta
    - 18-12-2019_17° Seduta  (con spazio)
    - 12°Seduta_25-11-2020_  (con underscore finale)
    - 18-12-2020 (solo data, senza numero seduta — 2018-2019)

    Args:
        nome_cartella: Nome della cartella da parsare.

    Returns:
        Tuple (data, numero_seduta) se parsing ok, None altrimenti.
        numero_seduta può essere None se non presente nel nome.
    """
    # Pattern 1: N°Seduta_DD-MM-YYYY o N° Seduta_DD-MM-YYYY
    pattern1 = re.compile(r'(\d+)\s*°\s*Seduta_(\d{2})-(\d{2})-(\d{4})', re.IGNORECASE)
    match = pattern1.search(nome_cartella)
    if match:
        n_seduta = int(match.group(1))
        giorno = int(match.group(2))
        mese = int(match.group(3))
        anno = int(match.group(4))
        try:
            data = datetime(anno, mese, giorno)
            return (data, n_seduta)
        except ValueError:
            logger.warning(f"Data invalida in '{nome_cartella}': {giorno}/{mese}/{anno}")
            return None

    # Pattern 2: DD-MM-YYYY_N°Seduta o DD-MM-YYYY_N° Seduta
    pattern2 = re.compile(r'(\d{2})-(\d{2})-(\d{4})_(\d+)\s*°\s*Seduta', re.IGNORECASE)
    match = pattern2.search(nome_cartella)
    if match:
        giorno = int(match.group(1))
        mese = int(match.group(2))
        anno = int(match.group(3))
        n_seduta = int(match.group(4))
        try:
            data = datetime(anno, mese, giorno)
            return (data, n_seduta)
        except ValueError:
            logger.warning(f"Data invalida in '{nome_cartella}': {giorno}/{mese}/{anno}")
            return None

    # Pattern 3: Solo data DD-MM-YYYY (2018-2019, senza numero seduta)
    pattern3 = re.compile(r'^(\d{2})-(\d{2})-(\d{4})$')
    match = pattern3.match(nome_cartella)
    if match:
        giorno = int(match.group(1))
        mese = int(match.group(2))
        anno = int(match.group(3))
        try:
            data = datetime(anno, mese, giorno)
            return (data, None)  # None = nessun numero seduta
        except ValueError:
            logger.warning(f"Data invalida in '{nome_cartella}': {giorno}/{mese}/{anno}")
            return None

    return None


def genera_nome_standard(data: datetime, n_seduta: Optional[int]) -> str:
    """Genera nome cartella nel formato standard.

    FORMATO CON SEDUTA: YYYY-MM-DD_Seduta_NN
    FORMATO SOLO DATA:  YYYY-MM-DD

    Esempio: 2020-12-18_Seduta_16  (con numero seduta)
             2018-11-20            (solo data, per 2018-2019)

    Args:
        data: Data della seduta.
        n_seduta: Numero della seduta, o None se non presente.

    Returns:
        Nome standardizzato.
    """
    if n_seduta is not None:
        return f"{data.strftime('%Y-%m-%d')}_Seduta_{n_seduta:02d}"
    else:
        # Solo data (2018-2019)
        return data.strftime('%Y-%m-%d')


def analizza_cartelle(dry_run: bool = True) -> dict:
    """Analizza tutte le cartelle e propone i rename.

    Args:
        dry_run: Se True, mostra solo cosa verrebbe fatto senza eseguire.

    Returns:
        Dict con statistiche e lista rename.
    """
    if not TRENTINGRANA_DIR.exists():
        logger.error(f"Directory non trovata: {TRENTINGRANA_DIR}")
        sys.exit(1)

    rename_plan = []
    errors = []
    skipped = []

    # Scansiona tutte le sottocartelle
    for root, dirs, files in TRENTINGRANA_DIR.walk():
        for dir_name in dirs:
            dir_path = root / dir_name

            # Salta cartelle che sono già nello standard
            if re.match(r'\d{4}-\d{2}-\d{2}_Seduta_\d{2}', dir_name):
                skipped.append(dir_name)
                continue

            # Prova a parsare
            parsed = parse_folder_name(dir_name)
            if parsed is None:
                # Non è una cartella seduta (es. "Thumbs.db", "I bimestre", ecc.)
                continue

            data, n_seduta = parsed
            nome_nuovo = genera_nome_standard(data, n_seduta)

            # Controlla se esiste già una cartella con quel nome
            nuovo_path = root / nome_nuovo
            if nuovo_path.exists() and nuovo_path != dir_path:
                errors.append({
                    'originale': dir_name,
                    'nuovo': nome_nuovo,
                    'errore': 'Cartella target già esistente (conflitto)',
                })
                continue

            rename_plan.append({
                'path_completo': dir_path,
                'nome_originale': dir_name,
                'nome_nuovo': nome_nuovo,
                'data': data,
                'n_seduta': n_seduta,
            })

    # Ordina per data
    rename_plan.sort(key=lambda x: (x['data'], x['n_seduta']))

    # Statistiche
    stats = {
        'totale_da_rinominare': len(rename_plan),
        'gia_standard': len(skipped),
        'errori': len(errors),
        'rename_plan': rename_plan,
        'errors': errors,
    }

    # Report
    logger.info("="*70)
    logger.info("ANALISI CARTELLE TRENTINGRANA")
    logger.info("="*70)
    logger.info(f"Cartelle da rinominare: {stats['totale_da_rinominare']}")
    logger.info(f"Cartelle già in formato standard: {stats['gia_standard']}")
    logger.info(f"Errori/Conflitti: {stats['errori']}")

    if errors:
        logger.warning("\nERRORI/CONFLITTI:")
        for err in errors:
            logger.warning(f"  {err['originale']} -> {err['nuovo']}: {err['errore']}")

    if rename_plan:
        logger.info(f"\n{'='*70}")
        logger.info("ANTEPRIMA RENAME (prime 20 cartelle)")
        logger.info('='*70)
        for item in rename_plan[:20]:
            logger.info(f"  {item['nome_originale']:<35} -> {item['nome_nuovo']}")

        if len(rename_plan) > 20:
            logger.info(f"  ... e altre {len(rename_plan) - 20} cartelle")

    return stats


def esegui_rename(stats: dict) -> None:
    """Esegue effettivamente i rename delle cartelle.

    Args:
        stats: Statistiche e piano rename da analizza_cartelle().
    """
    rename_plan = stats['rename_plan']

    logger.info(f"\n{'='*70}")
    logger.info("ESECUZIONE RENAME")
    logger.info('='*70)

    successi = 0
    fallimenti = 0

    for item in rename_plan:
        path_old = item['path_completo']
        path_new = path_old.parent / item['nome_nuovo']

        try:
            path_old.rename(path_new)
            successi += 1
            logger.debug(f"OK {item['nome_originale']} -> {item['nome_nuovo']}")
        except Exception as e:
            fallimenti += 1
            logger.error(f"ERR {item['nome_originale']}: {e}")

    logger.info(f"\n{'='*70}")
    logger.info(f"Successi: {successi}")
    logger.info(f"Fallimenti: {fallimenti}")
    logger.info('='*70)

    if successi > 0:
        logger.info("\nOK Rename completato! Ora riesegui il validation script per verificare.")


def main():
    """Main function con conferma utente."""
    print("""
========================================================================
        STANDARDIZZAZIONE NOMI CARTELLE TRENTINGRANA
========================================================================

Questo script rinomina TUTTE le cartelle immagini a formato standard:

  FORMATO CON SEDUTA: YYYY-MM-DD_Seduta_NN  (es. 2020-12-18_Seduta_16)
  FORMATO SOLO DATA:  YYYY-MM-DD            (es. 2018-11-20, per 2018-2019)

Pattern supportati (verranno tutti convertiti):
  - 16 Seduta_18-12-2020  (con numero seduta)
  - 30-10-2019_9 Seduta   (con numero seduta)
  - 18-12-2020            (solo data, 2018-2019)

IMPORTANTE: Questa operazione e' IRREVERSIBILE (ma sicura).
""")

    # Step 1: Dry run (anteprima)
    logger.info("STEP 1: ANTEPRIMA (nessuna modifica effettuata)\n")
    stats = analizza_cartelle(dry_run=True)

    if stats['totale_da_rinominare'] == 0:
        logger.info("\nOK Tutte le cartelle sono gia in formato standard!")
        return

    if stats['errori'] > 0:
        logger.error(f"\nERR Trovati {stats['errori']} conflitti. Risolverli prima di procedere.")
        return

    # Step 2: Conferma utente
    print("\n" + "="*70)
    risposta = input(f"\nConfermi il rename di {stats['totale_da_rinominare']} cartelle? [y/N]: ")

    if risposta.lower() != 'y':
        logger.info("Operazione annullata dall'utente.")
        return

    # Step 3: Esegui rename
    logger.info("\nSTEP 2: ESECUZIONE RENAME\n")
    esegui_rename(stats)


if __name__ == "__main__":
    main()
