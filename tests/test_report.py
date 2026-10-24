"""Tests des comptes rendus et recommandations."""

from __future__ import annotations

from core.genetics import predict
from core.report import DISCLAIMER, build_recommendations, build_report


def test_report_contains_disease_and_probability():
    prediction = predict("drepanocytose", "A/S", "A/S", "S/S")
    report = build_report(prediction, "A/S", "A/S", "S/S")
    assert "Drépanocytose" in report
    assert "100.0 %" in report
    assert "S/S" in report
    assert "confirmation" in report.lower()


def test_report_does_not_confuse_unknown_with_zero():
    prediction = predict("drepanocytose", "inconnu", "inconnu", "inconnu")
    report = build_report(prediction)
    assert "insuffisantes" in report.lower()
    assert "0.0 %" not in report


def test_report_for_carrier_and_reduced_penetrance():
    carrier = predict("drepanocytose", "A/S", "A/S", "A/S")
    carrier_report = build_report(carrier, "A/S", "A/S", "A/S")
    assert "porteur" in carrier_report.lower()
    assert "0 %" in carrier_report

    reduced = predict("huntington", "A/RP", "A/A", "A/RP")
    reduced_report = build_report(reduced, "A/RP", "A/A", "A/RP")
    assert "pénétrance réduite" in reduced_report
    assert "45.0 %" in reduced_report


def test_report_mentions_sex_when_known():
    prediction = predict("hemophilie_A", "XY:sain", "XX:porteuse", sexe_enfant="M")
    report = build_report(prediction, "XY:sain", "XX:porteuse", sexe_enfant="M")
    assert "Sexe de l'enfant : M" in report
    assert "50.0 %" in report


def test_recommendations_by_status():
    assert "hématologie" in build_recommendations("drepanocytose", "malade").lower()
    assert "dépistage du partenaire" in build_recommendations("drepanocytose", "porteur").lower()
    assert "insuffisantes" in build_recommendations("drepanocytose", "inconnu").lower()
    assert "conseil génétique" in build_recommendations("drepanocytose", "risque", 0.25).lower()
    assert "test génétique" in build_recommendations("drepanocytose", "risque", 0.0).lower()


def test_disclaimer_is_present_and_explicit():
    assert "AVERTISSEMENT MÉDICAL" in DISCLAIMER
    assert "ne remplace" in DISCLAIMER
