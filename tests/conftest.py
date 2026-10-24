"""Fixtures pytest communes."""

from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

LICENSE_KEY = "MINO-TEST-UNIT-0001"
INSTALLATION_ID = "inst-001"


@pytest.fixture
def license_env(monkeypatch, tmp_path):
    """Configure une base de licences isolée et une clé de test valide."""

    db_path = tmp_path / "license_db.json"
    keys = json.dumps(
        [
            {
                "key": LICENSE_KEY,
                "type": "trial",
                "max_machines": 3,
                "expires": "2099-12-31",
            }
        ]
    )
    monkeypatch.setenv("MINO_LICENSE_DB", str(db_path))
    monkeypatch.setenv("MINO_LICENSE_KEYS", keys)
    monkeypatch.setenv("MINO_IP_HASH_SALT", "test-salt")
    return {"db_path": db_path, "key": LICENSE_KEY}


@pytest.fixture
def app(license_env):
    from api.app import create_app

    return create_app(
        {
            "TESTING": True,
            "USE_LLM": False,
            "LOAD_LLM_ON_STARTUP": False,
        }
    )


@pytest.fixture
def client(app):
    return app.test_client()


@pytest.fixture
def auth_headers(client, license_env):
    response = client.post(
        "/license/activate",
        json={
            "license_key": license_env["key"],
            "installation_id": INSTALLATION_ID,
            "machine_name": "pytest",
        },
    )
    assert response.status_code == 200, response.get_json()
    return {
        "X-License-Key": license_env["key"],
        "X-Installation-Id": INSTALLATION_ID,
    }
