"""
Nome Script: Pulizia Commenti Grana Trentino - Fase A (Pulizia Minima)
Scopo: Applicare pulizie minime su commenti per renderli leggibili e consistenti
Input: CSV da "07_captioning risultati grana Trentino/GT commenti liberi/csv dataset/"
Output: CSV puliti in data/interim/fase_A/ + report in reports/ + log dettagliato

Autore: Claude Code
Data: 2026-02-13

Fase A include:
- Encoding (sostituire \xa0, rimuovere doppi spazi, strip)
- Espansione abbreviazioni comuni (leg, legg, abb, sol, piu)
- Correzione apostrofi (intensita' → intensità, ecc.)
- Rimozione punti finali isolati
- Gestione nan
- Capitalizzazione attributi
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
        logging.FileHandler(LOG_DIR / 'fase_A_cleaning.log', mode='w', encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Costanti
PROJECT_ROOT = Path(__file__).parent.parent.parent
DATA_DIR = PROJECT_ROOT / "07_captioning risultati grana Trentino" / "GT commenti liberi" / "csv dataset"
OUTPUT_DIR = PROJECT_ROOT / "data" / "interim" / "fase_A"
REPORTS_DIR = PROJECT_ROOT / "reports"

# Assicurarsi che le directory esistano
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
REPORTS_DIR.mkdir(parents=True, exist_ok=True)


def clean_encoding(text: str) -> Tuple[str, bool]:
    """
    Pulisce problemi di encoding e spazi.

    Args:
        text: Testo da pulire

    Returns:
        Tupla (testo_pulito, modificato)
    """
    if pd.isna(text) or text == '' or str(text).lower() == 'nan':
        return '', False

    original = str(text)
    cleaned = original

    # Sostituire \xa0 (non-breaking space) con spazio normale
    cleaned = cleaned.replace('\xa0', ' ')
    cleaned = cleaned.replace('\u00a0', ' ')

    # Rimuovere doppi/multipli spazi → spazio singolo
    cleaned = re.sub(r'\s+', ' ', cleaned)

    # Strip inizio e fine
    cleaned = cleaned.strip()

    modified = (cleaned != original)
    return cleaned, modified


def expand_abbreviations(text: str) -> Tuple[str, List[str]]:
    """
    Espande abbreviazioni comuni usando word boundaries.

    Args:
        text: Testo da processare

    Returns:
        Tupla (testo_espanso, lista_modifiche_applicate)
    """
    if not text:
        return text, []

    modifications = []
    result = text

    # \b = word boundary, assicura che siano parole intere

    # leg → leggermente (solo parola intera, non in "allegro")
    pattern = r'\bleg\b'
    if re.search(pattern, result, re.IGNORECASE):
        result = re.sub(pattern, 'leggermente', result, flags=re.IGNORECASE)
        modifications.append('leg→leggermente')

    # legg → leggermente (variante)
    pattern = r'\blegg\b'
    if re.search(pattern, result, re.IGNORECASE):
        result = re.sub(pattern, 'leggermente', result, flags=re.IGNORECASE)
        modifications.append('legg→leggermente')

    # legg. → leggermente (con punto)
    pattern = r'\blegg\.\b'
    if re.search(pattern, result, re.IGNORECASE):
        result = re.sub(pattern, 'leggermente', result, flags=re.IGNORECASE)
        modifications.append('legg.→leggermente')

    # abb → abbastanza (solo parola intera)
    pattern = r'\babb\b'
    if re.search(pattern, result, re.IGNORECASE):
        result = re.sub(pattern, 'abbastanza', result, flags=re.IGNORECASE)
        modifications.append('abb→abbastanza')

    # sol → solubile (solo parola intera, NON in "solubile" già intero)
    pattern = r'\bsol\b'
    if re.search(pattern, result, re.IGNORECASE):
        # Verifica che non sia già "solubile" o "solubilità"
        if not re.search(r'\bsolubil', result, re.IGNORECASE):
            result = re.sub(pattern, 'solubile', result, flags=re.IGNORECASE)
            modifications.append('sol→solubile')

    # piu' → più (con apostrofo finale - da fare PRIMA di "piu" senza apostrofo)
    pattern = r"\bpiu'"
    if re.search(pattern, result, re.IGNORECASE):
        result = re.sub(pattern, 'più', result, flags=re.IGNORECASE)
        modifications.append("piu'→più")

    # piu → più (solo parola intera, non in "piuma")
    pattern = r'\bpiu\b'
    if re.search(pattern, result, re.IGNORECASE):
        result = re.sub(pattern, 'più', result, flags=re.IGNORECASE)
        modifications.append('piu→più')

    return result, modifications


def fix_apostrophes(text: str) -> Tuple[str, List[str]]:
    """
    Corregge apostrofi mancanti in parole comuni.

    Args:
        text: Testo da correggere

    Returns:
        Tupla (testo_corretto, lista_modifiche_applicate)
    """
    if not text:
        return text, []

    modifications = []
    result = text

    # intensita' → intensità
    if "intensita'" in result or "intensita " in result.lower():
        result = re.sub(r"intensita['\s]", 'intensità ', result, flags=re.IGNORECASE)
        modifications.append("intensita'→intensità")

    # sapidit' → sapidità
    if "sapidit'" in result or "sapidit " in result.lower():
        result = re.sub(r"sapidit['\s]", 'sapidità ', result, flags=re.IGNORECASE)
        modifications.append("sapidit'→sapidità")

    # solubilit' → solubilità
    if "solubilit'" in result or "solubilit " in result.lower():
        result = re.sub(r"solubilit['\s]", 'solubilità ', result, flags=re.IGNORECASE)
        modifications.append("solubilit'→solubilità")

    # friabilit' → friabilità
    if "friabilit'" in result or "friabilit " in result.lower():
        result = re.sub(r"friabilit['\s]", 'friabilità ', result, flags=re.IGNORECASE)
        modifications.append("friabilit'→friabilità")

    # umidit' → umidità
    if "umidit'" in result or "umidit " in result.lower():
        result = re.sub(r"umidit['\s]", 'umidità ', result, flags=re.IGNORECASE)
        modifications.append("umidit'→umidità")

    # Pulisce eventuali doppi spazi creati
    result = re.sub(r'\s+', ' ', result).strip()

    return result, modifications


def remove_final_dots(text: str) -> Tuple[str, bool]:
    """
    Rimuove punti finali isolati inappropriati.

    Args:
        text: Testo da processare

    Returns:
        Tupla (testo_senza_punti_finali, modificato)
    """
    if not text:
        return text, False

    original = text

    # Rimuove punto finale solo se isolato (non in abbreviazioni tipo "es." o "etc.")
    # Pattern: punto finale seguito da nulla o spazi
    if text.endswith('.'):
        # Verifica che non sia un'abbreviazione valida come "mm." o "cm."
        # Se l'ultima parola è più lunga di 3 caratteri, probabilmente il punto è inappropriato
        words = text.rstrip('.').split()
        if words:
            last_word = words[-1]
            # Se ultima parola > 3 caratteri O è parola comune (fine, sale, ecc), rimuovi punto
            if len(last_word) > 3 or last_word.lower() in ['fine', 'sale', 'dolce', 'buona', 'bella']:
                text = text.rstrip('.')

    modified = (text != original)
    return text, modified


def standardize_attribute_names(df: pd.DataFrame, filename: str) -> pd.DataFrame:
    """
    Standardizza la capitalizzazione dei nomi degli attributi.

    Args:
        df: DataFrame da processare
        filename: Nome del file per determinare l'attributo

    Returns:
        DataFrame con nomi attributi standardizzati
    """
    # Mapping standardizzato
    standard_names = {
        'profumo': 'Profumo',
        'sapore': 'Sapore',
        'aroma': 'Aroma',
        'texture': 'Texture',
        'spessore della crosta': 'Spessore della Crosta',
        'spessore della Crosta': 'Spessore della Crosta',
        'struttura della pasta': 'Struttura della Pasta',
        'struttura della Pasta': 'Struttura della Pasta',
        'colore della pasta': 'Colore della Pasta',
        'colore della Pasta': 'Colore della Pasta',
    }

    # Per file 2018, potrebbe esserci una colonna con nome attributo
    for col in df.columns:
        col_lower = col.strip().lower()
        if col_lower in standard_names:
            df = df.rename(columns={col: standard_names[col_lower]})

    return df


def process_comment(text: str) -> Tuple[str, Dict[str, Any]]:
    """
    Applica tutte le pulizie Fase A a un singolo commento.

    Args:
        text: Commento da pulire

    Returns:
        Tupla (commento_pulito, dizionario_statistiche)
    """
    stats = {
        'encoding_fixed': False,
        'abbreviations': [],
        'apostrophes': [],
        'final_dot_removed': False,
        'was_nan': False
    }

    # 1. Gestione nan
    if pd.isna(text) or str(text).lower() == 'nan':
        stats['was_nan'] = True
        return '', stats

    # 2. Pulizia encoding
    text, encoding_fixed = clean_encoding(text)
    stats['encoding_fixed'] = encoding_fixed

    if not text:
        return '', stats

    # 3. Espansione abbreviazioni
    text, abbrev_mods = expand_abbreviations(text)
    stats['abbreviations'] = abbrev_mods

    # 4. Correzione apostrofi
    text, apost_mods = fix_apostrophes(text)
    stats['apostrophes'] = apost_mods

    # 5. Rimozione punti finali
    text, dot_removed = remove_final_dots(text)
    stats['final_dot_removed'] = dot_removed

    # 6. Pulizia finale spazi
    text = text.strip()

    return text, stats


def process_csv_file(filepath: Path) -> Tuple[pd.DataFrame, pd.DataFrame, Dict[str, Any]]:
    """
    Processa un singolo file CSV applicando le pulizie Fase A.

    Args:
        filepath: Path del file CSV da processare

    Returns:
        Tupla (df_originale, df_pulito, statistiche)
    """
    logger.info(f"Processando {filepath.name}...")

    # Carica CSV
    try:
        df_original = pd.read_csv(filepath, encoding='utf-8')
    except UnicodeDecodeError:
        df_original = pd.read_csv(filepath, encoding='latin-1')

    df_clean = df_original.copy()

    # Standardizza nomi attributi
    df_clean = standardize_attribute_names(df_clean, filepath.name)

    # Determina la colonna dei commenti
    comment_col = None
    for col in df_clean.columns:
        if 'commenti' in col.lower():
            comment_col = col
            break

    if comment_col is None:
        logger.warning(f"Colonna 'Commenti' non trovata in {filepath.name}")
        return df_original, df_clean, {}

    # Statistiche
    stats = {
        'total_rows': len(df_clean),
        'total_modifications': 0,
        'encoding_fixes': 0,
        'abbreviation_expansions': Counter(),
        'apostrophe_fixes': Counter(),
        'final_dots_removed': 0,
        'nan_replaced': 0,
        'unchanged_comments': 0,
        'examples_by_type': defaultdict(list)
    }

    # Processa ogni commento
    for idx, row in df_clean.iterrows():
        original_comment = row[comment_col]
        cleaned_comment, comment_stats = process_comment(original_comment)

        df_clean.at[idx, comment_col] = cleaned_comment

        # Aggiorna statistiche
        if comment_stats['was_nan']:
            stats['nan_replaced'] += 1
            stats['examples_by_type']['nan_replaced'].append({
                'original': str(original_comment),
                'cleaned': cleaned_comment,
                'row': idx
            })

        if comment_stats['encoding_fixed']:
            stats['encoding_fixes'] += 1
            stats['total_modifications'] += 1
            if len(stats['examples_by_type']['encoding_fixed']) < 10:
                stats['examples_by_type']['encoding_fixed'].append({
                    'original': str(original_comment),
                    'cleaned': cleaned_comment,
                    'row': idx
                })

        for abbrev in comment_stats['abbreviations']:
            stats['abbreviation_expansions'][abbrev] += 1
            stats['total_modifications'] += 1
            if len(stats['examples_by_type'][f'abbrev_{abbrev}']) < 10:
                stats['examples_by_type'][f'abbrev_{abbrev}'].append({
                    'original': str(original_comment),
                    'cleaned': cleaned_comment,
                    'row': idx
                })

        for apost in comment_stats['apostrophes']:
            stats['apostrophe_fixes'][apost] += 1
            stats['total_modifications'] += 1
            if len(stats['examples_by_type'][f'apostrophe_{apost}']) < 10:
                stats['examples_by_type'][f'apostrophe_{apost}'].append({
                    'original': str(original_comment),
                    'cleaned': cleaned_comment,
                    'row': idx
                })

        if comment_stats['final_dot_removed']:
            stats['final_dots_removed'] += 1
            stats['total_modifications'] += 1
            if len(stats['examples_by_type']['final_dot_removed']) < 10:
                stats['examples_by_type']['final_dot_removed'].append({
                    'original': str(original_comment),
                    'cleaned': cleaned_comment,
                    'row': idx
                })

        # Conta commenti non modificati
        if str(original_comment) == str(cleaned_comment):
            stats['unchanged_comments'] += 1

    logger.info(f"  - {stats['total_modifications']} modifiche totali su {stats['total_rows']} righe")

    return df_original, df_clean, stats


def generate_report(all_stats: Dict[str, Dict], output_path: Path):
    """
    Genera un report markdown con le statistiche di pulizia.

    Args:
        all_stats: Dizionario con statistiche per ogni file
        output_path: Path dove salvare il report
    """
    logger.info(f"Generando report in {output_path}...")

    with open(output_path, 'w', encoding='utf-8') as f:
        f.write("# REPORT PULIZIA FASE A - Commenti Grana Trentino\n\n")
        f.write(f"**Data elaborazione:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
        f.write("---\n\n")

        # Statistiche aggregate
        f.write("## 1. STATISTICHE AGGREGATE\n\n")

        total_rows = sum(s['total_rows'] for s in all_stats.values())
        total_mods = sum(s['total_modifications'] for s in all_stats.values())
        total_encoding = sum(s['encoding_fixes'] for s in all_stats.values())
        total_dots = sum(s['final_dots_removed'] for s in all_stats.values())
        total_nan = sum(s['nan_replaced'] for s in all_stats.values())

        f.write(f"- **Righe totali processate:** {total_rows}\n")
        f.write(f"- **Modifiche totali applicate:** {total_mods}\n")
        f.write(f"- **Encoding fixes (\\xa0, spazi):** {total_encoding}\n")
        f.write(f"- **Punti finali rimossi:** {total_dots}\n")
        f.write(f"- **Valori 'nan' sostituiti:** {total_nan}\n\n")

        # Abbreviazioni
        f.write("### 1.1 Espansioni Abbreviazioni\n\n")
        all_abbrevs = Counter()
        for stats in all_stats.values():
            all_abbrevs.update(stats['abbreviation_expansions'])

        f.write("| Abbreviazione | Espansione | Occorrenze |\n")
        f.write("|---------------|------------|------------|\n")
        for abbrev, count in all_abbrevs.most_common():
            parts = abbrev.split('→')
            f.write(f"| {parts[0]} | {parts[1]} | {count} |\n")
        f.write("\n")

        # Apostrofi
        f.write("### 1.2 Correzioni Apostrofi\n\n")
        all_apostrophes = Counter()
        for stats in all_stats.values():
            all_apostrophes.update(stats['apostrophe_fixes'])

        f.write("| Forma Errata | Forma Corretta | Occorrenze |\n")
        f.write("|--------------|----------------|------------|\n")
        for apost, count in all_apostrophes.most_common():
            parts = apost.split('→')
            f.write(f"| {parts[0]} | {parts[1]} | {count} |\n")
        f.write("\n")

        # Esempi per tipo di modifica
        f.write("## 2. ESEMPI DI MODIFICHE\n\n")

        # Raccogli esempi da tutti i file
        examples_by_type = defaultdict(list)
        for stats in all_stats.values():
            for example_type, examples in stats['examples_by_type'].items():
                examples_by_type[example_type].extend(examples[:3])  # Max 3 per file

        # Encoding fixes
        if examples_by_type['encoding_fixed']:
            f.write("### 2.1 Encoding Fixes (\\xa0, doppi spazi)\n\n")
            for i, ex in enumerate(examples_by_type['encoding_fixed'][:10], 1):
                f.write(f"**Esempio {i}:**\n")
                f.write(f"- **Prima:** `{ex['original']}`\n")
                f.write(f"- **Dopo:** `{ex['cleaned']}`\n\n")

        # Abbreviazioni
        abbrev_types = [k for k in examples_by_type.keys() if k.startswith('abbrev_')]
        if abbrev_types:
            f.write("### 2.2 Espansioni Abbreviazioni\n\n")
            for abbrev_type in sorted(abbrev_types)[:5]:  # Top 5 tipi
                examples = examples_by_type[abbrev_type][:5]
                abbrev_name = abbrev_type.replace('abbrev_', '')
                f.write(f"**{abbrev_name}:**\n\n")
                for i, ex in enumerate(examples, 1):
                    f.write(f"{i}. Prima: `{ex['original']}` → Dopo: `{ex['cleaned']}`\n")
                f.write("\n")

        # Apostrofi
        apost_types = [k for k in examples_by_type.keys() if k.startswith('apostrophe_')]
        if apost_types:
            f.write("### 2.3 Correzioni Apostrofi\n\n")
            for apost_type in sorted(apost_types):
                examples = examples_by_type[apost_type][:5]
                apost_name = apost_type.replace('apostrophe_', '')
                f.write(f"**{apost_name}:**\n\n")
                for i, ex in enumerate(examples, 1):
                    f.write(f"{i}. Prima: `{ex['original']}` → Dopo: `{ex['cleaned']}`\n")
                f.write("\n")

        # Punti finali
        if examples_by_type['final_dot_removed']:
            f.write("### 2.4 Rimozione Punti Finali\n\n")
            for i, ex in enumerate(examples_by_type['final_dot_removed'][:10], 1):
                f.write(f"**Esempio {i}:**\n")
                f.write(f"- **Prima:** `{ex['original']}`\n")
                f.write(f"- **Dopo:** `{ex['cleaned']}`\n\n")

        # Commenti già puliti
        f.write("## 3. COMMENTI NON MODIFICATI\n\n")
        total_unchanged = sum(s['unchanged_comments'] for s in all_stats.values())
        pct_unchanged = (total_unchanged / total_rows * 100) if total_rows > 0 else 0
        f.write(f"**Totale commenti già puliti:** {total_unchanged} ({pct_unchanged:.1f}%)\n\n")
        f.write("Questi commenti non hanno richiesto alcuna modifica, indicando che erano già\n")
        f.write("ben formattati o che non contenevano abbreviazioni/errori comuni.\n\n")

        # Statistiche per file
        f.write("## 4. DETTAGLIO PER FILE\n\n")
        f.write("| File | Righe | Modifiche | Encoding | Abbreviazioni | Apostrofi | Punti |\n")
        f.write("|------|-------|-----------|----------|---------------|-----------|-------|\n")

        for filename, stats in sorted(all_stats.items()):
            total_abbrev = sum(stats['abbreviation_expansions'].values())
            total_apost = sum(stats['apostrophe_fixes'].values())
            f.write(f"| {filename} | {stats['total_rows']} | {stats['total_modifications']} | ")
            f.write(f"{stats['encoding_fixes']} | {total_abbrev} | {total_apost} | {stats['final_dots_removed']} |\n")

        f.write("\n---\n\n")
        f.write("**Note:**\n")
        f.write("- Modifiche totali possono includere più interventi sullo stesso commento\n")
        f.write("- I commenti vuoti ('nan') sono stati sostituiti con stringhe vuote\n")
        f.write("- Le abbreviazioni sono state espanse usando word boundaries per evitare falsi positivi\n")

    logger.info("Report generato con successo")


def main():
    """Funzione principale dello script."""
    logger.info("="*80)
    logger.info("INIZIO PULIZIA FASE A - Commenti Grana Trentino")
    logger.info("="*80)

    try:
        # Trova tutti i CSV da processare (escludi il file delle date)
        csv_files = [
            f for f in DATA_DIR.glob("*.csv")
            if 'date_sedute' not in f.name.lower()
        ]

        logger.info(f"Trovati {len(csv_files)} file CSV da processare")

        all_statistics = {}

        # Processa ogni file
        for csv_file in sorted(csv_files):
            df_original, df_clean, stats = process_csv_file(csv_file)

            # Salva il file pulito
            output_filename = csv_file.stem + "_cleaned.csv"
            output_path = OUTPUT_DIR / output_filename
            df_clean.to_csv(output_path, index=False, encoding='utf-8')
            logger.info(f"  Salvato in: {output_path}")

            all_statistics[csv_file.name] = stats

        # Genera report
        report_path = REPORTS_DIR / "02_pulizia_fase_A.md"
        generate_report(all_statistics, report_path)

        logger.info("="*80)
        logger.info("PULIZIA FASE A COMPLETATA CON SUCCESSO")
        logger.info(f"Output salvato in: {OUTPUT_DIR}")
        logger.info(f"Report salvato in: {report_path}")
        logger.info("="*80)

    except Exception as e:
        logger.error(f"Errore durante elaborazione: {e}", exc_info=True)
        raise

if __name__ == "__main__":
    main()
