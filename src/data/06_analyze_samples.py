"""
Nome Script: Analisi Distribuzione Campioni Grana Trentino
Scopo: Analizzare distribuzione attributi, panelisti, e qualità dati per training
Input: data/processed/campioni_completi.csv
Output: Report con tabelle + grafici

Autore: Claude Code
Data: 2026-02-14
"""

import logging
from pathlib import Path
from typing import List, Dict, Any, Tuple
import pandas as pd
import json
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
from collections import Counter, defaultdict
from datetime import datetime

# Setup logging
LOG_DIR = Path("logs")
LOG_DIR.mkdir(exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(LOG_DIR / '06_analysis.log', mode='w', encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Costanti
PROJECT_ROOT = Path(__file__).parent.parent.parent
INPUT_FILE = PROJECT_ROOT / "data" / "processed" / "campioni_completi.csv"
REPORTS_DIR = PROJECT_ROOT / "reports"
FIGURES_DIR = REPORTS_DIR / "figures"

# Assicurarsi che le directory esistano
FIGURES_DIR.mkdir(parents=True, exist_ok=True)

# Lista attributi sensoriali
ATTRIBUTI = [
    'Profumo', 'Sapore', 'Aroma', 'Texture',
    'Struttura della Pasta', 'Colore della Pasta', 'Spessore della Crosta'
]

# Commenti generici
COMMENTI_GENERICI = {'nella norma', 'regolare', 'ok', 'buono', 'buona'}


def normalize_attr_name(attr: str) -> str:
    """
    Normalizza nome attributo per matching con colonne CSV.

    Args:
        attr: Nome attributo originale

    Returns:
        Nome normalizzato per colonna commenti_*
    """
    return attr.lower().replace(' della ', '_').replace(' ', '_')


def is_comment_valid(comment: str) -> bool:
    """
    Verifica se un commento è valido (non vuoto, non placeholder).

    Args:
        comment: Commento da verificare

    Returns:
        True se il commento è valido
    """
    if not comment or pd.isna(comment):
        return False

    comment_str = str(comment).strip()

    # Escludi commenti di review
    if comment_str.startswith('[REVIEW:'):
        return False

    # Escludi commenti vuoti
    if not comment_str:
        return False

    return True


def is_comment_generic(comment: str) -> bool:
    """
    Verifica se un commento è generico.

    Args:
        comment: Commento da verificare

    Returns:
        True se il commento è generico
    """
    if not comment or pd.isna(comment):
        return False

    comment_str = str(comment).strip().lower()
    return comment_str in COMMENTI_GENERICI


def count_commented_attributes(row: pd.Series) -> int:
    """
    Conta quanti attributi hanno almeno 1 commento valido per un campione.

    Args:
        row: Riga del DataFrame

    Returns:
        Numero di attributi con commenti
    """
    count = 0
    for attr in ATTRIBUTI:
        col_name = f"commenti_{normalize_attr_name(attr)}"

        if col_name in row:
            try:
                commenti_list = json.loads(row[col_name])
                # Ha commento se c'è almeno 1 commento valido
                has_valid = any(is_comment_valid(c) for c in commenti_list)
                if has_valid:
                    count += 1
            except:
                pass

    return count


def count_non_generic_comments(row: pd.Series) -> int:
    """
    Conta quanti commenti non-generici ha un campione.

    Args:
        row: Riga del DataFrame

    Returns:
        Numero di commenti non-generici
    """
    count = 0
    for attr in ATTRIBUTI:
        col_name = f"commenti_{normalize_attr_name(attr)}"

        if col_name in row:
            try:
                commenti_list = json.loads(row[col_name])
                for comment in commenti_list:
                    if is_comment_valid(comment) and not is_comment_generic(comment):
                        count += 1
            except:
                pass

    return count


def analyze_attribute_distribution(df: pd.DataFrame) -> Dict[str, pd.DataFrame]:
    """
    Analisi 1: Distribuzione attributi commentati per campione.

    Args:
        df: DataFrame campioni completi

    Returns:
        Dict con tabelle aggregate (totale + per anno)
    """
    logger.info("="*80)
    logger.info("ANALISI 1: DISTRIBUZIONE ATTRIBUTI COMMENTATI")
    logger.info("="*80)

    # Aggiungi colonna con conteggio attributi
    df['n_attributi_commentati'] = df.apply(count_commented_attributes, axis=1)

    # Tabella totale
    dist_totale = df['n_attributi_commentati'].value_counts().sort_index()
    totale_campioni = len(df)

    rows_totale = []
    cum_pct = 0
    for n_attr in range(8):  # 0 a 7
        count = dist_totale.get(n_attr, 0)
        pct = count / totale_campioni * 100
        cum_pct += pct

        rows_totale.append({
            'n_attributi': n_attr,
            'n_campioni': count,
            'percentuale': pct,
            'percentuale_cumulativa': cum_pct
        })

    df_totale = pd.DataFrame(rows_totale)

    # Tabelle per anno
    dfs_anno = {}
    for anno in sorted(df['anno'].dropna().unique()):
        df_anno = df[df['anno'] == anno]
        dist_anno = df_anno['n_attributi_commentati'].value_counts().sort_index()
        totale_anno = len(df_anno)

        rows_anno = []
        cum_pct_anno = 0
        for n_attr in range(8):
            count = dist_anno.get(n_attr, 0)
            pct = count / totale_anno * 100 if totale_anno > 0 else 0
            cum_pct_anno += pct

            rows_anno.append({
                'n_attributi': n_attr,
                'n_campioni': count,
                'percentuale': pct,
                'percentuale_cumulativa': cum_pct_anno
            })

        dfs_anno[int(anno)] = pd.DataFrame(rows_anno)

    logger.info(f"Distribuzione attributi calcolata per {totale_campioni} campioni")

    return {
        'totale': df_totale,
        **{f'anno_{anno}': dfs_anno[anno] for anno in dfs_anno}
    }


def analyze_panelisti_distribution(df: pd.DataFrame) -> pd.DataFrame:
    """
    Analisi 2: Distribuzione panelisti per campione.

    Args:
        df: DataFrame campioni completi

    Returns:
        DataFrame con distribuzione
    """
    logger.info("="*80)
    logger.info("ANALISI 2: DISTRIBUZIONE PANELISTI")
    logger.info("="*80)

    # Binning panelisti
    def bin_panelisti(n):
        if pd.isna(n) or n == 0:
            return '0'
        elif n == 1:
            return '1'
        elif 2 <= n <= 3:
            return '2-3'
        elif 4 <= n <= 6:
            return '4-6'
        elif 7 <= n <= 9:
            return '7-9'
        else:
            return '10+'

    df['panelisti_bin'] = df['n_panelisti'].apply(bin_panelisti)

    dist = df['panelisti_bin'].value_counts()
    totale = len(df)

    # Ordine custom
    order = ['0', '1', '2-3', '4-6', '7-9', '10+']

    rows = []
    for bin_label in order:
        count = dist.get(bin_label, 0)
        pct = count / totale * 100

        rows.append({
            'n_panelisti': bin_label,
            'n_campioni': count,
            'percentuale': pct
        })

    logger.info(f"Distribuzione panelisti calcolata")

    return pd.DataFrame(rows)


def analyze_missing_attributes(df: pd.DataFrame) -> Dict[str, pd.DataFrame]:
    """
    Analisi 3: Attributi mancanti.

    Args:
        df: DataFrame campioni completi

    Returns:
        Dict con tabelle (totale + per anno)
    """
    logger.info("="*80)
    logger.info("ANALISI 3: ATTRIBUTI MANCANTI")
    logger.info("="*80)

    # Calcola per ogni attributo quanti campioni NON lo hanno commentato
    totale = len(df)

    rows_totale = []
    for attr in ATTRIBUTI:
        col_name = f"commenti_{normalize_attr_name(attr)}"

        missing_count = 0
        for _, row in df.iterrows():
            try:
                commenti_list = json.loads(row[col_name])
                has_valid = any(is_comment_valid(c) for c in commenti_list)
                if not has_valid:
                    missing_count += 1
            except:
                missing_count += 1

        rows_totale.append({
            'attributo': attr,
            'n_campioni_senza_commento': missing_count,
            'percentuale': missing_count / totale * 100
        })

    df_totale = pd.DataFrame(rows_totale).sort_values('n_campioni_senza_commento', ascending=False)

    # Per anno
    dfs_anno = {}
    for anno in sorted(df['anno'].dropna().unique()):
        df_anno = df[df['anno'] == anno]
        totale_anno = len(df_anno)

        rows_anno = []
        for attr in ATTRIBUTI:
            col_name = f"commenti_{normalize_attr_name(attr)}"

            missing_count = 0
            for _, row in df_anno.iterrows():
                try:
                    commenti_list = json.loads(row[col_name])
                    has_valid = any(is_comment_valid(c) for c in commenti_list)
                    if not has_valid:
                        missing_count += 1
                except:
                    missing_count += 1

            rows_anno.append({
                'attributo': attr,
                'n_campioni_senza_commento': missing_count,
                'percentuale': missing_count / totale_anno * 100
            })

        dfs_anno[int(anno)] = pd.DataFrame(rows_anno).sort_values('n_campioni_senza_commento', ascending=False)

    logger.info("Attributi mancanti calcolati")

    return {
        'totale': df_totale,
        **{f'anno_{anno}': dfs_anno[anno] for anno in dfs_anno}
    }


def analyze_images_without_comments(df: pd.DataFrame) -> pd.DataFrame:
    """
    Analisi 4: Campioni con immagini ma senza commenti.

    Args:
        df: DataFrame campioni completi

    Returns:
        DataFrame con breakdown per anno
    """
    logger.info("="*80)
    logger.info("ANALISI 4: IMMAGINI SENZA COMMENTI")
    logger.info("="*80)

    # Filtro: ha FETTA+GRANA ma 0 attributi commentati
    has_both_images = (df['n_immagini_fetta'] > 0) & (df['n_immagini_grana'] > 0)
    no_comments = df['n_attributi_commentati'] == 0

    inutilizzabili = df[has_both_images & no_comments]

    rows = []
    for anno in sorted(df['anno'].dropna().unique()):
        df_anno = df[df['anno'] == anno]
        inut_anno = inutilizzabili[inutilizzabili['anno'] == anno]

        rows.append({
            'anno': int(anno),
            'n_inutilizzabili': len(inut_anno),
            'n_totali_anno': len(df_anno),
            'percentuale': len(inut_anno) / len(df_anno) * 100 if len(df_anno) > 0 else 0
        })

    # Totale
    rows.append({
        'anno': 'Totale',
        'n_inutilizzabili': len(inutilizzabili),
        'n_totali_anno': len(df),
        'percentuale': len(inutilizzabili) / len(df) * 100
    })

    logger.info(f"Campioni inutilizzabili: {len(inutilizzabili)}")

    return pd.DataFrame(rows)


def analyze_punteggi_availability(df: pd.DataFrame) -> pd.DataFrame:
    """
    Analisi 5: Disponibilità punteggi.

    Args:
        df: DataFrame campioni completi

    Returns:
        DataFrame con disponibilità punteggi per anno
    """
    logger.info("="*80)
    logger.info("ANALISI 5: DISPONIBILITÀ PUNTEGGI")
    logger.info("="*80)

    rows = []

    # Per 2018: hanno punteggi individuali
    df_2018 = df[df['anno'] == 2018]
    # Controlla se almeno un punteggio non è None
    has_scores_2018 = df_2018.apply(
        lambda row: any(pd.notna(row[f"punteggio_{normalize_attr_name(attr)}"]) for attr in ATTRIBUTI),
        axis=1
    )

    rows.append({
        'anno': '2018',
        'con_punteggi': has_scores_2018.sum(),
        'senza_punteggi': (~has_scores_2018).sum(),
        'totale': len(df_2018)
    })

    # Per 2019-2021: NON hanno punteggi individuali (solo aggregati giuria)
    for anno in [2019, 2020, 2021]:
        df_anno = df[df['anno'] == anno]
        rows.append({
            'anno': str(anno),
            'con_punteggi': 0,  # Nessun punteggio individuale
            'senza_punteggi': len(df_anno),
            'totale': len(df_anno)
        })

    logger.info("Disponibilità punteggi calcolata")

    return pd.DataFrame(rows)


def simulate_thresholds(df: pd.DataFrame) -> Dict[str, pd.DataFrame]:
    """
    Analisi 6: Simulazione soglie.

    Args:
        df: DataFrame campioni completi

    Returns:
        Dict con tabelle (totale + per anno)
    """
    logger.info("="*80)
    logger.info("ANALISI 6: SIMULAZIONE SOGLIE")
    logger.info("="*80)

    # Tabella totale
    totale = len(df)
    rows_totale = []

    for soglia in range(3, 8):
        utilizzabili = df[df['n_attributi_commentati'] >= soglia]
        rows_totale.append({
            'soglia_min_attributi': f">= {soglia}" if soglia < 7 else "= 7",
            'campioni_utilizzabili': len(utilizzabili),
            'percentuale_totale': len(utilizzabili) / totale * 100
        })

    df_totale = pd.DataFrame(rows_totale)

    # Per anno
    dfs_anno = {}
    for anno in sorted(df['anno'].dropna().unique()):
        df_anno = df[df['anno'] == anno]
        totale_anno = len(df_anno)

        rows_anno = []
        for soglia in range(3, 8):
            utilizzabili = df_anno[df_anno['n_attributi_commentati'] >= soglia]
            rows_anno.append({
                'soglia_min_attributi': f">= {soglia}" if soglia < 7 else "= 7",
                'campioni_utilizzabili': len(utilizzabili),
                'percentuale_anno': len(utilizzabili) / totale_anno * 100 if totale_anno > 0 else 0
            })

        dfs_anno[int(anno)] = pd.DataFrame(rows_anno)

    logger.info("Simulazione soglie completata")

    return {
        'totale': df_totale,
        **{f'anno_{anno}': dfs_anno[anno] for anno in dfs_anno}
    }


def analyze_comment_quality(df: pd.DataFrame) -> pd.DataFrame:
    """
    Analisi 7: Qualità commenti.

    Args:
        df: DataFrame campioni completi

    Returns:
        DataFrame con statistiche qualità
    """
    logger.info("="*80)
    logger.info("ANALISI 7: QUALITÀ COMMENTI")
    logger.info("="*80)

    # Aggiungi colonna con conteggio commenti non-generici
    df['n_commenti_non_generici'] = df.apply(count_non_generic_comments, axis=1)

    # Filtro: campioni con almeno 1 commento
    has_comments = df[df['n_attributi_commentati'] > 0]

    # Filtro: campioni con almeno 1 commento non-generico
    has_non_generic = has_comments[has_comments['n_commenti_non_generici'] > 0]

    rows = []
    for anno in sorted(df['anno'].dropna().unique()):
        df_anno = df[df['anno'] == anno]
        has_comments_anno = df_anno[df_anno['n_attributi_commentati'] > 0]
        has_non_generic_anno = has_comments_anno[has_comments_anno['n_commenti_non_generici'] > 0]

        rows.append({
            'anno': int(anno),
            'con_commenti': len(has_comments_anno),
            'con_commenti_non_generici': len(has_non_generic_anno),
            'percentuale_non_generici': len(has_non_generic_anno) / len(has_comments_anno) * 100 if len(has_comments_anno) > 0 else 0
        })

    # Totale
    rows.append({
        'anno': 'Totale',
        'con_commenti': len(has_comments),
        'con_commenti_non_generici': len(has_non_generic),
        'percentuale_non_generici': len(has_non_generic) / len(has_comments) * 100 if len(has_comments) > 0 else 0
    })

    logger.info("Qualità commenti calcolata")

    return pd.DataFrame(rows)


def generate_plots(df: pd.DataFrame):
    """
    Analisi 8: Genera grafici.

    Args:
        df: DataFrame campioni completi
    """
    logger.info("="*80)
    logger.info("ANALISI 8: GENERAZIONE GRAFICI")
    logger.info("="*80)

    # Set stile
    sns.set_style('whitegrid')
    plt.rcParams['figure.figsize'] = (12, 6)

    # 1. Istogramma distribuzione attributi
    fig, ax = plt.subplots(figsize=(10, 6))
    dist = df['n_attributi_commentati'].value_counts().sort_index()

    ax.bar(dist.index, dist.values, color='steelblue', edgecolor='black', alpha=0.7)
    ax.set_xlabel('Numero di Attributi Commentati', fontsize=12)
    ax.set_ylabel('Numero di Campioni', fontsize=12)
    ax.set_title('Distribuzione Attributi Commentati per Campione', fontsize=14, fontweight='bold')
    ax.set_xticks(range(8))
    ax.grid(axis='y', alpha=0.3)

    # Aggiungi percentuali sopra le barre
    totale = len(df)
    for i, v in enumerate(dist.values):
        pct = v / totale * 100
        ax.text(dist.index[i], v + 5, f'{v}\n({pct:.1f}%)', ha='center', fontsize=10)

    plt.tight_layout()
    output_path = FIGURES_DIR / '06_distribuzione_attributi.png'
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    plt.close()
    logger.info(f"Grafico distribuzione salvato: {output_path}")

    # 2. Heatmap anno × attributo
    fig, ax = plt.subplots(figsize=(12, 6))

    anni = sorted(df['anno'].dropna().unique())
    matrix = []

    for anno in anni:
        df_anno = df[df['anno'] == anno]
        totale_anno = len(df_anno)

        row = []
        for attr in ATTRIBUTI:
            col_name = f"commenti_{normalize_attr_name(attr)}"

            commented_count = 0
            for _, r in df_anno.iterrows():
                try:
                    commenti_list = json.loads(r[col_name])
                    has_valid = any(is_comment_valid(c) for c in commenti_list)
                    if has_valid:
                        commented_count += 1
                except:
                    pass

            pct = commented_count / totale_anno * 100 if totale_anno > 0 else 0
            row.append(pct)

        matrix.append(row)

    # Crea heatmap
    sns.heatmap(matrix, annot=True, fmt='.1f', cmap='YlGnBu',
                xticklabels=[a.replace(' della ', '\n') for a in ATTRIBUTI],
                yticklabels=[int(a) for a in anni],
                cbar_kws={'label': '% Campioni con Commento'},
                ax=ax)

    ax.set_xlabel('Attributo Sensoriale', fontsize=12)
    ax.set_ylabel('Anno', fontsize=12)
    ax.set_title('Copertura Attributi per Anno (% Campioni con Commento)', fontsize=14, fontweight='bold')

    plt.tight_layout()
    output_path = FIGURES_DIR / '06_heatmap_anno_attributo.png'
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    plt.close()
    logger.info(f"Heatmap salvata: {output_path}")

    # 3. Boxplot panelisti per anno
    fig, ax = plt.subplots(figsize=(10, 6))

    data_per_anno = []
    labels = []
    for anno in sorted(df['anno'].dropna().unique()):
        df_anno = df[df['anno'] == anno]
        data_per_anno.append(df_anno['n_panelisti'].values)
        labels.append(int(anno))

    bp = ax.boxplot(data_per_anno, labels=labels, patch_artist=True,
                     boxprops=dict(facecolor='lightblue', edgecolor='black'),
                     medianprops=dict(color='red', linewidth=2),
                     whiskerprops=dict(color='black'),
                     capprops=dict(color='black'))

    ax.set_xlabel('Anno', fontsize=12)
    ax.set_ylabel('Numero di Panelisti', fontsize=12)
    ax.set_title('Distribuzione Panelisti per Anno', fontsize=14, fontweight='bold')
    ax.grid(axis='y', alpha=0.3)

    plt.tight_layout()
    output_path = FIGURES_DIR / '06_panelisti_per_anno.png'
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    plt.close()
    logger.info(f"Boxplot panelisti salvato: {output_path}")

    logger.info("Tutti i grafici generati con successo")


def generate_report(analyses: Dict, output_path: Path):
    """
    Genera report markdown completo.

    Args:
        analyses: Dict con tutte le analisi
        output_path: Path dove salvare il report
    """
    logger.info(f"Generando report in {output_path}...")

    with open(output_path, 'w', encoding='utf-8') as f:
        f.write("# REPORT ANALISI CAMPIONI - Grana Trentino\n\n")
        f.write(f"**Data elaborazione:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
        f.write("---\n\n")

        # Analisi 1
        f.write("## 1. DISTRIBUZIONE ATTRIBUTI COMMENTATI PER CAMPIONE\n\n")
        f.write("### Totale\n\n")
        df_dist = analyses['distribuzione_attributi']['totale']
        f.write(df_dist.to_markdown(index=False))
        f.write("\n\n")

        for anno in [2018, 2019, 2020, 2021]:
            key = f"anno_{anno}"
            if key in analyses['distribuzione_attributi']:
                f.write(f"### Anno {anno}\n\n")
                f.write(analyses['distribuzione_attributi'][key].to_markdown(index=False))
                f.write("\n\n")

        # Analisi 2
        f.write("## 2. DISTRIBUZIONE PANELISTI PER CAMPIONE\n\n")
        f.write(analyses['distribuzione_panelisti'].to_markdown(index=False))
        f.write("\n\n")

        # Analisi 3
        f.write("## 3. ATTRIBUTI MANCANTI\n\n")
        f.write("### Totale\n\n")
        f.write(analyses['attributi_mancanti']['totale'].to_markdown(index=False))
        f.write("\n\n")

        for anno in [2018, 2019, 2020, 2021]:
            key = f"anno_{anno}"
            if key in analyses['attributi_mancanti']:
                f.write(f"### Anno {anno}\n\n")
                f.write(analyses['attributi_mancanti'][key].to_markdown(index=False))
                f.write("\n\n")

        # Analisi 4
        f.write("## 4. CAMPIONI CON IMMAGINI MA SENZA COMMENTI\n\n")
        f.write(analyses['immagini_senza_commenti'].to_markdown(index=False))
        f.write("\n\n")

        # Analisi 5
        f.write("## 5. DISPONIBILITÀ PUNTEGGI\n\n")
        f.write(analyses['disponibilita_punteggi'].to_markdown(index=False))
        f.write("\n\n")

        # Analisi 6
        f.write("## 6. SIMULAZIONE SOGLIE\n\n")
        f.write("### Totale\n\n")
        f.write(analyses['simulazione_soglie']['totale'].to_markdown(index=False))
        f.write("\n\n")

        for anno in [2018, 2019, 2020, 2021]:
            key = f"anno_{anno}"
            if key in analyses['simulazione_soglie']:
                f.write(f"### Anno {anno}\n\n")
                f.write(analyses['simulazione_soglie'][key].to_markdown(index=False))
                f.write("\n\n")

        # Analisi 7
        f.write("## 7. QUALITÀ COMMENTI\n\n")
        f.write(analyses['qualita_commenti'].to_markdown(index=False))
        f.write("\n\n")

        # Grafici
        f.write("## 8. GRAFICI\n\n")
        f.write("![Distribuzione Attributi](figures/06_distribuzione_attributi.png)\n\n")
        f.write("![Heatmap Anno x Attributo](figures/06_heatmap_anno_attributo.png)\n\n")
        f.write("![Panelisti per Anno](figures/06_panelisti_per_anno.png)\n\n")

        f.write("---\n\n")
        f.write("**Note:**\n")
        f.write("- Un attributo è 'commentato' se ha almeno 1 commento valido (non vuoto, non [REVIEW:...])\n")
        f.write("- Commenti generici: 'nella norma', 'regolare', 'ok', 'buono', 'buona'\n")

    logger.info("Report generato con successo")


def main():
    """Funzione principale dello script."""
    logger.info("="*80)
    logger.info("INIZIO ANALISI CAMPIONI - Grana Trentino")
    logger.info("="*80)

    try:
        # Carica dataset
        logger.info(f"Caricamento dataset da {INPUT_FILE}...")
        df = pd.read_csv(INPUT_FILE, encoding='utf-8')
        logger.info(f"Dataset caricato: {len(df)} campioni")

        # Esegui analisi
        analyses = {}

        # 1. Distribuzione attributi
        analyses['distribuzione_attributi'] = analyze_attribute_distribution(df)

        # 2. Distribuzione panelisti
        analyses['distribuzione_panelisti'] = analyze_panelisti_distribution(df)

        # 3. Attributi mancanti
        analyses['attributi_mancanti'] = analyze_missing_attributes(df)

        # 4. Immagini senza commenti
        analyses['immagini_senza_commenti'] = analyze_images_without_comments(df)

        # 5. Disponibilità punteggi
        analyses['disponibilita_punteggi'] = analyze_punteggi_availability(df)

        # 6. Simulazione soglie
        analyses['simulazione_soglie'] = simulate_thresholds(df)

        # 7. Qualità commenti
        analyses['qualita_commenti'] = analyze_comment_quality(df)

        # 8. Genera grafici
        generate_plots(df)

        # Genera report
        report_path = REPORTS_DIR / "06_analisi_campioni.md"
        generate_report(analyses, report_path)

        # Statistiche finali
        logger.info("="*80)
        logger.info("RISULTATI CHIAVE")
        logger.info("="*80)

        # 1. Tabella distribuzione attributi
        logger.info("\n1. DISTRIBUZIONE ATTRIBUTI COMMENTATI (TOTALE):")
        logger.info("\n" + analyses['distribuzione_attributi']['totale'].to_string(index=False))

        # 2. Tabella simulazione soglie
        logger.info("\n2. SIMULAZIONE SOGLIE:")
        logger.info("\n" + analyses['simulazione_soglie']['totale'].to_string(index=False))

        # 3. Anno con qualità migliore
        media_per_anno = {}
        for anno in sorted(df['anno'].dropna().unique()):
            df_anno = df[df['anno'] == anno]
            media = df_anno['n_attributi_commentati'].mean()
            media_per_anno[int(anno)] = media

        anno_migliore = max(media_per_anno, key=media_per_anno.get)
        logger.info(f"\n3. ANNO CON QUALITÀ DATI MIGLIORE: {anno_migliore}")
        logger.info(f"   Media attributi commentati: {media_per_anno[anno_migliore]:.2f}")
        for anno, media in sorted(media_per_anno.items()):
            logger.info(f"   - Anno {anno}: {media:.2f} attributi/campione")

        # 4. Attributo più mancante
        df_miss = analyses['attributi_mancanti']['totale']
        attr_piu_mancante = df_miss.iloc[0]
        logger.info(f"\n4. ATTRIBUTO PIÙ SPESSO MANCANTE: {attr_piu_mancante['attributo']}")
        logger.info(f"   Mancante in {attr_piu_mancante['n_campioni_senza_commento']} campioni ({attr_piu_mancante['percentuale']:.1f}%)")

        logger.info("="*80)
        logger.info("ANALISI COMPLETATA CON SUCCESSO")
        logger.info(f"Report salvato in: {report_path}")
        logger.info(f"Grafici salvati in: {FIGURES_DIR}")
        logger.info("="*80)

    except Exception as e:
        logger.error(f"Errore durante elaborazione: {e}", exc_info=True)
        raise


if __name__ == "__main__":
    main()
