"""
Nome Script: Pulizia Commenti Grana Trentino - Fase B (Correzioni Pre-LLM)
Scopo: Correggere typo, gestire commenti vuoti 2018, flaggare anomalie
Input: CSV da data/interim/fase_A/
Output: CSV in data/interim/fase_B/ + anomalie_da_verificare.csv + report

Autore: Claude Code
Data: 2026-02-13

Fase B include:
- Correzione typo evidenti (dizionario noto)
- Gestione commenti vuoti 2018 basata su punteggio
- Flag anomalie per revisione manuale
- Aggiunta metadata (anno, attributo, flag)
"""

import logging
from pathlib import Path
from typing import List, Dict, Any, Tuple
import pandas as pd
import re
from collections import defaultdict, Counter
from datetime import datetime

# Setup logging
LOG_DIR = Path("logs")
LOG_DIR.mkdir(exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(LOG_DIR / 'fase_B_cleaning.log', mode='w', encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Costanti
PROJECT_ROOT = Path(__file__).parent.parent.parent
INPUT_DIR = PROJECT_ROOT / "data" / "interim" / "fase_A"
OUTPUT_DIR = PROJECT_ROOT / "data" / "interim" / "fase_B"
METADATA_DIR = PROJECT_ROOT / "data" / "metadata"
REPORTS_DIR = PROJECT_ROOT / "reports"

# Assicurarsi che le directory esistano
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
METADATA_DIR.mkdir(parents=True, exist_ok=True)
REPORTS_DIR.mkdir(parents=True, exist_ok=True)

# DIZIONARIO TYPO NOTI
TYPO_NOTI = {
    'cristali': 'cristalli',
    'proprionica': 'propionica',
    'yogurth': 'yogurt',
    'legg': 'leggermente',
    'abbastanza equilib': 'abbastanza equilibrato',
    "complessita'": 'complessità',
    "acidita'": 'acidità',
    'umidit': 'umidità'
}

# PAROLE ANOMALE STRICT (veramente fuori contesto caseario)
PAROLE_ANOMALE_STRICT = {
    'miami', 'km', 'uht', 'facebook', 'twitter',
    'ciao', 'boh', 'bah', 'mah', 'eh', 'ah'
}


def extract_year_from_filename(filename: str) -> int:
    """
    Estrae l'anno dal nome del file.

    Args:
        filename: Nome del file

    Returns:
        Anno come intero
    """
    if '2018' in filename:
        return 2018
    elif '2019' in filename:
        return 2019
    elif '2020' in filename:
        return 2020
    elif '2021' in filename:
        return 2021
    else:
        return 0


def extract_attribute_from_filename(filename: str) -> str:
    """
    Estrae l'attributo sensoriale dal nome del file.

    Args:
        filename: Nome del file

    Returns:
        Attributo con capitalizzazione corretta
    """
    filename_lower = filename.lower()

    if 'profumo' in filename_lower:
        return 'Profumo'
    elif 'sapore' in filename_lower:
        return 'Sapore'
    elif 'aroma' in filename_lower:
        return 'Aroma'
    elif 'texture' in filename_lower:
        return 'Texture'
    elif 'spessore' in filename_lower:
        return 'Spessore della Crosta'
    elif 'struttura' in filename_lower:
        return 'Struttura della Pasta'
    elif 'colore' in filename_lower:
        return 'Colore della Pasta'
    else:
        return 'Unknown'


def fix_typos(text: str) -> Tuple[str, List[str]]:
    """
    Corregge typo evidenti usando il dizionario TYPO_NOTI.

    Args:
        text: Testo da correggere

    Returns:
        Tupla (testo_corretto, lista_modifiche)
    """
    if pd.isna(text) or not text:
        return text, []

    modifications = []
    result = str(text)

    for typo, correct in TYPO_NOTI.items():
        # Usa word boundaries per evitare sostituzioni parziali
        pattern = r'\b' + re.escape(typo) + r'\b'
        if re.search(pattern, result, re.IGNORECASE):
            result = re.sub(pattern, correct, result, flags=re.IGNORECASE)
            modifications.append(f"{typo}→{correct}")

    return result, modifications


def check_anomalies(text: str, attributo: str = '') -> bool:
    """
    Verifica se il commento contiene anomalie evidenti.

    Usa criteri rigorosi per minimizzare falsi positivi.

    Args:
        text: Testo da verificare
        attributo: Attributo sensoriale (per eccezioni specifiche)

    Returns:
        True se ci sono anomalie genuine
    """
    if pd.isna(text) or not text:
        return False

    text_str = str(text).strip()
    text_lower = text_str.lower()

    # 1. Commenti troppo corti (< 3 caratteri totali)
    # ECCEZIONE: "ok", "Ok", "OK" sono accettabili
    if len(text_str) < 3:
        if text_lower not in ['ok']:
            return True

    # 2. Commenti composti solo da cifre
    # ECCEZIONE: per "Spessore della Crosta", i numeri sono misure legittime (mm/cm)
    # Anche "Ok" è accettabile
    is_numeric = text_str.replace('.', '').replace(',', '').replace(' ', '').isdigit()
    if is_numeric and 'spessore' not in attributo.lower():
        return True

    # 3. Pattern tastiera battuta per errore
    if re.search(r'\?{3,}|\!{3,}|\.{4,}', text_str):
        return True

    # 4. Parole specifiche fuori contesto (STRICT)
    tokens = re.findall(r'\b\w+\b', text_lower)
    for token in tokens:
        if token in PAROLE_ANOMALE_STRICT:
            return True

    # Se nessuna condizione è verificata, il commento è OK
    return False


def handle_empty_comment_2018(comment: str, score: float) -> Tuple[str, bool, bool]:
    """
    Gestisce commenti vuoti per i file 2018 basandosi sul punteggio.

    Args:
        comment: Commento (può essere vuoto/NaN)
        score: Punteggio numerico del panelista

    Returns:
        Tupla (nuovo_commento, flag_revisione, flag_vuoto_compilato)
    """
    # Se il commento non è vuoto, ritorna invariato
    if pd.notna(comment) and str(comment).strip():
        return comment, False, False

    # Se lo score non è valido, lascia vuoto
    if pd.isna(score):
        return '', False, False

    try:
        score_float = float(score)
    except (ValueError, TypeError):
        return '', False, False

    # Logica basata su punteggio
    if 6.5 <= score_float <= 7.5:
        return 'nella norma', False, True

    elif score_float < 5.0:
        return '[REVIEW: punteggio basso senza commento]', True, False

    elif score_float > 8.5:
        return '[REVIEW: punteggio alto senza commento]', True, False

    else:
        # Punteggio tra 5.0-6.5 o 7.5-8.5: lascia vuoto
        return '', False, False


def process_csv_file(filepath: Path) -> Tuple[pd.DataFrame, Dict[str, Any]]:
    """
    Processa un singolo file CSV applicando le pulizie Fase B.

    Args:
        filepath: Path del file CSV da processare

    Returns:
        Tupla (df_pulito, statistiche)
    """
    logger.info(f"Processando {filepath.name}...")

    # Carica CSV
    try:
        df = pd.read_csv(filepath, encoding='utf-8')
    except UnicodeDecodeError:
        df = pd.read_csv(filepath, encoding='latin-1')

    # Estrai anno e attributo
    year = extract_year_from_filename(filepath.name)
    attribute = extract_attribute_from_filename(filepath.name)

    # Trova colonna commenti
    comment_col = None
    for col in df.columns:
        if 'commenti' in col.lower():
            comment_col = col
            break

    if comment_col is None:
        logger.warning(f"  Colonna 'Commenti' non trovata in {filepath.name}")
        return df, {}

    # Aggiungi colonne metadata
    df['anno'] = year
    df['attributo'] = attribute
    df['commento_originale_A'] = df[comment_col].copy()
    df['flag_revisione'] = False
    df['flag_anomalia'] = False
    df['flag_vuoto_compilato'] = False

    # Statistiche
    stats = {
        'file': filepath.name,
        'total_rows': len(df),
        'typo_corrections': Counter(),
        'empty_handled': 0,
        'empty_review_low': 0,
        'empty_review_high': 0,
        'empty_filled': 0,
        'anomalies_flagged': 0,
        'examples_typo': [],
        'examples_empty': [],
        'examples_anomaly': []
    }

    # Determina se è un file 2018
    is_2018 = year == 2018

    # Per file 2018, trova la colonna del punteggio (colonna 3, indice 3)
    score_col = None
    if is_2018 and len(df.columns) > 3:
        # La colonna del punteggio ha nome variabile (Profumo, Sapore, ecc.)
        # ed è tipicamente la 4a colonna (indice 3)
        score_col = df.columns[3]

    # Processa ogni commento
    for idx, row in df.iterrows():
        original_comment = row[comment_col]
        comment = original_comment
        flag_rev = False
        flag_vuoto = False

        # 1. Correzione typo
        comment, typo_mods = fix_typos(comment)
        if typo_mods:
            stats['typo_corrections'].update(typo_mods)
            if len(stats['examples_typo']) < 5:
                stats['examples_typo'].append({
                    'original': str(original_comment),
                    'fixed': comment,
                    'modifications': typo_mods
                })

        # 2. Gestione commenti vuoti 2018
        if is_2018 and score_col:
            score = row[score_col]
            comment, flag_rev, flag_vuoto = handle_empty_comment_2018(comment, score)

            if flag_rev:
                stats['empty_handled'] += 1
                if 'basso' in comment:
                    stats['empty_review_low'] += 1
                else:
                    stats['empty_review_high'] += 1

                if len(stats['examples_empty']) < 5:
                    stats['examples_empty'].append({
                        'score': score,
                        'comment': comment
                    })

            if flag_vuoto:
                stats['empty_handled'] += 1
                stats['empty_filled'] += 1
                if len(stats['examples_empty']) < 5:
                    stats['examples_empty'].append({
                        'score': score,
                        'comment': comment
                    })

        # 3. Check anomalie (passa l'attributo per eccezioni specifiche)
        has_anomaly = check_anomalies(comment, attribute)
        if has_anomaly:
            stats['anomalies_flagged'] += 1
            if len(stats['examples_anomaly']) < 5:
                stats['examples_anomaly'].append({
                    'comment': str(comment),
                    'row': idx
                })

        # Aggiorna DataFrame
        df.at[idx, comment_col] = comment
        df.at[idx, 'flag_revisione'] = flag_rev
        df.at[idx, 'flag_anomalia'] = has_anomaly
        df.at[idx, 'flag_vuoto_compilato'] = flag_vuoto

    logger.info(f"  - Typo corretti: {sum(stats['typo_corrections'].values())}")
    logger.info(f"  - Commenti vuoti gestiti: {stats['empty_handled']}")
    logger.info(f"  - Anomalie flaggate: {stats['anomalies_flagged']}")

    return df, stats


def generate_anomalies_file(all_dfs: List[pd.DataFrame], output_path: Path):
    """
    Genera un file CSV con tutti i commenti flaggati per revisione.

    Args:
        all_dfs: Lista di DataFrame processati
        output_path: Path dove salvare il file
    """
    logger.info(f"Generando file anomalie in {output_path}...")

    # Concatena tutti i DataFrame
    df_all = pd.concat(all_dfs, ignore_index=True)

    # Filtra solo righe con flag_revisione o flag_anomalia
    df_anomalies = df_all[
        (df_all['flag_revisione'] == True) |
        (df_all['flag_anomalia'] == True)
    ].copy()

    # Riordina colonne per leggibilità
    cols = ['anno', 'attributo', 'Commenti', 'commento_originale_A',
            'flag_revisione', 'flag_anomalia', 'flag_vuoto_compilato']

    # Trova la colonna commenti (nome variabile)
    comment_col = None
    for col in df_anomalies.columns:
        if 'commenti' in col.lower():
            comment_col = col
            break

    if comment_col and comment_col != 'Commenti':
        cols[2] = comment_col

    # Seleziona colonne disponibili
    available_cols = [c for c in cols if c in df_anomalies.columns]

    df_anomalies = df_anomalies[available_cols]

    # Salva
    df_anomalies.to_csv(output_path, index=False, encoding='utf-8')
    logger.info(f"  Salvati {len(df_anomalies)} commenti da verificare")


def generate_report(all_stats: Dict[str, Dict], output_path: Path):
    """
    Genera un report markdown con le statistiche di pulizia Fase B.

    Args:
        all_stats: Dizionario con statistiche per ogni file
        output_path: Path dove salvare il report
    """
    logger.info(f"Generando report in {output_path}...")

    with open(output_path, 'w', encoding='utf-8') as f:
        f.write("# REPORT PULIZIA FASE B - Commenti Grana Trentino\n\n")
        f.write(f"**Data elaborazione:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
        f.write("---\n\n")

        # Statistiche aggregate
        f.write("## 1. STATISTICHE AGGREGATE\n\n")

        total_rows = sum(s['total_rows'] for s in all_stats.values())
        total_typo = sum(sum(s['typo_corrections'].values()) for s in all_stats.values())
        total_empty = sum(s['empty_handled'] for s in all_stats.values())
        total_empty_filled = sum(s['empty_filled'] for s in all_stats.values())
        total_empty_low = sum(s['empty_review_low'] for s in all_stats.values())
        total_empty_high = sum(s['empty_review_high'] for s in all_stats.values())
        total_anomalies = sum(s['anomalies_flagged'] for s in all_stats.values())

        f.write(f"- **Righe totali processate:** {total_rows}\n")
        f.write(f"- **Typo corretti:** {total_typo}\n")
        f.write(f"- **Commenti vuoti 2018 gestiti:** {total_empty}\n")
        f.write(f"  - Compilati con 'nella norma': {total_empty_filled}\n")
        f.write(f"  - Flaggati (punteggio basso): {total_empty_low}\n")
        f.write(f"  - Flaggati (punteggio alto): {total_empty_high}\n")
        f.write(f"- **Anomalie flaggate:** {total_anomalies}\n\n")

        # Breakdown typo per tipo
        f.write("### 1.1 Typo Corretti per Tipo\n\n")
        all_typo = Counter()
        for stats in all_stats.values():
            all_typo.update(stats['typo_corrections'])

        if all_typo:
            f.write("| Typo | Correzione | Occorrenze |\n")
            f.write("|------|-----------|------------|\n")
            for typo_fix, count in all_typo.most_common():
                parts = typo_fix.split('→')
                f.write(f"| {parts[0]} | {parts[1]} | {count} |\n")
            f.write("\n")
        else:
            f.write("Nessun typo corretto.\n\n")

        # Esempi typo
        f.write("## 2. ESEMPI DI MODIFICHE\n\n")
        f.write("### 2.1 Correzioni Typo\n\n")

        typo_examples = []
        for stats in all_stats.values():
            typo_examples.extend(stats['examples_typo'][:3])

        if typo_examples:
            for i, ex in enumerate(typo_examples[:10], 1):
                f.write(f"**Esempio {i}:**\n")
                f.write(f"- **Prima:** `{ex['original']}`\n")
                f.write(f"- **Dopo:** `{ex['fixed']}`\n")
                f.write(f"- **Modifiche:** {', '.join(ex['modifications'])}\n\n")
        else:
            f.write("Nessun esempio disponibile.\n\n")

        # Esempi commenti vuoti 2018
        f.write("### 2.2 Gestione Commenti Vuoti 2018\n\n")

        empty_examples = []
        for stats in all_stats.values():
            empty_examples.extend(stats['examples_empty'][:3])

        if empty_examples:
            for i, ex in enumerate(empty_examples[:10], 1):
                f.write(f"**Esempio {i}:**\n")
                f.write(f"- **Punteggio:** {ex['score']}\n")
                f.write(f"- **Commento generato:** `{ex['comment']}`\n\n")
        else:
            f.write("Nessun commento vuoto gestito.\n\n")

        # Esempi anomalie
        f.write("### 2.3 Anomalie Flaggate\n\n")

        anomaly_examples = []
        for stats in all_stats.values():
            anomaly_examples.extend(stats['examples_anomaly'][:3])

        if anomaly_examples:
            for i, ex in enumerate(anomaly_examples[:10], 1):
                f.write(f"**Esempio {i}:**\n")
                f.write(f"- **Commento:** `{ex['comment']}`\n")
                f.write(f"- **Riga:** {ex['row']}\n\n")
        else:
            f.write("Nessuna anomalia flaggata.\n\n")

        # Dettaglio per file
        f.write("## 3. DETTAGLIO PER FILE\n\n")
        f.write("| File | Righe | Typo | Vuoti Gestiti | Anomalie |\n")
        f.write("|------|-------|------|---------------|----------|\n")

        for filename, stats in sorted(all_stats.items()):
            typo_count = sum(stats['typo_corrections'].values())
            f.write(f"| {filename} | {stats['total_rows']} | {typo_count} | ")
            f.write(f"{stats['empty_handled']} | {stats['anomalies_flagged']} |\n")

        f.write("\n---\n\n")
        f.write("**Note:**\n")
        f.write("- I commenti con flag_revisione o flag_anomalia sono stati salvati in ")
        f.write("data/metadata/anomalie_da_verificare.csv\n")
        f.write("- Per i file 2018, i commenti vuoti con punteggio 6.5-7.5 sono stati ")
        f.write("compilati con 'nella norma'\n")

    logger.info("Report generato con successo")


def main():
    """Funzione principale dello script."""
    logger.info("="*80)
    logger.info("INIZIO PULIZIA FASE B - Commenti Grana Trentino")
    logger.info("="*80)

    try:
        # Trova tutti i CSV da processare
        csv_files = list(INPUT_DIR.glob("*_cleaned.csv"))
        logger.info(f"Trovati {len(csv_files)} file CSV da processare")

        all_statistics = {}
        all_dataframes = []

        # Processa ogni file
        for csv_file in sorted(csv_files):
            df_clean, stats = process_csv_file(csv_file)

            # Salva il file pulito
            output_filename = csv_file.stem.replace('_cleaned', '') + "_fase_B.csv"
            output_path = OUTPUT_DIR / output_filename
            df_clean.to_csv(output_path, index=False, encoding='utf-8')
            logger.info(f"  Salvato in: {output_path}")

            all_statistics[csv_file.name] = stats
            all_dataframes.append(df_clean)

        # Genera file anomalie
        anomalies_path = METADATA_DIR / "anomalie_da_verificare.csv"
        generate_anomalies_file(all_dataframes, anomalies_path)

        # Genera report
        report_path = REPORTS_DIR / "03_pulizia_fase_B.md"
        generate_report(all_statistics, report_path)

        # Statistiche finali
        logger.info("="*80)
        logger.info("STATISTICHE FINALI")
        logger.info("="*80)

        total_typo = sum(sum(s['typo_corrections'].values()) for s in all_statistics.values())
        total_empty = sum(s['empty_handled'] for s in all_statistics.values())
        total_empty_filled = sum(s['empty_filled'] for s in all_statistics.values())
        total_empty_low = sum(s['empty_review_low'] for s in all_statistics.values())
        total_empty_high = sum(s['empty_review_high'] for s in all_statistics.values())
        total_anomalies = sum(s['anomalies_flagged'] for s in all_statistics.values())

        logger.info(f"Totale typo corretti: {total_typo}")
        logger.info(f"Totale commenti vuoti 2018 gestiti: {total_empty}")
        logger.info(f"  - Compilati con 'nella norma': {total_empty_filled}")
        logger.info(f"  - Flaggati (punteggio basso): {total_empty_low}")
        logger.info(f"  - Flaggati (punteggio alto): {total_empty_high}")
        logger.info(f"Totale anomalie flaggate: {total_anomalies}")

        logger.info("="*80)
        logger.info("PULIZIA FASE B COMPLETATA CON SUCCESSO")
        logger.info(f"Output salvato in: {OUTPUT_DIR}")
        logger.info(f"Anomalie salvate in: {anomalies_path}")
        logger.info(f"Report salvato in: {report_path}")
        logger.info("="*80)

    except Exception as e:
        logger.error(f"Errore durante elaborazione: {e}", exc_info=True)
        raise

if __name__ == "__main__":
    main()
