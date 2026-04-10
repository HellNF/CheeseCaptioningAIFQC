#!/usr/bin/env python
"""
Script 09a — Compilazione vocabolari validati per attributo.

Legge i documenti di revisione umana in:
  data/interim/vocabolari_revisione_umana/

Genera i JSON vocabolario in:
  data/interim/vocabolari_validati_per_attributo/

Genera il report:
  data/interim/vocabolari_revisione_umana/revisione_status.md

Usage:
    python src/data/09a_compila_vocabolari.py
    python src/data/09a_compila_vocabolari.py --dry-run
"""
import sys
import argparse
from pathlib import Path
from datetime import date

# Aggiunge root del progetto al path per import del modulo
sys.path.insert(0, str(Path(__file__).parents[2]))
from src.data.compila_vocabolari import compile_all, REVISIONE_DIR, OUTPUT_DIR


def build_status_report(results: dict) -> str:
    lines = [
        f"# Revisione Status — {date.today()}",
        "",
        "| Attributo | Stato | Dubbi aperti | JSON generato |",
        "|---|---|---|---|",
    ]
    for attributo, info in sorted(results.items()):
        status_emoji = {
            "ok": "[OK]",
            "open_doubts": "[DUBBI]",
            "not_approved": "[NON APPROVATO]",
        }.get(info["status"], "[?]")
        lines.append(
            f"| {attributo.replace('_', ' ')} "
            f"| {status_emoji} {info['status']} "
            f"| {info['n_doubts']} "
            f"| `{Path(info['path']).name}` |"
        )
    lines.append("")
    n_ok = sum(1 for r in results.values() if r["status"] == "ok")
    n_open = sum(1 for r in results.values() if r["status"] == "open_doubts")
    n_not = sum(1 for r in results.values() if r["status"] == "not_approved")
    lines.append(f"**Totale:** {len(results)} attributi — "
                 f"{n_ok} completi, {n_open} con dubbi aperti, {n_not} non approvati")
    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(description="Compila vocabolari revisione → JSON")
    parser.add_argument("--dry-run", action="store_true",
                        help="Mostra cosa farebbe senza scrivere file")
    parser.add_argument("--revisione-dir", type=Path, default=REVISIONE_DIR)
    parser.add_argument("--output-dir", type=Path, default=OUTPUT_DIR)
    args = parser.parse_args()

    if not args.revisione_dir.exists():
        print(f"ERRORE: Directory non trovata: {args.revisione_dir}")
        sys.exit(1)

    files = list(args.revisione_dir.glob("*_revisione.md"))
    if not files:
        print(f"⚠️  Nessun file *_revisione.md trovato in {args.revisione_dir}")
        sys.exit(0)

    print(f"Trovati {len(files)} file da compilare...")

    if args.dry_run:
        print("Dry-run: nessun file scritto.")
        for f in sorted(files):
            print(f"  - {f.name}")
        return

    results = compile_all(args.revisione_dir, args.output_dir)

    # Salva report
    report = build_status_report(results)
    report_path = args.revisione_dir / "revisione_status.md"
    report_path.write_text(report, encoding="utf-8")

    # Stampa riepilogo
    print("\n" + report)
    print(f"\nReport salvato in: {report_path}")
    print(f"JSON generati in:  {args.output_dir}")

    # Exit code 1 se ci sono dubbi aperti o non approvati
    if any(r["status"] != "ok" for r in results.values()):
        sys.exit(1)


if __name__ == "__main__":
    main()
