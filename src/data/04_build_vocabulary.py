"""
Nome Script: Costruzione Vocabolario Controllato
Scopo: Analizzare i commenti puliti e costruire un vocabolario controllato con categorizzazione
Input: CSV puliti da data/interim/fase_A/
Output: data/metadata/vocabolario_controllato.csv + report in reports/

Autore: Claude Code
Data: 2026-02-13

Il vocabolario include:
- Conteggio occorrenze per termine
- Distribuzione per anno e attributo
- Categorizzazione automatica (tecnico_caseario, stopword, modificatore, ecc.)
- Decisione mantieni/sostituisci basata su soglia frequenza
"""

import logging
from pathlib import Path
from typing import List, Dict, Any, Set, Tuple
import pandas as pd
import re
from collections import defaultdict, Counter
from datetime import datetime
import json

# Setup logging
LOG_DIR = Path("logs")
LOG_DIR.mkdir(exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(LOG_DIR / '04_vocabulary_building.log', mode='w', encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Costanti
PROJECT_ROOT = Path(__file__).parent.parent.parent
INPUT_DIR = PROJECT_ROOT / "data" / "interim" / "fase_A"
OUTPUT_DIR = PROJECT_ROOT / "data" / "metadata"
REPORTS_DIR = PROJECT_ROOT / "reports"

# Assicurarsi che le directory esistano
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
REPORTS_DIR.mkdir(parents=True, exist_ok=True)

# Soglia di frequenza per mantenere un termine
FREQUENCY_THRESHOLD = 5

# TERMINI TECNICI CASEARI (da regole-pulizia-testo.md sezione 3)
TERMINI_TECNICI_CASEARI = {
    # Anatomia della forma
    'scalzo', 'scalzi', 'piatti', 'piatto', 'sottocrosta', 'angoli', 'spigoli',

    # Caratteristiche struttura
    'microocchiatura', 'occhiatura', 'grana', 'frattura', 'stirata',
    'cristalli', 'tirosina', 'granulosa', 'granuloso', 'grossolana',

    # Riferimenti a formaggi/processi
    'nostrano', 'insilato', 'gorgonzola',

    # Altri termini specialistici
    'solubile', 'solubilità', 'friabile', 'friabilità',
    'compatto', 'compattezza', 'cedevole'
}

# STOPWORDS ITALIANE COMUNI
STOPWORDS_ITALIANE = {
    'il', 'lo', 'la', 'i', 'gli', 'le', 'un', 'uno', 'una',
    'di', 'da', 'in', 'con', 'su', 'per', 'tra', 'fra',
    'a', 'al', 'allo', 'alla', 'ai', 'agli', 'alle',
    'del', 'dello', 'della', 'dei', 'degli', 'delle',
    'dal', 'dallo', 'dalla', 'dai', 'dagli', 'dalle',
    'nel', 'nello', 'nella', 'nei', 'negli', 'nelle',
    'sul', 'sullo', 'sulla', 'sui', 'sugli', 'sulle',
    'e', 'o', 'ma', 'però', 'anche', 'oppure',
    'non', 'né', 'neanche', 'nemmeno', 'neppure',
    'che', 'cui', 'quale', 'quali',
    'questo', 'questa', 'questi', 'queste',
    'quello', 'quella', 'quelli', 'quelle',
    'si', 'ci', 'vi', 'ne',
    'mi', 'ti', 'lo', 'la', 'li', 'le',
    'mio', 'tuo', 'suo', 'nostro', 'vostro', 'loro',
    'più', 'meno', 'molto', 'poco', 'tanto', 'troppo',
    'tutto', 'tutti', 'tutta', 'tutte',
    'altro', 'altra', 'altri', 'altre',
    'stesso', 'stessa', 'stessi', 'stesse',
    'ogni', 'qualche', 'alcuni', 'alcune',
    'essere', 'avere', 'fare', 'stare', 'dare', 'andare'
}

# MODIFICATORI (intensità, quantità, ecc.)
MODIFICATORI = {
    'troppo', 'leggermente', 'abbastanza', 'molto', 'poco',
    'appena', 'quasi', 'eccessivamente', 'lievemente',
    'estremamente', 'moderatamente', 'parecchio', 'assai',
    'ben', 'bene', 'male', 'discretamente'
}

# TERMINI DI GIUDIZIO
TERMINI_GIUDIZIO = {
    'buono', 'buona', 'buoni', 'buone',
    'ottimo', 'ottima', 'ottimi', 'ottime',
    'bello', 'bella', 'belli', 'belle',
    'brutto', 'brutta', 'brutti', 'brutte',
    'eccellente', 'eccellenti',
    'difettoso', 'difettosa', 'difettosi', 'difettose',
    'negativo', 'negativa', 'negativi', 'negative',
    'positivo', 'positiva', 'positivi', 'positive',
    'scarso', 'scarsa', 'scarsi', 'scarse',
    'pessimo', 'pessima', 'pessimi', 'pessime',
    'accettabile', 'accettabili',
    'sufficiente', 'sufficienti',
    'insufficiente', 'insufficienti'
}


def tokenize_text(text: str) -> List[str]:
    """
    Tokenizza un testo in parole singole.

    Args:
        text: Testo da tokenizzare

    Returns:
        Lista di token in minuscolo
    """
    if pd.isna(text) or not text:
        return []

    # Converti in minuscolo
    text = str(text).lower()

    # Sostituisci punteggiatura con spazi (preserva apostrofi interni come in "all'apertura")
    # Pattern: sostituisci punteggiatura ma non apostrofi tra lettere
    text = re.sub(r'[,;:!?.()\[\]{}"«»]', ' ', text)

    # Split su spazi
    tokens = text.split()

    # Filtra token
    filtered_tokens = []
    for token in tokens:
        # Rimuovi token vuoti
        if not token:
            continue

        # Rimuovi token < 2 caratteri (eccetto "è", "e", "o", "a")
        if len(token) < 2 and token not in ['è', 'e', 'o', 'a']:
            continue

        # Rimuovi numeri puri (ma non "5mm" o "2cm")
        if token.replace('.', '').replace(',', '').isdigit():
            continue

        filtered_tokens.append(token)

    return filtered_tokens


def extract_year_from_filename(filename: str) -> str:
    """
    Estrae l'anno dal nome del file.

    Args:
        filename: Nome del file

    Returns:
        Anno come stringa ('2018', '2019', '2020', '2021')
    """
    if '2018' in filename:
        return '2018'
    elif '2019' in filename:
        return '2019'
    elif '2020' in filename:
        return '2020'
    elif '2021' in filename:
        return '2021'
    else:
        return 'unknown'


def extract_attribute_from_filename(filename: str) -> str:
    """
    Estrae l'attributo sensoriale dal nome del file.

    Args:
        filename: Nome del file

    Returns:
        Attributo in minuscolo ('profumo', 'sapore', ecc.)
    """
    filename_lower = filename.lower()

    if 'profumo' in filename_lower:
        return 'profumo'
    elif 'sapore' in filename_lower:
        return 'sapore'
    elif 'aroma' in filename_lower:
        return 'aroma'
    elif 'texture' in filename_lower:
        return 'texture'
    elif 'spessore' in filename_lower:
        return 'spessore_crosta'
    elif 'struttura' in filename_lower:
        return 'struttura_pasta'
    elif 'colore' in filename_lower:
        return 'colore_pasta'
    else:
        return 'unknown'


def categorize_term(term: str, frequency: int) -> Tuple[str, str]:
    """
    Categorizza un termine e determina se mantenerlo o sostituirlo.

    Args:
        term: Termine da categorizzare
        frequency: Frequenza del termine

    Returns:
        Tupla (categoria, decisione)
    """
    # 1. Termini tecnici caseari → mantieni sempre
    if term in TERMINI_TECNICI_CASEARI:
        return 'tecnico_caseario', 'mantieni'

    # 2. Stopwords → ignora
    if term in STOPWORDS_ITALIANE:
        return 'stopword', 'ignora'

    # 3. Modificatori
    if term in MODIFICATORI:
        return 'modificatore', 'mantieni'

    # 4. Termini di giudizio
    if term in TERMINI_GIUDIZIO:
        return 'giudizio', 'mantieni'

    # 5. Misure (contiene mm, cm, ml o solo cifre+lettera)
    if re.search(r'\d+(mm|cm|ml|kg|g)', term) or re.match(r'\d+[a-z]+', term):
        return 'misura', 'mantieni'

    # 6. Frequenza < soglia → sostituisci
    if frequency < FREQUENCY_THRESHOLD:
        return 'sconosciuto', 'sostituisci'

    # 7. Frequenza >= soglia → mantieni (da categorizzare manualmente)
    return 'sconosciuto', 'mantieni'


def build_vocabulary(input_dir: Path) -> pd.DataFrame:
    """
    Costruisce il vocabolario controllato dai file CSV puliti.

    Args:
        input_dir: Directory contenente i CSV puliti

    Returns:
        DataFrame con il vocabolario
    """
    logger.info("Inizio costruzione vocabolario...")

    # Strutture dati per conteggi
    term_counts = Counter()  # Conteggio totale
    term_files = defaultdict(set)  # Set di file in cui appare ogni termine
    term_years = defaultdict(lambda: defaultdict(int))  # Conteggio per anno
    term_attributes = defaultdict(lambda: defaultdict(int))  # Conteggio per attributo

    # Carica tutti i CSV
    csv_files = list(input_dir.glob("*_cleaned.csv"))
    logger.info(f"Trovati {len(csv_files)} file CSV da processare")

    for csv_file in csv_files:
        logger.info(f"  Processando {csv_file.name}...")

        # Carica CSV
        try:
            df = pd.read_csv(csv_file, encoding='utf-8')
        except UnicodeDecodeError:
            df = pd.read_csv(csv_file, encoding='latin-1')

        # Trova colonna commenti
        comment_col = None
        for col in df.columns:
            if 'commenti' in col.lower():
                comment_col = col
                break

        if comment_col is None:
            logger.warning(f"  Colonna 'Commenti' non trovata in {csv_file.name}")
            continue

        # Estrai anno e attributo
        year = extract_year_from_filename(csv_file.name)
        attribute = extract_attribute_from_filename(csv_file.name)

        # Processa ogni commento
        for idx, row in df.iterrows():
            comment = row[comment_col]
            tokens = tokenize_text(comment)

            for token in tokens:
                term_counts[token] += 1
                term_files[token].add(csv_file.name)
                term_years[token][year] += 1
                term_attributes[token][attribute] += 1

    logger.info(f"Trovati {len(term_counts)} termini unici")

    # Costruisci DataFrame
    vocabulary_data = []

    for term, total_count in term_counts.items():
        # Conteggi per anno
        occ_2018 = term_years[term].get('2018', 0)
        occ_2019 = term_years[term].get('2019', 0)
        occ_2020 = term_years[term].get('2020', 0)
        occ_2021 = term_years[term].get('2021', 0)

        # Conteggi per attributo (come JSON)
        occ_per_attributo = dict(term_attributes[term])

        # Categorizzazione
        categoria, decisione = categorize_term(term, total_count)

        vocabulary_data.append({
            'termine': term,
            'occorrenze_totali': total_count,
            'n_file_distinti': len(term_files[term]),
            'occ_2018': occ_2018,
            'occ_2019': occ_2019,
            'occ_2020': occ_2020,
            'occ_2021': occ_2021,
            'occ_per_attributo': json.dumps(occ_per_attributo, ensure_ascii=False),
            'categoria': categoria,
            'decisione': decisione,
            'categoria_padre': '',  # Da compilare manualmente
            'note': ''  # Campo libero
        })

    df_vocabulary = pd.DataFrame(vocabulary_data)

    # Ordina per occorrenze totali decrescenti
    df_vocabulary = df_vocabulary.sort_values('occorrenze_totali', ascending=False)

    logger.info("Vocabolario costruito con successo")

    return df_vocabulary


def generate_report(df_vocab: pd.DataFrame, output_path: Path):
    """
    Genera un report markdown sul vocabolario.

    Args:
        df_vocab: DataFrame del vocabolario
        output_path: Path dove salvare il report
    """
    logger.info(f"Generando report in {output_path}...")

    with open(output_path, 'w', encoding='utf-8') as f:
        f.write("# REPORT VOCABOLARIO CONTROLLATO - Commenti Grana Trentino\n\n")
        f.write(f"**Data elaborazione:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
        f.write("---\n\n")

        # Statistiche generali
        f.write("## 1. STATISTICHE GENERALI\n\n")

        total_terms = len(df_vocab)
        mantieni = len(df_vocab[df_vocab['decisione'] == 'mantieni'])
        sostituisci = len(df_vocab[df_vocab['decisione'] == 'sostituisci'])
        ignora = len(df_vocab[df_vocab['decisione'] == 'ignora'])

        f.write(f"- **Termini unici totali:** {total_terms}\n")
        f.write(f"- **Decisione 'mantieni':** {mantieni} ({mantieni/total_terms*100:.1f}%)\n")
        f.write(f"- **Decisione 'sostituisci':** {sostituisci} ({sostituisci/total_terms*100:.1f}%)\n")
        f.write(f"- **Decisione 'ignora' (stopwords):** {ignora} ({ignora/total_terms*100:.1f}%)\n\n")

        # Breakdown per categoria
        f.write("### 1.1 Breakdown per Categoria\n\n")
        f.write("| Categoria | Count | % |\n")
        f.write("|-----------|-------|---|\n")

        for cat, count in df_vocab['categoria'].value_counts().items():
            pct = count / total_terms * 100
            f.write(f"| {cat} | {count} | {pct:.1f}% |\n")
        f.write("\n")

        # Top 30 termini
        f.write("## 2. TOP 30 TERMINI PER FREQUENZA\n\n")
        f.write("| Termine | Occorrenze | Categoria | Decisione |\n")
        f.write("|---------|-----------|-----------|----------|\n")

        for idx, row in df_vocab.head(30).iterrows():
            f.write(f"| {row['termine']} | {row['occorrenze_totali']} | {row['categoria']} | {row['decisione']} |\n")
        f.write("\n")

        # Termini tecnici caseari trovati
        f.write("## 3. TERMINI TECNICI CASEARI TROVATI\n\n")
        tecnici_found = df_vocab[df_vocab['categoria'] == 'tecnico_caseario']
        f.write(f"**Totale termini tecnici trovati:** {len(tecnici_found)}\n\n")

        if len(tecnici_found) > 0:
            f.write("| Termine | Occorrenze | File Distinti |\n")
            f.write("|---------|-----------|---------------|\n")
            for idx, row in tecnici_found.sort_values('occorrenze_totali', ascending=False).iterrows():
                f.write(f"| {row['termine']} | {row['occorrenze_totali']} | {row['n_file_distinti']} |\n")
            f.write("\n")

        # Termini da sostituire (più frequenti)
        f.write("## 4. TERMINI DA SOSTITUIRE (Top 50 per frequenza)\n\n")
        f.write("Questi termini hanno frequenza < 5 e necessitano di revisione manuale.\n\n")

        da_sostituire = df_vocab[df_vocab['decisione'] == 'sostituisci'].head(50)
        f.write("| Termine | Occorrenze | File Distinti | Attributi Principali |\n")
        f.write("|---------|-----------|---------------|---------------------|\n")

        for idx, row in da_sostituire.iterrows():
            # Estrai i top 2 attributi
            occ_attr = json.loads(row['occ_per_attributo'])
            top_attrs = sorted(occ_attr.items(), key=lambda x: x[1], reverse=True)[:2]
            top_attrs_str = ', '.join([f"{k}:{v}" for k, v in top_attrs])

            f.write(f"| {row['termine']} | {row['occorrenze_totali']} | {row['n_file_distinti']} | {top_attrs_str} |\n")
        f.write("\n")

        # Distribuzione occorrenze
        f.write("## 5. DISTRIBUZIONE OCCORRENZE\n\n")
        f.write("| Range Occorrenze | Count Termini | % |\n")
        f.write("|------------------|---------------|---|\n")

        ranges = [
            (1, 1, '1 occorrenza'),
            (2, 2, '2 occorrenze'),
            (3, 3, '3 occorrenze'),
            (4, 4, '4 occorrenze'),
            (5, 10, '5-10 occorrenze'),
            (11, 50, '11-50 occorrenze'),
            (51, 100, '51-100 occorrenze'),
            (101, float('inf'), '>100 occorrenze')
        ]

        for min_occ, max_occ, label in ranges:
            count = len(df_vocab[
                (df_vocab['occorrenze_totali'] >= min_occ) &
                (df_vocab['occorrenze_totali'] <= max_occ)
            ])
            pct = count / total_terms * 100
            f.write(f"| {label} | {count} | {pct:.1f}% |\n")

        f.write("\n---\n\n")
        f.write("**Note:**\n")
        f.write("- Il campo 'categoria_padre' per termini con decisione='sostituisci' ")
        f.write("va compilato manualmente durante la revisione\n")
        f.write("- La soglia di frequenza per 'mantieni' è impostata a 5 occorrenze\n")

    logger.info("Report generato con successo")


def main():
    """Funzione principale dello script."""
    logger.info("="*80)
    logger.info("INIZIO COSTRUZIONE VOCABOLARIO CONTROLLATO")
    logger.info("="*80)

    try:
        # Costruisci vocabolario
        df_vocabulary = build_vocabulary(INPUT_DIR)

        # Salva vocabolario
        output_csv = OUTPUT_DIR / "vocabolario_controllato.csv"
        df_vocabulary.to_csv(output_csv, index=False, encoding='utf-8')
        logger.info(f"Vocabolario salvato in: {output_csv}")

        # Genera report
        report_path = REPORTS_DIR / "04_vocabolario.md"
        generate_report(df_vocabulary, report_path)

        # Stampa statistiche finali
        logger.info("="*80)
        logger.info("STATISTICHE FINALI")
        logger.info("="*80)
        logger.info(f"Termini unici trovati: {len(df_vocabulary)}")

        mantieni = len(df_vocabulary[df_vocabulary['decisione'] == 'mantieni'])
        sostituisci = len(df_vocabulary[df_vocabulary['decisione'] == 'sostituisci'])
        ignora = len(df_vocabulary[df_vocabulary['decisione'] == 'ignora'])

        logger.info(f"Decisione 'mantieni': {mantieni}")
        logger.info(f"Decisione 'sostituisci': {sostituisci}")
        logger.info(f"Decisione 'ignora': {ignora}")

        logger.info("\nTop 10 termini da sostituire (più frequenti):")
        top_sostituisci = df_vocabulary[df_vocabulary['decisione'] == 'sostituisci'].head(10)
        for idx, row in top_sostituisci.iterrows():
            logger.info(f"  - {row['termine']}: {row['occorrenze_totali']} occorrenze")

        logger.info("="*80)
        logger.info("COSTRUZIONE VOCABOLARIO COMPLETATA CON SUCCESSO")
        logger.info(f"Output salvato in: {output_csv}")
        logger.info(f"Report salvato in: {report_path}")
        logger.info("="*80)

    except Exception as e:
        logger.error(f"Errore durante elaborazione: {e}", exc_info=True)
        raise

if __name__ == "__main__":
    main()
