#!/usr/bin/env python3
"""Validate that every comment row can be linked to TrentinGrana image assets."""
from __future__ import annotations

import argparse
import csv
from collections import Counter, defaultdict
from dataclasses import dataclass
from datetime import datetime
import re
from pathlib import Path
from typing import Dict, Iterable, List, Optional, Sequence, Tuple

REQUIRED_COLUMNS_2019 = {
    "Data Seduta di valutazione",
    "N° Seduta",
    "Prodotto",
}
REQUIRED_COLUMNS_2018 = {
    "Sogg",
    "Seduta",
    "Prod",
}
SESSION_DATE_FORMATS = ("%Y-%m-%d", "%d/%m/%Y", "%d-%m-%Y")
CASEIFICIO_COL = 0
PRODOTTO_COL = 1


@dataclass
class RowIssue:
    csv_file: str
    line_number: int
    issue_type: str
    detail: str
    data_seduta: Optional[str]
    seduta_number: Optional[int]
    prodotto: str
    caseificio: Optional[str]
    session_folder: Optional[str]

    def as_dict(self) -> Dict[str, Optional[str]]:
        return {
            "csv_file": self.csv_file,
            "line_number": str(self.line_number),
            "issue_type": self.issue_type,
            "detail": self.detail,
            "data_seduta": self.data_seduta or "",
            "seduta_number": str(self.seduta_number) if self.seduta_number is not None else "",
            "prodotto": self.prodotto,
            "caseificio": self.caseificio or "",
            "session_folder": self.session_folder or "",
        }


def parse_args() -> argparse.Namespace:
    repo_root = Path(__file__).resolve().parents[1]
    default_dataset = repo_root / "07_captioning risultati grana Trentino" / "GT commenti liberi" / "csv dataset"
    default_codifica = repo_root / "07_captioning risultati grana Trentino" / "GT commenti liberi" / "codifiche" / "codifica caseifici_codici caseifici.csv"
    default_trentin = repo_root / "07_captioning risultati grana Trentino" / "TrentinGrana"
    default_report = repo_root / "07_captioning risultati grana Trentino" / "validation_reports" / "session_validation_report.csv"
    default_date_map_2018 = repo_root / "07_captioning risultati grana Trentino" / "GT commenti liberi" / "csv dataset" / "Commenti TOT_2018_date_sedute_2018.csv"

    parser = argparse.ArgumentParser(description="Check that comment rows resolve to session folders and assets.")
    parser.add_argument("--dataset-dir", type=Path, default=default_dataset, help="Folder containing the CSV comment files.")
    parser.add_argument("--codifica-file", type=Path, default=default_codifica, help="CSV file mapping caseifici codes to prodotto codes.")
    parser.add_argument("--trentin-dir", type=Path, default=default_trentin, help="Root folder with TrentinGrana assets.")
    parser.add_argument("--report-path", type=Path, default=default_report, help="Where to write the detailed validation report.")
    parser.add_argument("--date-map-2018", type=Path, default=default_date_map_2018, help="CSV file mapping 2018 session numbers to dates.")
    parser.add_argument("--pattern", default="Commenti liberi", help="Only CSV files containing this substring will be validated.")
    return parser.parse_args()


def load_codifica_map(csv_path: Path) -> Dict[str, str]:
    mapping: Dict[str, str] = {}
    with csv_path.open(mode="r", encoding="utf-8-sig", newline="") as handle:
        reader = csv.reader(handle)
        for row in reader:
            if len(row) < 2:
                continue
            prodotto_code = row[PRODOTTO_COL].strip()
            caseificio = row[CASEIFICIO_COL].strip()
            if not prodotto_code or not caseificio:
                continue
            mapping[prodotto_code] = caseificio
    return mapping


def load_session_date_map_2018(csv_path: Path) -> Dict[int, str]:
    """Carica mapping Seduta → Data per il 2018.

    Args:
        csv_path: Path al file date_sedute_2018.csv

    Returns:
        Dict che mappa numero seduta → data ISO (YYYY-MM-DD)
    """
    mapping: Dict[int, str] = {}
    with csv_path.open(mode="r", encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        for row in reader:
            try:
                session_num = int(row.get("Session", "").strip())
                date_str = row.get("Date", "").strip()
                if session_num and date_str:
                    mapping[session_num] = date_str
            except (ValueError, KeyError):
                continue
    return mapping


def normalize_date(value: Optional[str]) -> Optional[str]:
    if not value:
        return None
    text = value.strip()
    for fmt in SESSION_DATE_FORMATS:
        try:
            return datetime.strptime(text, fmt).strftime("%Y-%m-%d")
        except ValueError:
            continue
    return None


def parse_session_number(raw_value: Optional[str]) -> Optional[int]:
    if not raw_value:
        return None
    match = re.search(r"(\d+)", raw_value)
    if not match:
        return None
    try:
        return int(match.group(1))
    except ValueError:
        return None


def parse_session_dir_name(name: str) -> Optional[str]:
    """Estrae la data dal nome della cartella.

    Formati supportati:
    - YYYY-MM-DD_Seduta_NN (2019-2022 con numero seduta)
    - YYYY-MM-DD (2018-2019 solo data)

    Returns:
        Data in formato ISO (YYYY-MM-DD) o None se non parsabile.
    """
    # Rimuovi caratteri speciali e "Seduta"
    degree = "\N{DEGREE SIGN}"
    sanitized = name.replace(degree, "").replace("Seduta", "").replace("seduta", "")

    # Caso 1: Formato YYYY-MM-DD_Seduta_NN → estrai parte prima di "_"
    if "_" in sanitized:
        date_part = sanitized.split("_", 1)[0].strip()
    else:
        # Caso 2: Formato YYYY-MM-DD (solo data, 2018-2019)
        date_part = sanitized.strip()

    # Normalizza e valida la data
    iso_date = normalize_date(date_part)
    return iso_date


def build_session_index(root: Path) -> Dict[str, List[Path]]:
    """Costruisce indice delle cartelle seduta per data.

    Returns:
        Dict che mappa data ISO → lista di cartelle con quella data.
    """
    index: Dict[str, List[Path]] = defaultdict(list)
    if not root.is_dir():
        return index
    for session_dir in root.rglob("*"):
        if not session_dir.is_dir():
            continue
        iso_date = parse_session_dir_name(session_dir.name)
        if iso_date:
            index[iso_date].append(session_dir)
    return index


def find_caseificio_files(session_dirs: Sequence[Path], caseificio: str) -> List[Path]:
    """Trova file immagini per un caseificio nelle cartelle seduta.

    Cerca sia il codice completo (es. TN302) che solo la parte numerica (302).
    Questo gestisce formati diversi: 2019-2021 usano codici completi,
    2018 usa solo numeri nei nomi file.
    """
    target_full = caseificio.replace("_", "").upper()

    # Estrai anche solo la parte numerica (per compatibilità 2018)
    numeric_part = re.search(r'\d+', caseificio)
    target_numeric = numeric_part.group(0) if numeric_part else None

    matches: List[Path] = []
    for session_dir in session_dirs:
        if not session_dir.exists():
            continue
        for item in session_dir.iterdir():
            if not item.is_file():
                continue
            stem_upper = item.stem.upper().replace("_", "")

            # Match su codice completo O parte numerica
            if target_full in stem_upper or (target_numeric and target_numeric in stem_upper):
                matches.append(item)
    return matches


def validate_row(
    csv_file: Path,
    line_number: int,
    row: Dict[str, str],
    codifica_map: Dict[str, str],
    session_index: Dict[str, List[Path]],
    session_date_map_2018: Optional[Dict[int, str]] = None,
) -> List[RowIssue]:
    """Valida una riga CSV.

    Supporta due formati:
    - 2019-2021: Data Seduta di valutazione, N° Seduta, Prodotto
    - 2018: Seduta (numero), Prod (usa session_date_map_2018 per convertire)
    """
    issues: List[RowIssue] = []

    # Formato 2018: usa numero Seduta + mapping per ottenere la data
    if "Seduta" in row and "Prod" in row and session_date_map_2018:
        seduta_number = parse_session_number(row.get("Seduta"))
        data_seduta = session_date_map_2018.get(seduta_number) if seduta_number else None
        prodotto = (row.get("Prod") or "").strip()
    else:
        # Formato 2019-2021: leggi direttamente la data
        data_seduta = normalize_date(row.get("Data Seduta di valutazione"))
        seduta_number = parse_session_number(row.get("N° Seduta"))
        prodotto = (row.get("Prodotto") or "").strip()

    caseificio = codifica_map.get(prodotto)

    # Match basato SOLO sulla data (numero seduta opzionale)
    session_dirs = session_index.get(data_seduta) if data_seduta else None
    if not data_seduta:
        issues.append(
            RowIssue(
                csv_file=csv_file.name,
                line_number=line_number,
                issue_type="missing_date",
                detail="Data Seduta di valutazione non valida",
                data_seduta=row.get("Data Seduta di valutazione"),
                seduta_number=seduta_number,
                prodotto=prodotto,
                caseificio=caseificio,
                session_folder=None,
            )
        )
    if seduta_number is None:
        issues.append(
            RowIssue(
                csv_file=csv_file.name,
                line_number=line_number,
                issue_type="missing_seduta",
                detail="N° Seduta non valido",
                data_seduta=data_seduta,
                seduta_number=None,
                prodotto=prodotto,
                caseificio=caseificio,
                session_folder=None,
            )
        )
    if not prodotto:
        issues.append(
            RowIssue(
                csv_file=csv_file.name,
                line_number=line_number,
                issue_type="missing_prodotto",
                detail="Campo Prodotto vuoto",
                data_seduta=data_seduta,
                seduta_number=seduta_number,
                prodotto="",
                caseificio=None,
                session_folder=None,
            )
        )
    if prodotto and not caseificio:
        issues.append(
            RowIssue(
                csv_file=csv_file.name,
                line_number=line_number,
                issue_type="prodotto_non_mappato",
                detail="Prodotto non presente nella codifica",
                data_seduta=data_seduta,
                seduta_number=seduta_number,
                prodotto=prodotto,
                caseificio=None,
                session_folder=None,
            )
        )
    # Segnala errore solo se la data è valida ma non troviamo cartelle
    if data_seduta and not session_dirs:
        issues.append(
            RowIssue(
                csv_file=csv_file.name,
                line_number=line_number,
                issue_type="sessione_inesistente",
                detail=f"Nessuna cartella trovata per la data {data_seduta}",
                data_seduta=data_seduta,
                seduta_number=seduta_number,
                prodotto=prodotto,
                caseificio=caseificio,
                session_folder=None,
            )
        )
    if session_dirs and caseificio:
        matches = find_caseificio_files(session_dirs, caseificio)
        if not matches:
            issues.append(
                RowIssue(
                    csv_file=csv_file.name,
                    line_number=line_number,
                    issue_type="asset_mancante",
                    detail="Nessun file trovato per il caseificio nella seduta",
                    data_seduta=data_seduta,
                    seduta_number=seduta_number,
                    prodotto=prodotto,
                    caseificio=caseificio,
                    session_folder=str(session_dirs[0]),
                )
            )
    return issues


def process_csv_file(
    csv_path: Path,
    codifica_map: Dict[str, str],
    session_index: Dict[str, List[Path]],
    session_date_map_2018: Optional[Dict[int, str]] = None,
) -> Tuple[Counter, List[RowIssue]]:
    stats = Counter(total_rows=0, ok_rows=0)
    issues: List[RowIssue] = []
    with csv_path.open(mode="r", encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        fieldnames = reader.fieldnames or []

        # Rileva formato: 2018 o 2019-2021
        is_2018 = REQUIRED_COLUMNS_2018.issubset(set(fieldnames))
        is_2019 = REQUIRED_COLUMNS_2019.issubset(set(fieldnames))

        if not is_2018 and not is_2019:
            return stats, issues

        for line_number, row in enumerate(reader, start=2):
            stats["total_rows"] += 1
            row_issues = validate_row(
                csv_path, line_number, row, codifica_map, session_index,
                session_date_map_2018 if is_2018 else None
            )
            if row_issues:
                issues.extend(row_issues)
            else:
                stats["ok_rows"] += 1
    return stats, issues


def write_report(rows: Iterable[RowIssue], report_path: Path) -> None:
    report_path.parent.mkdir(parents=True, exist_ok=True)
    fieldnames = [
        "csv_file",
        "line_number",
        "issue_type",
        "detail",
        "data_seduta",
        "seduta_number",
        "prodotto",
        "caseificio",
        "session_folder",
    ]
    with report_path.open(mode="w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        for row in rows:
            writer.writerow(row.as_dict())


def main() -> None:
    args = parse_args()
    codifica_map = load_codifica_map(args.codifica_file)
    if not codifica_map:
        raise SystemExit(f"Nessuna codifica trovata in {args.codifica_file}")

    # Carica mapping sedute 2018 (opzionale)
    session_date_map_2018: Optional[Dict[int, str]] = None
    if args.date_map_2018.exists():
        session_date_map_2018 = load_session_date_map_2018(args.date_map_2018)
        print(f"Caricato mapping 2018: {len(session_date_map_2018)} sedute")

    session_index = build_session_index(args.trentin_dir)
    if not session_index:
        raise SystemExit(f"Nessuna seduta trovata in {args.trentin_dir}")

    csv_files = sorted(p for p in args.dataset_dir.glob("*.csv") if args.pattern in p.name)
    if not csv_files:
        raise SystemExit(f"Nessun file CSV trovato in {args.dataset_dir} con pattern '{args.pattern}'")

    global_stats = Counter(files=len(csv_files), total_rows=0, ok_rows=0)
    all_issues: List[RowIssue] = []
    for csv_file in csv_files:
        stats, issues = process_csv_file(csv_file, codifica_map, session_index, session_date_map_2018)
        global_stats["total_rows"] += stats["total_rows"]
        global_stats["ok_rows"] += stats["ok_rows"]
        all_issues.extend(issues)
        print(
            f"{csv_file.name}: {stats['ok_rows']}/{stats['total_rows']} righe collegate" if stats["total_rows"] else f"{csv_file.name}: colonne richieste mancanti",
        )

    write_report(all_issues, args.report_path)
    print(
        f"Completato. Righe valide: {global_stats['ok_rows']}/{global_stats['total_rows']} su {global_stats['files']} file."
    )
    print(f"Report dettagliato: {args.report_path}")


if __name__ == "__main__":
    main()
