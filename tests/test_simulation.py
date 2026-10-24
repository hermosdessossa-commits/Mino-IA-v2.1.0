"""Tests de la simulation de trios."""

from __future__ import annotations

import random
from collections import Counter

import pytest

from core.diseases import DISEASE_IDS
from core.genetics import predict
from core.simulation import (
    POPULATIONS,
    apply_missingness,
    generate_evaluation,
    generate_trio,
    validate_population_data,
)


def test_population_data_is_valid():
    validate_population_data()
    assert len(POPULATIONS) == 6


@pytest.mark.parametrize("disease", DISEASE_IDS)
def test_generated_trios_are_always_parseable(disease):
    rng = random.Random(1234)
    population = POPULATIONS["Méditerranée"]
    statuses = Counter()
    for _ in range(200):
        trio = generate_trio(disease, population, rng, case_rate=0.35)
        prediction = predict(
            disease,
            trio["parent1"],
            trio["parent2"],
            trio["enfant"],
            trio["sexe_enfant"],
        )
        statuses[prediction.status] += 1
    assert statuses
    assert "inconnu" not in statuses


@pytest.mark.parametrize("disease", DISEASE_IDS)
def test_enrichment_produces_positive_cases(disease):
    rng = random.Random(99)
    population = POPULATIONS["Europe du Nord"]
    statuses = Counter()
    for _ in range(80):
        evaluation = generate_evaluation(disease, population, rng, case_rate=1.0, missing_rate=0.0)
        statuses[evaluation["prediction"].status] += 1
    positive = {
        "malade",
        "porteur",
        "porteuse",
        "porteur_im",
        "a_risque",
        "trait",
    }
    assert positive & set(statuses), statuses


def test_missingness_never_hides_everything():
    rng = random.Random(7)
    trio = {
        "parent1": "A/S",
        "parent2": "A/S",
        "enfant": "S/S",
        "sexe_enfant": "M",
    }
    for _ in range(200):
        observed = apply_missingness(trio, rng, missing_rate=1.0)
        assert any(observed[key] != "inconnu" for key in ("parent1", "parent2", "enfant"))


def test_alpha_simulation_never_creates_impossible_genotype():
    rng = random.Random(5)
    for _ in range(500):
        trio = generate_trio("thalassemie_alpha", POPULATIONS["Asie"], rng)
        for key in ("parent1", "parent2", "enfant"):
            assert trio[key].count("A") <= 4
            assert set(trio[key]) <= {"A", "-", "/"}
