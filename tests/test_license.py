"""Tests du stockage et de la logique de licence."""

from __future__ import annotations

import json
import stat

from api.license import (
    check_license,
    deactivate_license,
    get_license_status,
    license_keys_configured,
    validate_license,
)


def test_activation_persists_and_checks(license_env):
    result = validate_license(license_env["key"], "inst-001", "127.0.0.1", "poste")
    assert result["valid"] is True
    assert result["machines_active"] == 1
    assert check_license(license_env["key"], "inst-001") is True
    assert license_env["db_path"].exists()

    db = json.loads(license_env["db_path"].read_text(encoding="utf-8"))
    entry = db["installations"]["inst-001"]
    assert entry["active"] is True
    assert entry["machine_name"] == "poste"
    assert "ip_address" not in entry
    assert len(entry["ip_hash"]) == 16
    assert stat.S_IMODE(license_env["db_path"].stat().st_mode) == 0o600


def test_machine_limit(license_env):
    for index in range(3):
        assert validate_license(license_env["key"], f"inst-{index}")["valid"] is True
    fourth = validate_license(license_env["key"], "inst-4")
    assert fourth["valid"] is False
    assert fourth["code"] == "machine_limit"
    assert fourth["machines_active"] == 3


def test_deactivation_and_reactivation(license_env):
    assert validate_license(license_env["key"], "inst-001")["valid"]
    deactivated = deactivate_license(license_env["key"], "inst-001")
    assert deactivated["valid"] is True
    assert deactivated["active"] is False
    assert check_license(license_env["key"], "inst-001") is False

    status = get_license_status(license_env["key"], "inst-001")
    assert status["valid"] is False
    assert status["code"] == "inactive"

    assert validate_license(license_env["key"], "inst-001")["valid"]
    assert check_license(license_env["key"], "inst-001") is True


def test_expired_license_is_rejected(license_env, monkeypatch):
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
    result = validate_license(license_env["key"], "inst-001")
    assert result["valid"] is False
    assert result["code"] == "expired"
    assert check_license(license_env["key"], "inst-001") is False


def test_invalid_key_and_input(license_env):
    assert validate_license("CLE-INVALIDE-0000", "inst-001")["code"] == "invalid_key"
    assert validate_license(license_env["key"], "x")["code"] == "invalid_request"
    assert validate_license("", "inst-001")["code"] == "invalid_request"


def test_installation_conflict(license_env, monkeypatch):
    assert validate_license(license_env["key"], "inst-001")["valid"]
    monkeypatch.setenv(
        "MINO_LICENSE_KEYS",
        json.dumps(
            [
                {
                    "key": license_env["key"],
                    "type": "trial",
                    "max_machines": 3,
                    "expires": "2099-12-31",
                },
                {
                    "key": "MINO-AUTRE-CLE-0002",
                    "type": "standard",
                    "max_machines": 1,
                    "expires": "2099-12-31",
                },
            ]
        ),
    )
    result = validate_license("MINO-AUTRE-CLE-0002", "inst-001")
    assert result["valid"] is False
    assert result["code"] == "installation_conflict"


def test_status_ok_and_not_found(license_env):
    assert validate_license(license_env["key"], "inst-001")["valid"]
    status = get_license_status(license_env["key"], "inst-001")
    assert status["valid"] is True
    assert status["code"] == "ok"
    assert status["active"] is True
    assert get_license_status(license_env["key"], "inst-404")["code"] == "not_found"


def test_no_keys_configured(license_env, monkeypatch):
    monkeypatch.delenv("MINO_LICENSE_KEYS", raising=False)
    monkeypatch.delenv("MINO_LICENSE_KEYS_FILE", raising=False)
    assert license_keys_configured() is False
    result = validate_license(license_env["key"], "inst-001")
    assert result["valid"] is False
    assert result["code"] == "not_configured"
