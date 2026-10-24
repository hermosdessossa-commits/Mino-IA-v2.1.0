"""Tests de l'API Flask."""

from __future__ import annotations

import json

from tests.conftest import INSTALLATION_ID, LICENSE_KEY


class FakeEngine:
    available = True
    model_name = "fake-llm"

    def __init__(self, report: dict | None = None) -> None:
        self.report = report

    def generate_report(self, _prompt: str) -> dict | None:
        return self.report


def test_health_and_index(client):
    health = client.get("/health")
    assert health.status_code == 200
    payload = health.get_json()
    assert payload["status"] == "ok"
    assert payload["deterministic_engine"] == "ok"
    assert payload["version"] == "2.1.0"
    assert payload["llm_loaded"] is False
    assert payload["license_configured"] is True

    index = client.get("/")
    assert index.status_code == 200
    body = index.get_json()
    assert len(body["maladies_supportees"]) == 12
    assert "MINO-IA-TEST" not in json.dumps(body)


def test_predict_requires_license(client):
    response = client.post("/predict", json={"maladie": "drepanocytose"})
    assert response.status_code == 401
    assert response.get_json()["code"] == "license_required"


def test_activation_and_prediction(client, auth_headers):
    response = client.post(
        "/predict",
        json={
            "maladie": "drepanocytose",
            "genotype_parent1": "A/S",
            "genotype_parent2": "A/S",
            "genotype_enfant": "S/S",
        },
        headers=auth_headers,
    )
    assert response.status_code == 200
    payload = response.get_json()
    assert payload["probabilite"] == 1.0
    assert payload["statut"] == "malade"
    assert payload["methode"] == "genotype"
    assert payload["llm_used"] is False
    assert payload["model_used"] == "deterministic"
    assert "Drépanocytose" in payload["rapport"]
    assert payload["disclaimer"].startswith("AVERTISSEMENT MÉDICAL")
    assert response.headers["X-Request-Id"]
    assert response.headers["Cache-Control"] == "no-store"


def test_unknown_data_returns_null_not_zero(client, auth_headers):
    response = client.post(
        "/predict",
        json={"maladie": "drepanocytose"},
        headers=auth_headers,
    )
    assert response.status_code == 200
    payload = response.get_json()
    assert payload["probabilite"] is None
    assert payload["statut"] == "inconnu"
    assert payload["methode"] == "insufficient_data"
    assert "0.0 %" not in payload["rapport"]


def test_parental_risk_without_child_genotype(client, auth_headers):
    response = client.post(
        "/predict",
        json={
            "maladie": "drepanocytose",
            "genotype_parent1": "A/S",
            "genotype_parent2": "A/S",
        },
        headers=auth_headers,
    )
    assert response.status_code == 200
    payload = response.get_json()
    assert payload["probabilite"] == 0.25
    assert payload["statut"] == "risque"
    assert payload["distribution"]["S/S"] == 0.25


def test_hemophilia_a_is_accepted(client, auth_headers):
    response = client.post(
        "/predict",
        json={
            "maladie": "hemophilie_A",
            "genotype_parent1": "XY:sain",
            "genotype_parent2": "XX:porteuse",
            "sexe_enfant": "M",
        },
        headers=auth_headers,
    )
    assert response.status_code == 200
    payload = response.get_json()
    assert payload["maladie"] == "hemophilie_A"
    assert payload["probabilite"] == 0.5
    assert payload["details"]["risques_par_sexe"] == {"M": 0.5, "F": 0.0}


def test_hemophilia_a_without_sex_uses_unconditional_risk(client, auth_headers):
    response = client.post(
        "/predict",
        json={
            "maladie": "Hémophilie A",
            "genotype_parent1": "XY:sain",
            "genotype_parent2": "XX:porteuse",
        },
        headers=auth_headers,
    )
    assert response.status_code == 200
    assert response.get_json()["probabilite"] == 0.25


def test_invalid_requests(client, auth_headers):
    invalid_disease = client.post("/predict", json={"maladie": "cancer"}, headers=auth_headers)
    assert invalid_disease.status_code == 400
    assert invalid_disease.get_json()["code"] == "validation_error"

    invalid_genotype = client.post(
        "/predict",
        json={"maladie": "drepanocytose", "genotype_enfant": "A/X"},
        headers=auth_headers,
    )
    assert invalid_genotype.status_code == 422
    assert invalid_genotype.get_json()["code"] == "invalid_genotype"

    invalid_sex = client.post(
        "/predict",
        json={"maladie": "hemophilie_A", "sexe_enfant": "X"},
        headers=auth_headers,
    )
    assert invalid_sex.status_code == 400

    extra_field = client.post(
        "/predict",
        json={"maladie": "drepanocytose", "champ_inconnu": 1},
        headers=auth_headers,
    )
    assert extra_field.status_code == 400


def test_malformed_json_and_content_type(client):
    malformed = client.post(
        "/license/activate",
        data="{",
        content_type="application/json",
    )
    assert malformed.status_code == 400
    assert malformed.get_json()["code"] == "invalid_json"

    wrong_type = client.post("/license/activate", data="{}")
    assert wrong_type.status_code == 415


def test_batch_partial_errors(client, auth_headers):
    response = client.post(
        "/predict/batch",
        json={
            "predictions": [
                {
                    "maladie": "drepanocytose",
                    "genotype_parent1": "A/S",
                    "genotype_parent2": "A/S",
                    "genotype_enfant": "S/S",
                },
                {"maladie": "drepanocytose", "genotype_enfant": "A/X"},
            ]
        },
        headers=auth_headers,
    )
    assert response.status_code == 200
    payload = response.get_json()
    assert payload["count"] == 1
    assert len(payload["errors"]) == 1
    assert payload["errors"][0]["index"] == 1
    assert payload["errors"][0]["code"] == "invalid_genotype"


def test_batch_limit(client, auth_headers):
    predictions = [{"maladie": "drepanocytose"} for _ in range(51)]
    response = client.post(
        "/predict/batch", json={"predictions": predictions}, headers=auth_headers
    )
    assert response.status_code == 400


def test_license_status_and_deactivation(client, auth_headers):
    status = client.post(
        "/license/status",
        json={"license_key": LICENSE_KEY, "installation_id": INSTALLATION_ID},
    )
    assert status.status_code == 200
    assert status.get_json()["valid"] is True

    deactivated = client.post(
        "/license/deactivate",
        json={"license_key": LICENSE_KEY, "installation_id": INSTALLATION_ID},
    )
    assert deactivated.status_code == 200
    assert deactivated.get_json()["active"] is False

    denied = client.post(
        "/predict",
        json={"maladie": "drepanocytose"},
        headers=auth_headers,
    )
    assert denied.status_code == 403
    assert denied.get_json()["code"] == "license_invalid"


def test_machine_limit_via_api(client, license_env):
    for index in range(3):
        response = client.post(
            "/license/activate",
            json={
                "license_key": license_env["key"],
                "installation_id": f"machine-{index}",
            },
        )
        assert response.status_code == 200
    fourth = client.post(
        "/license/activate",
        json={"license_key": license_env["key"], "installation_id": "machine-4"},
    )
    assert fourth.status_code == 403
    assert fourth.get_json()["code"] == "machine_limit"


def test_expired_license_via_api(client, license_env, monkeypatch):
    monkeypatch.setenv(
        "MINO_LICENSE_KEYS",
        json.dumps(
            [
                {
                    "key": license_env["key"],
                    "type": "trial",
                    "max_machines": 1,
                    "expires": "2000-01-01",
                }
            ]
        ),
    )
    response = client.post(
        "/license/activate",
        json={"license_key": license_env["key"], "installation_id": "inst-001"},
    )
    assert response.status_code == 403
    assert response.get_json()["code"] == "expired"


def test_request_id_is_echoed_or_replaced(client):
    response = client.get("/health", headers={"X-Request-Id": "req-12345678"})
    assert response.headers["X-Request-Id"] == "req-12345678"
    response = client.get("/health", headers={"X-Request-Id": "x"})
    assert response.headers["X-Request-Id"] != "x"
    assert len(response.headers["X-Request-Id"]) == 32


def test_json_404_and_405(client, auth_headers):
    not_found = client.get("/inconnu")
    assert not_found.status_code == 404
    assert not_found.get_json()["code"] == "not_found"

    method = client.get("/predict", headers=auth_headers)
    assert method.status_code == 405
    assert method.get_json()["code"] == "method_not_allowed"


def test_llm_reformulation_keeps_deterministic_values(client, auth_headers):
    client.application.extensions["llm"] = FakeEngine(
        {"rapport": "Rapport rédigé par le LLM.", "recommandations": "Recos LLM."}
    )
    response = client.post(
        "/predict",
        json={
            "maladie": "drepanocytose",
            "genotype_parent1": "A/S",
            "genotype_parent2": "A/S",
            "genotype_enfant": "S/S",
        },
        headers=auth_headers,
    )
    assert response.status_code == 200
    payload = response.get_json()
    assert payload["llm_used"] is True
    assert payload["model_used"] == "fake-llm"
    assert payload["probabilite"] == 1.0
    assert payload["statut"] == "malade"
    assert payload["rapport"] == "Rapport rédigé par le LLM."


def test_llm_failure_falls_back_to_deterministic(client, auth_headers):
    client.application.extensions["llm"] = FakeEngine(None)
    response = client.post(
        "/predict",
        json={
            "maladie": "drepanocytose",
            "genotype_parent1": "A/S",
            "genotype_parent2": "A/S",
            "genotype_enfant": "S/S",
        },
        headers=auth_headers,
    )
    assert response.status_code == 200
    payload = response.get_json()
    assert payload["llm_used"] is False
    assert payload["model_used"] == "deterministic"
    assert "Drépanocytose" in payload["rapport"]
