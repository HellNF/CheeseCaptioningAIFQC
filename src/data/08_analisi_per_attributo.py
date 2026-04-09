"""
Nome Script: 08_analisi_per_attributo.py
Scopo:
  Fase 1 — Analisi statistica per attributo (distribuzione termini, soglie quantitative)
  Fase 2 — Automazione NotebookLM: crea notebook, carica sorgenti raw, esegue 4 query
            sequenziali per generare il vocabolario bozza.

Input:
  - CSV raw: 07_captioning.../GT commenti liberi/csv dataset/
  - Score CSV: .../codifiche/Risultati_2019-21_*.csv
  - Score 2018: incluso nei CSV raw (4a colonna = score individuale)

Output:
  - data/interim/analisi_statistica_per_attributo/{Attributo}_statistiche.md
  - data/interim/analisi_statistica_per_attributo/{Attributo}_contesto_notebooklm.md
  - data/interim/vocabolari_bozza_per_attributo/{Attributo}_vocabolario_nblm.md
  - data/interim/vocabolari_bozza_per_attributo/notebook_ids.json

Uso:
  python src/data/08_analisi_per_attributo.py
  python src/data/08_analisi_per_attributo.py --attributo "Aroma"
  python src/data/08_analisi_per_attributo.py --solo-analisi
  python src/data/08_analisi_per_attributo.py --solo-nblm

Autore: Claude Opus 4.6  —  branch: feature/per-attribute-captioning
Data: 2026-04-09
"""

import argparse
import json
import logging
import re
import subprocess
import sys
import time
from collections import Counter
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple

import pandas as pd

# ─────────────────────────────────────────────
# Logging
# ─────────────────────────────────────────────
LOG_DIR = Path("logs")
LOG_DIR.mkdir(exist_ok=True)

# Forza UTF-8 sul terminale Windows (Python 3.7+)
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler(LOG_DIR / "08_analisi_per_attributo.log", mode="w", encoding="utf-8"),
        logging.StreamHandler(sys.stdout),
    ],
)
logger = logging.getLogger(__name__)

# ─────────────────────────────────────────────
# Percorsi
# ─────────────────────────────────────────────
PROJECT_ROOT = Path(__file__).parent.parent.parent
RAW_CSV_DIR = PROJECT_ROOT / "07_captioning risultati grana Trentino" / "GT commenti liberi" / "csv dataset"
SCORES_DIR = PROJECT_ROOT / "07_captioning risultati grana Trentino" / "GT commenti liberi" / "codifiche"
ANALISI_DIR = PROJECT_ROOT / "data" / "interim" / "analisi_statistica_per_attributo"
VOCABOLARI_BOZZA_DIR = PROJECT_ROOT / "data" / "interim" / "vocabolari_bozza_per_attributo"
REPORTS_DIR = PROJECT_ROOT / "reports"

for d in [ANALISI_DIR, VOCABOLARI_BOZZA_DIR, REPORTS_DIR]:
    d.mkdir(parents=True, exist_ok=True)

# ─────────────────────────────────────────────
# Configurazione attributi
# ─────────────────────────────────────────────
ATTRIBUTI_CONFIG: Dict[str, Dict] = {
    "Aroma": {
        "suffisso_2018":    "Aroma",
        "suffisso_2019_21": "Aroma",
        "score_col_2018":   "Aroma",
        "is_visual":        False,
        "has_quantitative": False,
        "descrizione_nblm": (
            "L'Aroma è la percezione retrolfattiva che si sviluppa durante la masticazione, "
            "quando i composti volatili salgono alla cavità nasale attraverso il rinofaringe. "
            "È tipicamente più intensa del Profumo e include note lattiche, burro fuso, panna, "
            "frutta (ananas, mela), vegetale, animale (brodo, prosciutto), insilato, ossidato/rancido. "
            "Un aroma 'nella norma' è quello caratteristico del Grana Trentino stagionato."
        ),
    },
    "Profumo": {
        "suffisso_2018":    "Profumo",
        "suffisso_2019_21": "Profumo",
        "score_col_2018":   "Profumo",
        "is_visual":        False,
        "has_quantitative": False,
        "descrizione_nblm": (
            "Il Profumo è la percezione olfattiva diretta (ortonasale), prima e durante il consumo. "
            "Include intensità (debole, moderato, intenso), qualità (caratteristico, atipico) "
            "e note specifiche: burro, latte, panna, frutta, vegetale, note di cantina, note anomale. "
            "Il profumo caratteristico del TrentinGrana è latteo con note di burro fuso e frutta secca."
        ),
    },
    "Sapore": {
        "suffisso_2018":    "Sapore",
        "suffisso_2019_21": "Sapore",
        "score_col_2018":   "Sapore",
        "is_visual":        False,
        "has_quantitative": False,
        "descrizione_nblm": (
            "Il Sapore copre le percezioni gustative: dolce, salato, amaro, acido, umami. "
            "Include equilibrio (tra i gusti), piccantezza, persistenza retrogustativa. "
            "Un Sapore equilibrato ha dolce e salato bilanciati, senza amaro o piccante eccessivi. "
            "Difetti tipici: eccessiva piccantezza, amarezza, acidità anomala, sapore piatto/anonimo."
        ),
    },
    "Texture": {
        "suffisso_2018":    "Texture",
        "suffisso_2019_21": "Texture",
        "score_col_2018":   "Texture",
        "is_visual":        True,
        "has_quantitative": False,
        "descrizione_nblm": (
            "La Texture descrive le caratteristiche meccaniche percepite in bocca e visibili al taglio: "
            "solubilità (quanto si scioglie rapidamente), friabilità (tendenza a sbriciolarsi), "
            "durezza, presenza e dimensione di cristalli di tirosina, umidità residua. "
            "I cristalli di tirosina (bianchi, puntiformi) sono un indicatore positivo di stagionatura. "
            "Una texture 'nella norma' per il TrentinGrana è friabile, moderatamente solubile, con cristalli presenti."
        ),
    },
    "Struttura della Pasta": {
        "suffisso_2018":    "Struttura della Pasta",
        "suffisso_2019_21": "Struttura della pasta",
        "score_col_2018":   "Struttura della Pasta",
        "is_visual":        True,
        "has_quantitative": False,
        "descrizione_nblm": (
            "La Struttura della Pasta descrive le caratteristiche visive e strutturali della sezione del formaggio. "
            "Include: grana (finezza/grossolanità), tipo di frattura (netta, irregolare, stirata), "
            "microocchiatura (piccoli fori diffusi), occhiatura (fori più grandi), "
            "disomogeneità (zone con caratteristiche diverse), colore interno. "
            "Una struttura 'nella norma' ha grana fine uniforme, frattura tipica, microocchiatura diffusa regolare."
        ),
    },
    "Colore della Pasta": {
        "suffisso_2018":    "Colore della Pasta",
        "suffisso_2019_21": "Colore della pasta",
        "score_col_2018":   "Colore della Pasta",
        "is_visual":        True,
        "has_quantitative": False,
        "descrizione_nblm": (
            "Il Colore della Pasta descrive la tonalità e l'uniformità della sezione del formaggio. "
            "Il range va da bianco latte (stagionatura breve) a giallo paglierino intenso (stagionatura avanzata). "
            "Include: presenza di alone centrale più scuro o rosato, disomogeneità, "
            "sottocrosta (zona immediatamente sotto la crosta, di solito più chiara). "
            "Difetti: colore anomalo (troppo scuro, verdastro, con aloni irregolari)."
        ),
    },
    "Spessore della Crosta": {
        "suffisso_2018":    "Spessore della Crosta",
        "suffisso_2019_21": "Spessore della crosta",
        "score_col_2018":   "Spessore della Crosta",
        "is_visual":        True,
        "has_quantitative": True,
        "descrizione_nblm": (
            "Lo Spessore della Crosta misura lo spessore della crosta esterna in mm o cm, "
            "su piatti (facce piane) e scalzi (bordi laterali). Include anche la regolarità "
            "(omogeneo vs disomogeneo) e difetti (piatti senza crosta, spigoli molto accentuati). "
            "I commenti spesso riportano misure esplicite: '1cm', '10mm', '0,8 piatti 1,4 scalzi'. "
            "Un range tipico per TrentinGrana è 7–14mm su piatti, maggiore sugli scalzi."
        ),
    },
}

# Termini tecnici da non normalizzare
TERMINI_TECNICI = (
    "scalzo, scalzi, piatti, piatto, sottocrosta, angoli, spigoli, "
    "microocchiatura, occhiatura, grana, frattura, stirata, cristalli, tirosina, "
    "nostrano, insilato, solubile, solubilità, friabile, friabilità, compatto, compattezza, cedevole"
)

# ─────────────────────────────────────────────
# Utilità
# ─────────────────────────────────────────────
def attr_to_slug(attributo: str) -> str:
    """Converte nome attributo in slug per filename."""
    return attributo.replace(" ", "_")


def get_raw_csv_path(attributo: str, anno: int) -> Optional[Path]:
    """Restituisce il Path del CSV raw per un attributo e anno."""
    config = ATTRIBUTI_CONFIG[attributo]
    if anno == 2018:
        nome = f"Commenti TOT_2018_{config['suffisso_2018']}.csv"
    elif anno == 2019:
        nome = f"Commenti liberi_QTG_2019_{config['suffisso_2019_21']}.csv"
    elif anno == 2020:
        nome = f"Commenti liberi_QTG_2020_{config['suffisso_2019_21']}.csv"
    elif anno == 2021:
        nome = f"Commenti liberi_TEST_2021_{config['suffisso_2019_21']}.csv"
    else:
        return None

    path = RAW_CSV_DIR / nome
    return path if path.exists() else None


def carica_commenti(attributo: str) -> Dict[int, pd.DataFrame]:
    """Carica i CSV raw per tutti gli anni. Restituisce {anno: DataFrame}."""
    dfs: Dict[int, pd.DataFrame] = {}
    for anno in [2018, 2019, 2020, 2021]:
        path = get_raw_csv_path(attributo, anno)
        if path is None:
            logger.warning(f"  CSV non trovato: {attributo} {anno}")
            continue
        df = pd.read_csv(path, encoding="utf-8-sig", dtype=str)
        df["anno_dati"] = anno
        dfs[anno] = df
        logger.debug(f"  Caricato {path.name}: {len(df)} righe")
    return dfs


# ─────────────────────────────────────────────
# FASE 1A — Analisi statistica
# ─────────────────────────────────────────────
_STOPWORDS_IT = {
    "il", "lo", "la", "i", "gli", "le", "un", "uno", "una", "di", "da", "in",
    "con", "su", "per", "tra", "fra", "a", "e", "o", "ma", "non", "che", "è",
    "si", "al", "del", "della", "dei", "degli", "delle", "nel", "nella",
    "un", "più", "molto", "poco", "abbastanza", "leggermente", "lieve",
}


def tokenizza(testo: str) -> List[str]:
    """Tokenizzazione minima: parole alfa >= 2 char, escluse stopwords."""
    parole = re.findall(r"\b[a-zA-ZàèéìíîòóùúÀÈÉÌÍÎÒÓÙÚ]{2,}\b", testo.lower())
    return [p for p in parole if p not in _STOPWORDS_IT]


def analisi_statistica(attributo: str, dfs: Dict[int, pd.DataFrame]) -> Dict:
    """Analisi statistica dei commenti per un attributo."""
    stats_per_anno: Dict[int, Dict] = {}
    tutti_commenti: List[str] = []
    tutti_termini: List[str] = []

    for anno, df in dfs.items():
        commenti_col = df["Commenti"] if "Commenti" in df.columns else pd.Series(dtype=str)
        commenti = commenti_col.dropna().astype(str).str.strip()
        commenti_validi = commenti[commenti.str.len() > 0]

        n_tot = len(df)
        n_validi = len(commenti_validi)
        lunghezze = commenti_validi.str.len()

        stats_per_anno[anno] = {
            "n_totale": n_tot,
            "n_validi": n_validi,
            "n_vuoti": n_tot - n_validi,
            "perc_vuoti": round((n_tot - n_validi) / n_tot * 100, 1) if n_tot else 0,
            "lungh_media": round(lunghezze.mean(), 1) if n_validi else 0,
            "lungh_mediana": round(lunghezze.median(), 1) if n_validi else 0,
            "lungh_max": int(lunghezze.max()) if n_validi else 0,
        }

        tutti_commenti.extend(commenti_validi.tolist())
        for c in commenti_validi:
            tutti_termini.extend(tokenizza(c))

    counter = Counter(tutti_termini)
    top_50 = counter.most_common(50)

    return {
        "attributo": attributo,
        "stats_per_anno": stats_per_anno,
        "top_50_termini": top_50,
        "n_commenti_totali": len(tutti_commenti),
        "n_termini_unici": len(counter),
        "tutti_commenti": tutti_commenti,
    }


# ─────────────────────────────────────────────
# FASE 1B — Analisi quantitativa (Spessore della Crosta)
# ─────────────────────────────────────────────
_REGEX_QUANTITATIVI = [
    (r"(\d+)[,.](\d+)\s*cm",  "cm_dec"),   # 1,2 cm  o  1.2 cm
    (r"(\d+)\s*cm\b",         "cm_int"),   # 1 cm
    (r"(\d+)[,.](\d+)\s*mm",  "mm_dec"),   # 12,5 mm
    (r"(\d+)\s*-\s*(\d+)\s*mm", "mm_rng"), # 9-10 mm
    (r"(\d+)\s*mm\b",         "mm_int"),   # 10 mm
]


def estrai_misura_mm(commento: str) -> Optional[float]:
    """Estrae misura numerica in mm dal testo. Ritorna None se non trovata."""
    for pattern, tipo in _REGEX_QUANTITATIVI:
        m = re.search(pattern, commento, re.IGNORECASE)
        if m:
            try:
                if tipo == "cm_dec":
                    return float(f"{m.group(1)}.{m.group(2)}") * 10
                elif tipo == "cm_int":
                    return float(m.group(1)) * 10
                elif tipo == "mm_dec":
                    return float(f"{m.group(1)}.{m.group(2)}")
                elif tipo == "mm_rng":
                    return (float(m.group(1)) + float(m.group(2))) / 2
                elif tipo == "mm_int":
                    return float(m.group(1))
            except (ValueError, IndexError):
                continue
    return None


def analisi_quantitativa_spessore(df_2018: pd.DataFrame) -> Dict:
    """
    Correla misure mm nei commenti con i punteggi individuali 2018.
    Restituisce soglie qualitative stimate.
    """
    score_col = "Spessore della Crosta"
    records = []

    for _, row in df_2018.iterrows():
        commento = str(row.get("Commenti", "")).strip()
        misura = estrai_misura_mm(commento)
        if misura is None:
            continue

        # Parse score (formato italiano "7,48" o float "7.5")
        raw_score = str(row.get(score_col, "")).replace(",", ".").strip()
        try:
            score = float(raw_score)
        except ValueError:
            continue

        # Filtra valori anomali (es. "7 km" typo → ~7000 mm)
        if misura > 50:
            logger.debug(f"  Misura anomala ignorata: {misura}mm — '{commento[:60]}'")
            continue

        records.append({"misura_mm": misura, "score": score, "commento": commento})

    if not records:
        return {"soglie": [], "n_misure": 0, "range_mm": None}

    df_m = pd.DataFrame(records)
    logger.info(f"  Spessore Crosta: {len(df_m)} misure estratte, range {df_m['misura_mm'].min():.1f}–{df_m['misura_mm'].max():.1f} mm")

    # Binning in 4 categorie
    bins   = [0,   7,   12,   18,   200]
    labels = ["molto_sottile", "nella_norma", "spessa", "molto_spessa"]
    df_m["categoria"] = pd.cut(df_m["misura_mm"], bins=bins, labels=labels, right=False)

    agg = (
        df_m.groupby("categoria", observed=True)["score"]
        .agg(score_medio="mean", score_std="std", n_misure="count")
        .reset_index()
    )

    return {
        "soglie": agg.to_dict("records"),
        "n_misure": len(records),
        "range_mm": {"min": df_m["misura_mm"].min(), "max": df_m["misura_mm"].max()},
        "esempi": df_m.head(10).to_dict("records"),
    }


# ─────────────────────────────────────────────
# FASE 1C — Generazione output markdown
# ─────────────────────────────────────────────
def genera_statistiche_md(attributo: str, stats: Dict, soglie: Optional[Dict]) -> str:
    """Genera report statistico .md per l'attributo."""
    slug = attr_to_slug(attributo)
    lines = [
        f"# Statistiche Per-Attributo — {attributo}",
        f"**Generato:** {datetime.now().strftime('%Y-%m-%d %H:%M')}",
        "",
        "## Commenti per anno",
        "",
        "| Anno | Totale | Validi | % vuoti | Lungh. media | Lungh. mediana | Max |",
        "|------|--------|--------|---------|-------------|----------------|-----|",
    ]

    for anno, s in stats["stats_per_anno"].items():
        lines.append(
            f"| {anno} | {s['n_totale']} | {s['n_validi']} | "
            f"{s['perc_vuoti']}% | {s['lungh_media']} | {s['lungh_mediana']} | {s['lungh_max']} |"
        )

    lines += [
        "",
        f"**Commenti validi totali:** {stats['n_commenti_totali']}",
        f"**Termini unici (post-stopword):** {stats['n_termini_unici']}",
        "",
        "## Top 50 termini (escluse stopword)",
        "",
        "| Rank | Termine | Occorrenze |",
        "|------|---------|------------|",
    ]
    for i, (termine, occ) in enumerate(stats["top_50_termini"], 1):
        lines.append(f"| {i} | {termine} | {occ} |")

    if soglie and soglie["n_misure"] > 0:
        lines += [
            "",
            "## Analisi quantitativa — Soglie mm×score (2018)",
            "",
            f"**Misure estratte:** {soglie['n_misure']}  ",
            f"**Range:** {soglie['range_mm']['min']:.1f}–{soglie['range_mm']['max']:.1f} mm",
            "",
            "| Categoria | Score medio | ±Std | N misure |",
            "|-----------|------------|------|----------|",
        ]
        for s in soglie["soglie"]:
            std_str = f"{s.get('score_std', 0):.2f}" if s.get("score_std") else "—"
            lines.append(f"| {s['categoria']} | {s['score_medio']:.2f} | {std_str} | {s['n_misure']} |")

        lines += [
            "",
            "### Esempi misure estratte",
            "",
            "| Misura (mm) | Score | Commento |",
            "|------------|-------|----------|",
        ]
        for e in soglie.get("esempi", []):
            commento_trunc = e["commento"][:60].replace("|", "│")
            lines.append(f"| {e['misura_mm']:.1f} | {e['score']:.2f} | {commento_trunc} |")

    return "\n".join(lines)


def genera_context_report(attributo: str, stats: Dict, soglie: Optional[Dict]) -> str:
    """Genera il context report .md da caricare come prima sorgente su NotebookLM."""
    config = ATTRIBUTI_CONFIG[attributo]
    top20 = ", ".join(f'"{t}"' for t, _ in stats["top_50_termini"][:20])

    table_rows = "\n".join(
        f"| {anno} | {s['n_totale']} | {s['n_validi']} | {s['perc_vuoti']}% | {s['lungh_media']} |"
        for anno, s in stats["stats_per_anno"].items()
    )

    report = f"""# Contesto Analisi Sensoriale Grana Trentino — {attributo}

## Il formaggio
Il TrentinGrana (Grana Trentino) è un formaggio a pasta dura e cotta prodotto in Trentino,
tutelato da disciplinare. Le sessioni di valutazione sensoriale (2018–2021) coinvolgono un
panel di assaggiatori professionisti che valutano ogni campione su 7 attributi sensoriali.
Ogni panelista compila una scheda individuale con punteggio numerico (1–10) e commento
testuale libero, scritto durante la degustazione — quindi spesso telegrafico.

## Questo attributo: {attributo}
{config['descrizione_nblm']}

## Come leggere i CSV caricati

I file CSV che hai come sorgenti contengono i dati originali non modificati.

- **Colonna "Commenti"**: il testo libero scritto dal panelista — **questa è la colonna da analizzare**
- **Colonna "Prodotto" / "Prod"**: codice anonimo del campione (es. "C0A", "TN302")
- **Colonna "Panelista" / "Sogg"**: codice anonimo del valutatore (es. "Q_02", "TG_20")
- **File 2018**: la 4a colonna (`{config['score_col_2018']}`) è il **punteggio numerico individuale**
  assegnato dallo stesso panelista (formato con virgola: "7,48" = 7.48 su scala 1–10)
- **File Risultati_Medie Giuria***: punteggi medi di giuria per campione (medie su tutti i panelisti)

## Statistiche dei commenti per {attributo}

| Anno | Totale righe | Commenti validi | % vuoti | Lungh. media (char) |
|------|-------------|-----------------|---------|---------------------|
{table_rows}

**Termini più frequenti (top 20):** {top20}

## Caratteristiche importanti dei commenti

I commenti sono spesso telegrafici perché scritti in tempo reale durante la degustazione:
- Termini singoli: `"burro"`, `"panna"`, `"stalla"`, `"nella norma"`
- Elenchi: `"burro, fruttato, intenso"`
- Giudizi sintetici: `"non tipico"`, `"difetto"`, `"ok"`
- Abbreviazioni: `"legg."` (= leggermente), `"mediam."` (= mediamente)
- Termini dialettali o colloquiali possibili

Non aggiungere interpretazioni non presenti nel testo originale.
Non interpretare l'assenza di commento come dato negativo.
"""

    if soglie and soglie["n_misure"] > 0:
        report += f"""
## Nota speciale — Termini quantitativi in {attributo}

Questo attributo contiene spesso misure numeriche nei commenti (mm, cm).
Da una analisi preliminare su {soglie['n_misure']} misure del dataset 2018:

| Range mm | Categoria stimata | Score medio associato |
|----------|------------------|----------------------|
| < 7 mm   | molto_sottile    | (vedi tabella stats)  |
| 7–12 mm  | nella_norma      | (vedi tabella stats)  |
| 12–18 mm | spessa           | (vedi tabella stats)  |
| > 18 mm  | molto_spessa     | (vedi tabella stats)  |

Queste sono **stime preliminari** — il tuo obiettivo è confermare o correggere
questi range basandoti su tutti i commenti, non solo quelli con misure esplicite.
"""

    report += f"""
## Obiettivo della tua analisi

Costruire un **dizionario di normalizzazione** per l'attributo {attributo}:
identificare tutti i termini usati dai panelisti e proporre una forma standard,
raggruppando sinonimi, varianti ortografiche, abbreviazioni e dialettalismi
che descrivono lo stesso concetto sensoriale.

## Termini tecnici INVARIABILI — non normalizzarli mai

`{TERMINI_TECNICI}`

Questi termini hanno significato tecnico preciso in caseificazione.
Non sostituirli con sinonimi generici.
"""
    return report


# ─────────────────────────────────────────────
# FASE 2 — Automazione NotebookLM
# ─────────────────────────────────────────────
QUERY_ORIENTAMENTO = """\
Hai caricato {n_sorgenti} fonti relative all'attributo sensoriale "{attributo}" \
del formaggio Grana Trentino. Leggi il documento "Contesto Analisi" per capire \
il progetto. Poi conferma brevemente: quante fonti CSV hai, \
qual è il range temporale dei dati, e qual è la colonna che contiene \
i commenti dei panelisti da analizzare.\
"""

QUERY_1_INVENTARIO = """\
Dalla colonna "Commenti" di tutte le fonti CSV caricate, estrai TUTTI i termini \
e le espressioni distinte usate dai panelisti per descrivere "{attributo}".
Includi anche i termini che compaiono una sola volta.

Per ogni termine o espressione produci una riga nella tabella:
| Termine / Espressione | Occorrenze (stima) | Anni in cui compare | Esempio di frase completa |

Ordina per frequenza decrescente. Non saltare termini rari o insoliti: \
quelli sono spesso i più utili per la normalizzazione.\
"""

QUERY_2_CLUSTER = """\
Basandoti sui termini che hai identificato per "{attributo}", \
raggruppa quelli che descrivono lo stesso concetto sensoriale in cluster semantici.

Per ogni cluster usa questo formato:

**Cluster: [nome del concetto sensoriale]**
- Varianti trovate nei dati: termine1, termine2, termine3, ...
- Forma canonica proposta: [la forma più chiara e corretta]
- Motivazione della scelta: [perché questa forma]
- Frequenza stimata del cluster: [somma delle occorrenze delle varianti]

Regola importante: i seguenti termini tecnici caseari sono INVARIABILI \
e non devono essere normalizzati — inseriscili nel proprio cluster senza \
modificarli: {termini_tecnici}\
"""

QUERY_3_ANOMALIE = """\
Per l'attributo "{attributo}", identifica nelle fonti i casi che richiedono \
normalizzazione speciale:

1. **ABBREVIAZIONI** — termini troncati o contratti
   (es: "legg." → probabilmente "leggermente"?)

2. **DIALETTALISMI / COLLOQUIALISMI** — espressioni non standard italiano

3. **ERRORI ORTOGRAFICI / TYPO** — parole scritte in modo errato

4. **ESPRESSIONI QUANTITATIVE** — numeri, misure (mm, cm, %), scale numeriche
   Per ogni valore trovato: a quale punteggio corrisponde nel file 2018? \
   Proponi una conversione qualitativa (es: "1cm → nella norma")

5. **CONTRADDIZIONI** — valutazioni opposte di panelisti diversi sullo stesso campione

Per ciascun caso usa la tabella:
| Termine trovato | Tipo (1–5) | Proposta di normalizzazione | Confidenza (alta/media/bassa) | Note |\
"""

QUERY_4_DUBBI = """\
Per concludere l'analisi di "{attributo}", elenca tutti i casi dove \
NON sei sicuro della normalizzazione corretta e serve una decisione umana.

Per ogni dubbio usa questo formato:

---
**DUBBIO N:** "[termine o espressione esatta dal testo]"
- **Perché è ambiguo:** [spiegazione del problema]
- **Opzione A:** [prima interpretazione possibile]
- **Opzione B:** [seconda interpretazione possibile]
- **Suggerimento NotebookLM:** [quale preferiresti e perché]
- **Dati a supporto:** [citazioni dal testo o punteggi che orientano la scelta]
---

Sii esaustivo: è meglio segnalare un dubbio in più che lasciarne uno irrisolto. \
Il revisore umano prenderà la decisione finale su ogni caso.\
"""


def run_nblm(args: List[str], timeout: int = 90, use_json: bool = True) -> Dict:
    """Esegue un comando notebooklm CLI. Ritorna dict JSON o {'returncode': N}."""
    cmd = ["notebooklm"] + args
    if use_json and "--json" not in args:
        cmd.append("--json")

    result = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout, encoding="utf-8")

    if result.returncode not in (0, 2):  # 2 = timeout wait (accettabile)
        raise RuntimeError(
            f"notebooklm fallito (exit {result.returncode}): "
            f"{result.stderr[:300] or result.stdout[:300]}"
        )

    if use_json and result.stdout.strip():
        try:
            return json.loads(result.stdout)
        except json.JSONDecodeError:
            return {"raw": result.stdout, "returncode": result.returncode}

    return {"returncode": result.returncode, "stdout": result.stdout}


def check_nblm_auth():
    """Verifica che notebooklm sia installato e autenticato."""
    try:
        result = run_nblm(["auth", "check"])
        if not result.get("checks", {}).get("sid_cookie"):
            logger.error("NotebookLM non autenticato. Esegui: notebooklm login")
            sys.exit(1)
        logger.info("NotebookLM: autenticato [OK]")
    except (FileNotFoundError, RuntimeError) as e:
        logger.error(f"notebooklm non disponibile: {e}")
        sys.exit(1)


def crea_notebook(attributo: str) -> str:
    """Crea un notebook NotebookLM per l'attributo. Ritorna notebook_id."""
    titolo = f"Grana Trentino — {attributo}"
    logger.info(f"  Creazione notebook: '{titolo}'")
    result = run_nblm(["create", titolo])
    nb_id = result["id"]
    logger.info(f"  Notebook ID: {nb_id}")
    return nb_id


def aggiungi_sorgente(nb_id: str, filepath: Path, descrizione: str = "") -> Optional[str]:
    """Aggiunge un file sorgente al notebook. Ritorna source_id o None."""
    if not filepath.exists():
        logger.warning(f"  File non trovato, salto: {filepath.name}")
        return None
    label = descrizione or filepath.name
    logger.info(f"  Upload: {label}")
    try:
        result = run_nblm(["source", "add", str(filepath), "--notebook", nb_id])
        sid = result.get("source_id")
        logger.info(f"    → source_id: {sid[:12]}..." if sid else "    → source_id non ricevuto")
        return sid
    except RuntimeError as e:
        logger.warning(f"  Upload fallito per {label}: {e}")
        return None


def attendi_tutte_sorgenti(nb_id: str, source_ids: List[str], timeout_sec: int = 120):
    """Attende che tutte le sorgenti siano elaborate da NotebookLM."""
    logger.info(f"  Attesa elaborazione {len(source_ids)} sorgenti...")
    run_nblm(["use", nb_id], use_json=False)  # Imposta contesto

    for sid in source_ids:
        if not sid:
            continue
        logger.info(f"    Attendo {sid[:12]}...")
        try:
            r = run_nblm(["source", "wait", sid, "-n", nb_id, "--timeout", str(timeout_sec)],
                         timeout=timeout_sec + 10, use_json=False)
            if r["returncode"] == 0:
                logger.info(f"    [OK] pronta")
            elif r["returncode"] == 2:
                logger.warning(f"    Timeout — continuo comunque")
            else:
                logger.warning(f"    Errore elaborazione (non bloccante)")
        except RuntimeError as e:
            logger.warning(f"    Errore wait: {e}")
    logger.info("  Tutte le sorgenti processate.")


def esegui_query(query: str, conversation_id: Optional[str] = None,
                 max_retries: int = 3) -> Tuple[str, str]:
    """
    Esegue una query su NotebookLM (contesto già impostato con `use`).
    Ritorna (risposta_testo, conversation_id).
    """
    args = ["ask", query]
    if conversation_id:
        args += ["-c", conversation_id]

    for attempt in range(max_retries):
        try:
            time.sleep(3 if attempt == 0 else 20 * attempt)  # backoff su retry
            result = run_nblm(args, timeout=120)
            answer = result.get("answer", result.get("raw", ""))
            conv_id = result.get("conversation_id", conversation_id or "")
            return answer, conv_id
        except (RuntimeError, subprocess.TimeoutExpired) as e:
            if attempt < max_retries - 1:
                wait = 30 * (2 ** attempt)
                logger.warning(f"    Query fallita (tentativo {attempt+1}/{max_retries}), attendo {wait}s: {e}")
                time.sleep(wait)
            else:
                logger.error(f"    Query fallita dopo {max_retries} tentativi: {e}")
                return f"[ERRORE: {e}]", conversation_id or ""


def esegui_4_query_sequenziali(nb_id: str, attributo: str) -> Dict[str, str]:
    """
    Esegue le 4+1 query sequenziali per l'attributo.
    Ritorna dict con chiavi: orientamento, q1, q2, q3, q4.
    """
    # Imposta contesto notebook
    run_nblm(["use", nb_id], use_json=False)

    # Conta sorgenti caricate
    try:
        src_list = run_nblm(["source", "list"])
        n_sorgenti = len(src_list.get("sources", []))
    except Exception:
        n_sorgenti = "N/A"

    risultati: Dict[str, str] = {}
    conv_id: Optional[str] = None

    # Query 0 — Orientamento (warm-up, non inclusa nel vocabolario bozza)
    logger.info("  Query 0: orientamento...")
    q0 = QUERY_ORIENTAMENTO.format(attributo=attributo, n_sorgenti=n_sorgenti)
    risposta0, conv_id = esegui_query(q0)
    risultati["orientamento"] = risposta0
    logger.info(f"    Risposta ricevuta ({len(risposta0)} char), conv_id: {conv_id[:12] if conv_id else 'N/A'}...")

    # Query 1 — Inventario termini
    logger.info("  Query 1: inventario termini...")
    q1 = QUERY_1_INVENTARIO.format(attributo=attributo)
    risposta1, conv_id = esegui_query(q1, conv_id)
    risultati["q1_inventario"] = risposta1
    logger.info(f"    Risposta: {len(risposta1)} char")

    # Query 2 — Cluster semantici
    logger.info("  Query 2: cluster semantici...")
    q2 = QUERY_2_CLUSTER.format(attributo=attributo, termini_tecnici=TERMINI_TECNICI)
    risposta2, conv_id = esegui_query(q2, conv_id)
    risultati["q2_cluster"] = risposta2
    logger.info(f"    Risposta: {len(risposta2)} char")

    # Query 3 — Anomalie e quantitativi
    logger.info("  Query 3: anomalie...")
    q3 = QUERY_3_ANOMALIE.format(attributo=attributo)
    risposta3, conv_id = esegui_query(q3, conv_id)
    risultati["q3_anomalie"] = risposta3
    logger.info(f"    Risposta: {len(risposta3)} char")

    # Query 4 — Dubbi per revisione umana
    logger.info("  Query 4: dubbi per revisione umana...")
    q4 = QUERY_4_DUBBI.format(attributo=attributo)
    risposta4, conv_id = esegui_query(q4, conv_id)
    risultati["q4_dubbi"] = risposta4
    logger.info(f"    Risposta: {len(risposta4)} char")

    return risultati


def salva_vocabolario_bozza(attributo: str, nb_id: str, risultati: Dict[str, str],
                             soglie: Optional[Dict] = None):
    """Salva il vocabolario bozza NotebookLM in un file .md strutturato."""
    slug = attr_to_slug(attributo)
    out_path = VOCABOLARI_BOZZA_DIR / f"{slug}_vocabolario_nblm.md"
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")

    # Soglie quantitative (solo Spessore della Crosta)
    soglie_md = ""
    if soglie and soglie["n_misure"] > 0:
        righe = "\n".join(
            f"| {s['categoria']} | {s['score_medio']:.2f} ± {s.get('score_std', 0):.2f} | {s['n_misure']} |"
            for s in soglie["soglie"]
        )
        soglie_md = f"""
---

## Soglie Quantitative — Analisi Script (da validare)

Correlazione misure mm×score 2018. **{soglie['n_misure']} misure estratte.**

| Categoria | Score medio ± std | N misure |
|-----------|------------------|----------|
{righe}

> Confronta questa stima con l'analisi quantitativa di NotebookLM (Query 3)
> per decidere i range definitivi nella revisione umana.
"""

    contenuto = f"""# Vocabolario Bozza — {attributo}

**Generato:** {timestamp}
**Notebook NotebookLM:** `{nb_id}`
**Stato:** BOZZA — richiede revisione umana prima di procedere con script 09

---

## Orientamento iniziale NotebookLM

{risultati.get('orientamento', '[non disponibile]')}

---

## Query 1 — Inventario termini

{risultati.get('q1_inventario', '[non disponibile]')}

---

## Query 2 — Cluster semantici

{risultati.get('q2_cluster', '[non disponibile]')}

---

## Query 3 — Anomalie e termini quantitativi

{risultati.get('q3_anomalie', '[non disponibile]')}

---

## Query 4 — Dubbi per revisione umana

{risultati.get('q4_dubbi', '[non disponibile]')}
{soglie_md}
---

## Istruzioni per la revisione umana

1. Leggi ogni sezione e valida / correggi le proposte di normalizzazione
2. Risolvi ogni dubbio in Query 4 scegliendo Opzione A, B o altra
3. Per Spessore della Crosta: confronta soglie script vs analisi NBLM e scegli i range definitivi
4. Salva le decisioni finali in: `data/interim/vocabolari_validati_per_attributo/{slug}_vocabolario.json`
5. Usa come template: `docs/template_vocabolario_validato.json` (generato da questo script)
"""

    out_path.write_text(contenuto, encoding="utf-8")
    logger.info(f"  Vocabolario bozza salvato: {out_path.name}")


def salva_template_vocabolario_json(attributo: str):
    """Salva un template JSON vuoto da compilare durante la revisione umana."""
    slug = attr_to_slug(attributo)
    out_path = VOCABOLARI_BOZZA_DIR / f"{slug}_vocabolario_TEMPLATE.json"

    template = {
        "attributo": attributo,
        "versione": "1.0",
        "data_validazione": "YYYY-MM-DD",
        "validato_da": "",
        "note_generali": "",
        "termini_tecnici_invariabili": TERMINI_TECNICI.split(", "),
        "cluster": [
            {
                "_esempio": "rimuovi questo blocco e sostituisci con cluster reali",
                "nome_cluster": "nome_concetto_sensoriale",
                "forma_canonica": "termine_standard",
                "varianti": ["variante1", "variante2"],
                "frequenza_stimata": 0
            }
        ],
        "sinonimi_diretti": [
            {"da": "termine_originale", "a": "forma_canonica", "tipo": "sinonimo|abbreviazione|dialetto|typo"}
        ],
        "conversioni_quantitative": [
            {
                "_nota": "solo per Spessore della Crosta",
                "pattern_regex": r"\d+\s*mm",
                "range_min_mm": 0,
                "range_max_mm": 7,
                "forma_canonica": "molto sottile"
            }
        ],
        "dubbi_non_risolti": []
    }

    out_path.write_text(json.dumps(template, ensure_ascii=False, indent=2), encoding="utf-8")
    logger.info(f"  Template JSON salvato: {out_path.name}")


# ─────────────────────────────────────────────
# Pipeline principale
# ─────────────────────────────────────────────
def fase1_analisi(attributo: str) -> Tuple[Dict, Optional[Dict]]:
    """Esegue l'analisi statistica per un attributo."""
    logger.info(f"\n{'='*50}")
    logger.info(f"FASE 1 — Analisi statistica: {attributo}")
    logger.info(f"{'='*50}")

    dfs = carica_commenti(attributo)
    if not dfs:
        logger.error(f"Nessun CSV trovato per {attributo}")
        return {}, None

    stats = analisi_statistica(attributo, dfs)
    logger.info(f"  Commenti totali: {stats['n_commenti_totali']} | "
                f"Termini unici: {stats['n_termini_unici']}")

    soglie = None
    if ATTRIBUTI_CONFIG[attributo]["has_quantitative"] and 2018 in dfs:
        logger.info("  Analisi quantitativa Spessore della Crosta...")
        soglie = analisi_quantitativa_spessore(dfs[2018])

    # Salva statistiche .md
    slug = attr_to_slug(attributo)
    stats_md = genera_statistiche_md(attributo, stats, soglie)
    path_stats = ANALISI_DIR / f"{slug}_statistiche.md"
    path_stats.write_text(stats_md, encoding="utf-8")
    logger.info(f"  Statistiche salvate: {path_stats.name}")

    # Salva context report .md (per NotebookLM)
    ctx_md = genera_context_report(attributo, stats, soglie)
    path_ctx = ANALISI_DIR / f"{slug}_contesto_notebooklm.md"
    path_ctx.write_text(ctx_md, encoding="utf-8")
    logger.info(f"  Context report salvato: {path_ctx.name}")

    return stats, soglie


def fase2_notebooklm(attributo: str, soglie: Optional[Dict],
                      notebook_ids: Dict[str, str], timeout_source: int = 120):
    """Crea notebook, carica sorgenti, esegue query, salva vocabolario bozza."""
    logger.info(f"\n{'='*50}")
    logger.info(f"FASE 2 — NotebookLM: {attributo}")
    logger.info(f"{'='*50}")

    slug = attr_to_slug(attributo)

    # Crea notebook
    nb_id = crea_notebook(attributo)
    notebook_ids[attributo] = nb_id

    # Salva notebook_ids progressivamente (in caso di interruzione)
    ids_path = VOCABOLARI_BOZZA_DIR / "notebook_ids.json"
    ids_path.write_text(json.dumps(notebook_ids, ensure_ascii=False, indent=2), encoding="utf-8")

    # Prepara lista sorgenti da caricare
    sorgenti: List[Tuple[Path, str]] = []

    # 1. Context report PRIMA (orienta NBLM)
    ctx_path = ANALISI_DIR / f"{slug}_contesto_notebooklm.md"
    sorgenti.append((ctx_path, "Contesto Analisi"))

    # 2. CSV raw per anno
    for anno in [2018, 2019, 2020, 2021]:
        p = get_raw_csv_path(attributo, anno)
        if p:
            sorgenti.append((p, f"Commenti {anno}"))

    # 3. File punteggi aggregati (solo i CSV, non i .xlsx)
    for anno in [2019, 2020, 2021]:
        # Cerca file corrispondente (nome con spazio dopo "2020_Q ")
        pattern = f"Risultati_2019-21_Medie Giuria{anno}_Q"
        for f in SCORES_DIR.iterdir():
            if pattern in f.name and f.suffix == ".csv":
                sorgenti.append((f, f"Punteggi giuria {anno}"))
                break

    # Carica tutte le sorgenti
    logger.info(f"  Caricamento {len(sorgenti)} sorgenti...")
    source_ids: List[str] = []
    for filepath, label in sorgenti:
        sid = aggiungi_sorgente(nb_id, filepath, label)
        if sid:
            source_ids.append(sid)
        time.sleep(1)  # piccola pausa tra upload

    # Attendi elaborazione
    attendi_tutte_sorgenti(nb_id, source_ids, timeout_source)

    # Pausa aggiuntiva per assicurare indicizzazione completa
    logger.info("  Pausa 10s per completare indicizzazione...")
    time.sleep(10)

    # Esegui 4 query sequenziali
    logger.info("  Avvio query sequenziali...")
    risultati = esegui_4_query_sequenziali(nb_id, attributo)

    # Salva vocabolario bozza .md
    salva_vocabolario_bozza(attributo, nb_id, risultati, soglie)

    # Salva template JSON per revisione umana
    salva_template_vocabolario_json(attributo)

    logger.info(f"  [OK] {attributo} completato")


def genera_report_finale(attributi_processati: List[str]):
    """Genera il report markdown complessivo in reports/."""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    righe_ids = ""
    ids_path = VOCABOLARI_BOZZA_DIR / "notebook_ids.json"
    if ids_path.exists():
        ids = json.loads(ids_path.read_text(encoding="utf-8"))
        righe_ids = "\n".join(
            f"| {attr} | `{nid}` |" for attr, nid in ids.items()
        )

    contenuto = f"""# Report Analisi Per-Attributo + NotebookLM

**Data elaborazione:** {timestamp}

---

## Attributi processati

{', '.join(attributi_processati)}

## Notebook NotebookLM creati

| Attributo | Notebook ID |
|-----------|------------|
{righe_ids}

## Output generati

### Fase 1 — Analisi statistica
```
data/interim/analisi_statistica_per_attributo/
  {{Attributo}}_statistiche.md          ← distribuzione, top termini, soglie quantitative
  {{Attributo}}_contesto_notebooklm.md  ← caricato come prima sorgente su NotebookLM
```

### Fase 2 — Vocabolario bozza NotebookLM
```
data/interim/vocabolari_bozza_per_attributo/
  {{Attributo}}_vocabolario_nblm.md     ← risposte alle 4 query (da revisionare)
  {{Attributo}}_vocabolario_TEMPLATE.json ← template vuoto per la revisione umana
  notebook_ids.json                     ← IDs notebook per riferimento futuro
```

## Passo successivo (manuale)

1. Per ogni attributo, apri `{{Attributo}}_vocabolario_nblm.md`
2. Leggi le 4 sezioni (inventario, cluster, anomalie, dubbi)
3. Compila `{{Attributo}}_vocabolario_TEMPLATE.json` con le decisioni finali
4. Rinomina il file compilato: `{{Attributo}}_vocabolario.json`
5. Sposta in: `data/interim/vocabolari_validati_per_attributo/`
6. Quando tutti i vocabolari sono validati → esegui script 09
"""

    out_path = REPORTS_DIR / "08_analisi_per_attributo.md"
    out_path.write_text(contenuto, encoding="utf-8")
    logger.info(f"\nReport finale salvato: {out_path}")


# ─────────────────────────────────────────────
# Entry point
# ─────────────────────────────────────────────
def parse_args():
    parser = argparse.ArgumentParser(
        description="Analisi statistica per attributo + automazione NotebookLM"
    )
    parser.add_argument(
        "--attributo",
        choices=list(ATTRIBUTI_CONFIG.keys()),
        help="Processa solo questo attributo (default: tutti)"
    )
    parser.add_argument(
        "--solo-analisi", action="store_true",
        help="Esegue solo la Fase 1 (analisi statistica), senza NotebookLM"
    )
    parser.add_argument(
        "--solo-nblm", action="store_true",
        help="Esegue solo la Fase 2 (NotebookLM), usa output analisi già esistente"
    )
    parser.add_argument(
        "--timeout-source", type=int, default=120,
        help="Secondi di attesa per ogni sorgente NotebookLM (default: 120)"
    )
    return parser.parse_args()


def main():
    args = parse_args()

    attributi = [args.attributo] if args.attributo else list(ATTRIBUTI_CONFIG.keys())
    esegui_analisi = not args.solo_nblm
    esegui_nblm = not args.solo_analisi

    logger.info(f"Attributi da processare: {attributi}")
    logger.info(f"Fase 1 (analisi): {'sì' if esegui_analisi else 'no'}")
    logger.info(f"Fase 2 (NotebookLM): {'sì' if esegui_nblm else 'no'}")

    if esegui_nblm:
        check_nblm_auth()

    # Carica notebook_ids esistenti (per ripresa in caso di interruzione)
    ids_path = VOCABOLARI_BOZZA_DIR / "notebook_ids.json"
    notebook_ids: Dict[str, str] = {}
    if ids_path.exists():
        notebook_ids = json.loads(ids_path.read_text(encoding="utf-8"))

    # Crea directory validati (servirà per script 09)
    (PROJECT_ROOT / "data" / "interim" / "vocabolari_validati_per_attributo").mkdir(
        parents=True, exist_ok=True
    )

    attributi_processati = []

    for attributo in attributi:
        try:
            soglie = None

            if esegui_analisi:
                _, soglie = fase1_analisi(attributo)

            if esegui_nblm:
                fase2_notebooklm(
                    attributo, soglie, notebook_ids,
                    timeout_source=args.timeout_source
                )

            attributi_processati.append(attributo)

        except KeyboardInterrupt:
            logger.warning("\nInterrotto dall'utente. Progresso salvato.")
            break
        except Exception as e:
            logger.error(f"Errore su {attributo}: {e}", exc_info=True)
            logger.warning(f"Continuo con il prossimo attributo...")

    genera_report_finale(attributi_processati)
    logger.info(f"\n[DONE] Completato. {len(attributi_processati)}/{len(attributi)} attributi processati.")


if __name__ == "__main__":
    main()
