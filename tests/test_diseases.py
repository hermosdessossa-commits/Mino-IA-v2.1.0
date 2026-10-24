"""Tests du registre des maladies."""

from __future__ import annotations

import pytest

from core.diseases import (
    DISEASE_IDS,
    DISEASES,
    STATUS_VALUES,
    TRANSMISSION_LABELS,
    get_disease,
    normalize_disease_id,
)


def test_registry_contains_twelve_unique_diseases():
    assert len(DISEASES) == 12
    assert len(DISEASE_IDS) == 12
    assert len(set(DISEASE_IDS)) == 12
    assert all(disease.id in DISEASE_IDS for disease in DISEASES.values())


def test_transmission_labels_cover_all_diseases():
    for disease in DISEASES.values():
        assert disease.transmission in TRANSMISSION_LABELS


@pytest.mark.parametrize(
    ("raw", "expected"),
    [
        ("Hémophilie A", "hemophilie_A"),
        ("hemophilie_A", "hemophilie_A"),
        ("Hémophilie B", "hemophilie_B"),
        ("Drépanocytose", "drepanocytose"),
        ("drépanocytose", "drepanocytose"),
        ("NF1", "neurofibromatose1"),
        ("PKU", "phenylcetonurie"),
        ("PKD", "polykystose_renale"),
        ("maladie de Huntington", "huntington"),
        ("Thalassémie alpha", "thalassemie_alpha"),
        ("  mucoviscidose  ", "mucoviscidose"),
    ],
)
def test_normalize_disease_id(raw, expected):
    assert normalize_disease_id(raw) == expected


def test_normalize_rejects_unknown_disease():
    with pytest.raises(ValueError, match="Maladie non supportée"):
        normalize_disease_id("maladie_inventee")
    with pytest.raises(ValueError):
        normalize_disease_id("")


def test_get_disease_returns_canonical_object():
    disease = get_disease("Hémophilie A")
    assert disease.id == "hemophilie_A"
    assert disease.is_xlinked
    assert disease.name == "Hémophilie A"


def test_status_values_are_coherent():
    assert "malade" in STATUS_VALUES
    assert "inconnu" in STATUS_VALUES
    assert "risque" in STATUS_VALUES
