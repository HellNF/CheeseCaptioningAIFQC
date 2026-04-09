"""
Nome Script: Join Campioni - Collegamento Immagini e Commenti
Scopo: Costruire dataset completo collegando immagini BMP e commenti per ogni campione
Input: Immagini BMP + CSV Fase B + Mapping caseifici + Date 2018
Output: campioni_completi.csv + campioni_statistiche.csv + report

Autore: Claude Code
Data: 2026-02-14

Chiave univoca campione: codice_caseificio + data_seduta
"""

import logging
from pathlib import Path
from typing import List, Dict, Any, Tuple, Optional
import pandas as pd
import re
import json
from collections import defaultdict, Counter
from datetime import datetime

# Setup logging
LOG_DIR = Path("logs")
LOG_DIR.mkdir(exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(LOG_DIR / '05_join_campioni.log', mode='w', encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Costanti
PROJECT_ROOT = Path(__file__).parent.parent.parent
DATA_DIR = PROJECT_ROOT / "07_captioning risultati grana Trentino"
IMAGES_DIR = DATA_DIR / "TrentinGrana"
COMMENTS_DIR = PROJECT_ROOT / "data" / "interim" / "fase_B"
CODIFICHE_DIR = DATA_DIR / "GT commenti liberi" / "codifiche"
EXCEL_DIR = DATA_DIR / "GT commenti liberi"
OUTPUT_DIR = PROJECT_ROOT / "data" / "processed"
REPORTS_DIR = PROJECT_ROOT / "reports"

# Assicurarsi che le directory esistano
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
REPORTS_DIR.mkdir(parents=True, exist_ok=True)

# Lista attributi sensoriali
ATTRIBUTI = [
    'Profumo', 'Sapore', 'Aroma', 'Texture',
    'Struttura della Pasta', 'Colore della Pasta', 'Spessore della Crosta'
]


def parse_bmp_filename_2018(filename: str) -> Optional[Dict[str, Any]]:
    """
    Parse naming convention 2018-2019: P{pos}{lato}_{codice}_{vista}.bmp

    Esempio: P1a_302_fetta.bmp

    Args:
        filename: Nome del file BMP

    Returns:
        Dict con codice, vista, posizione, lato, o None se non match
    """
    pattern = r'P(\d+)([ab])_(\d+)_(fetta|grana)\.bmp'
    match = re.match(pattern, filename, re.IGNORECASE)

    if match:
        pos, lato, codice, vista = match.groups()
        return {
            'codice_caseificio': f"TN{codice}",
            'vista': vista.upper(),
            'posizione_camera': int(pos),
            'lato': lato.upper(),
            'id_forma': None,
            'replica': None
        }
    return None


def parse_bmp_filename_2019(filename: str) -> Optional[Dict[str, Any]]:
    """
    Parse naming convention 2019-2020: P{pos}{lato}_TN{codice}_{vista}.bmp

    Esempio: P1a_TN302_Fetta.bmp

    Args:
        filename: Nome del file BMP

    Returns:
        Dict con codice, vista, posizione, lato, o None se non match
    """
    pattern = r'P(\d+)([ab])_TN(\d+)_(Fetta|Grana|FETTA|GRANA)\.bmp'
    match = re.match(pattern, filename, re.IGNORECASE)

    if match:
        pos, lato, codice, vista = match.groups()
        return {
            'codice_caseificio': f"TN{codice}",
            'vista': vista.upper(),
            'posizione_camera': int(pos),
            'lato': lato.upper(),
            'id_forma': None,
            'replica': None
        }
    return None


def parse_bmp_filename_2020(filename: str) -> Optional[Dict[str, Any]]:
    """
    Parse naming convention 2020-2021: P{pos}{LATO}_TN{codice}_{id}_{VISTA}.bmp

    Esempio: P1A_TN302_527_FETTA.bmp

    Args:
        filename: Nome del file BMP

    Returns:
        Dict con codice, vista, posizione, lato, id_forma, o None se non match
    """
    pattern = r'P(\d+)([AB])_TN(\d+)_(\d+)_(FETTA|GRANA)\.bmp'
    match = re.match(pattern, filename, re.IGNORECASE)

    if match:
        pos, lato, codice, id_forma, vista = match.groups()
        return {
            'codice_caseificio': f"TN{codice}",
            'vista': vista.upper(),
            'posizione_camera': int(pos),
            'lato': lato.upper(),
            'id_forma': id_forma,
            'replica': None
        }
    return None


def parse_bmp_filename_2021(filename: str) -> Optional[Dict[str, Any]]:
    """
    Parse naming convention 2021-2022: P{pos}_TN{codice}_{id}_{VISTA}_{replica}.bmp

    Esempio: P1_TN302_680_FETTA_A.bmp

    Args:
        filename: Nome del file BMP

    Returns:
        Dict con codice, vista, posizione, id_forma, replica, o None se non match
    """
    pattern = r'P(\d+)_TN(\d+)_(\d+)_(FETTA|GRANA)_([AB])\.bmp'
    match = re.match(pattern, filename, re.IGNORECASE)

    if match:
        pos, codice, id_forma, vista, replica = match.groups()
        return {
            'codice_caseificio': f"TN{codice}",
            'vista': vista.upper(),
            'posizione_camera': int(pos),
            'lato': None,
            'id_forma': id_forma,
            'replica': replica.upper()
        }
    return None


def extract_date_from_folder_path(folder_path: Path) -> Optional[str]:
    """
    Estrae la data dalla struttura delle cartelle.

    Esempi di strutture:
    - 2018-2019: TrentinGrana/2018-2019_Trentingrana/2018-08-29/
    - 2019-2020: TrentinGrana/2019-2020_Trentingrana/I bimestre/2019-09-04_Seduta_01/
    - 2020-2021: TrentinGrana/2020-2021_Trentingrana/I bimestre/2020-09-09_Seduta_01/
    - 2021-2022: TrentinGrana/2021-2022_Trentingrana/1° Seduta/2021-09-14/

    Args:
        folder_path: Path della cartella

    Returns:
        Data in formato YYYY-MM-DD o None
    """
    # Cerca pattern YYYY-MM-DD in qualsiasi parte del path
    parts = folder_path.parts
    for part in reversed(parts):  # Inizia dalla cartella più specifica
        match = re.search(r'(\d{4})-(\d{2})-(\d{2})', part)
        if match:
            return match.group(0)

    return None


def parse_all_images() -> List[Dict[str, Any]]:
    """
    Parse tutte le immagini BMP nelle cartelle TrentinGrana.

    Returns:
        Lista di dict con metadati per ogni immagine
    """
    logger.info("="*80)
    logger.info("PARSING IMMAGINI BMP")
    logger.info("="*80)

    images = []
    parse_functions = [
        parse_bmp_filename_2018,
        parse_bmp_filename_2019,
        parse_bmp_filename_2020,
        parse_bmp_filename_2021
    ]

    # Trova tutti i file BMP
    bmp_files = list(IMAGES_DIR.rglob("*.bmp"))
    logger.info(f"Trovati {len(bmp_files)} file BMP totali")

    parsed_count = 0
    failed_count = 0
    failed_files = []

    for bmp_path in bmp_files:
        filename = bmp_path.name

        # Prova tutti i pattern fino a trovare un match
        parsed = None
        for parse_func in parse_functions:
            parsed = parse_func(filename)
            if parsed:
                break

        if parsed:
            # Estrai data dalla cartella
            data_seduta = extract_date_from_folder_path(bmp_path.parent)

            if data_seduta:
                # Determina anno dal path
                anno = None
                if '2018-2019' in str(bmp_path):
                    anno = 2018
                elif '2019-2020' in str(bmp_path):
                    anno = 2019
                elif '2020-2021' in str(bmp_path):
                    anno = 2020
                elif '2021-2022' in str(bmp_path):
                    anno = 2021

                images.append({
                    'path': bmp_path.relative_to(PROJECT_ROOT).as_posix(),
                    'codice_caseificio': parsed['codice_caseificio'],
                    'data_seduta': data_seduta,
                    'vista': parsed['vista'],
                    'anno': anno,
                    'lato': parsed['lato'],
                    'posizione_camera': parsed['posizione_camera'],
                    'id_forma': parsed['id_forma'],
                    'replica': parsed['replica']
                })
                parsed_count += 1
            else:
                logger.warning(f"Immagine parsata ma senza data: {bmp_path}")
                failed_count += 1
                failed_files.append((filename, "no_date"))
        else:
            logger.warning(f"Immagine non parsata: {filename}")
            failed_count += 1
            failed_files.append((filename, "no_pattern_match"))

    logger.info(f"Immagini parsate con successo: {parsed_count}")
    logger.info(f"Immagini fallite: {failed_count}")

    if failed_files and len(failed_files) <= 10:
        logger.info("Esempi di file falliti:")
        for fname, reason in failed_files[:10]:
            logger.info(f"  - {fname} ({reason})")

    return images


def load_mapping_caseifici() -> Dict[str, str]:
    """
    Carica il mapping codice_prodotto → codice_caseificio.

    File: codifica caseifici_codici caseifici.csv
    Schema (senza header): TN_302 | C0A | A

    Returns:
        Dict {codice_prodotto: codice_caseificio}
    """
    logger.info("Caricamento mapping caseifici...")

    mapping_path = CODIFICHE_DIR / "codifica caseifici_codici caseifici.csv"

    if not mapping_path.exists():
        logger.error(f"File mapping non trovato: {mapping_path}")
        return {}

    # Leggi CSV senza header
    df = pd.read_csv(mapping_path, header=None, encoding='utf-8')

    # Costruisci mapping: colonna 1 (C0A) → colonna 0 (TN_302)
    mapping = {}
    for _, row in df.iterrows():
        codice_caseificio = str(row[0]).strip()  # TN_302
        codice_prodotto = str(row[1]).strip()     # C0A

        # Normalizza formato caseificio: TN_302 → TN302
        codice_caseificio = codice_caseificio.replace('_', '')

        mapping[codice_prodotto] = codice_caseificio

    logger.info(f"Mapping caseifici caricato: {len(mapping)} voci")
    return mapping


def load_date_sedute_2018() -> Dict[int, str]:
    """
    Carica il mapping numero_seduta → data_seduta per anno 2018.

    File: Commenti TOT_2018.xlsx, foglio 'date_sedute_2018'
    Schema: Session | Date

    Returns:
        Dict {numero_seduta: data_seduta}
    """
    logger.info("Caricamento date sedute 2018...")

    excel_path = EXCEL_DIR / "Commenti TOT_2018.xlsx"

    if not excel_path.exists():
        logger.warning(f"File Excel 2018 non trovato: {excel_path}")
        return {}

    try:
        df = pd.read_excel(excel_path, sheet_name='date_sedute_2018')

        # Costruisci mapping: Session → Date
        mapping = {}
        for _, row in df.iterrows():
            session = int(row['Session'])
            date = pd.to_datetime(row['Date']).strftime('%Y-%m-%d')
            mapping[session] = date

        logger.info(f"Date sedute 2018 caricate: {len(mapping)} voci")
        return mapping

    except Exception as e:
        logger.error(f"Errore caricamento date 2018: {e}")
        return {}


def parse_comments_fase_b(mapping_caseifici: Dict[str, str],
                          date_2018: Dict[int, str]) -> Dict[Tuple[str, str], Dict]:
    """
    Parse tutti i CSV della Fase B e raggruppa i commenti per campione.

    Chiave: (codice_caseificio, data_seduta)

    Args:
        mapping_caseifici: Mapping codice_prodotto → codice_caseificio
        date_2018: Mapping numero_seduta → data_seduta per 2018

    Returns:
        Dict {(codice_caseificio, data_seduta): {attributo: [commenti], ...}}
    """
    logger.info("="*80)
    logger.info("PARSING COMMENTI FASE B")
    logger.info("="*80)

    samples = defaultdict(lambda: {
        'commenti': defaultdict(list),
        'punteggi_2018': defaultdict(list),  # Solo per 2018
        'anno': None,
        'n_panelisti': 0,
        'panelisti': set()
    })

    csv_files = list(COMMENTS_DIR.glob("*_fase_B.csv"))
    logger.info(f"Trovati {len(csv_files)} file CSV Fase B")

    for csv_path in csv_files:
        logger.info(f"Processing {csv_path.name}...")

        df = pd.read_csv(csv_path, encoding='utf-8')

        # Determina anno e attributo dal filename
        # Formato: Commenti TOT_2018_Profumo_fase_B.csv
        anno = None
        attributo = None

        if '2018' in csv_path.name:
            anno = 2018
        elif '2019' in csv_path.name:
            anno = 2019
        elif '2020' in csv_path.name:
            anno = 2020
        elif '2021' in csv_path.name:
            anno = 2021

        # Estrai attributo
        for attr in ATTRIBUTI:
            if attr.lower() in csv_path.name.lower():
                attributo = attr
                break

        if not attributo:
            logger.warning(f"Attributo non identificato per {csv_path.name}")
            continue

        # Trova colonna commenti (gestisce 'Commenti' e 'Commenti ' con spazio trailing)
        comment_col = None
        for col in df.columns:
            if 'commenti' in col.lower():
                comment_col = col
                break

        if not comment_col:
            logger.warning(f"  Colonna 'Commenti' non trovata in {csv_path.name}")
            continue  # Salta questo file se non c'è colonna commenti

        # Parse righe
        for _, row in df.iterrows():
            codice_prodotto = None
            data_seduta = None
            commento = None
            punteggio = None
            panelista_id = None

            # Schema dipende dall'anno
            if anno == 2018:
                # Schema: Sogg, Seduta, Prod, {Attributo}, Commenti
                seduta_num = row.get('Seduta')
                codice_prodotto = row.get('Prod')
                commento = row.get(comment_col)  # Fix: usa colonna trovata dinamicamente
                panelista_id = f"Sogg_{row.get('Sogg')}"

                # Converti numero seduta in data
                if pd.notna(seduta_num) and int(seduta_num) in date_2018:
                    data_seduta = date_2018[int(seduta_num)]

                # Estrai punteggio (colonna con nome attributo)
                if attributo in row:
                    punteggio = row[attributo]

            else:
                # Schema 2019-2021: Data Seduta, Panelista, Prodotto, Commenti
                data_seduta_raw = row.get('Data Seduta di valutazione')
                codice_prodotto = row.get('Prodotto')
                commento = row.get(comment_col)  # Fix: usa colonna trovata dinamicamente
                panelista_id = row.get('Panelista')

                # Converti data in formato standard
                if pd.notna(data_seduta_raw):
                    try:
                        data_seduta = pd.to_datetime(data_seduta_raw).strftime('%Y-%m-%d')
                    except:
                        logger.warning(f"Data non valida: {data_seduta_raw}")
                        continue

            # Salta se manca prodotto o data
            if pd.isna(codice_prodotto) or not data_seduta:
                continue

            # Converti codice_prodotto in codice_caseificio
            codice_prodotto_str = str(codice_prodotto).strip()
            codice_caseificio = mapping_caseifici.get(codice_prodotto_str)

            if not codice_caseificio:
                # Prova senza normalizzazione
                logger.warning(f"Codice prodotto non trovato nel mapping: {codice_prodotto_str}")
                continue

            # Chiave campione
            sample_key = (codice_caseificio, data_seduta)

            # Aggiungi commento se non vuoto
            if pd.notna(commento) and str(commento).strip():
                samples[sample_key]['commenti'][attributo].append(str(commento).strip())

            # Aggiungi punteggio 2018 se disponibile
            if anno == 2018 and pd.notna(punteggio):
                try:
                    # Converti punteggio italiano (virgola) in float
                    punteggio_str = str(punteggio).replace(',', '.')
                    punteggio_float = float(punteggio_str)
                    samples[sample_key]['punteggi_2018'][attributo].append(punteggio_float)
                except:
                    pass

            # Traccia panelista
            if pd.notna(panelista_id):
                samples[sample_key]['panelisti'].add(str(panelista_id))

            # Imposta anno
            if not samples[sample_key]['anno']:
                samples[sample_key]['anno'] = anno

    # Conta panelisti per campione
    for sample_key in samples:
        samples[sample_key]['n_panelisti'] = len(samples[sample_key]['panelisti'])

    logger.info(f"Trovati {len(samples)} campioni unici con commenti")

    return dict(samples)


def join_images_and_comments(images: List[Dict], comments: Dict) -> pd.DataFrame:
    """
    Join immagini e commenti per campione.

    Args:
        images: Lista di dict con metadati immagini
        comments: Dict di commenti per campione

    Returns:
        DataFrame con campioni completi
    """
    logger.info("="*80)
    logger.info("JOIN IMMAGINI E COMMENTI")
    logger.info("="*80)

    # Raggruppa immagini per campione
    samples_images = defaultdict(lambda: {
        'fetta': [],
        'grana': []
    })

    for img in images:
        sample_key = (img['codice_caseificio'], img['data_seduta'])
        if img['vista'] == 'FETTA':
            samples_images[sample_key]['fetta'].append(img)
        elif img['vista'] == 'GRANA':
            samples_images[sample_key]['grana'].append(img)

    logger.info(f"Campioni con immagini: {len(samples_images)}")
    logger.info(f"Campioni con commenti: {len(comments)}")

    # Unisci tutte le chiavi
    all_keys = set(samples_images.keys()) | set(comments.keys())
    logger.info(f"Campioni totali (union): {len(all_keys)}")

    # Costruisci dataset
    rows = []

    for sample_key in all_keys:
        codice_caseificio, data_seduta = sample_key

        # Immagini
        imgs = samples_images.get(sample_key, {'fetta': [], 'grana': []})
        fetta_imgs = imgs['fetta']
        grana_imgs = imgs['grana']

        # Commenti
        sample_comments = comments.get(sample_key, {})

        # Determina anno
        anno = sample_comments.get('anno')
        if not anno and fetta_imgs:
            anno = fetta_imgs[0]['anno']
        if not anno and grana_imgs:
            anno = grana_imgs[0]['anno']

        # Scegli immagine primaria (preferenza per posizione P1)
        def get_primary_image(img_list):
            if not img_list:
                return None
            # Preferisci posizione 1
            for img in img_list:
                if img['posizione_camera'] == 1:
                    return img['path']
            # Altrimenti prendi la prima
            return img_list[0]['path']

        path_fetta = get_primary_image(fetta_imgs)
        path_grana = get_primary_image(grana_imgs)

        # Paths tutti
        paths_fetta_all = [img['path'] for img in fetta_imgs]
        paths_grana_all = [img['path'] for img in grana_imgs]

        # Flags completezza
        has_images = bool(path_fetta or path_grana)
        has_comments = bool(sample_comments.get('commenti'))
        flag_dati_incompleti = not (has_images and has_comments)

        # Note qualità
        note = []
        if not path_fetta:
            note.append("Mancano immagini FETTA")
        if not path_grana:
            note.append("Mancano immagini GRANA")
        if not has_comments:
            note.append("Nessun commento")
        else:
            for attr in ATTRIBUTI:
                if attr not in sample_comments['commenti'] or not sample_comments['commenti'][attr]:
                    note.append(f"Nessun commento {attr}")

        note_qualita = "; ".join(note) if note else ""

        # Prepara row
        row = {
            'sample_id': f"{codice_caseificio}_{data_seduta}",
            'codice_caseificio': codice_caseificio,
            'data_seduta': data_seduta,
            'anno': anno,
            'n_immagini_fetta': len(fetta_imgs),
            'n_immagini_grana': len(grana_imgs),
            'path_fetta_primaria': path_fetta or "",
            'path_grana_primaria': path_grana or "",
            'paths_fetta_tutti': json.dumps(paths_fetta_all),
            'paths_grana_tutti': json.dumps(paths_grana_all),
            'n_panelisti': sample_comments.get('n_panelisti', 0),
            'flag_dati_incompleti': flag_dati_incompleti,
            'note_qualita': note_qualita
        }

        # Aggiungi commenti per attributo (JSON list)
        for attr in ATTRIBUTI:
            col_name = f"commenti_{attr.lower().replace(' della ', '_').replace(' ', '_')}"
            commenti_list = sample_comments.get('commenti', {}).get(attr, [])
            row[col_name] = json.dumps(commenti_list, ensure_ascii=False)

        # Aggiungi punteggi (media per 2018, None per altri)
        for attr in ATTRIBUTI:
            col_name = f"punteggio_{attr.lower().replace(' della ', '_').replace(' ', '_')}"
            punteggi_list = sample_comments.get('punteggi_2018', {}).get(attr, [])
            if punteggi_list:
                row[col_name] = sum(punteggi_list) / len(punteggi_list)
            else:
                row[col_name] = None

        # Punteggio complessivo (None per ora)
        row['punteggio_complessivo'] = None

        rows.append(row)

    df = pd.DataFrame(rows)

    logger.info(f"Dataset finale: {len(df)} campioni")
    logger.info(f"Campioni completi: {len(df[~df['flag_dati_incompleti']])}")
    logger.info(f"Campioni incompleti: {len(df[df['flag_dati_incompleti']])}")

    return df


def generate_statistics(df: pd.DataFrame) -> pd.DataFrame:
    """
    Genera statistiche aggregate per validazione.

    Args:
        df: DataFrame campioni completi

    Returns:
        DataFrame con statistiche
    """
    stats = []

    # Totale campioni
    stats.append({
        'metrica': 'Totale campioni',
        'valore': len(df),
        'percentuale': 100.0
    })

    # Campioni con entrambe le immagini
    both_images = df[(df['n_immagini_fetta'] > 0) & (df['n_immagini_grana'] > 0)]
    stats.append({
        'metrica': 'Campioni con FETTA + GRANA',
        'valore': len(both_images),
        'percentuale': len(both_images) / len(df) * 100
    })

    # Campioni con tutti gli attributi commentati
    def has_all_comments(row):
        for attr in ATTRIBUTI:
            col_name = f"commenti_{attr.lower().replace(' della ', '_').replace(' ', '_')}"
            commenti = json.loads(row[col_name])
            if not commenti:
                return False
        return True

    all_comments = df[df.apply(has_all_comments, axis=1)]
    stats.append({
        'metrica': 'Campioni con tutti gli attributi commentati',
        'valore': len(all_comments),
        'percentuale': len(all_comments) / len(df) * 100
    })

    # Campioni completi
    completi = df[~df['flag_dati_incompleti']]
    stats.append({
        'metrica': 'Campioni completi (immagini + commenti)',
        'valore': len(completi),
        'percentuale': len(completi) / len(df) * 100
    })

    # Breakdown per anno
    for anno in sorted(df['anno'].dropna().unique()):
        anno_df = df[df['anno'] == anno]
        stats.append({
            'metrica': f'Campioni anno {int(anno)}',
            'valore': len(anno_df),
            'percentuale': len(anno_df) / len(df) * 100
        })

        # Completi per anno
        anno_completi = anno_df[~anno_df['flag_dati_incompleti']]
        stats.append({
            'metrica': f'Campioni completi anno {int(anno)}',
            'valore': len(anno_completi),
            'percentuale': len(anno_completi) / len(anno_df) * 100 if len(anno_df) > 0 else 0
        })

    return pd.DataFrame(stats)


def generate_report(df: pd.DataFrame, stats_df: pd.DataFrame, output_path: Path):
    """
    Genera report markdown.

    Args:
        df: DataFrame campioni completi
        stats_df: DataFrame statistiche
        output_path: Path dove salvare il report
    """
    logger.info(f"Generando report in {output_path}...")

    with open(output_path, 'w', encoding='utf-8') as f:
        f.write("# REPORT JOIN CAMPIONI - Grana Trentino\n\n")
        f.write(f"**Data elaborazione:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
        f.write("---\n\n")

        # Statistiche aggregate
        f.write("## 1. STATISTICHE AGGREGATE\n\n")
        f.write("| Metrica | Valore | Percentuale |\n")
        f.write("|---------|--------|-------------|\n")
        for _, row in stats_df.iterrows():
            f.write(f"| {row['metrica']} | {row['valore']} | {row['percentuale']:.1f}% |\n")
        f.write("\n")

        # Top problemi
        f.write("## 2. TOP 10 PROBLEMI PIÙ COMUNI\n\n")
        incompleti = df[df['flag_dati_incompleti']]

        problem_counter = Counter()
        for _, row in incompleti.iterrows():
            problems = row['note_qualita'].split("; ")
            for prob in problems:
                if prob:
                    problem_counter[prob] += 1

        f.write("| Problema | Occorrenze |\n")
        f.write("|----------|------------|\n")
        for prob, count in problem_counter.most_common(10):
            f.write(f"| {prob} | {count} |\n")
        f.write("\n")

        # Esempi campioni completi
        f.write("## 3. ESEMPI CAMPIONI COMPLETI\n\n")
        completi = df[~df['flag_dati_incompleti']]

        for i, (_, row) in enumerate(completi.head(3).iterrows(), 1):
            f.write(f"### Esempio {i}: {row['sample_id']}\n\n")
            f.write(f"- **Anno:** {int(row['anno']) if pd.notna(row['anno']) else 'N/A'}\n")
            f.write(f"- **Immagini FETTA:** {row['n_immagini_fetta']}\n")
            f.write(f"- **Immagini GRANA:** {row['n_immagini_grana']}\n")
            f.write(f"- **Panelisti:** {row['n_panelisti']}\n")
            f.write(f"- **Commenti per attributo:**\n")

            for attr in ATTRIBUTI:
                col_name = f"commenti_{attr.lower().replace(' della ', '_').replace(' ', '_')}"
                commenti = json.loads(row[col_name])
                f.write(f"  - {attr}: {len(commenti)} commenti\n")
            f.write("\n")

        # Esempi campioni incompleti
        f.write("## 4. ESEMPI CAMPIONI INCOMPLETI\n\n")

        for i, (_, row) in enumerate(incompleti.head(3).iterrows(), 1):
            f.write(f"### Esempio {i}: {row['sample_id']}\n\n")
            f.write(f"- **Anno:** {int(row['anno']) if pd.notna(row['anno']) else 'N/A'}\n")
            f.write(f"- **Immagini FETTA:** {row['n_immagini_fetta']}\n")
            f.write(f"- **Immagini GRANA:** {row['n_immagini_grana']}\n")
            f.write(f"- **Panelisti:** {row['n_panelisti']}\n")
            f.write(f"- **Motivo:** {row['note_qualita']}\n\n")

        f.write("---\n\n")
        f.write("**Note:**\n")
        f.write("- Campioni con flag_dati_incompleti=True sono inclusi ma potrebbero essere esclusi dal training\n")
        f.write("- I commenti sono salvati come JSON list per mantenere tutti i commenti dei panelisti\n")

    logger.info("Report generato con successo")


def main():
    """Funzione principale dello script."""
    logger.info("="*80)
    logger.info("INIZIO JOIN CAMPIONI - Grana Trentino")
    logger.info("="*80)

    try:
        # 1. Parse immagini
        images = parse_all_images()

        # 2. Carica mapping e date
        mapping_caseifici = load_mapping_caseifici()
        date_2018 = load_date_sedute_2018()

        # 3. Parse commenti
        comments = parse_comments_fase_b(mapping_caseifici, date_2018)

        # 4. Join
        df_campioni = join_images_and_comments(images, comments)

        # 5. Salva campioni completi
        output_path = OUTPUT_DIR / "campioni_completi.csv"
        df_campioni.to_csv(output_path, index=False, encoding='utf-8')
        logger.info(f"Campioni completi salvati in: {output_path}")

        # 6. Genera statistiche
        stats_df = generate_statistics(df_campioni)
        stats_path = OUTPUT_DIR / "campioni_statistiche.csv"
        stats_df.to_csv(stats_path, index=False, encoding='utf-8')
        logger.info(f"Statistiche salvate in: {stats_path}")

        # 7. Genera report
        report_path = REPORTS_DIR / "05_join_campioni.md"
        generate_report(df_campioni, stats_df, report_path)

        # 8. Statistiche finali
        logger.info("="*80)
        logger.info("STATISTICHE FINALI")
        logger.info("="*80)

        completi = df_campioni[~df_campioni['flag_dati_incompleti']]
        incompleti = df_campioni[df_campioni['flag_dati_incompleti']]

        logger.info(f"Totale campioni trovati: {len(df_campioni)}")
        logger.info(f"Campioni COMPLETI: {len(completi)} ({len(completi)/len(df_campioni)*100:.1f}%)")
        logger.info(f"Campioni INCOMPLETI: {len(incompleti)} ({len(incompleti)/len(df_campioni)*100:.1f}%)")

        # Breakdown per anno
        logger.info("\nBreakdown per anno:")
        for anno in sorted(df_campioni['anno'].dropna().unique()):
            anno_df = df_campioni[df_campioni['anno'] == anno]
            anno_completi = anno_df[~anno_df['flag_dati_incompleti']]
            logger.info(f"  Anno {int(anno)}: {len(anno_df)} totali, {len(anno_completi)} completi")

        # Top 3 problemi
        logger.info("\nTop 3 problemi più frequenti:")
        problem_counter = Counter()
        for _, row in incompleti.iterrows():
            problems = row['note_qualita'].split("; ")
            for prob in problems:
                if prob:
                    problem_counter[prob] += 1

        for i, (prob, count) in enumerate(problem_counter.most_common(3), 1):
            logger.info(f"  {i}. {prob}: {count} occorrenze")

        logger.info("="*80)
        logger.info("JOIN CAMPIONI COMPLETATO CON SUCCESSO")
        logger.info(f"Output salvato in: {OUTPUT_DIR}")
        logger.info(f"Report salvato in: {report_path}")
        logger.info("="*80)

    except Exception as e:
        logger.error(f"Errore durante elaborazione: {e}", exc_info=True)
        raise


if __name__ == "__main__":
    main()
