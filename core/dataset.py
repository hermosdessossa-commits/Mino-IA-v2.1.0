"""Lecture, écriture et validation du dataset synthétique.

Le dataset est un CSV contenant un trio par maladie évaluée, les colonnes de
vérité terrain et les paires prompt/cible utilisées pour l'entraînement. Ce
module centralise le format afin que le générateur, l'entraînement et les tests
restent alignés.
"""

from __future__ import annotations

import csv
import json
import os
import tempfile
from collections import Counter, defaultdict
from collections.abc import Iterable
from pathlib import Path

from core.diseases import DISEASE_IDS, STATUS_VALUES, normalize_disease_id
from core.genetics import GenotypeError, predict

__all__ = [
    "BASE_COLUMNS",
    "COLUMNS",
    "DISEASE_FIELDS",
    "DatasetError",
    "load_pairs",
    "read_rows",
    "summarize",
    "validate_dataset",
    "validate_rows",
    "write_rows",
]

DISEASE_FIELDS: tuple[str, ...] = (
    "parent1",
    "parent2",
    "enfant",
    "sexe_enfant",
    "statut",
    "proba",
    "methode",
)

BASE_COLUMNS: tuple[str, ...] = (
    "id",
    "origine",
    "age_pere",
    "age_mere",
    "antecedents_familiaux",
    "maladies_evaluees",
)

COLUMNS: tuple[str, ...] = (
    BASE_COLUMNS
    + tuple(f"{disease}_{field}" for disease in DISEASE_IDS for field in DISEASE_FIELDS)
    + ("prompt_entree", "prompt_sortie")
)


class DatasetError(ValueError):
    """Dataset absent, illisible ou incohérent."""


def read_rows(path: str | Path) -> list[dict[str, str]]:
    """Lit un CSV de dataset en conservant toutes les colonnes."""

    path = Path(path)
    if not path.exists():
        raise DatasetError(f"Dataset introuvable : {path}")
    with path.open("r", encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle)
        if reader.fieldnames is None:
            raise DatasetError(f"Dataset sans en-tête : {path}")
        return [dict(row) for row in reader]


def write_rows(
    path: str | Path,
    rows: Iterable[dict],
    fieldnames: Iterable[str] | None = None,
) -> None:
    """Écrit un CSV de façon atomique (fichier temporaire puis remplacement)."""

    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    columns = list(fieldnames or COLUMNS)
    temp_name = None
    try:
        with tempfile.NamedTemporaryFile(
            "w",
            encoding="utf-8",
            newline="",
            dir=path.parent,
            prefix=f".{path.name}.",
            suffix=".tmp",
            delete=False,
        ) as handle:
            temp_name = handle.name
            writer = csv.DictWriter(
                handle,
                fieldnames=columns,
                extrasaction="ignore",
                lineterminator="\n",
            )
            writer.writeheader()
            writer.writerows(rows)
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temp_name, path)
    finally:
        if temp_name and os.path.exists(temp_name):
            os.unlink(temp_name)


def _split_diseases(row: dict) -> list[str]:
    raw = (row.get("maladies_evaluees") or "").strip()
    if not raw:
        return []
    return [part.strip() for part in raw.split("|") if part.strip()]


def _parse_json_list(row: dict, key: str, row_id: str) -> list:
    raw = row.get(key)
    if not raw:
        raise DatasetError(f"{row_id} : colonne {key} vide.")
    try:
        value = json.loads(raw)
    except json.JSONDecodeError as exc:
        raise DatasetError(f"{row_id} : {key} n'est pas un JSON valide ({exc}).") from exc
    if not isinstance(value, list):
        raise DatasetError(f"{row_id} : {key} doit être une liste JSON.")
    return value


def load_pairs(path: str | Path) -> list[dict]:
    """Charge toutes les paires prompt/cible, une par maladie évaluée."""

    pairs: list[dict] = []
    for row in read_rows(path):
        row_id = row.get("id") or "?"
        diseases = _split_diseases(row)
        prompts = _parse_json_list(row, "prompt_entree", row_id)
        targets = _parse_json_list(row, "prompt_sortie", row_id)
        if len(diseases) != len(prompts) or len(prompts) != len(targets):
            raise DatasetError(
                f"{row_id} : incohérence entre maladies ({len(diseases)}), "
                f"prompts ({len(prompts)}) et cibles ({len(targets)})."
            )
        for disease, prompt, target in zip(diseases, prompts, targets, strict=True):
            if not isinstance(prompt, str) or not isinstance(target, str):
                raise DatasetError(f"{row_id} : prompt ou cible non textuel.")
            pairs.append(
                {
                    "id": row_id,
                    "maladie": disease,
                    "prompt": prompt,
                    "target": target,
                }
            )
    return pairs


def _parse_probability(value: object) -> float | None:
    if value is None:
        return None
    if isinstance(value, str):
        value = value.strip()
        if value == "":
            return None
    try:
        probability = float(value)
    except (TypeError, ValueError) as exc:
        raise DatasetError(f"Probabilité non numérique : {value!r}") from exc
    if not 0.0 <= probability <= 1.0:
        raise DatasetError(f"Probabilité hors de [0, 1] : {probability}")
    return probability


def validate_rows(rows: Iterable[dict[str, str]], check_predictions: bool = True) -> list[str]:
    """Valide la structure, les cibles et la cohérence avec le moteur.

    Retourne une liste d'erreurs lisibles ; une liste vide signifie que le
    dataset est valide.
    """

    errors: list[str] = []
    for index, row in enumerate(rows):
        row_id = row.get("id") or f"ligne_{index + 1}"
        diseases = _split_diseases(row)
        if not diseases:
            errors.append(f"{row_id} : aucune maladie évaluée.")
            continue
        try:
            prompts = _parse_json_list(row, "prompt_entree", row_id)
            targets = _parse_json_list(row, "prompt_sortie", row_id)
        except DatasetError as exc:
            errors.append(str(exc))
            continue
        if len(diseases) != len(prompts) or len(prompts) != len(targets):
            errors.append(
                f"{row_id} : incohérence maladies/prompts/cibles "
                f"({len(diseases)}/{len(prompts)}/{len(targets)})."
            )
            continue

        for position, disease_raw in enumerate(diseases):
            try:
                disease = normalize_disease_id(disease_raw)
            except ValueError as exc:
                errors.append(f"{row_id} : {exc}")
                continue

            target_raw = targets[position]
            try:
                target = json.loads(target_raw)
            except (json.JSONDecodeError, TypeError) as exc:
                errors.append(f"{row_id}/{disease} : cible JSON invalide ({exc}).")
                continue
            if not isinstance(target, dict):
                errors.append(f"{row_id}/{disease} : la cible doit être un objet JSON.")
                continue

            status = target.get("statut")
            if status not in STATUS_VALUES:
                errors.append(f"{row_id}/{disease} : statut inconnu {status!r}.")
            try:
                target_probability = _parse_probability(target.get("probabilite"))
            except DatasetError as exc:
                errors.append(f"{row_id}/{disease} : {exc}")
                continue
            if not target.get("rapport"):
                errors.append(f"{row_id}/{disease} : rapport vide.")
            if not target.get("recommandations"):
                errors.append(f"{row_id}/{disease} : recommandations vides.")
            if not target.get("disclaimer"):
                errors.append(f"{row_id}/{disease} : disclaimer vide.")

            column_status = row.get(f"{disease}_statut", "")
            if column_status and column_status != status:
                errors.append(
                    f"{row_id}/{disease} : statut CSV {column_status!r} != cible {status!r}."
                )
            try:
                column_probability = _parse_probability(row.get(f"{disease}_proba", ""))
            except DatasetError as exc:
                errors.append(f"{row_id}/{disease} : {exc}")
                continue
            if column_probability != target_probability:
                errors.append(
                    f"{row_id}/{disease} : probabilité CSV {column_probability} "
                    f"!= cible {target_probability}."
                )

            if not check_predictions:
                continue
            try:
                prediction = predict(
                    disease,
                    row.get(f"{disease}_parent1", "inconnu"),
                    row.get(f"{disease}_parent2", "inconnu"),
                    row.get(f"{disease}_enfant", "inconnu"),
                    row.get(f"{disease}_sexe_enfant", "inconnu"),
                )
            except (GenotypeError, ValueError) as exc:
                errors.append(f"{row_id}/{disease} : génotype invalide ({exc}).")
                continue
            if prediction.status != status:
                errors.append(
                    f"{row_id}/{disease} : statut recalculé {prediction.status!r} "
                    f"!= cible {status!r}."
                )
            if prediction.probability != target_probability:
                errors.append(
                    f"{row_id}/{disease} : probabilité recalculée "
                    f"{prediction.probability} != cible {target_probability}."
                )

    return errors


def summarize(rows: Iterable[dict[str, str]]) -> dict:
    """Calcule des statistiques de couverture et de positivité."""

    rows = list(rows)
    status_counts: Counter[str] = Counter()
    per_disease: dict[str, Counter[str]] = defaultdict(Counter)
    probabilities = {"none": 0, "zero": 0, "between": 0, "one": 0}
    evaluations = 0

    for row in rows:
        for disease in _split_diseases(row):
            evaluations += 1
            status = row.get(f"{disease}_statut", "") or "inconnu"
            status_counts[status] += 1
            per_disease[disease][status] += 1
            try:
                probability = _parse_probability(row.get(f"{disease}_proba", ""))
            except DatasetError:
                probability = None
            if probability is None:
                probabilities["none"] += 1
            elif probability == 0:
                probabilities["zero"] += 1
            elif probability == 1:
                probabilities["one"] += 1
            else:
                probabilities["between"] += 1

    return {
        "rows": len(rows),
        "evaluations": evaluations,
        "status": dict(status_counts),
        "probabilities": probabilities,
        "per_disease": {disease: dict(counts) for disease, counts in sorted(per_disease.items())},
    }


def validate_dataset(path: str | Path, check_predictions: bool = True) -> dict:
    """Valide un fichier et retourne un rapport structuré."""

    rows = read_rows(path)
    errors = validate_rows(rows, check_predictions=check_predictions)
    return {
        "path": str(path),
        "valid": not errors,
        "errors": errors,
        "stats": summarize(rows),
    }
