"""Gestion des licences de l'API.

Les clés ne sont jamais stockées en clair : seules leurs empreintes SHA-256
figurent en mémoire. La base d'installations est écrite de façon atomique et
protégée par un verrou inter-processus. Les adresses IP sont hachées et salées
avant stockage ; aucun géocodage externe n'est effectué.
"""

from __future__ import annotations

import hashlib
import ipaddress
import json
import os
import re
import tempfile
import threading
from collections.abc import Iterator
from contextlib import contextmanager
from datetime import date, datetime, timezone
from pathlib import Path
from typing import Any

try:  # pragma: no cover - dépend du système
    import fcntl
except ImportError:  # pragma: no cover - Windows
    fcntl = None  # type: ignore[assignment]

BASE_DIR = Path(__file__).resolve().parent.parent
DEFAULT_DB_PATH = BASE_DIR / "var" / "license_db.json"

ENV_KEYS = "MINO_LICENSE_KEYS"
ENV_KEYS_FILE = "MINO_LICENSE_KEYS_FILE"
ENV_DB = "MINO_LICENSE_DB"
ENV_IP_SALT = "MINO_IP_HASH_SALT"

_INSTALLATION_RE = re.compile(r"^[A-Za-z0-9._:-]{3,128}$")
_THREAD_LOCK = threading.Lock()
_MAX_LOGS = 2000


class LicenseError(RuntimeError):
    """Configuration ou base de licences invalide."""


def license_db_path() -> Path:
    raw = os.environ.get(ENV_DB)
    path = Path(raw).expanduser() if raw else DEFAULT_DB_PATH
    if not path.is_absolute():
        path = BASE_DIR / path
    return path


def _now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def _today() -> date:
    return datetime.now(timezone.utc).date()


def _result(valid: bool, code: str, message: str, **extra: Any) -> dict[str, Any]:
    result: dict[str, Any] = {
        "valid": valid,
        "code": code,
        "message": message,
        "installation_id": "",
        "machines_active": 0,
        "country": "",
        "type": "",
        "expires": None,
        "active": False,
    }
    result.update(extra)
    return result


def hash_ip(ip_address: str) -> str:
    """Hache l'IP avec un sel configurable, pour minimiser les données."""

    salt = os.environ.get(ENV_IP_SALT, "mino-ia")
    return hashlib.sha256(f"{salt}|{ip_address}".encode()).hexdigest()[:16]


def get_country_from_ip(ip_address: str) -> str:
    """Retourne un pays approximatif sans appel externe.

    Les adresses privées et de bouclage sont marquées « Local ». Les autres
    restent « Inconnu » tant qu'un service de géolocalisation n'est pas branché.
    """

    if not ip_address:
        return "Inconnu"
    try:
        address = ipaddress.ip_address(ip_address)
    except ValueError:
        return "Inconnu"
    if address.is_loopback or address.is_private or address.is_link_local:
        return "Local"
    return "Inconnu"


def _load_license_keys() -> dict[str, dict[str, Any]]:
    """Charge les clés depuis ``MINO_LICENSE_KEYS_FILE`` ou ``MINO_LICENSE_KEYS``."""

    raw = ""
    file_path = os.environ.get(ENV_KEYS_FILE)
    if file_path:
        path = Path(file_path).expanduser()
        try:
            raw = path.read_text(encoding="utf-8")
        except OSError as exc:
            raise LicenseError(f"Impossible de lire le fichier de licences : {path}") from exc
    else:
        raw = os.environ.get(ENV_KEYS, "")
    if not raw.strip():
        return {}

    try:
        payload = json.loads(raw)
    except json.JSONDecodeError as exc:
        raise LicenseError("La configuration des licences n'est pas un JSON valide.") from exc

    if isinstance(payload, dict) and isinstance(payload.get("keys"), list):
        payload = payload["keys"]

    entries: list[tuple[str, dict[str, Any]]] = []
    if isinstance(payload, list):
        for item in payload:
            if not isinstance(item, dict) or not isinstance(item.get("key"), str):
                raise LicenseError("Chaque licence doit être un objet avec une clé « key ».")
            entries.append((item["key"], item))
    elif isinstance(payload, dict):
        for key, item in payload.items():
            if not isinstance(key, str) or not isinstance(item, dict):
                raise LicenseError("Format de licences attendu : {clé: configuration}.")
            entries.append((key, item))
    else:
        raise LicenseError("Format de licences non supporté.")

    index: dict[str, dict[str, Any]] = {}
    for key, item in entries:
        key = key.strip()
        if len(key) < 8 or len(key) > 128:
            raise LicenseError("Une clé de licence doit contenir entre 8 et 128 caractères.")
        try:
            max_machines = int(item.get("max_machines", 1))
        except (TypeError, ValueError) as exc:
            raise LicenseError("max_machines invalide dans la configuration des licences.") from exc
        if max_machines < 1:
            raise LicenseError("max_machines doit être supérieur ou égal à 1.")
        expires = item.get("expires")
        if expires is not None:
            try:
                date.fromisoformat(str(expires))
            except ValueError as exc:
                raise LicenseError(f"Date d'expiration invalide : {expires!r}.") from exc
        digest = hashlib.sha256(key.encode("utf-8")).hexdigest()
        if digest in index:
            raise LicenseError("Deux clés de licence sont identiques.")
        index[digest] = {
            "type": str(item.get("type", "standard")),
            "max_machines": max_machines,
            "expires": str(expires) if expires is not None else None,
        }
    return index


def license_keys_configured() -> bool:
    try:
        return bool(_load_license_keys())
    except LicenseError:
        return False


def _is_expired(info: dict[str, Any]) -> bool:
    expires = info.get("expires")
    if not expires:
        return False
    return _today() > date.fromisoformat(str(expires))


def _load_db(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {"version": 1, "installations": {}, "logs": []}
    try:
        with path.open("r", encoding="utf-8") as handle:
            db = json.load(handle)
    except (OSError, json.JSONDecodeError) as exc:
        raise LicenseError(f"Base de licences illisible : {path}") from exc
    if not isinstance(db, dict) or not isinstance(db.get("installations", {}), dict):
        raise LicenseError("Structure de la base de licences invalide.")
    db.setdefault("version", 1)
    db.setdefault("installations", {})
    db.setdefault("logs", [])
    if not isinstance(db["logs"], list):
        db["logs"] = []
    # Migration : ne jamais conserver d'IP en clair.
    for entry in db["installations"].values():
        if isinstance(entry, dict) and "ip_address" in entry:
            entry.setdefault("ip_hash", hash_ip(str(entry.get("ip_address") or "")))
            entry.pop("ip_address", None)
    return db


def _save_db(path: Path, db: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temp_name = None
    try:
        with tempfile.NamedTemporaryFile(
            "w",
            encoding="utf-8",
            dir=path.parent,
            prefix=f".{path.name}.",
            suffix=".tmp",
            delete=False,
        ) as handle:
            temp_name = handle.name
            json.dump(db, handle, ensure_ascii=False, indent=2)
            handle.write("\n")
            handle.flush()
            os.fsync(handle.fileno())
        os.chmod(temp_name, 0o600)
        os.replace(temp_name, path)
        try:
            directory_fd = os.open(path.parent, os.O_RDONLY)
            try:
                os.fsync(directory_fd)
            finally:
                os.close(directory_fd)
        except OSError:
            pass
    finally:
        if temp_name and os.path.exists(temp_name):
            os.unlink(temp_name)


@contextmanager
def _locked_db() -> Iterator[tuple[dict[str, Any], dict[str, bool]]]:
    """Verrouille la base et ne l'écrit que si ``state['save']`` reste vrai."""

    path = license_db_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    lock_path = path.parent / f".{path.name}.lock"
    with _THREAD_LOCK:
        with lock_path.open("a+", encoding="utf-8") as lock_handle:
            if fcntl is not None:
                fcntl.flock(lock_handle.fileno(), fcntl.LOCK_EX)
            try:
                db = _load_db(path)
                state = {"save": True}
                try:
                    yield db, state
                except Exception:
                    raise
                else:
                    if state["save"]:
                        _save_db(path, db)
            finally:
                if fcntl is not None:
                    fcntl.flock(lock_handle.fileno(), fcntl.LOCK_UN)


def _append_log(db: dict[str, Any], action: str, **fields: Any) -> None:
    logs = db.setdefault("logs", [])
    logs.append({"timestamp": _now(), "action": action, **fields})
    if len(logs) > _MAX_LOGS:
        db["logs"] = logs[-_MAX_LOGS:]


def _active_for_key(installations: dict[str, Any], key_hash: str) -> int:
    return sum(
        1
        for entry in installations.values()
        if isinstance(entry, dict)
        and entry.get("license_key_hash") == key_hash
        and entry.get("active", False)
    )


def _validate_inputs(license_key: str, installation_id: str) -> str | None:
    if not isinstance(license_key, str) or not 8 <= len(license_key) <= 128:
        return "Clé de licence invalide."
    if not isinstance(installation_id, str) or not _INSTALLATION_RE.match(installation_id):
        return "Identifiant d'installation invalide (3 à 128 caractères alphanumériques, . _ : -)."
    return None


def validate_license(
    license_key: str,
    installation_id: str,
    ip_address: str = "",
    machine_name: str = "",
) -> dict[str, Any]:
    """Valide une clé et enregistre ou réactive une installation."""

    input_error = _validate_inputs(license_key, installation_id)
    if input_error:
        return _result(False, "invalid_request", input_error)

    try:
        keys = _load_license_keys()
    except LicenseError as exc:
        return _result(False, "not_configured", str(exc))
    if not keys:
        return _result(
            False,
            "not_configured",
            "Aucune clé de licence n'est configurée sur le serveur.",
        )

    key_hash = hashlib.sha256(license_key.encode("utf-8")).hexdigest()
    info = keys.get(key_hash)
    if info is None:
        return _result(False, "invalid_key", "Clé de licence invalide ou inconnue.")
    if _is_expired(info):
        return _result(
            False,
            "expired",
            f"Licence expirée le {info['expires']}.",
            type=info["type"],
            expires=info["expires"],
        )

    country = get_country_from_ip(ip_address)
    ip_hash = hash_ip(ip_address)
    machine_name = (machine_name or "").strip()[:120]

    try:
        with _locked_db() as (db, state):
            installations = db.setdefault("installations", {})
            existing = installations.get(installation_id)
            if existing is not None and existing.get("license_key_hash") != key_hash:
                state["save"] = False
                return _result(
                    False,
                    "installation_conflict",
                    "Cet identifiant d'installation est déjà associé à une autre licence.",
                    installation_id=installation_id,
                    country=country,
                )
            if (
                existing is None
                and _active_for_key(installations, key_hash) >= info["max_machines"]
            ):
                state["save"] = False
                return _result(
                    False,
                    "machine_limit",
                    f"Nombre maximum de machines atteint ({info['max_machines']}). "
                    "Désactivez une installation existante.",
                    installation_id=installation_id,
                    machines_active=_active_for_key(installations, key_hash),
                    country=country,
                    type=info["type"],
                    expires=info["expires"],
                )

            installations[installation_id] = {
                "license_key_hash": key_hash,
                "type": info["type"],
                "first_activation": (existing or {}).get("first_activation", _now()),
                "last_check": _now(),
                "country": country,
                "machine_name": machine_name,
                "ip_hash": ip_hash,
                "active": True,
            }
            _append_log(
                db,
                "activation",
                installation_id=installation_id,
                country=country,
                type=info["type"],
            )
            machines_active = _active_for_key(installations, key_hash)
    except LicenseError as exc:
        return _result(False, "license_store_error", str(exc))
    except OSError:
        return _result(False, "license_store_error", "La base de licences n'est pas accessible.")

    return _result(
        True,
        "ok",
        "Licence activée avec succès.",
        installation_id=installation_id,
        machines_active=machines_active,
        country=country,
        type=info["type"],
        expires=info["expires"],
        active=True,
    )


def check_license(license_key: str, installation_id: str) -> bool:
    """Vérification rapide utilisée par le middleware, sans écriture."""

    if _validate_inputs(license_key, installation_id):
        return False
    try:
        keys = _load_license_keys()
        info = keys.get(hashlib.sha256(license_key.encode("utf-8")).hexdigest())
        if info is None or _is_expired(info):
            return False
        db = _load_db(license_db_path())
    except LicenseError:
        return False
    entry = db.get("installations", {}).get(installation_id)
    if not isinstance(entry, dict) or not entry.get("active", False):
        return False
    return entry.get("license_key_hash") == hashlib.sha256(license_key.encode("utf-8")).hexdigest()


def deactivate_license(license_key: str, installation_id: str) -> dict[str, Any]:
    """Désactive une installation existante."""

    input_error = _validate_inputs(license_key, installation_id)
    if input_error:
        return _result(False, "invalid_request", input_error)
    try:
        keys = _load_license_keys()
    except LicenseError as exc:
        return _result(False, "not_configured", str(exc))
    key_hash = hashlib.sha256(license_key.encode("utf-8")).hexdigest()
    info = keys.get(key_hash)
    if info is None:
        return _result(False, "invalid_key", "Clé de licence invalide ou inconnue.")

    try:
        with _locked_db() as (db, state):
            installations = db.setdefault("installations", {})
            entry = installations.get(installation_id)
            if not isinstance(entry, dict):
                state["save"] = False
                return _result(False, "not_found", "Installation inconnue.")
            if entry.get("license_key_hash") != key_hash:
                state["save"] = False
                return _result(
                    False,
                    "installation_conflict",
                    "Cette installation n'est pas associée à cette licence.",
                )
            entry["active"] = False
            entry["last_check"] = _now()
            _append_log(
                db,
                "deactivation",
                installation_id=installation_id,
                country=entry.get("country", ""),
                type=entry.get("type", ""),
            )
            machines_active = _active_for_key(installations, key_hash)
    except LicenseError as exc:
        return _result(False, "license_store_error", str(exc))
    except OSError:
        return _result(False, "license_store_error", "La base de licences n'est pas accessible.")

    return _result(
        True,
        "ok",
        "Licence désactivée pour cette installation.",
        installation_id=installation_id,
        machines_active=machines_active,
        country=entry.get("country", ""),
        type=entry.get("type", info["type"]),
        expires=info["expires"],
        active=False,
    )


def get_license_status(license_key: str, installation_id: str) -> dict[str, Any]:
    """Retourne le statut d'une installation sans modifier la base."""

    input_error = _validate_inputs(license_key, installation_id)
    if input_error:
        return _result(False, "invalid_request", input_error)
    try:
        keys = _load_license_keys()
        info = keys.get(hashlib.sha256(license_key.encode("utf-8")).hexdigest())
        if info is None:
            return _result(False, "invalid_key", "Clé de licence invalide ou inconnue.")
        db = _load_db(license_db_path())
    except LicenseError as exc:
        return _result(False, "license_store_error", str(exc))

    key_hash = hashlib.sha256(license_key.encode("utf-8")).hexdigest()
    entry = db.get("installations", {}).get(installation_id)
    if not isinstance(entry, dict) or entry.get("license_key_hash") != key_hash:
        return _result(False, "not_found", "Installation inconnue pour cette licence.")

    expired = _is_expired(info)
    active = bool(entry.get("active", False)) and not expired
    if expired:
        code, message = "expired", f"Licence expirée le {info['expires']}."
    elif not entry.get("active", False):
        code, message = "inactive", "Licence désactivée pour cette installation."
    else:
        code, message = "ok", "Licence active."
    return _result(
        active,
        code,
        message,
        installation_id=installation_id,
        machines_active=_active_for_key(db.get("installations", {}), key_hash),
        country=entry.get("country", ""),
        type=info["type"],
        expires=info["expires"],
        active=bool(entry.get("active", False)),
    )
