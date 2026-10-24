#!/usr/bin/env python3
"""Génère un dataset synthétique cohérent avec le moteur mendélien.

Le script tire des trios parent-enfant, applique un bruit de disponibilité des
génotypes, puis laisse ``core.genetics.predict`` calculer la vérité terrain.
Aucune probabilité n'est inventée : les colonnes, les prompts et les cibles JSON
sont toutes dérivées du moteur déterministe.

Usage :
    python scripts/generation_dataset.py
    python scripts/generation_dataset.py --samples 5000 --seed 42
    python scripts/generation_dataset.py --samples 200 --output-dir /tmp/mino
"""

from __future__ import annotations

import argparse
import json
import random
import shutil
import sys
from datetime import datetime
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from core.dataset import COLUMNS, DatasetError, summarize, validate_dataset, write_rows  # noqa: E402
from core.diseases import DISEASE_IDS, DISEASES  # noqa: E402
from core.prompts import build_training_target, build_user_prompt  # noqa: E402
from core.report import build_recommendations, build_report  # noqa: E402
from core.simulation import (  # noqa: E402
    choose_population,
    generate_evaluation,
    validate_population_data,
)

POSITIVE_STATUSES = {"malade", "porteur", "porteuse", "porteur_im", "a_risque", "trait"}


def _clamp(value: float, minimum: int, maximum: int) -> int:
    return int(max(minimum, min(maximum, round(value))))


def _has_family_history(evaluation: dict) -> bool:
    prediction = evaluation["prediction"]
    if prediction.status in POSITIVE_STATUSES:
        return True
    return prediction.probability is not None and prediction.probability > 0


def _choose_diseases(rng: random.Random, index: int) -> list[str]:
    """Garantit une couverture régulière de toutes les maladies."""

    primary = DISEASE_IDS[index % len(DISEASE_IDS)]
    others = [disease for disease in DISEASE_IDS if disease != primary]
    extra_count = rng.randint(0, 3)
    return [primary, *rng.sample(others, extra_count)]


def build_row(
    rng: random.Random,
    index: int,
    case_rate: float,
    missing_rate: float,
) -> dict:
    """Construit une ligne complète du dataset."""

    population = choose_population(rng)
    age_pere = _clamp(rng.gauss(34, 6), 18, 55)
    age_mere = _clamp(rng.gauss(31, 6), 18, 50)
    diseases = _choose_diseases(rng, index)

    evaluations: dict[str, dict] = {}
    for disease in diseases:
        evaluations[disease] = generate_evaluation(
            disease,
            population,
            rng,
            case_rate=case_rate,
            missing_rate=missing_rate,
        )

    antecedents = "non"
    candidates = [disease for disease in diseases if _has_family_history(evaluations[disease])]
    if candidates and rng.random() < 0.85:
        disease = rng.choice(candidates)
        antecedents = f"oui ({DISEASES[disease].name})"

    meta = {
        "origine": population.name,
        "age_pere": age_pere,
        "age_mere": age_mere,
        "antecedents": antecedents,
    }

    row: dict[str, object] = {
        "id": f"sample_{index:05d}",
        "origine": population.name,
        "age_pere": age_pere,
        "age_mere": age_mere,
        "antecedents_familiaux": antecedents,
    }

    prompts: list[str] = []
    targets: list[str] = []

    for disease in DISEASE_IDS:
        if disease not in evaluations:
            for field in (
                "parent1",
                "parent2",
                "enfant",
                "sexe_enfant",
                "statut",
                "proba",
                "methode",
            ):
                row[f"{disease}_{field}"] = ""
            continue

        evaluation = evaluations[disease]
        genotypes = evaluation["genotypes"]
        prediction = evaluation["prediction"]

        report = build_report(
            prediction,
            parent1=genotypes["parent1"],
            parent2=genotypes["parent2"],
            enfant=genotypes["enfant"],
            sexe_enfant=genotypes["sexe_enfant"],
            meta=meta,
        )
        recommendations = build_recommendations(disease, prediction.status, prediction.probability)
        prompt = build_user_prompt(
            maladie=disease,
            genotype_parent1=genotypes["parent1"],
            genotype_parent2=genotypes["parent2"],
            genotype_enfant=genotypes["enfant"],
            origine=population.name,
            age_pere=age_pere,
            age_mere=age_mere,
            antecedents=antecedents,
            sexe_enfant=genotypes["sexe_enfant"],
            prediction=prediction,
            draft_report=report,
            draft_recommendations=recommendations,
        )
        target = build_training_target(prediction, report, recommendations)

        row[f"{disease}_parent1"] = genotypes["parent1"]
        row[f"{disease}_parent2"] = genotypes["parent2"]
        row[f"{disease}_enfant"] = genotypes["enfant"]
        row[f"{disease}_sexe_enfant"] = genotypes["sexe_enfant"]
        row[f"{disease}_statut"] = prediction.status
        row[f"{disease}_proba"] = "" if prediction.probability is None else prediction.probability
        row[f"{disease}_methode"] = prediction.method
        prompts.append(prompt)
        targets.append(target)

    evaluated_order = [disease for disease in DISEASE_IDS if disease in evaluations]
    row["maladies_evaluees"] = "|".join(evaluated_order)
    row["prompt_entree"] = json.dumps(prompts, ensure_ascii=False)
    row["prompt_sortie"] = json.dumps(targets, ensure_ascii=False)
    return row


def _backup(path: Path) -> Path | None:
    if not path.exists():
        return None
    backup_dir = path.parent / "backups"
    backup_dir.mkdir(parents=True, exist_ok=True)
    stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    destination = backup_dir / f"{path.stem}_{stamp}{path.suffix}"
    shutil.copy2(path, destination)
    return destination


def _print_stats(stats: dict) -> None:
    print("\n=== Statistiques ===")
    print(f"  Lignes            : {stats['rows']}")
    print(f"  Évaluations       : {stats['evaluations']}")
    print(f"  Statuts           : {stats['status']}")
    print(f"  Probabilités      : {stats['probabilities']}")
    print("\n  Positivité par maladie :")
    for disease, counts in stats["per_disease"].items():
        positives = (
            counts.get("malade", 0)
            + counts.get("porteur", 0)
            + counts.get("porteuse", 0)
            + counts.get("porteur_im", 0)
            + counts.get("a_risque", 0)
            + counts.get("trait", 0)
        )
        print(f"    {disease:24s} {counts}  (porteurs/atteints: {positives})")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Génère le dataset synthétique Mino-IA")
    parser.add_argument("--samples", type=int, default=5000, help="Nombre d'échantillons")
    parser.add_argument("--seed", type=int, default=42, help="Graine aléatoire")
    parser.add_argument("--test-ratio", type=float, default=0.20, help="Proportion du jeu de test")
    parser.add_argument(
        "--case-rate", type=float, default=0.35, help="Taux d'enrichissement en cas positifs"
    )
    parser.add_argument(
        "--missing-rate", type=float, default=0.15, help="Taux de génotypes manquants"
    )
    parser.add_argument("--output-dir", type=Path, default=BASE_DIR / "data")
    parser.add_argument(
        "--no-backup", action="store_true", help="Ne pas sauvegarder les anciens CSV"
    )
    parser.add_argument(
        "--strict", action="store_true", help="Échec si la validation signale une erreur"
    )
    args = parser.parse_args(argv)

    if args.samples < 12:
        parser.error("--samples doit être supérieur ou égal à 12.")
    if not 0 <= args.test_ratio < 0.5:
        parser.error("--test-ratio doit être compris entre 0 et 0,5.")
    if not 0 <= args.case_rate <= 1:
        parser.error("--case-rate doit être compris entre 0 et 1.")
    if not 0 <= args.missing_rate <= 0.9:
        parser.error("--missing-rate doit être compris entre 0 et 0,9.")

    validate_population_data()

    output_dir = args.output_dir
    output_dir.mkdir(parents=True, exist_ok=True)
    train_path = output_dir / "dataset_synthetique.csv"
    test_path = output_dir / "dataset_test.csv"

    if not args.no_backup:
        for path in (train_path, test_path):
            backup = _backup(path)
            if backup:
                print(f"Sauvegarde : {path} -> {backup}")

    rng = random.Random(args.seed)
    print(f"Génération de {args.samples} échantillons (seed={args.seed})...")
    rows = []
    for index in range(args.samples):
        rows.append(build_row(rng, index, args.case_rate, args.missing_rate))
        if (index + 1) % 500 == 0:
            print(f"  {index + 1}/{args.samples} générés")

    split_rng = random.Random(args.seed ^ 0x5EED)
    split_rng.shuffle(rows)
    n_test = int(args.samples * args.test_ratio)
    test_rows = rows[:n_test]
    train_rows = rows[n_test:]

    write_rows(train_path, train_rows, COLUMNS)
    write_rows(test_path, test_rows, COLUMNS)
    print(f"\nTrain : {len(train_rows)} échantillons -> {train_path}")
    print(f"Test  : {len(test_rows)} échantillons -> {test_path}")

    patients_path = output_dir / "patients_reels.json"
    if not patients_path.exists():
        patients_path.write_text(
            json.dumps(
                {
                    "description": "Base de données patients réels, à remplir par le médecin.",
                    "patients": [],
                },
                ensure_ascii=False,
                indent=2,
            )
            + "\n",
            encoding="utf-8",
        )
        print(f"Base patients vierge -> {patients_path}")

    _print_stats(summarize(train_rows + test_rows))

    all_errors: list[str] = []
    for path in (train_path, test_path):
        try:
            report = validate_dataset(path)
        except DatasetError as exc:
            all_errors.append(f"{path.name}: {exc}")
            print(f"Validation {path.name} : ERREURS")
            continue
        all_errors.extend(f"{path.name}: {error}" for error in report["errors"])
        print(f"Validation {path.name} : {'OK' if report['valid'] else 'ERREURS'}")

    if all_errors:
        print("\n=== Erreurs de validation ===")
        for error in all_errors[:50]:
            print(f"  - {error}")
        if len(all_errors) > 50:
            print(f"  ... et {len(all_errors) - 50} autres.")
        if args.strict:
            return 1

    zero_positive = [
        disease
        for disease, counts in summarize(train_rows + test_rows)["per_disease"].items()
        if not any(
            counts.get(status, 0)
            for status in ("malade", "porteur", "porteuse", "porteur_im", "a_risque", "trait")
        )
    ]
    if zero_positive:
        print(f"\nAttention : aucune évaluation positive pour {', '.join(zero_positive)}.")
        print("Augmentez --samples ou --case-rate si ces maladies doivent être couvertes.")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
