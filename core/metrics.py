"""Métriques d'évaluation réutilisables (sans dépendance ML)."""

from __future__ import annotations

from collections.abc import Iterable

__all__ = [
    "auroc",
    "binary_classification_metrics",
    "evaluate_records",
    "mae",
    "regression_metrics",
    "rmse",
]


def _clean_pairs(y_true: Iterable[float | None], y_pred: Iterable[float | None]):
    true_values = list(y_true)
    pred_values = list(y_pred)
    if len(true_values) != len(pred_values):
        raise ValueError("y_true et y_pred doivent avoir la même longueur.")
    pairs = [
        (float(true), float(pred))
        for true, pred in zip(true_values, pred_values, strict=True)
        if true is not None and pred is not None
    ]
    return pairs


def mae(y_true: Iterable[float | None], y_pred: Iterable[float | None]) -> float | None:
    pairs = _clean_pairs(y_true, y_pred)
    if not pairs:
        return None
    return sum(abs(true - pred) for true, pred in pairs) / len(pairs)


def rmse(y_true: Iterable[float | None], y_pred: Iterable[float | None]) -> float | None:
    pairs = _clean_pairs(y_true, y_pred)
    if not pairs:
        return None
    return (sum((true - pred) ** 2 for true, pred in pairs) / len(pairs)) ** 0.5


def regression_metrics(
    y_true: Iterable[float | None], y_pred: Iterable[float | None]
) -> dict[str, float | int | None]:
    pairs = _clean_pairs(y_true, y_pred)
    if not pairs:
        return {"n": 0, "mae": None, "rmse": None}
    return {
        "n": len(pairs),
        "mae": mae([p[0] for p in pairs], [p[1] for p in pairs]),
        "rmse": rmse([p[0] for p in pairs], [p[1] for p in pairs]),
    }


def binary_classification_metrics(
    y_true: Iterable[int], y_pred: Iterable[int]
) -> dict[str, float | int | None]:
    """Métriques binaires classiques.

    ``y_true`` et ``y_pred`` ne doivent contenir que des 0/1. Les listes vides
    retournent des métriques à ``None`` plutôt que des divisions par zéro.
    """

    true = [int(value) for value in y_true]
    pred = [int(value) for value in y_pred]
    if len(true) != len(pred):
        raise ValueError("y_true et y_pred doivent avoir la même longueur.")
    n = len(true)
    if n == 0:
        return {
            "n": 0,
            "tp": 0,
            "tn": 0,
            "fp": 0,
            "fn": 0,
            "accuracy": None,
            "sensitivity": None,
            "specificity": None,
            "precision": None,
            "f1": None,
        }

    tp = sum(1 for t, p in zip(true, pred, strict=True) if t == 1 and p == 1)
    tn = sum(1 for t, p in zip(true, pred, strict=True) if t == 0 and p == 0)
    fp = sum(1 for t, p in zip(true, pred, strict=True) if t == 0 and p == 1)
    fn = sum(1 for t, p in zip(true, pred, strict=True) if t == 1 and p == 0)

    accuracy = (tp + tn) / n
    sensitivity = tp / (tp + fn) if (tp + fn) else None
    specificity = tn / (tn + fp) if (tn + fp) else None
    precision = tp / (tp + fp) if (tp + fp) else None
    f1 = (
        2 * precision * sensitivity / (precision + sensitivity)
        if precision is not None and sensitivity is not None and (precision + sensitivity) > 0
        else None
    )
    return {
        "n": n,
        "tp": tp,
        "tn": tn,
        "fp": fp,
        "fn": fn,
        "accuracy": accuracy,
        "sensitivity": sensitivity,
        "specificity": specificity,
        "precision": precision,
        "f1": f1,
    }


def auroc(y_true: Iterable[int], y_score: Iterable[float]) -> float | None:
    """Aire sous la courbe ROC, avec gestion des ex æquo.

    Retourne ``None`` si une seule classe est présente.
    """

    true_values = list(y_true)
    score_values = list(y_score)
    if len(true_values) != len(score_values):
        raise ValueError("y_true et y_score doivent avoir la même longueur.")
    pairs = [
        (int(label), float(score)) for label, score in zip(true_values, score_values, strict=True)
    ]
    positives = [score for label, score in pairs if label == 1]
    negatives = [score for label, score in pairs if label == 0]
    if not positives or not negatives:
        return None

    wins = 0.0
    for positive in positives:
        for negative in negatives:
            if positive > negative:
                wins += 1.0
            elif positive == negative:
                wins += 0.5
    return wins / (len(positives) * len(negatives))


def _is_positive(probability: float | None, status: str | None) -> int | None:
    if probability is None:
        if status == "inconnu" or status is None:
            return None
        return 1 if status == "malade" else 0
    return 1 if probability >= 0.5 else 0


def evaluate_records(records: Iterable[dict]) -> dict:
    """Évalue des couples ``expected`` / ``predicted``.

    Chaque enregistrement contient deux dictionnaires avec au moins
    ``probabilite`` et ``statut``. Les valeurs ``None`` sont ignorées pour la
    régression ; les statuts inconnus sont ignorés pour la classification.
    """

    expected_probs: list[float | None] = []
    predicted_probs: list[float | None] = []
    true_labels: list[int] = []
    pred_labels: list[int] = []
    auc_labels: list[int] = []
    auc_scores: list[float] = []
    n_records = 0
    n_parsed = 0

    for record in records:
        n_records += 1
        expected = record.get("expected") or {}
        predicted = record.get("predicted") or {}
        if predicted:
            n_parsed += 1

        expected_prob = expected.get("probabilite")
        predicted_prob = predicted.get("probabilite")
        expected_status = expected.get("statut")
        predicted_status = predicted.get("statut")

        expected_probs.append(expected_prob)
        predicted_probs.append(predicted_prob)

        true_label = _is_positive(expected_prob, expected_status)
        pred_label = _is_positive(predicted_prob, predicted_status)
        if true_label is not None and pred_label is not None:
            true_labels.append(true_label)
            pred_labels.append(pred_label)
        if true_label is not None and predicted_prob is not None:
            auc_labels.append(true_label)
            auc_scores.append(float(predicted_prob))

    regression = regression_metrics(expected_probs, predicted_probs)
    classification = binary_classification_metrics(true_labels, pred_labels)
    classification["auroc"] = auroc(auc_labels, auc_scores)
    classification["parse_rate"] = n_parsed / n_records if n_records else None
    return {
        "n_records": n_records,
        "regression": regression,
        "classification": classification,
    }
