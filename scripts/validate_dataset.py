#!/usr/bin/env python3
"""Valide un dataset synthétique et affiche ses statistiques.

Usage :
    python scripts/validate_dataset.py data/dataset_synthetique.csv
    python scripts/validate_dataset.py data/dataset_synthetique.csv data/dataset_test.csv
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from core.dataset import DatasetError, validate_dataset  # noqa: E402


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Valide un dataset Mino-IA")
    parser.add_argument("paths", nargs="+", type=Path, help="Fichiers CSV à valider")
    parser.add_argument(
        "--no-prediction-check",
        action="store_true",
        help="Ne pas recalculer les statuts/probabilités avec le moteur",
    )
    parser.add_argument("--json", action="store_true", help="Sortie JSON")
    args = parser.parse_args(argv)

    exit_code = 0
    for path in args.paths:
        try:
            report = validate_dataset(path, check_predictions=not args.no_prediction_check)
        except DatasetError as exc:
            print(f"ERREUR : {exc}", file=sys.stderr)
            exit_code = 2
            continue
        if args.json:
            print(json.dumps(report, ensure_ascii=False, indent=2))
        else:
            print(f"\n{path}")
            print(f"  Valide       : {report['valid']}")
            print(f"  Lignes       : {report['stats']['rows']}")
            print(f"  Évaluations  : {report['stats']['evaluations']}")
            print(f"  Statuts      : {report['stats']['status']}")
            print(f"  Probabilités : {report['stats']['probabilities']}")
            if report["errors"]:
                print(f"  Erreurs      : {len(report['errors'])}")
                for error in report["errors"][:20]:
                    print(f"    - {error}")
                if len(report["errors"]) > 20:
                    print(f"    ... et {len(report['errors']) - 20} autres.")
        if not report["valid"]:
            exit_code = 1

    return exit_code


if __name__ == "__main__":
    raise SystemExit(main())
