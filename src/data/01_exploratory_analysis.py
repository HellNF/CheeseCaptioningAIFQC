"""
Nome Script: Analisi Esplorativa Dataset Grana Trentino
Scopo: Eseguire una analisi esplorativa completa dei dati tabulari (commenti sensoriali,
       punteggi, codifiche) per il progetto di image captioning del Grana Trentino.
       Questo è il PRIMO script del progetto: ogni sezione è commentata in dettaglio
       per documentare le scelte e i risultati intermedi.

Input:
    - 07_captioning risultati grana Trentino/GT commenti liberi/*.xlsx  (4 file commenti)
    - 07_captioning risultati grana Trentino/GT commenti liberi/csv dataset/*.csv
    - 07_captioning risultati grana Trentino/GT commenti liberi/codifiche/*
    - 07_captioning risultati grana Trentino/validation_reports/session_validation_report.csv

Output:
    - reports/01_analisi_esplorativa.md           (report markdown completo)
    - reports/figures/*.png                        (grafici distribuzione, correlazione, ecc.)
    - data/metadata/data_quality_summary.csv       (riassunto qualità dati)

Autore: CheeseCaptioningAIFQC Team
Data: 2026-02-10
"""

import logging
import re
import sys
import warnings
from collections import Counter
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import matplotlib
matplotlib.use('Agg')  # Backend non-interattivo per generare PNG senza GUI
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns

# ============================================================================
# CONFIGURAZIONE E COSTANTI
# ============================================================================

# Percorso root del progetto (src/data/ -> root del progetto)
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
DATA_DIR = PROJECT_ROOT / "07_captioning risultati grana Trentino"
COMMENTI_DIR = DATA_DIR / "GT commenti liberi"
CSV_DIR = COMMENTI_DIR / "csv dataset"
CODIFICHE_DIR = COMMENTI_DIR / "codifiche"
VALIDATION_DIR = DATA_DIR / "validation_reports"

# Directory di output
REPORTS_DIR = PROJECT_ROOT / "reports"
FIGURES_DIR = REPORTS_DIR / "figures"
METADATA_DIR = PROJECT_ROOT / "data" / "metadata"
LOGS_DIR = PROJECT_ROOT / "logs"

# Gli 8 attributi sensoriali valutati dal panel
ATTRIBUTI_SENSORIALI: List[str] = [
    "Spessore della Crosta",
    "Struttura della Pasta",
    "Colore della Pasta",
    "Aspetto Esteriore",
    "Profumo",
    "Sapore",
    "Aroma",
    "Texture",
]

# I 4 file Excel principali con i commenti liberi, nell'ordine cronologico
FILE_COMMENTI_EXCEL: Dict[str, str] = {
    "2018": "Commenti TOT_2018.xlsx",
    "2019": "Commenti liberi_QTG_2019.xlsx",
    "2020": "Commenti liberi_QTG_2020.xlsx",
    "2021": "Commenti liberi_TEST_2021.xlsx",
}

# Configurazione grafici
plt.rcParams.update({
    'figure.figsize': (12, 8),
    'font.size': 11,
    'axes.titlesize': 13,
    'axes.labelsize': 11,
})
sns.set_theme(style="whitegrid")

# Sopprimiamo warning di pandas/openpyxl non rilevanti per l'analisi
warnings.filterwarnings("ignore", category=FutureWarning)
warnings.filterwarnings("ignore", message=".*select_dtypes.*")  # Pandas4Warning su str/object

# ============================================================================
# SETUP LOGGING
# ============================================================================

def setup_logging() -> logging.Logger:
    """Configura il sistema di logging con output su file e console.

    Returns:
        Logger configurato per lo script.
    """
    LOGS_DIR.mkdir(parents=True, exist_ok=True)

    logger = logging.getLogger("exploratory_analysis")
    logger.setLevel(logging.DEBUG)

    # Formato dettagliato per il file di log
    file_handler = logging.FileHandler(
        LOGS_DIR / "01_exploratory_analysis.log",
        mode='w',
        encoding='utf-8'
    )
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(logging.Formatter(
        '%(asctime)s - %(levelname)s - %(message)s'
    ))

    # Formato sintetico per la console
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(logging.Formatter(
        '%(levelname)s: %(message)s'
    ))

    logger.addHandler(file_handler)
    logger.addHandler(console_handler)

    return logger


logger = setup_logging()


# ============================================================================
# UTILITÀ
# ============================================================================

def pulisci_testo(testo: Any) -> str:
    """Normalizza un campo testuale: gestisce NaN, \xa0, spazi multipli.

    Questa funzione è il primo livello di pulizia:
    - Converte NaN/None in stringa vuota
    - Sostituisce non-breaking space (\xa0) con spazio normale
    - Rimuove spazi in eccesso a inizio/fine e spazi multipli interni

    Args:
        testo: Valore da normalizzare (può essere str, float NaN, None).

    Returns:
        Stringa pulita, o stringa vuota se il valore era mancante.
    """
    if pd.isna(testo) or testo is None:
        return ""
    s = str(testo)
    # \xa0 è il non-breaking space, molto comune nei file 2021
    s = s.replace('\xa0', ' ')
    # Rimuovi spazi multipli
    s = re.sub(r'\s+', ' ', s).strip()
    return s


def parse_punteggio_italiano(valore: Any) -> Optional[float]:
    """Converte un punteggio dal formato italiano (virgola decimale) a float.

    Nel file 2018, i punteggi per Profumo/Sapore/Aroma sono stringhe
    con virgola decimale (es. "7,48"). Questa funzione gestisce:
    - Stringhe con virgola ("7,48" -> 7.48)
    - Float già numerici (7.5 -> 7.5)
    - Valori mancanti (NaN -> None)

    Args:
        valore: Il punteggio da convertire.

    Returns:
        Float con il punteggio, o None se il valore non è valido.
    """
    if pd.isna(valore) or valore is None:
        return None
    if isinstance(valore, (int, float)):
        return float(valore)
    # Gestisci stringhe con virgola italiana
    s = str(valore).strip().replace(',', '.')
    try:
        return float(s)
    except ValueError:
        return None


# ============================================================================
# REGISTRO CORREZIONI IN MEMORIA
# ============================================================================

class RegistroCorrezioni:
    """Registro globale delle correzioni applicate in memoria ai dati.

    Traccia ogni correzione effettuata durante il caricamento dei DataFrame,
    SENZA modificare i file originali su disco. Il registro viene poi incluso
    nel report markdown e nel CSV di qualità, così il lettore sa esattamente
    cosa è stato normalizzato e quante volte.
    """

    def __init__(self) -> None:
        self._correzioni: List[Dict[str, Any]] = []
        self._contatori: Counter = Counter()

    def registra(self, tipo: str, file: str, dettaglio: str, conteggio: int = 1) -> None:
        """Registra una correzione applicata.

        Args:
            tipo: Categoria della correzione (es. 'xa0_sostituiti', 'righe_vuote_rimosse').
            file: Nome del file sorgente in cui è stata applicata.
            dettaglio: Descrizione leggibile della correzione.
            conteggio: Quante occorrenze sono state corrette.
        """
        self._correzioni.append({
            'tipo': tipo,
            'file': file,
            'dettaglio': dettaglio,
            'conteggio': conteggio,
        })
        self._contatori[tipo] += conteggio
        logger.debug(f"  [CORREZIONE] {tipo}: {dettaglio}")

    @property
    def correzioni(self) -> List[Dict[str, Any]]:
        return self._correzioni

    @property
    def riepilogo(self) -> Dict[str, int]:
        return dict(self._contatori)

    @property
    def totale(self) -> int:
        return sum(self._contatori.values())


# Istanza globale — usata da tutte le funzioni di caricamento
registro = RegistroCorrezioni()

# Mappatura per normalizzare la capitalizzazione dei nomi attributi.
# I file usano forme diverse ("Colore della pasta" vs "Colore della Pasta"):
# qui definiamo la forma canonica per ognuno.
NORMALIZZAZIONE_ATTRIBUTI: Dict[str, str] = {
    'spessore della crosta': 'Spessore della Crosta',
    'struttura della pasta': 'Struttura della Pasta',
    'colore della pasta': 'Colore della Pasta',
    'aspetto esteriore': 'Aspetto Esteriore',
    'profumo': 'Profumo',
    'sapore': 'Sapore',
    'aroma': 'Aroma',
    'texture': 'Texture',
}


def normalizza_nome_attributo(nome: str) -> str:
    """Normalizza il nome di un attributo sensoriale alla forma canonica.

    Gestisce varianti di capitalizzazione (es. "colore della pasta" -> "Colore della Pasta")
    e spazi trailing.

    Args:
        nome: Nome attributo come appare nel file.

    Returns:
        Nome canonico se riconosciuto, altrimenti il nome originale con strip.
    """
    return NORMALIZZAZIONE_ATTRIBUTI.get(nome.strip().lower(), nome.strip())


def pulisci_dataframe(df: pd.DataFrame, nome_file: str) -> pd.DataFrame:
    """Applica correzioni in memoria a un DataFrame appena caricato.

    IMPORTANTE: NON modifica il file originale su disco. Le correzioni sono
    solo nel DataFrame in memoria, per garantire che l'analisi lavori su
    dati puliti. Ogni correzione viene registrata nel RegistroCorrezioni
    globale per documentazione.

    Correzioni applicate:
    1. Strip spazi bianchi dai nomi colonne (es. "Commenti " -> "Commenti")
    2. Rimozione colonne "Unnamed:" (artefatti di export Excel/CSV)
    3. Sostituzione \\xa0 (non-breaking space) con spazio normale in tutte le celle
    4. Rimozione righe completamente vuote (tutte NaN)
    5. Normalizzazione date a formato ISO YYYY-MM-DD (dove riconoscibili)

    Args:
        df: DataFrame da pulire.
        nome_file: Nome del file sorgente (per il registro).

    Returns:
        DataFrame con le correzioni applicate.
    """
    # 1. Strip spazi bianchi dai nomi colonne (es. "Commenti " → "Commenti")
    nomi_originali = list(df.columns)
    df.columns = [col.strip() if isinstance(col, str) else col for col in df.columns]
    nomi_corretti = sum(1 for o, n in zip(nomi_originali, df.columns) if o != n)
    if nomi_corretti > 0:
        registro.registra(
            'spazi_nomi_colonne', nome_file,
            f"Rimossi spazi trailing da {nomi_corretti} nomi colonne",
            nomi_corretti,
        )

    # 2. Rimuovi colonne "Unnamed:" (artefatti da Excel → CSV export)
    colonne_unnamed = [c for c in df.columns if isinstance(c, str) and c.startswith('Unnamed')]
    if colonne_unnamed:
        df = df.drop(columns=colonne_unnamed)
        registro.registra(
            'colonne_unnamed_rimosse', nome_file,
            f"Rimosse {len(colonne_unnamed)} colonne artefatto: {colonne_unnamed}",
            len(colonne_unnamed),
        )

    # 3. Sostituzione \xa0 in tutti i campi stringa
    n_xa0 = 0
    for col in df.select_dtypes(include=['object']).columns:
        mask = df[col].astype(str).str.contains('\xa0', na=False)
        conteggio_col = int(mask.sum())
        if conteggio_col > 0:
            df[col] = df[col].astype(str).str.replace('\xa0', ' ', regex=False)
            n_xa0 += conteggio_col
    if n_xa0 > 0:
        registro.registra(
            'xa0_sostituiti', nome_file,
            f"Sostituiti \\xa0 → spazio in {n_xa0} celle",
            n_xa0,
        )

    # 4. Rimozione righe completamente vuote
    righe_vuote = int(df.isna().all(axis=1).sum())
    if righe_vuote > 0:
        df = df.dropna(how='all').reset_index(drop=True)
        registro.registra(
            'righe_vuote_rimosse', nome_file,
            f"Rimosse {righe_vuote} righe completamente vuote",
            righe_vuote,
        )

    # 5. Normalizzazione date (colonne con "data"/"Data" nel nome, tipo object)
    for col in df.columns:
        if isinstance(col, str) and 'data' in col.lower() and df[col].dtype == 'object':
            originali = df[col].copy()
            try:
                date_parsed = pd.to_datetime(df[col], dayfirst=True, errors='coerce')
                # Applichiamo solo se almeno il 50% è stato parsato (evita falsi positivi)
                n_parsed = date_parsed.notna().sum()
                if n_parsed > len(df) * 0.5:
                    df[col] = date_parsed.dt.strftime('%Y-%m-%d')
                    # Contiamo solo le date effettivamente cambiate di formato
                    modificate = int(((originali.astype(str) != df[col]) & df[col].notna()).sum())
                    if modificate > 0:
                        registro.registra(
                            'date_normalizzate', nome_file,
                            f"Normalizzate {modificate} date in '{col}' a formato ISO",
                            modificate,
                        )
            except Exception:
                pass  # Se fallisce, lasciamo le date invariate

    return df


# ============================================================================
# SEZIONE 1: ANALISI STRUTTURA FILE
# ============================================================================

def analizza_struttura_excel(percorso_file: Path) -> List[Dict[str, Any]]:
    """Analizza la struttura di un file Excel: fogli, righe, colonne, schema.

    Per ogni foglio del file Excel, documenta:
    - Nome del foglio
    - Numero di righe e colonne
    - Nomi delle colonne (schema)
    - Tipi di dato per colonna

    Args:
        percorso_file: Percorso al file Excel.

    Returns:
        Lista di dizionari, uno per foglio, con le informazioni strutturali.
    """
    risultati: List[Dict[str, Any]] = []

    try:
        # Leggiamo tutti i fogli del file Excel
        xlsx = pd.ExcelFile(percorso_file)
        nomi_fogli = xlsx.sheet_names

        for nome_foglio in nomi_fogli:
            df = pd.read_excel(percorso_file, sheet_name=nome_foglio)

            info_foglio: Dict[str, Any] = {
                'file': percorso_file.name,
                'foglio': nome_foglio,
                'righe': len(df),
                'colonne': len(df.columns),
                'nomi_colonne': list(df.columns),
                'tipi_dato': {col: str(df[col].dtype) for col in df.columns},
                'valori_nulli_per_colonna': df.isnull().sum().to_dict(),
                'esempio_prima_riga': df.head(1).to_dict('records')[0] if len(df) > 0 else {},
            }
            risultati.append(info_foglio)

            logger.debug(
                f"  Foglio '{nome_foglio}': {len(df)} righe x {len(df.columns)} colonne "
                f"-> {list(df.columns)}"
            )

    except Exception as e:
        logger.error(f"Errore leggendo {percorso_file}: {e}")

    return risultati


def analizza_struttura_csv(percorso_file: Path) -> Dict[str, Any]:
    """Analizza la struttura di un singolo file CSV.

    Args:
        percorso_file: Percorso al file CSV.

    Returns:
        Dizionario con informazioni strutturali del CSV.
    """
    try:
        df = pd.read_csv(percorso_file, encoding='utf-8')
        return {
            'file': percorso_file.name,
            'righe': len(df),
            'colonne': len(df.columns),
            'nomi_colonne': list(df.columns),
            'tipi_dato': {col: str(df[col].dtype) for col in df.columns},
            'valori_nulli_per_colonna': df.isnull().sum().to_dict(),
        }
    except Exception as e:
        logger.error(f"Errore leggendo CSV {percorso_file}: {e}")
        return {'file': percorso_file.name, 'errore': str(e)}


def esegui_analisi_struttura() -> Dict[str, Any]:
    """Esegue l'analisi strutturale completa di tutti i file dati.

    Scansiona:
    1. I 4 file Excel dei commenti liberi
    2. I file CSV nella cartella csv dataset/
    3. I file nelle codifiche/

    Identifica le differenze schema tra 2018 e 2019-2021.

    Returns:
        Dizionario con tutti i risultati dell'analisi strutturale.
    """
    logger.info("=" * 60)
    logger.info("SEZIONE 1: ANALISI STRUTTURA FILE")
    logger.info("=" * 60)

    risultati: Dict[str, Any] = {
        'excel_commenti': {},
        'csv_commenti': [],
        'csv_codifiche': [],
        'differenze_schema': {},
    }

    # --- 1a. Analisi file Excel commenti ---
    logger.info("Analisi dei 4 file Excel dei commenti liberi...")
    for anno, nome_file in FILE_COMMENTI_EXCEL.items():
        percorso = COMMENTI_DIR / nome_file
        if percorso.exists():
            logger.info(f"  Analizzando {nome_file}...")
            fogli = analizza_struttura_excel(percorso)
            risultati['excel_commenti'][anno] = fogli
        else:
            logger.warning(f"  File non trovato: {percorso}")

    # --- 1b. Analisi file CSV commenti ---
    logger.info("Analisi dei file CSV nella cartella csv dataset/...")
    if CSV_DIR.exists():
        for csv_file in sorted(CSV_DIR.glob("*.csv")):
            info = analizza_struttura_csv(csv_file)
            risultati['csv_commenti'].append(info)
            logger.debug(f"  CSV {csv_file.name}: {info.get('righe', '?')} righe")

    # --- 1c. Analisi file codifiche ---
    logger.info("Analisi dei file nelle codifiche/...")
    if CODIFICHE_DIR.exists():
        for f in sorted(CODIFICHE_DIR.glob("*.xlsx")):
            fogli = analizza_struttura_excel(f)
            risultati['csv_codifiche'].extend(fogli)
        for f in sorted(CODIFICHE_DIR.glob("*.csv")):
            info = analizza_struttura_csv(f)
            risultati['csv_codifiche'].append(info)

    # --- 1d. Identifica differenze schema 2018 vs 2019-2021 ---
    logger.info("Confronto schema 2018 vs 2019-2021...")
    schema_2018: List[str] = []
    schema_2019_2021: List[str] = []

    if "2018" in risultati['excel_commenti'] and risultati['excel_commenti']['2018']:
        # Prendiamo il primo foglio attributo (non date_sedute)
        for foglio in risultati['excel_commenti']['2018']:
            if foglio['foglio'] != 'date_sedute_2018':
                schema_2018 = foglio['nomi_colonne']
                break

    if "2019" in risultati['excel_commenti'] and risultati['excel_commenti']['2019']:
        schema_2019_2021 = risultati['excel_commenti']['2019'][0]['nomi_colonne']

    risultati['differenze_schema'] = {
        'schema_2018': schema_2018,
        'schema_2019_2021': schema_2019_2021,
        'colonne_solo_2018': [c for c in schema_2018 if c not in schema_2019_2021],
        'colonne_solo_2019_2021': [c for c in schema_2019_2021 if c not in schema_2018],
        'nota': (
            "Il 2018 ha punteggi numerici individuali per panelista (colonna con nome attributo). "
            "Il 2019-2021 ha solo commenti (7 colonne, senza punteggi). "
            "Inoltre il 2018 usa 'Sogg' e 'Seduta' come identificativi, "
            "mentre il 2019-2021 usa 'Panelista' e 'Data Seduta di valutazione'."
        ),
    }

    logger.info(f"  Schema 2018: {schema_2018}")
    logger.info(f"  Schema 2019-2021: {schema_2019_2021}")

    return risultati


# ============================================================================
# SEZIONE 2: ANALISI PUNTEGGI NUMERICI
# ============================================================================

def carica_punteggi_2018() -> Dict[str, pd.DataFrame]:
    """Carica i punteggi individuali dal file 2018.

    Il file 2018 è l'unico con punteggi per-panelista. Ogni foglio ha
    una colonna con il nome dell'attributo che contiene il punteggio numerico.

    ATTENZIONE: Profumo/Sapore/Aroma usano il formato virgola italiana ("7,48"),
    mentre Spessore/Struttura/Colore sono float diretti.

    Returns:
        Dizionario {nome_attributo: DataFrame con colonne [Sogg, Seduta, Prod, punteggio, Commenti]}.
    """
    percorso = COMMENTI_DIR / FILE_COMMENTI_EXCEL["2018"]
    dati: Dict[str, pd.DataFrame] = {}

    if not percorso.exists():
        logger.warning(f"File 2018 non trovato: {percorso}")
        return dati

    xlsx = pd.ExcelFile(percorso)

    for nome_foglio in xlsx.sheet_names:
        # Saltiamo il foglio delle date
        if 'date' in nome_foglio.lower():
            continue

        df = pd.read_excel(percorso, sheet_name=nome_foglio)

        # Applica correzioni in memoria (strip colonne, rimuovi Unnamed, \xa0, righe vuote)
        df = pulisci_dataframe(df, f"{percorso.name}/{nome_foglio}")

        # Identifica la colonna del punteggio: è quella che NON è Sogg/Seduta/Prod/Commenti
        colonne_fisse = {'Sogg', 'Seduta', 'Prod'}
        colonna_commenti = None
        colonna_punteggio = None

        for col in df.columns:
            col_pulito = col.strip()
            if col_pulito == 'Commenti' or col_pulito.startswith('Commenti'):
                colonna_commenti = col
            elif col_pulito not in colonne_fisse:
                colonna_punteggio = col

        if colonna_punteggio is None:
            logger.warning(f"  Foglio '{nome_foglio}': colonna punteggio non trovata")
            continue

        # Conta punteggi in formato virgola italiana PRIMA della conversione
        n_virgole = sum(
            1 for v in df[colonna_punteggio]
            if isinstance(v, str) and ',' in v
        )
        if n_virgole > 0:
            registro.registra(
                'virgola_italiana_convertita', percorso.name,
                f"Convertiti {n_virgole} punteggi da formato '7,48' a float in '{nome_foglio}'",
                n_virgole,
            )

        # Converti i punteggi in float (gestendo virgola italiana)
        df['punteggio'] = df[colonna_punteggio].apply(parse_punteggio_italiano)

        # Pulisci commenti
        if colonna_commenti:
            df['commento_pulito'] = df[colonna_commenti].apply(pulisci_testo)
        else:
            df['commento_pulito'] = ""

        # Normalizza il nome dell'attributo (es. "crosta" → "Crosta")
        nome_canonico = normalizza_nome_attributo(nome_foglio)
        if nome_canonico != nome_foglio.strip():
            registro.registra(
                'nome_attributo_normalizzato', percorso.name,
                f"'{nome_foglio}' → '{nome_canonico}'",
            )
        dati[nome_canonico] = df

        n_validi = df['punteggio'].notna().sum()
        logger.info(
            f"  2018 - {nome_foglio}: {len(df)} righe, "
            f"{n_validi} punteggi validi, "
            f"range [{df['punteggio'].min():.2f} - {df['punteggio'].max():.2f}]"
        )

    return dati


def carica_punteggi_aggregati() -> Dict[str, pd.DataFrame]:
    """Carica i punteggi medi della giuria dal file Risultati_2019-21.xlsx.

    Questo file contiene le medie dei punteggi calcolate sull'intero panel
    per ogni campione/sessione. Utile per analizzare le distribuzioni degli
    attributi anche per gli anni 2019-2021 (che non hanno punteggi individuali
    nei commenti liberi).

    Returns:
        Dizionario {anno: DataFrame} con i punteggi aggregati.
    """
    percorso = CODIFICHE_DIR / "Risultati_2019-21.xlsx"
    dati: Dict[str, pd.DataFrame] = {}

    if not percorso.exists():
        logger.warning(f"File risultati aggregati non trovato: {percorso}")
        return dati

    xlsx = pd.ExcelFile(percorso)

    for nome_foglio in xlsx.sheet_names:
        df = pd.read_excel(percorso, sheet_name=nome_foglio)

        # Applica correzioni in memoria (strip colonne, rimuovi Unnamed, \xa0, righe vuote)
        df = pulisci_dataframe(df, f"{percorso.name}/{nome_foglio}")

        # Estraiamo l'anno dal nome del foglio (es. "Medie Giuria2019_Q" -> "2019")
        match = re.search(r'(\d{4})', nome_foglio)
        if match:
            anno = match.group(1)
            dati[anno] = df
            logger.info(
                f"  Risultati {anno}: {len(df)} campioni, "
                f"{len(df.columns)} colonne -> {list(df.columns)}"
            )

    return dati


def calcola_statistiche_punteggi(
    punteggi_2018: Dict[str, pd.DataFrame],
    punteggi_aggregati: Dict[str, pd.DataFrame]
) -> Dict[str, Any]:
    """Calcola statistiche descrittive per tutti i punteggi disponibili.

    Per il 2018 (punteggi individuali per panelista):
    - Media, mediana, deviazione standard, min, max, quartili
    - Varianza inter-panelista (stesso campione, panelisti diversi)

    Per 2019-2021 (punteggi medi aggregati della giuria):
    - Stesse statistiche descrittive

    Args:
        punteggi_2018: Dati per-panelista dal file 2018.
        punteggi_aggregati: Medie giuria dal file Risultati_2019-21.

    Returns:
        Dizionario strutturato con tutte le statistiche calcolate.
    """
    logger.info("Calcolo statistiche descrittive sui punteggi...")

    statistiche: Dict[str, Any] = {
        'individuali_2018': {},
        'aggregati_per_anno': {},
        'varianza_inter_panelista': {},
    }

    # --- Statistiche 2018 (punteggi individuali) ---
    for attributo, df in punteggi_2018.items():
        valori = df['punteggio'].dropna()
        if len(valori) == 0:
            continue

        statistiche['individuali_2018'][attributo] = {
            'conteggio': int(len(valori)),
            'media': float(valori.mean()),
            'mediana': float(valori.median()),
            'std': float(valori.std()),
            'min': float(valori.min()),
            'max': float(valori.max()),
            'q25': float(valori.quantile(0.25)),
            'q75': float(valori.quantile(0.75)),
        }

    # --- Varianza inter-panelista (2018) ---
    # Per ogni campione (Seduta + Prod), calcoliamo la std tra panelisti diversi.
    # Questo ci dice quanto i panelisti concordano sui punteggi.
    logger.info("Calcolo varianza inter-panelista (2018)...")
    for attributo, df in punteggi_2018.items():
        df_validi = df.dropna(subset=['punteggio'])
        if len(df_validi) == 0:
            continue

        # Raggruppiamo per campione (Seduta + Prod = campione unico)
        varianze = df_validi.groupby(['Seduta', 'Prod'])['punteggio'].agg(['std', 'count'])
        # Consideriamo solo campioni con almeno 2 valutazioni
        varianze = varianze[varianze['count'] >= 2]

        if len(varianze) > 0:
            statistiche['varianza_inter_panelista'][attributo] = {
                'media_std_tra_panelisti': float(varianze['std'].mean()),
                'mediana_std_tra_panelisti': float(varianze['std'].median()),
                'max_std_tra_panelisti': float(varianze['std'].max()),
                'n_campioni_analizzati': int(len(varianze)),
                'media_panelisti_per_campione': float(varianze['count'].mean()),
            }
            logger.info(
                f"  {attributo}: std media inter-panelista = "
                f"{varianze['std'].mean():.3f} "
                f"(su {len(varianze)} campioni)"
            )

    # --- Statistiche punteggi aggregati (2019-2021) ---
    for anno, df in punteggi_aggregati.items():
        statistiche['aggregati_per_anno'][anno] = {}
        for attr in ATTRIBUTI_SENSORIALI:
            # Cerchiamo la colonna con nome simile (gestendo capitalizzazione)
            colonna = None
            for col in df.columns:
                if col.strip().lower() == attr.lower():
                    colonna = col
                    break

            if colonna is None:
                continue

            valori = pd.to_numeric(df[colonna], errors='coerce').dropna()
            if len(valori) == 0:
                continue

            statistiche['aggregati_per_anno'][anno][attr] = {
                'conteggio': int(len(valori)),
                'media': float(valori.mean()),
                'mediana': float(valori.median()),
                'std': float(valori.std()),
                'min': float(valori.min()),
                'max': float(valori.max()),
                'q25': float(valori.quantile(0.25)),
                'q75': float(valori.quantile(0.75)),
            }

    return statistiche


def genera_grafici_punteggi(
    punteggi_2018: Dict[str, pd.DataFrame],
    punteggi_aggregati: Dict[str, pd.DataFrame]
) -> List[str]:
    """Genera grafici per la distribuzione e correlazione dei punteggi.

    Produce:
    1. Istogrammi distribuzione per attributo (2018, punteggi individuali)
    2. Boxplot confronto attributi (tutti gli anni aggregati)
    3. Matrice di correlazione tra attributi (2018 e aggregati)
    4. Boxplot varianza inter-panelista per attributo

    Args:
        punteggi_2018: Dati per-panelista 2018.
        punteggi_aggregati: Medie giuria 2019-2021.

    Returns:
        Lista dei percorsi ai file grafici generati.
    """
    logger.info("Generazione grafici punteggi...")
    grafici_generati: List[str] = []

    FIGURES_DIR.mkdir(parents=True, exist_ok=True)

    # --- Grafico 1: Istogrammi distribuzione 2018 per attributo ---
    if punteggi_2018:
        n_attributi = len(punteggi_2018)
        n_cols = 3
        n_rows = (n_attributi + n_cols - 1) // n_cols

        fig, axes = plt.subplots(n_rows, n_cols, figsize=(15, 4 * n_rows))
        axes = axes.flatten() if n_attributi > 1 else [axes]

        for idx, (attributo, df) in enumerate(punteggi_2018.items()):
            valori = df['punteggio'].dropna()
            if len(valori) == 0:
                continue
            ax = axes[idx]
            ax.hist(valori, bins=20, edgecolor='black', alpha=0.7, color='steelblue')
            ax.set_title(f"{attributo}\n(N={len(valori)}, μ={valori.mean():.2f})")
            ax.set_xlabel("Punteggio")
            ax.set_ylabel("Frequenza")
            ax.axvline(valori.mean(), color='red', linestyle='--', label=f'Media={valori.mean():.2f}')
            ax.axvline(valori.median(), color='orange', linestyle=':', label=f'Mediana={valori.median():.2f}')
            ax.legend(fontsize=8)

        # Nascondi assi vuoti
        for idx in range(len(punteggi_2018), len(axes)):
            axes[idx].set_visible(False)

        fig.suptitle("Distribuzione Punteggi Individuali 2018 per Attributo", fontsize=14, y=1.02)
        plt.tight_layout()
        percorso = FIGURES_DIR / "punteggi_2018_distribuzione.png"
        fig.savefig(percorso, dpi=150, bbox_inches='tight')
        plt.close(fig)
        grafici_generati.append(str(percorso.relative_to(PROJECT_ROOT)))
        logger.info(f"  Salvato: {percorso.name}")

    # --- Grafico 2: Boxplot confronto attributi per anno (aggregati) ---
    if punteggi_aggregati:
        fig, axes = plt.subplots(1, len(punteggi_aggregati), figsize=(6 * len(punteggi_aggregati), 8))
        if len(punteggi_aggregati) == 1:
            axes = [axes]

        for idx, (anno, df) in enumerate(sorted(punteggi_aggregati.items())):
            # Trova le colonne attributo
            dati_plot = {}
            for attr in ATTRIBUTI_SENSORIALI:
                for col in df.columns:
                    if col.strip().lower() == attr.lower():
                        valori = pd.to_numeric(df[col], errors='coerce').dropna()
                        if len(valori) > 0:
                            dati_plot[attr] = valori
                        break

            if dati_plot:
                box_df = pd.DataFrame(dict([(k, pd.Series(v.values)) for k, v in dati_plot.items()]))
                box_df.boxplot(ax=axes[idx], rot=45, grid=True)
                axes[idx].set_title(f"Punteggi Aggregati {anno}")
                axes[idx].set_ylabel("Punteggio")

        fig.suptitle("Distribuzione Punteggi Medi Giuria per Anno", fontsize=14, y=1.02)
        plt.tight_layout()
        percorso = FIGURES_DIR / "punteggi_aggregati_boxplot.png"
        fig.savefig(percorso, dpi=150, bbox_inches='tight')
        plt.close(fig)
        grafici_generati.append(str(percorso.relative_to(PROJECT_ROOT)))
        logger.info(f"  Salvato: {percorso.name}")

    # --- Grafico 3: Matrice di correlazione 2018 ---
    if punteggi_2018:
        # Creiamo un DataFrame pivot: per ogni campione, i punteggi medi per attributo
        punteggi_per_campione: Dict[str, pd.Series] = {}
        for attributo, df in punteggi_2018.items():
            medie = df.groupby(['Seduta', 'Prod'])['punteggio'].mean()
            punteggi_per_campione[attributo] = medie

        corr_df = pd.DataFrame(punteggi_per_campione)

        if len(corr_df.columns) >= 2:
            matrice_corr = corr_df.corr()

            fig, ax = plt.subplots(figsize=(10, 8))
            mask = np.triu(np.ones_like(matrice_corr, dtype=bool), k=1)
            sns.heatmap(
                matrice_corr,
                mask=mask,
                annot=True,
                fmt=".2f",
                cmap="RdBu_r",
                center=0,
                vmin=-1,
                vmax=1,
                ax=ax,
                square=True,
            )
            ax.set_title("Matrice Correlazione tra Attributi (2018, medie per campione)")
            plt.tight_layout()
            percorso = FIGURES_DIR / "correlazione_attributi_2018.png"
            fig.savefig(percorso, dpi=150, bbox_inches='tight')
            plt.close(fig)
            grafici_generati.append(str(percorso.relative_to(PROJECT_ROOT)))
            logger.info(f"  Salvato: {percorso.name}")

    # --- Grafico 4: Varianza inter-panelista ---
    if punteggi_2018:
        std_per_attributo: Dict[str, List[float]] = {}
        for attributo, df in punteggi_2018.items():
            df_validi = df.dropna(subset=['punteggio'])
            varianze = df_validi.groupby(['Seduta', 'Prod'])['punteggio'].std().dropna()
            if len(varianze) > 0:
                std_per_attributo[attributo] = varianze.values.tolist()

        if std_per_attributo:
            fig, ax = plt.subplots(figsize=(12, 6))
            box_data = [std_per_attributo[attr] for attr in std_per_attributo]
            bp = ax.boxplot(box_data, tick_labels=list(std_per_attributo.keys()), patch_artist=True)
            for patch in bp['boxes']:
                patch.set_facecolor('lightcoral')
            ax.set_title("Varianza Inter-Panelista per Attributo (2018)\n(Std dei punteggi tra panelisti per lo stesso campione)")
            ax.set_ylabel("Deviazione Standard")
            ax.tick_params(axis='x', rotation=45)
            plt.tight_layout()
            percorso = FIGURES_DIR / "varianza_inter_panelista_2018.png"
            fig.savefig(percorso, dpi=150, bbox_inches='tight')
            plt.close(fig)
            grafici_generati.append(str(percorso.relative_to(PROJECT_ROOT)))
            logger.info(f"  Salvato: {percorso.name}")

    return grafici_generati


def esegui_analisi_punteggi() -> Tuple[Dict[str, Any], List[str]]:
    """Esegue l'intera analisi dei punteggi numerici.

    Returns:
        Tuple con (statistiche calcolate, lista percorsi grafici generati).
    """
    logger.info("=" * 60)
    logger.info("SEZIONE 2: ANALISI PUNTEGGI NUMERICI")
    logger.info("=" * 60)

    punteggi_2018 = carica_punteggi_2018()
    punteggi_aggregati = carica_punteggi_aggregati()
    statistiche = calcola_statistiche_punteggi(punteggi_2018, punteggi_aggregati)
    grafici = genera_grafici_punteggi(punteggi_2018, punteggi_aggregati)

    return statistiche, grafici


# ============================================================================
# SEZIONE 3: ANALISI TESTUALE COMMENTI
# ============================================================================

def carica_tutti_commenti() -> Dict[str, Dict[str, pd.DataFrame]]:
    """Carica tutti i commenti da tutti gli anni e attributi.

    Usa i file CSV (già esportati dai fogli Excel) per uniformità.

    Returns:
        Dizionario annidato: {anno: {attributo: DataFrame}}.
    """
    logger.info("Caricamento commenti da tutti i file CSV...")
    tutti: Dict[str, Dict[str, pd.DataFrame]] = {}

    if not CSV_DIR.exists():
        logger.error(f"Cartella CSV non trovata: {CSV_DIR}")
        return tutti

    for csv_file in sorted(CSV_DIR.glob("*.csv")):
        nome = csv_file.stem  # es. "Commenti TOT_2018_Profumo"

        # Determina anno e attributo dal nome del file
        anno = None
        attributo = None

        if "2018" in nome:
            anno = "2018"
            # Attributo è tutto dopo "2018_"
            parts = nome.split("2018_", 1)
            if len(parts) > 1:
                attributo = parts[1]
        elif "2019" in nome:
            anno = "2019"
            parts = nome.split("2019_", 1)
            if len(parts) > 1:
                attributo = parts[1]
        elif "2020" in nome:
            anno = "2020"
            parts = nome.split("2020_", 1)
            if len(parts) > 1:
                attributo = parts[1]
        elif "2021" in nome:
            anno = "2021"
            parts = nome.split("2021_", 1)
            if len(parts) > 1:
                attributo = parts[1]

        # Salta file che non sono attributi (es. date_sedute)
        if anno is None or attributo is None:
            continue
        if 'date' in attributo.lower():
            continue

        try:
            df = pd.read_csv(csv_file, encoding='utf-8')

            # Applica correzioni in memoria (strip colonne, \xa0, righe vuote, ecc.)
            df = pulisci_dataframe(df, csv_file.name)

            # Trova la colonna commenti
            col_commenti = None
            for col in df.columns:
                if 'commenti' in col.lower() or 'comment' in col.lower():
                    col_commenti = col
                    break

            if col_commenti:
                df['commento_pulito'] = df[col_commenti].apply(pulisci_testo)

            # Normalizza il nome dell'attributo (es. "Colore della pasta" → "Colore della Pasta")
            attributo_canonico = normalizza_nome_attributo(attributo)
            if attributo_canonico != attributo:
                registro.registra(
                    'nome_attributo_normalizzato', csv_file.name,
                    f"Attributo '{attributo}' → '{attributo_canonico}'",
                )
                attributo = attributo_canonico

            if anno not in tutti:
                tutti[anno] = {}
            tutti[anno][attributo] = df

        except Exception as e:
            logger.warning(f"  Errore leggendo {csv_file.name}: {e}")

    for anno, attrs in tutti.items():
        logger.info(f"  Anno {anno}: {len(attrs)} attributi caricati")

    return tutti


def analisi_frequenza_parole(
    tutti_commenti: Dict[str, Dict[str, pd.DataFrame]],
    top_n: int = 50
) -> Dict[str, Dict[str, List[Tuple[str, int]]]]:
    """Calcola le parole più frequenti per ogni attributo.

    Per ogni attributo sensoriale, estrae le top N parole più usate
    nei commenti di TUTTI gli anni combinati. Questo serve per capire
    il vocabolario dei panelisti e identificare pattern.

    Args:
        tutti_commenti: Dati commenti per anno/attributo.
        top_n: Numero di parole top da estrarre.

    Returns:
        Dizionario {attributo: {anno: [(parola, conteggio), ...]}}.
    """
    logger.info(f"Analisi frequenza parole (top {top_n} per attributo)...")

    # Stopword italiane di base (le più comuni, non informative)
    stopwords_it = {
        'di', 'e', 'il', 'la', 'le', 'lo', 'i', 'gli', 'un', 'una', 'uno',
        'del', 'della', 'dei', 'degli', 'delle', 'al', 'alla', 'ai', 'alle',
        'da', 'dal', 'dalla', 'in', 'nel', 'nella', 'con', 'su', 'per', 'tra',
        'fra', 'a', 'che', 'non', 'si', 'ma', 'come', 'è', 'sono', 'ha', 'ho',
        'più', 'piu', 'molto', 'poco', 'anche', 'poi', 'già', 'se', 'o',
    }

    risultati: Dict[str, Dict[str, List[Tuple[str, int]]]] = {}

    # Raccogliamo tutti gli attributi unici
    tutti_attributi: set = set()
    for anno_data in tutti_commenti.values():
        tutti_attributi.update(anno_data.keys())

    for attributo in sorted(tutti_attributi):
        risultati[attributo] = {}

        # Conteggio globale (tutti gli anni)
        conteggio_globale: Counter = Counter()

        for anno, anno_data in sorted(tutti_commenti.items()):
            if attributo not in anno_data:
                continue

            df = anno_data[attributo]
            if 'commento_pulito' not in df.columns:
                continue

            conteggio_anno: Counter = Counter()

            for commento in df['commento_pulito']:
                if not commento or commento.strip() == "":
                    continue
                # Tokenizzazione semplice: split su spazi e punteggiatura
                parole = re.findall(r'[a-zà-ùA-ZÀ-Ù]+', commento.lower())
                parole_filtrate = [p for p in parole if p not in stopwords_it and len(p) > 1]
                conteggio_anno.update(parole_filtrate)
                conteggio_globale.update(parole_filtrate)

            risultati[attributo][anno] = conteggio_anno.most_common(top_n)

        risultati[attributo]['GLOBALE'] = conteggio_globale.most_common(top_n)

        top5 = conteggio_globale.most_common(5)
        logger.info(f"  {attributo}: top 5 globale = {top5}")

    return risultati


def identifica_pattern_telegrafici(
    tutti_commenti: Dict[str, Dict[str, pd.DataFrame]]
) -> Dict[str, Any]:
    """Identifica abbreviazioni e pattern telegrafici nei commenti.

    I panelisti usano spesso abbreviazioni come:
    - "cr." per "crosta", "sp." per "spessore", "str." per "struttura"
    - "ok", "normale", "nella norma" (commenti generici)
    - Punteggiatura speciale: "<", ">", "+"

    Args:
        tutti_commenti: Dati commenti per anno/attributo.

    Returns:
        Dizionario con pattern trovati e loro frequenza.
    """
    logger.info("Identificazione pattern telegrafici...")

    # Pattern regex per abbreviazioni comuni
    pattern_abbreviazioni = re.compile(
        r'\b([a-zà-ù]{1,4})\.',  # Parole corte seguite da punto (es. "cr.", "sp.")
        re.IGNORECASE
    )

    # Pattern per commenti generici
    pattern_generici = re.compile(
        r'^(ok|normale|nella norma|regolare|buon[oa]?|niente.*segnalare|nulla.*particolare)$',
        re.IGNORECASE
    )

    # Pattern punteggiatura speciale
    pattern_speciali = re.compile(r'[<>+/]')

    abbreviazioni: Counter = Counter()
    commenti_generici: Counter = Counter()
    punteggiatura_speciale: Counter = Counter()
    tutti_commenti_testo: List[str] = []

    for anno, anno_data in tutti_commenti.items():
        for attributo, df in anno_data.items():
            if 'commento_pulito' not in df.columns:
                continue

            for commento in df['commento_pulito']:
                if not commento:
                    continue

                tutti_commenti_testo.append(commento)

                # Cerca abbreviazioni
                for match in pattern_abbreviazioni.finditer(commento):
                    abbreviazioni[match.group(0).lower()] += 1

                # Cerca commenti generici
                if pattern_generici.match(commento.strip()):
                    commenti_generici[commento.strip().lower()] += 1

                # Cerca punteggiatura speciale
                for char in pattern_speciali.findall(commento):
                    punteggiatura_speciale[char] += 1

    risultati = {
        'abbreviazioni_top30': abbreviazioni.most_common(30),
        'commenti_generici_top20': commenti_generici.most_common(20),
        'punteggiatura_speciale': dict(punteggiatura_speciale.most_common()),
        'n_commenti_totali': len(tutti_commenti_testo),
        'n_commenti_vuoti': sum(1 for c in tutti_commenti_testo if c.strip() == ""),
        'lunghezza_media_commento': np.mean([len(c) for c in tutti_commenti_testo if c.strip()]) if tutti_commenti_testo else 0,
    }

    logger.info(f"  Abbreviazioni trovate: {len(abbreviazioni)}")
    logger.info(f"  Top 10 abbreviazioni: {abbreviazioni.most_common(10)}")
    logger.info(f"  Commenti generici: {sum(commenti_generici.values())}")

    return risultati


def analisi_termini_punteggio(
    punteggi_2018: Dict[str, pd.DataFrame]
) -> Dict[str, Dict[str, List[Tuple[str, int]]]]:
    """Analizza quali termini appaiono con punteggi alti vs bassi.

    Solo per il 2018 (unico anno con punteggi individuali + commenti).
    Divide i commenti in 3 fasce:
    - Punteggi bassi (1-4): commenti negativi o difetti
    - Punteggi medi (5-7): commenti standard
    - Punteggi alti (8-10): commenti positivi o eccellenti

    Args:
        punteggi_2018: Dati 2018 con punteggi e commenti.

    Returns:
        Dizionario {attributo: {fascia: [(parola, conteggio), ...]}}.
    """
    logger.info("Analisi correlazione termini-punteggio (2018)...")

    stopwords_it = {
        'di', 'e', 'il', 'la', 'le', 'lo', 'i', 'gli', 'un', 'una', 'uno',
        'del', 'della', 'dei', 'degli', 'delle', 'al', 'alla', 'ai', 'alle',
        'da', 'dal', 'dalla', 'in', 'nel', 'nella', 'con', 'su', 'per', 'tra',
        'fra', 'a', 'che', 'non', 'si', 'ma', 'come', 'è', 'sono', 'ha', 'ho',
        'più', 'piu', 'molto', 'poco', 'anche', 'poi', 'già', 'se', 'o',
    }

    fasce = {
        'bassi_1-4': (1.0, 4.99),
        'medi_5-7': (5.0, 7.0),
        'alti_8-10': (8.0, 10.0),
    }

    risultati: Dict[str, Dict[str, List[Tuple[str, int]]]] = {}

    for attributo, df in punteggi_2018.items():
        risultati[attributo] = {}

        for fascia_nome, (pmin, pmax) in fasce.items():
            mask = (df['punteggio'] >= pmin) & (df['punteggio'] <= pmax)
            commenti_fascia = df.loc[mask, 'commento_pulito']

            conteggio: Counter = Counter()
            for commento in commenti_fascia:
                if not commento:
                    continue
                parole = re.findall(r'[a-zà-ùA-ZÀ-Ù]+', commento.lower())
                parole_filtrate = [p for p in parole if p not in stopwords_it and len(p) > 1]
                conteggio.update(parole_filtrate)

            risultati[attributo][fascia_nome] = conteggio.most_common(30)

            logger.debug(
                f"  {attributo} [{fascia_nome}]: {mask.sum()} commenti, "
                f"top 5 = {conteggio.most_common(5)}"
            )

    return risultati


def identifica_termini_dialettali(
    tutti_commenti: Dict[str, Dict[str, pd.DataFrame]]
) -> List[Dict[str, Any]]:
    """Cerca termini potenzialmente dialettali o abbreviazioni non standard.

    Euristica: termini che non appartengono al vocabolario italiano standard
    e che appaiono più di una volta. Cerchiamo anche pattern specifici del
    dialetto trentino e abbreviazioni del settore caseario.

    Args:
        tutti_commenti: Dati commenti per anno/attributo.

    Returns:
        Lista di termini sospetti con contesto e frequenza.
    """
    logger.info("Identificazione termini potenzialmente dialettali/abbreviazioni...")

    # Termini sospetti noti dal dominio caseario trentino
    termini_sospetti_noti = {
        'nostrano', 'malga', 'scalzo', 'scalzi', 'piatti', 'cagliata',
        'insilato', 'propionica', 'butirrico', 'propionico',
    }

    # Raccogliamo tutti i termini unici con bassa frequenza
    conteggio_globale: Counter = Counter()
    contesti: Dict[str, List[str]] = {}

    for anno, anno_data in tutti_commenti.items():
        for attributo, df in anno_data.items():
            if 'commento_pulito' not in df.columns:
                continue
            for commento in df['commento_pulito']:
                if not commento:
                    continue
                parole = re.findall(r'[a-zà-ùA-ZÀ-Ù]+', commento.lower())
                for parola in parole:
                    if len(parola) > 2:
                        conteggio_globale[parola] += 1
                        if parola not in contesti:
                            contesti[parola] = []
                        if len(contesti[parola]) < 3:  # Salviamo max 3 contesti
                            contesti[parola].append(commento[:100])

    # Cerchiamo termini che sembrano abbreviazioni (parole < 4 caratteri che non sono comuni)
    parole_comuni_corte = {
        'di', 'e', 'il', 'la', 'le', 'lo', 'i', 'un', 'ma', 'no', 'sì',
        'si', 'me', 'te', 'mi', 'ti', 'ci', 'vi', 'ne', 'se', 'al', 'su',
        'da', 'in', 'ha', 'ho', 'ok', 'cm', 'mm', 'kg',
    }

    risultati: List[Dict[str, Any]] = []

    # Termini noti dal dominio
    for termine in termini_sospetti_noti:
        if termine in conteggio_globale:
            risultati.append({
                'termine': termine,
                'tipo': 'termine_dominio_caseario',
                'frequenza': conteggio_globale[termine],
                'contesto_esempio': contesti.get(termine, [''])[0],
            })

    # Abbreviazioni (parole corte non comuni, freq > 2)
    for parola, freq in conteggio_globale.items():
        if len(parola) <= 3 and parola not in parole_comuni_corte and freq >= 2:
            risultati.append({
                'termine': parola,
                'tipo': 'possibile_abbreviazione',
                'frequenza': freq,
                'contesto_esempio': contesti.get(parola, [''])[0],
            })

    # Termini con apostrofo o apice (indicativo di dialetto o abbreviazione)
    # Li cerchiamo nei commenti originali
    termini_con_apostrofo: Counter = Counter()
    for anno, anno_data in tutti_commenti.items():
        for attributo, df in anno_data.items():
            if 'commento_pulito' not in df.columns:
                continue
            for commento in df['commento_pulito']:
                if not commento:
                    continue
                matches = re.findall(r"[a-zà-ù]+['''][a-zà-ù]*", commento.lower())
                for m in matches:
                    termini_con_apostrofo[m] += 1

    for termine, freq in termini_con_apostrofo.most_common(30):
        if freq >= 2:
            risultati.append({
                'termine': termine,
                'tipo': 'termine_con_apostrofo',
                'frequenza': freq,
                'contesto_esempio': '',
            })

    logger.info(f"  Trovati {len(risultati)} termini sospetti/dialettali")

    return risultati


def genera_grafici_testo(
    frequenza_parole: Dict[str, Dict[str, List[Tuple[str, int]]]],
    termini_punteggio: Dict[str, Dict[str, List[Tuple[str, int]]]]
) -> List[str]:
    """Genera grafici per l'analisi testuale.

    Produce:
    1. Barplot top 20 parole per attributo (globale)
    2. Confronto parole con punteggi alti vs bassi (2018)

    Args:
        frequenza_parole: Risultato di analisi_frequenza_parole().
        termini_punteggio: Risultato di analisi_termini_punteggio().

    Returns:
        Lista percorsi grafici generati.
    """
    logger.info("Generazione grafici analisi testuale...")
    grafici_generati: List[str] = []

    # --- Grafico 1: Top 20 parole per attributo (globale) ---
    attributi_con_dati = [a for a in frequenza_parole if 'GLOBALE' in frequenza_parole[a] and frequenza_parole[a]['GLOBALE']]

    if attributi_con_dati:
        n_attr = len(attributi_con_dati)
        n_cols = 3
        n_rows = (n_attr + n_cols - 1) // n_cols

        fig, axes = plt.subplots(n_rows, n_cols, figsize=(18, 5 * n_rows))
        axes = axes.flatten()

        for idx, attributo in enumerate(sorted(attributi_con_dati)):
            top20 = frequenza_parole[attributo]['GLOBALE'][:20]
            if not top20:
                continue

            parole, conteggi = zip(*top20)
            ax = axes[idx]
            bars = ax.barh(range(len(parole)), conteggi, color='teal', alpha=0.7)
            ax.set_yticks(range(len(parole)))
            ax.set_yticklabels(parole, fontsize=9)
            ax.invert_yaxis()
            ax.set_title(f"{attributo}", fontsize=11)
            ax.set_xlabel("Frequenza")

        for idx in range(len(attributi_con_dati), len(axes)):
            axes[idx].set_visible(False)

        fig.suptitle("Top 20 Parole più Frequenti per Attributo (tutti gli anni)", fontsize=14, y=1.02)
        plt.tight_layout()
        percorso = FIGURES_DIR / "top20_parole_per_attributo.png"
        fig.savefig(percorso, dpi=150, bbox_inches='tight')
        plt.close(fig)
        grafici_generati.append(str(percorso.relative_to(PROJECT_ROOT)))
        logger.info(f"  Salvato: {percorso.name}")

    # --- Grafico 2: Confronto termini punteggi alti vs bassi (2018) ---
    if termini_punteggio:
        # Scegliamo gli attributi con dati significativi nelle fasce alta e bassa
        for attributo, fasce in termini_punteggio.items():
            alti = dict(fasce.get('alti_8-10', [])[:15])
            bassi = dict(fasce.get('bassi_1-4', [])[:15])

            if not alti and not bassi:
                continue

            # Uniamo i termini per confronto
            tutti_termini = sorted(set(list(alti.keys()) + list(bassi.keys())),
                                   key=lambda x: alti.get(x, 0) + bassi.get(x, 0),
                                   reverse=True)[:20]

            if len(tutti_termini) < 3:
                continue

            fig, ax = plt.subplots(figsize=(12, 7))
            y_pos = range(len(tutti_termini))

            freq_alti = [alti.get(t, 0) for t in tutti_termini]
            freq_bassi = [bassi.get(t, 0) for t in tutti_termini]

            ax.barh(y_pos, freq_alti, 0.4, label='Punteggi alti (8-10)', color='green', alpha=0.7)
            ax.barh([y + 0.4 for y in y_pos], freq_bassi, 0.4, label='Punteggi bassi (1-4)', color='red', alpha=0.7)
            ax.set_yticks([y + 0.2 for y in y_pos])
            ax.set_yticklabels(tutti_termini)
            ax.invert_yaxis()
            ax.set_xlabel("Frequenza")
            ax.set_title(f"{attributo}: Termini con Punteggi Alti vs Bassi (2018)")
            ax.legend()
            plt.tight_layout()

            nome_safe = re.sub(r'[^\w]', '_', attributo.lower())
            percorso = FIGURES_DIR / f"termini_alti_vs_bassi_{nome_safe}.png"
            fig.savefig(percorso, dpi=150, bbox_inches='tight')
            plt.close(fig)
            grafici_generati.append(str(percorso.relative_to(PROJECT_ROOT)))

        logger.info(f"  Generati {len(grafici_generati)} grafici confronto termini-punteggio")

    return grafici_generati


def esegui_analisi_testuale(
    punteggi_2018: Dict[str, pd.DataFrame]
) -> Tuple[Dict[str, Any], List[str]]:
    """Esegue l'intera analisi testuale dei commenti.

    Args:
        punteggi_2018: Dati 2018 per l'analisi termini-punteggio.

    Returns:
        Tuple con (risultati analisi, lista grafici generati).
    """
    logger.info("=" * 60)
    logger.info("SEZIONE 3: ANALISI TESTUALE COMMENTI")
    logger.info("=" * 60)

    tutti_commenti = carica_tutti_commenti()
    frequenza_parole = analisi_frequenza_parole(tutti_commenti)
    pattern_telegrafici = identifica_pattern_telegrafici(tutti_commenti)
    termini_punteggio = analisi_termini_punteggio(punteggi_2018)
    termini_dialettali = identifica_termini_dialettali(tutti_commenti)
    grafici = genera_grafici_testo(frequenza_parole, termini_punteggio)

    return {
        'frequenza_parole': frequenza_parole,
        'pattern_telegrafici': pattern_telegrafici,
        'termini_punteggio': termini_punteggio,
        'termini_dialettali': termini_dialettali,
    }, grafici


# ============================================================================
# SEZIONE 4: PROBLEMI QUALITÀ DATI
# ============================================================================

def verifica_encoding(tutti_commenti_dir: Path) -> List[Dict[str, Any]]:
    """Verifica problemi di encoding nei file CSV.

    Cerca:
    - Caratteri \xa0 (non-breaking space) — molto comuni nel 2021
    - Caratteri non-ASCII inaspettati
    - Mojibake (sequenze come Â, Ã che indicano encoding sbagliato)

    Args:
        tutti_commenti_dir: Directory con i file CSV.

    Returns:
        Lista di problemi di encoding trovati.
    """
    logger.info("Verifica encoding dei file...")
    problemi: List[Dict[str, Any]] = []

    if not tutti_commenti_dir.exists():
        return problemi

    pattern_mojibake = re.compile(r'[Â\x80-\x9f]')

    for csv_file in sorted(tutti_commenti_dir.glob("*.csv")):
        try:
            with open(csv_file, 'r', encoding='utf-8') as f:
                contenuto = f.read()

            # Conta \xa0
            n_nbsp = contenuto.count('\xa0')
            if n_nbsp > 0:
                problemi.append({
                    'file': csv_file.name,
                    'tipo': 'non_breaking_space',
                    'conteggio': n_nbsp,
                    'dettaglio': f"Trovati {n_nbsp} caratteri \\xa0 (non-breaking space)",
                })

            # Cerca mojibake
            mojibake_matches = pattern_mojibake.findall(contenuto)
            if mojibake_matches:
                problemi.append({
                    'file': csv_file.name,
                    'tipo': 'possibile_mojibake',
                    'conteggio': len(mojibake_matches),
                    'dettaglio': f"Trovati {len(mojibake_matches)} caratteri sospetti",
                })

        except UnicodeDecodeError as e:
            problemi.append({
                'file': csv_file.name,
                'tipo': 'errore_encoding',
                'conteggio': 1,
                'dettaglio': str(e),
            })

    logger.info(f"  Problemi encoding trovati: {len(problemi)}")
    return problemi


def analizza_dati_mancanti(tutti_commenti_dir: Path) -> List[Dict[str, Any]]:
    """Identifica righe con dati mancanti nei file CSV.

    Per ogni file, conta:
    - Righe completamente vuote
    - Campi specifici mancanti (Prodotto, Panelista, Commenti)

    Args:
        tutti_commenti_dir: Directory con i file CSV.

    Returns:
        Lista con statistiche missing data per file.
    """
    logger.info("Analisi dati mancanti...")
    risultati: List[Dict[str, Any]] = []

    if not tutti_commenti_dir.exists():
        return risultati

    for csv_file in sorted(tutti_commenti_dir.glob("*.csv")):
        if 'date' in csv_file.name.lower():
            continue

        try:
            df = pd.read_csv(csv_file, encoding='utf-8')

            info: Dict[str, Any] = {
                'file': csv_file.name,
                'righe_totali': len(df),
                'righe_completamente_vuote': int(df.isna().all(axis=1).sum()),
                'missing_per_colonna': {},
            }

            for col in df.columns:
                n_mancanti = int(df[col].isna().sum())
                if n_mancanti > 0:
                    info['missing_per_colonna'][col] = n_mancanti

            # Per 2019-2021 controlliamo specificamente Prodotto e Panelista
            for campo in ['Prodotto', 'Panelista']:
                if campo in df.columns:
                    n_vuoti = int(df[campo].isna().sum())
                    if n_vuoti > 0:
                        info[f'missing_{campo.lower()}'] = n_vuoti

            # Commenti vuoti
            col_commenti = None
            for col in df.columns:
                if 'commenti' in col.lower():
                    col_commenti = col
                    break
            if col_commenti:
                info['commenti_vuoti'] = int(df[col_commenti].isna().sum())

            risultati.append(info)

        except Exception as e:
            logger.warning(f"  Errore analizzando {csv_file.name}: {e}")

    n_problematici = sum(1 for r in risultati if r.get('righe_completamente_vuote', 0) > 0)
    logger.info(f"  File analizzati: {len(risultati)}, con righe vuote: {n_problematici}")

    return risultati


def analizza_validation_report() -> Dict[str, Any]:
    """Analizza il validation report esistente per cross-check.

    Il file session_validation_report.csv contiene issue di qualità dati
    già identificate in una fase precedente. Qui le categorizziamo e
    le quantifichiamo per tipo.

    Returns:
        Dizionario con analisi del validation report.
    """
    logger.info("Analisi validation report (cross-check)...")
    percorso = VALIDATION_DIR / "session_validation_report.csv"

    if not percorso.exists():
        logger.warning(f"  Validation report non trovato: {percorso}")
        return {'trovato': False}

    df = pd.read_csv(percorso, encoding='utf-8')

    risultati: Dict[str, Any] = {
        'trovato': True,
        'totale_issue': len(df),
        'colonne': list(df.columns),
        'issue_per_tipo': {},
        'issue_per_file': {},
        'issue_per_anno': {},
    }

    # Issue per tipo
    if 'issue_type' in df.columns:
        risultati['issue_per_tipo'] = df['issue_type'].value_counts().to_dict()

    # Issue per file sorgente
    if 'csv_file' in df.columns:
        risultati['issue_per_file'] = df['csv_file'].value_counts().to_dict()

    # Issue per anno (estratto dal nome del file)
    if 'csv_file' in df.columns:
        for anno in ['2018', '2019', '2020', '2021']:
            mask = df['csv_file'].str.contains(anno, na=False)
            risultati['issue_per_anno'][anno] = int(mask.sum())

    logger.info(f"  Totale issue: {risultati['totale_issue']}")
    logger.info(f"  Issue per tipo: {risultati.get('issue_per_tipo', {})}")

    return risultati


def trova_inconsistenze(
    risultati_struttura: Dict[str, Any]
) -> List[Dict[str, str]]:
    """Identifica inconsistenze tra file e strutture dati.

    Cerca:
    - Colonne extra non documentate (es. 8a colonna in Profumo 2020)
    - Formati date diversi
    - Capitalizzazione inconsistente nei nomi attributi

    Args:
        risultati_struttura: Output di esegui_analisi_struttura().

    Returns:
        Lista di inconsistenze trovate.
    """
    logger.info("Ricerca inconsistenze...")
    inconsistenze: List[Dict[str, str]] = []

    # Verifica colonne extra
    for anno, fogli in risultati_struttura.get('excel_commenti', {}).items():
        for foglio in fogli:
            n_col_attese = 5 if anno == "2018" else 7
            n_col_effettive = foglio['colonne']

            if n_col_effettive > n_col_attese:
                inconsistenze.append({
                    'tipo': 'colonna_extra',
                    'file': foglio['file'],
                    'foglio': foglio['foglio'],
                    'dettaglio': (
                        f"Attese {n_col_attese} colonne, trovate {n_col_effettive}. "
                        f"Colonne: {foglio['nomi_colonne']}"
                    ),
                })

    # Verifica capitalizzazione attributi nei nomi dei fogli
    nomi_fogli_visti: Dict[str, List[str]] = {}
    for anno, fogli in risultati_struttura.get('excel_commenti', {}).items():
        for foglio in fogli:
            nome_lower = foglio['foglio'].lower().strip()
            if nome_lower not in nomi_fogli_visti:
                nomi_fogli_visti[nome_lower] = []
            nomi_fogli_visti[nome_lower].append(f"{foglio['file']}: '{foglio['foglio']}'")

    for nome_lower, occorrenze in nomi_fogli_visti.items():
        nomi_originali = set(o.split(": '")[1].rstrip("'") for o in occorrenze)
        if len(nomi_originali) > 1:
            inconsistenze.append({
                'tipo': 'capitalizzazione_inconsistente',
                'file': 'multipli',
                'foglio': nome_lower,
                'dettaglio': f"Varianti trovate: {nomi_originali}",
            })

    logger.info(f"  Inconsistenze trovate: {len(inconsistenze)}")
    return inconsistenze


def esegui_analisi_qualita() -> Dict[str, Any]:
    """Esegue l'intera analisi di qualità dati.

    Returns:
        Dizionario con tutti i risultati dell'analisi qualità.
    """
    logger.info("=" * 60)
    logger.info("SEZIONE 4: PROBLEMI QUALITÀ DATI")
    logger.info("=" * 60)

    problemi_encoding = verifica_encoding(CSV_DIR)
    dati_mancanti = analizza_dati_mancanti(CSV_DIR)
    validation_report = analizza_validation_report()

    return {
        'encoding': problemi_encoding,
        'dati_mancanti': dati_mancanti,
        'validation_report': validation_report,
    }


# ============================================================================
# SEZIONE 5: GENERAZIONE OUTPUT
# ============================================================================

def genera_report_markdown(
    struttura: Dict[str, Any],
    statistiche_punteggi: Dict[str, Any],
    analisi_testo: Dict[str, Any],
    qualita: Dict[str, Any],
    inconsistenze: List[Dict[str, str]],
    grafici: List[str],
) -> str:
    """Genera il report markdown completo dell'analisi esplorativa.

    Il report è organizzato in sezioni che rispecchiano le 4 analisi principali,
    con tabelle, elenchi e riferimenti ai grafici generati.

    Args:
        struttura: Risultati analisi struttura file.
        statistiche_punteggi: Risultati analisi punteggi.
        analisi_testo: Risultati analisi testuale.
        qualita: Risultati analisi qualità dati.
        inconsistenze: Lista inconsistenze trovate.
        grafici: Lista percorsi grafici.

    Returns:
        Contenuto del report in formato markdown.
    """
    logger.info("Generazione report markdown...")

    md: List[str] = []
    md.append("# Analisi Esplorativa - Dataset Grana Trentino")
    md.append("")
    md.append(f"**Data generazione:** 2026-02-10")
    md.append(f"**Script:** `src/data/01_exploratory_analysis.py`")
    md.append("")
    md.append("---")
    md.append("")

    # ---- SEZIONE 1: STRUTTURA FILE ----
    md.append("## 1. Analisi Struttura File")
    md.append("")

    # File Excel commenti
    md.append("### 1.1 File Excel Commenti Liberi")
    md.append("")
    md.append("| File | Anno | N. Fogli | Fogli |")
    md.append("|------|------|----------|-------|")

    for anno, fogli in sorted(struttura.get('excel_commenti', {}).items()):
        nomi = [f['foglio'] for f in fogli]
        n_fogli = len(fogli)
        file_name = fogli[0]['file'] if fogli else "?"
        md.append(f"| {file_name} | {anno} | {n_fogli} | {', '.join(nomi)} |")

    md.append("")

    # Dettaglio per foglio
    md.append("### 1.2 Dettaglio per Foglio")
    md.append("")
    md.append("| File | Foglio | Righe | Colonne | Schema |")
    md.append("|------|--------|-------|---------|--------|")

    for anno, fogli in sorted(struttura.get('excel_commenti', {}).items()):
        for foglio in fogli:
            schema = ", ".join(foglio['nomi_colonne'][:5])
            if len(foglio['nomi_colonne']) > 5:
                schema += f", ... (+{len(foglio['nomi_colonne'])-5})"
            md.append(
                f"| {foglio['file']} | {foglio['foglio']} | "
                f"{foglio['righe']} | {foglio['colonne']} | {schema} |"
            )

    md.append("")

    # Differenze schema
    md.append("### 1.3 Differenze Schema 2018 vs 2019-2021")
    md.append("")
    diff = struttura.get('differenze_schema', {})
    md.append(f"**Schema 2018 (5 colonne):** `{diff.get('schema_2018', [])}`")
    md.append("")
    md.append(f"**Schema 2019-2021 (7 colonne):** `{diff.get('schema_2019_2021', [])}`")
    md.append("")
    md.append(f"**Nota:** {diff.get('nota', '')}")
    md.append("")

    # ---- SEZIONE 2: PUNTEGGI ----
    md.append("---")
    md.append("")
    md.append("## 2. Analisi Punteggi Numerici")
    md.append("")

    # Punteggi 2018
    md.append("### 2.1 Punteggi Individuali 2018")
    md.append("")
    if statistiche_punteggi.get('individuali_2018'):
        md.append("| Attributo | N | Media | Mediana | Std | Min | Max | Q25 | Q75 |")
        md.append("|-----------|---|-------|---------|-----|-----|-----|-----|-----|")
        for attr, stats in sorted(statistiche_punteggi['individuali_2018'].items()):
            md.append(
                f"| {attr} | {stats['conteggio']} | {stats['media']:.2f} | "
                f"{stats['mediana']:.2f} | {stats['std']:.2f} | {stats['min']:.2f} | "
                f"{stats['max']:.2f} | {stats['q25']:.2f} | {stats['q75']:.2f} |"
            )
        md.append("")

    # Varianza inter-panelista
    md.append("### 2.2 Varianza Inter-Panelista (2018)")
    md.append("")
    md.append("Questa misura indica quanto i panelisti concordano: una deviazione standard")
    md.append("bassa tra panelisti significa buona concordanza.")
    md.append("")
    if statistiche_punteggi.get('varianza_inter_panelista'):
        md.append("| Attributo | Std Media | Std Mediana | Std Max | N Campioni | Media Panelisti/Campione |")
        md.append("|-----------|-----------|-------------|---------|------------|--------------------------|")
        for attr, stats in sorted(statistiche_punteggi['varianza_inter_panelista'].items()):
            md.append(
                f"| {attr} | {stats['media_std_tra_panelisti']:.3f} | "
                f"{stats['mediana_std_tra_panelisti']:.3f} | "
                f"{stats['max_std_tra_panelisti']:.3f} | "
                f"{stats['n_campioni_analizzati']} | "
                f"{stats['media_panelisti_per_campione']:.1f} |"
            )
        md.append("")

    # Punteggi aggregati
    md.append("### 2.3 Punteggi Aggregati Giuria (2019-2021)")
    md.append("")
    for anno, attrs in sorted(statistiche_punteggi.get('aggregati_per_anno', {}).items()):
        md.append(f"#### Anno {anno}")
        md.append("")
        md.append("| Attributo | N | Media | Mediana | Std | Min | Max |")
        md.append("|-----------|---|-------|---------|-----|-----|-----|")
        for attr, stats in sorted(attrs.items()):
            md.append(
                f"| {attr} | {stats['conteggio']} | {stats['media']:.2f} | "
                f"{stats['mediana']:.2f} | {stats['std']:.2f} | {stats['min']:.2f} | "
                f"{stats['max']:.2f} |"
            )
        md.append("")

    # Riferimento grafici punteggi
    md.append("### 2.4 Grafici")
    md.append("")
    for g in grafici:
        if 'punteggi' in g or 'correlazione' in g or 'varianza' in g:
            md.append(f"![{Path(g).stem}]({g})")
            md.append("")

    # ---- SEZIONE 3: ANALISI TESTUALE ----
    md.append("---")
    md.append("")
    md.append("## 3. Analisi Testuale Commenti")
    md.append("")

    # Top parole per attributo
    freq = analisi_testo.get('frequenza_parole', {})
    md.append("### 3.1 Top 20 Parole per Attributo (tutti gli anni)")
    md.append("")
    for attributo in sorted(freq.keys()):
        globale = freq[attributo].get('GLOBALE', [])
        if not globale:
            continue
        md.append(f"#### {attributo}")
        md.append("")
        top20 = globale[:20]
        md.append("| # | Parola | Frequenza |")
        md.append("|---|--------|-----------|")
        for i, (parola, conteggio) in enumerate(top20, 1):
            md.append(f"| {i} | {parola} | {conteggio} |")
        md.append("")

    # Pattern telegrafici
    pt = analisi_testo.get('pattern_telegrafici', {})
    md.append("### 3.2 Pattern Telegrafici e Abbreviazioni")
    md.append("")
    md.append(f"- **Commenti totali analizzati:** {pt.get('n_commenti_totali', 0)}")
    md.append(f"- **Commenti vuoti:** {pt.get('n_commenti_vuoti', 0)}")
    md.append(f"- **Lunghezza media commento:** {pt.get('lunghezza_media_commento', 0):.1f} caratteri")
    md.append("")

    abbreviazioni = pt.get('abbreviazioni_top30', [])
    if abbreviazioni:
        md.append("**Abbreviazioni più frequenti:**")
        md.append("")
        md.append("| Abbreviazione | Frequenza |")
        md.append("|---------------|-----------|")
        for abbr, freq_val in abbreviazioni[:20]:
            md.append(f"| {abbr} | {freq_val} |")
        md.append("")

    generici = pt.get('commenti_generici_top20', [])
    if generici:
        md.append("**Commenti generici ricorrenti:**")
        md.append("")
        for commento, freq_val in generici:
            md.append(f"- \"{commento}\" ({freq_val}x)")
        md.append("")

    # Termini con punteggi alti vs bassi
    tp = analisi_testo.get('termini_punteggio', {})
    md.append("### 3.3 Termini Associati a Punteggi Alti vs Bassi (2018)")
    md.append("")
    for attributo, fasce in sorted(tp.items()):
        alti = fasce.get('alti_8-10', [])[:10]
        bassi = fasce.get('bassi_1-4', [])[:10]
        if not alti and not bassi:
            continue
        md.append(f"#### {attributo}")
        md.append("")
        md.append("| Punteggi Alti (8-10) | Freq | Punteggi Bassi (1-4) | Freq |")
        md.append("|----------------------|------|----------------------|------|")
        max_len = max(len(alti), len(bassi))
        for i in range(max_len):
            alto = f"{alti[i][0]} | {alti[i][1]}" if i < len(alti) else " | "
            basso = f"{bassi[i][0]} | {bassi[i][1]}" if i < len(bassi) else " | "
            md.append(f"| {alto} | {basso} |")
        md.append("")

    # Termini dialettali
    td = analisi_testo.get('termini_dialettali', [])
    md.append("### 3.4 Termini Dialettali e Abbreviazioni Non Standard")
    md.append("")
    if td:
        md.append("| Termine | Tipo | Frequenza | Contesto Esempio |")
        md.append("|---------|------|-----------|------------------|")
        for t in sorted(td, key=lambda x: x['frequenza'], reverse=True)[:30]:
            contesto = t['contesto_esempio'][:60].replace('|', '/') if t['contesto_esempio'] else ""
            md.append(f"| {t['termine']} | {t['tipo']} | {t['frequenza']} | {contesto} |")
        md.append("")

    # Grafici testo
    md.append("### 3.5 Grafici")
    md.append("")
    for g in grafici:
        if 'parole' in g or 'termini' in g:
            md.append(f"![{Path(g).stem}]({g})")
            md.append("")

    # ---- SEZIONE 4: QUALITÀ DATI ----
    md.append("---")
    md.append("")
    md.append("## 4. Problemi Qualità Dati")
    md.append("")

    # Encoding
    enc = qualita.get('encoding', [])
    md.append("### 4.1 Problemi di Encoding")
    md.append("")
    if enc:
        md.append("| File | Tipo Problema | Conteggio | Dettaglio |")
        md.append("|------|---------------|-----------|-----------|")
        for p in enc:
            md.append(f"| {p['file']} | {p['tipo']} | {p['conteggio']} | {p['dettaglio']} |")
        md.append("")
    else:
        md.append("Nessun problema di encoding rilevato.")
        md.append("")

    # Dati mancanti
    dm = qualita.get('dati_mancanti', [])
    md.append("### 4.2 Dati Mancanti")
    md.append("")
    if dm:
        md.append("| File | Righe Totali | Righe Vuote | Commenti Vuoti |")
        md.append("|------|-------------|-------------|----------------|")
        for d in dm:
            md.append(
                f"| {d['file']} | {d['righe_totali']} | "
                f"{d.get('righe_completamente_vuote', 0)} | "
                f"{d.get('commenti_vuoti', 'N/A')} |"
            )
        md.append("")

    # Validation report
    vr = qualita.get('validation_report', {})
    md.append("### 4.3 Cross-Check con Validation Report")
    md.append("")
    if vr.get('trovato'):
        md.append(f"**Totale issue:** {vr['totale_issue']}")
        md.append("")
        md.append("**Issue per tipo:**")
        md.append("")
        for tipo, conteggio in sorted(vr.get('issue_per_tipo', {}).items(), key=lambda x: -x[1]):
            md.append(f"- `{tipo}`: {conteggio}")
        md.append("")
        md.append("**Issue per anno:**")
        md.append("")
        for anno, conteggio in sorted(vr.get('issue_per_anno', {}).items()):
            md.append(f"- {anno}: {conteggio}")
        md.append("")
    else:
        md.append("Validation report non trovato.")
        md.append("")

    # Inconsistenze
    md.append("### 4.4 Inconsistenze Trovate")
    md.append("")
    if inconsistenze:
        for inc in inconsistenze:
            md.append(f"- **{inc['tipo']}** in `{inc.get('file', '')}` foglio `{inc.get('foglio', '')}`: {inc['dettaglio']}")
        md.append("")
    else:
        md.append("Nessuna inconsistenza rilevante trovata.")
        md.append("")

    # ---- SEZIONE 4.5: CORREZIONI APPLICATE IN MEMORIA ----
    md.append("### 4.5 Correzioni Applicate in Memoria")
    md.append("")
    md.append("> **NOTA:** Le correzioni seguenti sono state applicate **solo in memoria** durante")
    md.append("> l'analisi. I file originali su disco NON sono stati modificati. Questo garantisce")
    md.append("> che le statistiche e i grafici riflettano dati puliti, preservando i dati grezzi.")
    md.append("")

    if registro.totale > 0:
        md.append(f"**Totale correzioni applicate:** {registro.totale}")
        md.append("")

        # Riepilogo per tipo di correzione
        md.append("**Riepilogo per tipo:**")
        md.append("")
        md.append("| Tipo Correzione | Occorrenze | Descrizione |")
        md.append("|-----------------|------------|-------------|")
        descrizioni_tipo = {
            'spazi_nomi_colonne': "Rimossi spazi trailing dai nomi colonne",
            'colonne_unnamed_rimosse': "Rimosse colonne 'Unnamed:' (artefatti export)",
            'xa0_sostituiti': "Sostituiti caratteri \\xa0 con spazio normale",
            'righe_vuote_rimosse': "Rimosse righe completamente vuote (tutte NaN)",
            'date_normalizzate': "Date normalizzate a formato ISO (YYYY-MM-DD)",
            'virgola_italiana_convertita': "Punteggi convertiti da formato virgola ('7,48') a float",
            'nome_attributo_normalizzato': "Nomi attributi normalizzati (capitalizzazione)",
        }
        for tipo, conteggio in sorted(registro.riepilogo.items(), key=lambda x: -x[1]):
            desc = descrizioni_tipo.get(tipo, tipo)
            md.append(f"| `{tipo}` | {conteggio} | {desc} |")
        md.append("")

        # Dettaglio per file
        md.append("**Dettaglio per file (prime 30 correzioni):**")
        md.append("")
        md.append("| File | Tipo | Dettaglio |")
        md.append("|------|------|-----------|")
        for corr in registro.correzioni[:30]:
            md.append(f"| {corr['file']} | `{corr['tipo']}` | {corr['dettaglio']} |")
        if len(registro.correzioni) > 30:
            md.append(f"| ... | ... | *({len(registro.correzioni) - 30} correzioni aggiuntive omesse)* |")
        md.append("")
    else:
        md.append("Nessuna correzione necessaria.")
        md.append("")

    # ---- RIEPILOGO ----
    md.append("---")
    md.append("")
    md.append("## 5. Riepilogo e Prossimi Step")
    md.append("")
    md.append("### Findings Principali")
    md.append("")
    md.append("1. **Schema dati**: Il 2018 è l'unico anno con punteggi individuali per panelista (5 colonne). "
              "Dal 2019 al 2021 i file hanno 7 colonne con solo commenti.")
    md.append("2. **Punteggi**: I punteggi 2018 coprono una scala ~1-10. I punteggi aggregati 2019-2021 "
              "sono medie della giuria e si concentrano nella fascia 5-8.")
    md.append("3. **Commenti**: Brevi e telegrafici, spesso abbreviati. I panelisti usano un vocabolario "
              "specializzato del settore caseario.")
    md.append("4. **Qualità dati**: Problemi di encoding nel 2021 (\\xa0), righe vuote, e prodotti mancanti "
              "sono i problemi principali.")
    md.append("")
    md.append("### Azioni Suggerite per Fase 2")
    md.append("")
    md.append("1. Definire mappatura punteggi -> termini qualitativi basata sulle correlazioni trovate")
    md.append("2. Creare dizionario espansione abbreviazioni basato sui pattern telegrafici identificati")
    md.append("3. Gestire i termini dialettali con mappatura a italiano standard")
    md.append("4. Pulire encoding (\\xa0) e gestire righe con dati mancanti")
    md.append("5. Standardizzare capitalizzazione nomi attributi")
    md.append("")

    return "\n".join(md)


def genera_csv_qualita(
    qualita: Dict[str, Any],
    inconsistenze: List[Dict[str, str]]
) -> pd.DataFrame:
    """Genera il CSV riassuntivo della qualità dati.

    Args:
        qualita: Risultati analisi qualità.
        inconsistenze: Lista inconsistenze.

    Returns:
        DataFrame pronto per il salvataggio.
    """
    righe: List[Dict[str, str]] = []

    # Problemi encoding
    for p in qualita.get('encoding', []):
        righe.append({
            'categoria': 'encoding',
            'file': p['file'],
            'tipo_problema': p['tipo'],
            'conteggio': str(p['conteggio']),
            'dettaglio': p['dettaglio'],
        })

    # Dati mancanti significativi
    for d in qualita.get('dati_mancanti', []):
        if d.get('righe_completamente_vuote', 0) > 0:
            righe.append({
                'categoria': 'dati_mancanti',
                'file': d['file'],
                'tipo_problema': 'righe_vuote',
                'conteggio': str(d['righe_completamente_vuote']),
                'dettaglio': f"Righe completamente vuote su {d['righe_totali']} totali",
            })
        if d.get('commenti_vuoti', 0) > 0:
            righe.append({
                'categoria': 'dati_mancanti',
                'file': d['file'],
                'tipo_problema': 'commenti_vuoti',
                'conteggio': str(d.get('commenti_vuoti', 0)),
                'dettaglio': f"Commenti mancanti su {d['righe_totali']} righe",
            })

    # Inconsistenze
    for inc in inconsistenze:
        righe.append({
            'categoria': 'inconsistenza',
            'file': inc.get('file', ''),
            'tipo_problema': inc['tipo'],
            'conteggio': '1',
            'dettaglio': inc['dettaglio'],
        })

    # Validation report
    vr = qualita.get('validation_report', {})
    if vr.get('trovato'):
        for tipo, conteggio in vr.get('issue_per_tipo', {}).items():
            righe.append({
                'categoria': 'validation_report',
                'file': 'session_validation_report.csv',
                'tipo_problema': tipo,
                'conteggio': str(conteggio),
                'dettaglio': f"Issue pre-esistente dal validation report",
            })

    # Correzioni applicate in memoria (per documentazione)
    for corr in registro.correzioni:
        righe.append({
            'categoria': 'correzione_in_memoria',
            'file': corr['file'],
            'tipo_problema': corr['tipo'],
            'conteggio': str(corr['conteggio']),
            'dettaglio': f"[CORRETTO] {corr['dettaglio']}",
        })

    return pd.DataFrame(righe)


# ============================================================================
# MAIN
# ============================================================================

def main() -> None:
    """Funzione principale: orchestra tutte le analisi e genera gli output.

    Esegue in sequenza:
    1. Analisi struttura file
    2. Analisi punteggi numerici (+ grafici)
    3. Analisi testuale commenti (+ grafici)
    4. Analisi qualità dati
    5. Generazione report markdown e CSV riassuntivo
    """
    logger.info("=" * 60)
    logger.info("INIZIO ANALISI ESPLORATIVA - Dataset Grana Trentino")
    logger.info(f"Project root: {PROJECT_ROOT}")
    logger.info(f"Data dir: {DATA_DIR}")
    logger.info("=" * 60)

    # Verifica che la directory dati esista
    if not DATA_DIR.exists():
        logger.error(f"Directory dati non trovata: {DATA_DIR}")
        logger.error("Assicurati che la cartella '07_captioning risultati grana Trentino' sia presente.")
        sys.exit(1)

    # Crea directory output
    for d in [REPORTS_DIR, FIGURES_DIR, METADATA_DIR, LOGS_DIR]:
        d.mkdir(parents=True, exist_ok=True)

    try:
        # ----- SEZIONE 1: Struttura File -----
        risultati_struttura = esegui_analisi_struttura()

        # ----- SEZIONE 2: Punteggi Numerici -----
        statistiche_punteggi, grafici_punteggi = esegui_analisi_punteggi()

        # Salviamo i punteggi 2018 per l'analisi testuale (li ricarichiamo)
        punteggi_2018 = carica_punteggi_2018()

        # ----- SEZIONE 3: Analisi Testuale -----
        analisi_testo, grafici_testo = esegui_analisi_testuale(punteggi_2018)

        # ----- SEZIONE 4: Qualità Dati -----
        qualita = esegui_analisi_qualita()
        inconsistenze = trova_inconsistenze(risultati_struttura)

        # ----- SEZIONE 5: Generazione Output -----
        logger.info("=" * 60)
        logger.info("SEZIONE 5: GENERAZIONE OUTPUT")
        logger.info("=" * 60)

        tutti_grafici = grafici_punteggi + grafici_testo

        # 5a. Report Markdown
        report = genera_report_markdown(
            struttura=risultati_struttura,
            statistiche_punteggi=statistiche_punteggi,
            analisi_testo=analisi_testo,
            qualita=qualita,
            inconsistenze=inconsistenze,
            grafici=tutti_grafici,
        )

        percorso_report = REPORTS_DIR / "01_analisi_esplorativa.md"
        percorso_report.write_text(report, encoding='utf-8')
        logger.info(f"Report salvato: {percorso_report}")

        # 5b. CSV qualità dati
        df_qualita = genera_csv_qualita(qualita, inconsistenze)
        percorso_csv = METADATA_DIR / "data_quality_summary.csv"
        df_qualita.to_csv(percorso_csv, index=False, encoding='utf-8')
        logger.info(f"CSV qualità dati salvato: {percorso_csv} ({len(df_qualita)} righe)")

        # Riepilogo finale
        logger.info("")
        logger.info("=" * 60)
        logger.info("ANALISI ESPLORATIVA COMPLETATA")
        logger.info("=" * 60)
        logger.info(f"Report: {percorso_report}")
        logger.info(f"Grafici: {len(tutti_grafici)} file in {FIGURES_DIR}")
        logger.info(f"CSV qualità: {percorso_csv}")
        logger.info(f"Log completo: {LOGS_DIR / '01_exploratory_analysis.log'}")

    except Exception as e:
        logger.error(f"Errore fatale durante l'analisi: {e}", exc_info=True)
        raise


if __name__ == "__main__":
    main()
