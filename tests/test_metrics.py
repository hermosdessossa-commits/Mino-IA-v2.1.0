"""Tests des métriques d'évaluation."""

from __future__ import annotations

import pytest

from core.metrics import (
    auroc,
    binary_classification_metrics,
    evaluate_records,
    mae,
    rmse,
)


def test_regression_metrics_ignore_none():
    assert mae([0.0, 0.5, None], [0.0, 0.0, 1.0]) == pytest.approx(0.25)
    assert rmse([0.0, 0.5], [0.0, 0.0]) == pytest.approx((0.125) ** 0.5)
    assert mae([], []) is None


def test_binary_classification_metrics():
    metrics = binary_classification_metrics([1, 1, 0, 0], [1, 0, 1, 0])
    assert metrics["tp"] == 1
    assert metrics["fn"] == 1
    assert metrics["fp"] == 1
    assert metrics["tn"] == 1
    assert metrics["accuracy"] == pytest.approx(0.5)
    assert metrics["sensitivity"] == pytest.approx(0.5)
    assert metrics["specificity"] == pytest.approx(0.5)


def test_auroc_with_ties():
    assert auroc([0, 1], [0.0, 1.0]) == pytest.approx(1.0)
    assert auroc([0, 1], [1.0, 0.0]) == pytest.approx(0.0)
    assert auroc([0, 1], [0.5, 0.5]) == pytest.approx(0.5)
    assert auroc([1, 1], [0.1, 0.2]) is None


def test_evaluate_records_handles_unknown_expected():
    records = [
        {
            "expected": {"probabilite": 0.25, "statut": "risque"},
            "predicted": {"probabilite": 0.2, "statut": "risque"},
        },
        {
            "expected": {"probabilite": None, "statut": "inconnu"},
            "predicted": {"probabilite": None, "statut": "inconnu"},
        },
        {
            "expected": {"probabilite": 1.0, "statut": "malade"},
            "predicted": {"probabilite": 1.0, "statut": "malade"},
        },
    ]
    result = evaluate_records(records)
    assert result["n_records"] == 3
    assert result["regression"]["n"] == 2
    assert result["classification"]["n"] == 2
    assert result["classification"]["accuracy"] == 1.0
    assert result["classification"]["parse_rate"] == 1.0
