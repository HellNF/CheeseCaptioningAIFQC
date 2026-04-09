import logging
import os
import time
import json
from pathlib import Path
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime
import pandas as pd
from openai import OpenAI
from dotenv import load_dotenv

# Carica variabili d'ambiente
load_dotenv()

# Setup logging
LOG_DIR = Path("logs")
LOG_DIR.mkdir(exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(LOG_DIR / '07_caption_generation.log', mode='w', encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Costanti
PROJECT_ROOT = Path(__file__).parent.parent.parent
INPUT_FILE = PROJECT_ROOT / "data" / "processed" / "campioni_completi.csv"
OUTPUT_DIR = PROJECT_ROOT / "data" / "processed"
REPORTS_DIR = PROJECT_ROOT / "reports"

OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
REPORTS_DIR.mkdir(parents=True, exist_ok=True)

# Configurazione OpenAI
OPENAI_MODEL = "gpt-4o-mini"
MAX_TOKENS = 600
TEMPERATURE = 0.3
SLEEP_BETWEEN_CALLS = 0.5  # secondi
MAX_RETRIES = 3

# Configurazione processamento
TEST_MODE = False  # Modificare a False per run completo
SOGLIA_MIN_ATTRIBUTI = 3
CHECKPOINT_INTERVAL = 50

# Lista attributi
ATTRIBUTI = [
    'Profumo', 'Sapore', 'Aroma', 'Texture',
    'Struttura della Pasta', 'Colore della Pasta', 'Spessore della Crosta'
]

# System prompt
SYSTEM_PROMPT = """Sei un esperto di analisi sensoriale del formaggio Grana Trentino (TrentinGrana). Il tuo compito è sintetizzare i commenti di un panel di assaggiatori in una caption descrittiva completa.

REGOLE FONDAMENTALI:
1. Scrivi in italiano, in forma narrativa continua
2. Struttura la caption per attributo nell'ordine:
   Profumo → Sapore → Aroma → Texture → Struttura della Pasta → Colore della Pasta → Spessore della Crosta
3. Se un attributo non ha commenti ma ha punteggio:
   - Punteggio >= 7.5 → "eccellente/pronunciato/ottimo"
   - Punteggio 6.5-7.4 → "buono/nella norma"
   - Punteggio 5.5-6.4 → "modesto/nella norma inferiore"
   - Punteggio < 5.5 → "insufficiente — difetto"
4. Se un attributo non ha né commenti né punteggio → omettilo COMPLETAMENTE dalla caption, senza menzionarlo e senza spiegare la sua assenza. La caption deve leggere come se quell'attributo non esistesse.
5. DIFETTI: se anche 1 solo panelista riporta un difetto, includilo sempre con tag "— difetto"
6. Termini contestuali:
   - "leggermente piccante/amaro" → caratteristica appropriata
   - "troppo piccante/amaro" → piccantezza/amarezza eccessiva — difetto
   - Usa SEMPRE il punteggio per disambiguare se non c'è modificatore
7. Quando i panelisti si contraddicono, il punteggio decide il tono
8. Preserva SEMPRE i termini tecnici caseari:
   scalzo, piatti, sottocrosta, microocchiatura, occhiatura,
   grana, frattura, stirata, cristalli, tirosina, nostrano, insilato
9. Lunghezza target: 80-150 parole
10. NON iniziare con "Il campione" o "Questo formaggio" — inizia direttamente dall'attributo: "Il profumo è..."
11. REGOLA CRITICA - ATTRIBUTI MANCANTI:
    Se un attributo non ha dati, NON scrivere nulla su di esso.

    ❌ VIETATO (non scrivere MAI queste frasi o simili):
    - 'non è stato commentato'
    - 'non è stato menzionato'
    - 'non è stato descritto'
    - 'non sono disponibili informazioni'
    - 'non è possibile fornire dettagli'

    ✅ CORRETTO: se mancano dati su Colore e Spessore Crosta,
    la caption finisce semplicemente dopo l'ultimo attributo
    disponibile, senza alcuna menzione degli attributi assenti.

    Esempio SBAGLIATO: '...La texture è friabile.
    Il colore della pasta non è stato commentato.'

    Esempio CORRETTO: '...La texture è friabile.'
12. Descrivi SOLO caratteristiche sensoriali tecniche. NON fare valutazioni di consumo, NON suggerire occasioni di utilizzo, NON esprimere giudizi commerciali.

    ❌ VIETATO (non scrivere MAI frasi come queste):
    - '...un aspetto che potrebbe essere migliorato'
    - '...che dovrebbe essere corretto'
    - '...da migliorare nella produzione'
    - '...si abbina bene con...'
    - '...ideale per...'

    ✅ CORRETTO: descrivi il dato sensoriale in modo neutro e tecnico.
    Esempio SBAGLIATO: 'La texture risulta tenera, un aspetto che potrebbe essere migliorato.'
    Esempio CORRETTO:  'La texture risulta tenera.'"""


def normalize_attr_name(attr: str) -> str:
    """
    Normalizza nome attributo per matching con colonne CSV.

    Args:
        attr: Nome attributo originale

    Returns:
        Nome normalizzato per colonne CSV
    """
    return attr.lower().replace(' della ', '_').replace(' ', '_')


def filter_comments(comments_list: List[str]) -> List[str]:
    """
    Filtra commenti vuoti, [REVIEW:...] e "nella norma" (eccetto se unico).

    Args:
        comments_list: Lista di commenti

    Returns:
        Lista filtrata
    """
    # Rimuovi vuoti e [REVIEW:...]
    filtered = []
    for c in comments_list:
        c_str = str(c).strip()
        if c_str and not c_str.startswith('[REVIEW:'):
            filtered.append(c_str)

    # Se non c'è "nella norma", ritorna filtrato
    norma_variants = ['nella norma', 'regolare', 'ok', 'buono', 'buona']

    # Filtra "nella norma" solo se ci sono altri commenti
    non_norma = [c for c in filtered if c.lower() not in norma_variants]

    if non_norma:
        return non_norma
    else:
        # Se solo "nella norma", lo mantiene
        return filtered


def build_user_prompt(row: pd.Series) -> str:
    """
    Costruisce il prompt utente per un campione.

    Args:
        row: Riga del DataFrame campioni

    Returns:
        Stringa del prompt
    """
    sample_id = row['sample_id']
    anno = int(row['anno']) if pd.notna(row['anno']) else 'N/A'

    prompt_parts = [
        f"Campione: {sample_id}",
        f"Anno: {anno}",
        "",
        "COMMENTI DEI PANELISTI:",
        ""
    ]

    for attr in ATTRIBUTI:
        col_name = f"commenti_{normalize_attr_name(attr)}"
        score_col = f"punteggio_{normalize_attr_name(attr)}"

        # Carica commenti
        try:
            commenti_json = row[col_name]
            commenti_list = json.loads(commenti_json)
            commenti_filtered = filter_comments(commenti_list)
        except:
            commenti_filtered = []

        # Carica punteggio
        punteggio = row.get(score_col)
        punteggio_str = f"{punteggio:.2f}" if pd.notna(punteggio) else "N/A"

        # Se né commenti né punteggio → ometti attributo
        if not commenti_filtered and pd.isna(punteggio):
            continue

        # Costruisci sezione attributo
        n_commenti = len(commenti_filtered)

        prompt_parts.append(f"{attr} ({n_commenti} commenti, punteggio: {punteggio_str}):")

        if commenti_filtered:
            for i, comment in enumerate(commenti_filtered, 1):
                prompt_parts.append(f"  - {comment}")
        else:
            prompt_parts.append("  - Nessun commento disponibile")

        prompt_parts.append("")

    prompt_parts.append("Genera la caption descrittiva completa seguendo le regole.")

    return "\n".join(prompt_parts)


def generate_caption_with_retry(
    client: OpenAI,
    user_prompt: str,
    max_retries: int = MAX_RETRIES
) -> Tuple[Optional[str], int, bool]:
    """
    Genera caption con retry automatico su errori.

    Args:
        client: Client OpenAI
        user_prompt: Prompt utente
        max_retries: Numero massimo di tentativi

    Returns:
        Tupla (caption, tokens_usati, successo)
    """
    for attempt in range(max_retries):
        try:
            response = client.chat.completions.create(
                model=OPENAI_MODEL,
                messages=[
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user", "content": user_prompt}
                ],
                max_tokens=MAX_TOKENS,
                temperature=TEMPERATURE
            )

            content = response.choices[0].message.content
            if content is None:
                raise ValueError("Risposta vuota da OpenAI")
            
            caption = content.strip()
            tokens_used = response.usage.total_tokens if response.usage else 0

            return caption, tokens_used, True

        except Exception as e:
            wait_time = (2 ** attempt) * 1  # Exponential backoff: 1, 2, 4 secondi
            logger.warning(f"Tentativo {attempt + 1}/{max_retries} fallito: {e}")

            if attempt < max_retries - 1:
                logger.info(f"Attendo {wait_time} secondi prima di riprovare...")
                time.sleep(wait_time)
            else:
                logger.error(f"Tutti i {max_retries} tentativi falliti")
                return None, 0, False

    return None, 0, False


def save_checkpoint(df_results: pd.DataFrame, checkpoint_num: int):
    """
    Salva checkpoint intermedio.

    Args:
        df_results: DataFrame con risultati parziali
        checkpoint_num: Numero del checkpoint
    """
    checkpoint_path = OUTPUT_DIR / f"captions_checkpoint_{checkpoint_num}.csv"
    df_results.to_csv(checkpoint_path, index=False, encoding='utf-8')
    logger.info(f"Checkpoint salvato: {checkpoint_path}")


def filter_samples(df: pd.DataFrame) -> pd.DataFrame:
    """
    Filtra campioni utilizzabili per generazione caption.

    Args:
        df: DataFrame campioni completi

    Returns:
        DataFrame filtrato
    """
    logger.info("="*80)
    logger.info("FILTRAGGIO CAMPIONI")
    logger.info("="*80)

    # Conta attributi commentati
    def count_commented_attrs(row):
        count = 0
        for attr in ATTRIBUTI:
            col_name = f"commenti_{normalize_attr_name(attr)}"
            try:
                commenti_list = json.loads(row[col_name])
                filtered = filter_comments(commenti_list)
                if filtered:
                    count += 1
            except:
                pass
        return count

    df['n_attributi_commentati_filtered'] = df.apply(count_commented_attrs, axis=1)

    # Filtri
    mask_attributi = df['n_attributi_commentati_filtered'] >= SOGLIA_MIN_ATTRIBUTI
    mask_panelisti = df['n_panelisti'] > 0
    mask_immagini = (df['n_immagini_fetta'] > 0) & (df['n_immagini_grana'] > 0)

    df_filtered = df[mask_attributi & mask_panelisti & mask_immagini].copy()

    logger.info(f"Campioni totali: {len(df)}")
    logger.info(f"Campioni con >= {SOGLIA_MIN_ATTRIBUTI} attributi: {mask_attributi.sum()}")
    logger.info(f"Campioni con >= 1 panelista: {mask_panelisti.sum()}")
    logger.info(f"Campioni con FETTA+GRANA: {mask_immagini.sum()}")
    logger.info(f"Campioni utilizzabili (dopo filtri): {len(df_filtered)}")

    return df_filtered


def generate_captions(df_filtered: pd.DataFrame) -> pd.DataFrame:
    """
    Genera caption per tutti i campioni filtrati.

    Args:
        df_filtered: DataFrame campioni filtrati

    Returns:
        DataFrame con caption generate
    """
    logger.info("="*80)
    logger.info("GENERAZIONE CAPTION")
    logger.info("="*80)

    # Inizializza client OpenAI
    api_key = os.getenv('OPENAI_API_KEY')
    if not api_key:
        raise ValueError("OPENAI_API_KEY non trovata in variabili d'ambiente o file .env")

    client = OpenAI(api_key=api_key)

    # Limita campioni in TEST_MODE
    if TEST_MODE:
        # Test su 2 campioni specifici che avevano il problema
        test_samples = ['TN338_2019-11-20', 'TN313_2020-01-15']
        df_to_process = df_filtered[df_filtered['sample_id'].isin(test_samples)].copy()
        logger.info(f"TEST_MODE attivo: processando {len(df_to_process)} campioni specifici (fix regola 11)")
    else:
        df_to_process = df_filtered.copy()
        logger.info(f"FULL MODE: processando {len(df_to_process)} campioni")

    # Lista per risultati
    results = []
    failed_samples = []
    total_tokens = 0

    start_time = time.time()

    for idx, (_, row) in enumerate(df_to_process.iterrows(), 1):
        sample_id = row['sample_id']
        logger.info(f"[{idx}/{len(df_to_process)}] Processing {sample_id}...")

        # Costruisci prompt
        user_prompt = build_user_prompt(row)

        # Genera caption
        caption, tokens, success = generate_caption_with_retry(client, user_prompt)

        if success:
            results.append({
                'sample_id': sample_id,
                'anno': int(row['anno']) if pd.notna(row['anno']) else None,
                'codice_caseificio': row['codice_caseificio'],
                'data_seduta': row['data_seduta'],
                'path_fetta_primaria': row['path_fetta_primaria'],
                'path_grana_primaria': row['path_grana_primaria'],
                'caption': caption,
                'n_attributi_usati': row['n_attributi_commentati_filtered'],
                'n_panelisti': row['n_panelisti'],
                'tokens_usati': tokens,
                'timestamp_generazione': datetime.now().isoformat()
            })

            total_tokens += tokens

            if TEST_MODE:
                # In TEST_MODE stampa caption a schermo
                logger.info(f"\nCAPTION GENERATA:\n{caption}\n")
        else:
            failed_samples.append(sample_id)
            logger.error(f"Caption fallita per {sample_id}")

        # Sleep tra chiamate
        time.sleep(SLEEP_BETWEEN_CALLS)

        # Checkpoint ogni N campioni
        if idx % CHECKPOINT_INTERVAL == 0 and not TEST_MODE:
            df_partial = pd.DataFrame(results)
            save_checkpoint(df_partial, idx // CHECKPOINT_INTERVAL)

    end_time = time.time()
    elapsed = end_time - start_time

    # Statistiche finali
    logger.info("="*80)
    logger.info("STATISTICHE GENERAZIONE")
    logger.info("="*80)
    logger.info(f"Caption generate con successo: {len(results)}")
    logger.info(f"Caption fallite: {len(failed_samples)}")
    logger.info(f"Tokens totali usati: {total_tokens}")
    logger.info(f"Tempo totale: {elapsed:.1f} secondi")
    logger.info(f"Tempo medio per caption: {elapsed/len(df_to_process):.1f} secondi")

    if failed_samples:
        logger.warning(f"Campioni falliti: {', '.join(failed_samples)}")

    # Crea DataFrame risultati
    df_results = pd.DataFrame(results)

    return df_results


def generate_report(df_results: pd.DataFrame, output_path: Path):
    """
    Genera report markdown con caption generate.

    Args:
        df_results: DataFrame con risultati
        output_path: Path dove salvare il report
    """
    logger.info(f"Generando report in {output_path}...")

    with open(output_path, 'w', encoding='utf-8') as f:
        f.write("# REPORT GENERAZIONE CAPTION - Grana Trentino\n\n")
        f.write(f"**Data elaborazione:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
        f.write(f"**Modalità:** {'TEST (20 campioni)' if TEST_MODE else 'FULL'}\n\n")
        f.write("---\n\n")

        # Statistiche
        f.write("## STATISTICHE\n\n")
        f.write(f"- Caption generate: {len(df_results)}\n")
        f.write(f"- Tokens totali usati: {df_results['tokens_usati'].sum()}\n")
        f.write(f"- Tokens medi per caption: {df_results['tokens_usati'].mean():.1f}\n")
        f.write(f"- Lunghezza media caption: {df_results['caption'].str.split().str.len().mean():.1f} parole\n\n")

        # Costo stimato (ipotesi: $0.15 per 1M input tokens, $0.60 per 1M output tokens per gpt-4o-mini)
        # Approssimazione: ~70% input, 30% output
        total_tokens = df_results['tokens_usati'].sum()
        input_tokens_est = total_tokens * 0.7
        output_tokens_est = total_tokens * 0.3

        cost_est = (input_tokens_est / 1_000_000 * 0.15) + (output_tokens_est / 1_000_000 * 0.60)

        f.write(f"**Costo stimato (gpt-4o-mini):**\n")
        f.write(f"- Questo run: ${cost_est:.4f}\n")

        if TEST_MODE:
            # Stima costo full
            avg_tokens_per_sample = df_results['tokens_usati'].mean()
            estimated_full_tokens = avg_tokens_per_sample * 432  # 432 campioni totali
            input_est_full = estimated_full_tokens * 0.7
            output_est_full = estimated_full_tokens * 0.3
            cost_full = (input_est_full / 1_000_000 * 0.15) + (output_est_full / 1_000_000 * 0.60)

            f.write(f"- Run completo stimato (432 campioni): ${cost_full:.4f}\n\n")
        else:
            f.write("\n")

        # Esempi caption (prime 5)
        f.write("## ESEMPI CAPTION GENERATE\n\n")

        for i, (_, row) in enumerate(df_results.head(5).iterrows(), 1):
            f.write(f"### Esempio {i}: {row['sample_id']}\n\n")
            f.write(f"**Anno:** {int(row['anno']) if pd.notna(row['anno']) else 'N/A'}  \n")
            f.write(f"**Attributi usati:** {row['n_attributi_usati']}  \n")
            f.write(f"**Panelisti:** {row['n_panelisti']}  \n")
            f.write(f"**Tokens:** {row['tokens_usati']}  \n\n")
            f.write(f"**Caption:**\n\n")
            f.write(f"> {row['caption']}\n\n")

        f.write("---\n\n")
        f.write("**Note:**\n")
        f.write(f"- Modello: {OPENAI_MODEL}\n")
        f.write(f"- Temperature: {TEMPERATURE}\n")
        f.write(f"- Max tokens: {MAX_TOKENS}\n")

    logger.info("Report generato con successo")


def main():
    """Funzione principale dello script."""
    logger.info("="*80)
    logger.info("INIZIO GENERAZIONE CAPTION - Grana Trentino")
    logger.info("="*80)

    try:
        # 1. Carica dataset
        logger.info(f"Caricamento dataset da {INPUT_FILE}...")
        df = pd.read_csv(INPUT_FILE, encoding='utf-8')
        logger.info(f"Dataset caricato: {len(df)} campioni")

        # 2. Filtra campioni
        df_filtered = filter_samples(df)

        # 3. Genera caption
        df_results = generate_captions(df_filtered)

        # 4. Salva risultati
        if TEST_MODE:
            output_path = OUTPUT_DIR / "captions_test.csv"
            report_path = REPORTS_DIR / "07_captions_test.md"
        else:
            output_path = OUTPUT_DIR / "captions_finali.csv"
            report_path = REPORTS_DIR / "07_captions_finali.md"

        df_results.to_csv(output_path, index=False, encoding='utf-8')
        logger.info(f"Caption salvate in: {output_path}")

        # 5. Genera report
        generate_report(df_results, report_path)

        logger.info("="*80)
        logger.info("GENERAZIONE CAPTION COMPLETATA CON SUCCESSO")
        logger.info(f"Output: {output_path}")
        logger.info(f"Report: {report_path}")
        logger.info("="*80)

    except Exception as e:
        logger.error(f"Errore durante elaborazione: {e}", exc_info=True)
        raise


if __name__ == "__main__":
    main()
