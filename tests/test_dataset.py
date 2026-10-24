"""Tests du format de dataset, du générateur et de la validation."""

from __future__ import annotations

import random

import pytest

from core.dataset import load_pairs, read_rows, summarize, validate_dataset, validate_rows
from scripts.generation_dataset import build_row, main


def _rows(count: int = 30, seed: int = 42) -> list[dict]:
    rng = random.Random(seed)
    return [build_row(rng, index, case_rate=0.5, missing_rate=0.1) for index in range(count)]


def test_build_row_is_valid():
    rows = _rows()
    assert validate_rows(rows) == []
    stats = summarize(rows)
    assert stats["rows"] == len(rows)
    assert stats["evaluations"] > len(rows)
    assert stats["probabilities"]["none"] >= 0


def test_rows_contain_all_disease_columns():
    row = _rows(1)[0]
    assert row["maladies_evaluees"]
    for disease in row["maladies_evaluees"].split("|"):
        assert row[f"{disease}_parent1"]
        assert row[f"{disease}_parent2"]
        assert row[f"{disease}_enfant"]
        assert row[f"{disease}_statut"]
        assert row[f"{disease}_methode"]


def test_generator_cli_writes_valid_files(tmp_path):
    exit_code = main(
        [
            "--samples",
            "48",
            "--seed",
            "3",
            "--output-dir",
            str(tmp_path),
            "--no-backup",
        ]
    )
    assert exit_code == 0
    train_path = tmp_path / "dataset_synthetique.csv"
    test_path = tmp_path / "dataset_test.csv"
    assert train_path.exists()
    assert test_path.exists()
    assert validate_dataset(train_path)["valid"]
    assert validate_dataset(test_path)["valid"]

    rows = read_rows(train_path)
    pairs = load_pairs(train_path)
    assert len(pairs) == summarize(rows)["evaluations"]


def test_validation_detects_inconsistent_status():
    rows = _rows(5)
    disease = rows[0]["maladies_evaluees"].split("|")[0]
    rows[0][f"{disease}_statut"] = "malade" if rows[0][f"{disease}_statut"] != "malade" else "sain"
    errors = validate_rows(rows)
    assert errors
    assert any("statut" in error for error in errors)


def test_validation_detects_broken_prompt_json():
    rows = _rows(3)
    rows[0]["prompt_entree"] = "[not json"
    errors = validate_rows(rows)
    assert errors


def test_load_pairs_rejects_incoherent_lengths(tmp_path):
    rows = _rows(2)
    rows[0]["prompt_sortie"] = "[]"
    from core.dataset import write_rows

    path = tmp_path / "broken.csv"
    write_rows(path, rows)
    with pytest.raises(ValueError):
        load_pairs(path)
