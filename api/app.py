#!/usr/bin/env python3
"""API Flask de Mino-IA.

Le moteur mendélien déterministe calcule systématiquement le statut et la
probabilité. Le LLM est un composant optionnel de rédaction : s'il est absent,
échoue ou produit une sortie incohérente, l'API renvoie le compte rendu
déterministe sans dégrader le service.
"""

from __future__ import annotations

import argparse
import logging
import os
import re
import time
import uuid
from typing import Any

from flask import Flask, g, jsonify, request
from pydantic import ValidationError
from werkzeug.exceptions import HTTPException

from api.errors import ApiError
from api.license import (
    check_license,
    deactivate_license,
    get_license_status,
    license_keys_configured,
    validate_license,
)
from api.llm import DEFAULT_MODEL, LLMEngine
from api.schemas import (
    BatchItemError,
    BatchPredictRequest,
    BatchPredictResponse,
    ErrorResponse,
    HealthResponse,
    LicenseActivateRequest,
    LicenseDeactivateRequest,
    LicenseResponse,
    LicenseStatusRequest,
    PredictRequest,
    PredictResponse,
)
from core import __version__
from core.diseases import DISEASES, TRANSMISSION_LABELS
from core.genetics import GenotypeError, Prediction, predict
from core.prompts import build_user_prompt
from core.report import DISCLAIMER, build_recommendations, build_report

LOGGER = logging.getLogger(__name__)

PUBLIC_ENDPOINTS = {
    "index",
    "health",
    "license_activate",
    "license_deactivate",
    "license_status",
}
REQUEST_ID_PATTERN = re.compile(r"^[A-Za-z0-9._:-]{8,64}$")
API_VERSION = __version__

_LICENSE_STATUS_CODES = {
    "ok": 200,
    "invalid_request": 400,
    "invalid_key": 403,
    "expired": 403,
    "machine_limit": 403,
    "installation_conflict": 409,
    "not_found": 404,
    "not_configured": 503,
    "license_store_error": 503,
}


def _env_bool(name: str, default: bool = False) -> bool:
    value = os.environ.get(name)
    if value is None:
        return default
    return value.strip().lower() in {"1", "true", "yes", "on"}


def _request_id() -> str:
    candidate = (request.headers.get("X-Request-Id") or "").strip()
    if candidate and REQUEST_ID_PATTERN.match(candidate):
        return candidate
    return uuid.uuid4().hex


def _json_body() -> dict[str, Any]:
    if not request.is_json:
        raise ApiError(
            "Content-Type application/json requis.",
            status_code=415,
            code="unsupported_media_type",
        )
    try:
        data = request.get_json()
    except Exception as exc:
        raise ApiError(
            "Corps JSON invalide.",
            status_code=400,
            code="invalid_json",
        ) from exc
    if not isinstance(data, dict):
        raise ApiError(
            "Le corps de la requête doit être un objet JSON.",
            status_code=400,
            code="invalid_json",
        )
    return data


def _validate(model, data: dict[str, Any]):
    try:
        return model(**data)
    except ValidationError as exc:
        details = [
            {
                "loc": ".".join(str(part) for part in error.get("loc", ())),
                "msg": error.get("msg", "valeur invalide"),
                "type": error.get("type", "validation_error"),
            }
            for error in exc.errors()
        ]
        raise ApiError(
            "Requête invalide.",
            status_code=400,
            code="validation_error",
            details=details,
        ) from exc


def _predict_one(req: PredictRequest, engine: LLMEngine) -> dict[str, Any]:
    prediction: Prediction = predict(
        req.maladie,
        req.genotype_parent1,
        req.genotype_parent2,
        req.genotype_enfant,
        req.sexe_enfant,
    )
    report = build_report(
        prediction,
        parent1=req.genotype_parent1 or "inconnu",
        parent2=req.genotype_parent2 or "inconnu",
        enfant=req.genotype_enfant or "inconnu",
        sexe_enfant=req.sexe_enfant or "inconnu",
        meta={
            "origine": req.origine,
            "age_pere": req.age_pere,
            "age_mere": req.age_mere,
            "antecedents": req.antecedents_familiaux,
        },
    )
    recommendations = build_recommendations(req.maladie, prediction.status, prediction.probability)

    llm_used = False
    if engine.available:
        prompt = build_user_prompt(
            maladie=req.maladie,
            genotype_parent1=req.genotype_parent1 or "inconnu",
            genotype_parent2=req.genotype_parent2 or "inconnu",
            genotype_enfant=req.genotype_enfant or "inconnu",
            origine=req.origine,
            age_pere=req.age_pere,
            age_mere=req.age_mere,
            antecedents=req.antecedents_familiaux,
            sexe_enfant=req.sexe_enfant or "inconnu",
            prediction=prediction,
            draft_report=report,
            draft_recommendations=recommendations,
        )
        generated = engine.generate_report(prompt)
        if generated:
            report = generated["rapport"]
            recommendations = generated["recommandations"]
            llm_used = True

    details = dict(prediction.details)
    if prediction.message:
        details["message"] = prediction.message

    payload = {
        "maladie": prediction.disease,
        "probabilite": prediction.probability,
        "statut": prediction.status,
        "rapport": report,
        "recommandations": recommendations,
        "disclaimer": DISCLAIMER,
        "methode": prediction.method,
        "genotype_enfant": prediction.genotype_enfant,
        "distribution": prediction.risk_distribution,
        "details": details,
        "model_used": engine.model_name if llm_used else "deterministic",
        "llm_used": llm_used,
        "inference_time_s": 0.0,
        "request_id": g.request_id,
    }
    return PredictResponse(**payload).model_dump()


def _license_payload(result: dict[str, Any]) -> tuple[dict[str, Any], int]:
    status = _LICENSE_STATUS_CODES.get(result.get("code", ""), 400)
    return LicenseResponse(**result).model_dump(), status


def _register_routes(app: Flask) -> None:
    @app.route("/", methods=["GET"])
    def index():
        return jsonify(
            {
                "nom": "Mino-IA — API de conseil génétique",
                "version": API_VERSION,
                "description": (
                    "Moteur mendélien déterministe avec rédaction optionnelle par LLM. "
                    "Les probabilités sont calculées par core.genetics, jamais par le LLM."
                ),
                "endpoints": {
                    "GET /health": "État du service",
                    "GET /": "Documentation",
                    "POST /predict": "Prédiction (licence requise)",
                    "POST /predict/batch": "Prédiction en lot (licence requise)",
                    "POST /license/activate": "Activation d'une licence",
                    "POST /license/status": "Statut d'une licence",
                    "POST /license/deactivate": "Désactivation d'une installation",
                },
                "maladies_supportees": [
                    {
                        "id": disease.id,
                        "nom": disease.name,
                        "transmission": TRANSMISSION_LABELS[disease.transmission],
                    }
                    for disease in DISEASES.values()
                ],
                "disclaimer": DISCLAIMER,
            }
        )

    @app.route("/health", methods=["GET"])
    def health():
        engine: LLMEngine = app.extensions["llm"]
        llm_status = engine.status()
        llm_enabled = bool(llm_status["enabled"])
        llm_loaded = bool(llm_status["loaded"])
        overall = "ok" if not llm_enabled or llm_loaded else "degraded"
        payload = HealthResponse(
            status=overall,
            version=API_VERSION,
            deterministic_engine="ok",
            llm_enabled=llm_enabled,
            llm_loaded=llm_loaded,
            model_loaded=llm_loaded,
            model_name=str(llm_status["model_name"]),
            device=str(llm_status["device"]),
            environment=os.environ.get("MINO_ENV", "development"),
            license_configured=license_keys_configured(),
            llm_error=llm_status.get("error"),
        ).model_dump()
        return jsonify(payload)

    @app.route("/license/activate", methods=["POST"])
    def license_activate():
        req = _validate(LicenseActivateRequest, _json_body())
        result = validate_license(
            license_key=req.license_key,
            installation_id=req.installation_id,
            ip_address=request.remote_addr or "",
            machine_name=req.machine_name,
        )
        payload, status = _license_payload(result)
        return jsonify(payload), status

    @app.route("/license/deactivate", methods=["POST"])
    def license_deactivate():
        req = _validate(LicenseDeactivateRequest, _json_body())
        result = deactivate_license(req.license_key, req.installation_id)
        payload, status = _license_payload(result)
        return jsonify(payload), status

    @app.route("/license/status", methods=["POST"])
    def license_status():
        req = _validate(LicenseStatusRequest, _json_body())
        result = get_license_status(req.license_key, req.installation_id)
        payload, status = _license_payload(result)
        return jsonify(payload), status

    @app.route("/predict", methods=["POST"])
    def predict_route():
        req = _validate(PredictRequest, _json_body())
        engine: LLMEngine = app.extensions["llm"]
        started = time.perf_counter()
        try:
            payload = _predict_one(req, engine)
        except GenotypeError as exc:
            raise ApiError(str(exc), status_code=422, code="invalid_genotype") from exc
        except ValueError as exc:
            raise ApiError(str(exc), status_code=422, code="invalid_disease") from exc
        payload["inference_time_s"] = round(time.perf_counter() - started, 4)
        return jsonify(payload), 200

    @app.route("/predict/batch", methods=["POST"])
    def predict_batch():
        req = _validate(BatchPredictRequest, _json_body())
        engine: LLMEngine = app.extensions["llm"]
        results: list[dict[str, Any]] = []
        errors: list[dict[str, Any]] = []

        for index, item in enumerate(req.predictions):
            started = time.perf_counter()
            try:
                payload = _predict_one(item, engine)
            except GenotypeError as exc:
                errors.append(
                    BatchItemError(
                        index=index,
                        maladie=item.maladie,
                        error=str(exc),
                        code="invalid_genotype",
                    ).model_dump()
                )
                continue
            except ValueError as exc:
                errors.append(
                    BatchItemError(
                        index=index,
                        maladie=item.maladie,
                        error=str(exc),
                        code="invalid_disease",
                    ).model_dump()
                )
                continue
            payload["inference_time_s"] = round(time.perf_counter() - started, 4)
            results.append(payload)

        response = BatchPredictResponse(
            predictions=results,
            errors=errors,
            count=len(results),
            request_id=g.request_id,
        ).model_dump()
        return jsonify(response), 200


def _register_middleware(app: Flask) -> None:
    @app.before_request
    def verify_license():
        g.request_id = _request_id()
        g.request_start = time.perf_counter()

        if request.endpoint in PUBLIC_ENDPOINTS or request.endpoint in {None, "static"}:
            return None

        license_key = (request.headers.get("X-License-Key") or "").strip()
        installation_id = (request.headers.get("X-Installation-Id") or "").strip()
        if not license_key or not installation_id:
            raise ApiError(
                "Licence requise. Fournissez les en-têtes X-License-Key et X-Installation-Id.",
                status_code=401,
                code="license_required",
            )
        if not check_license(license_key, installation_id):
            raise ApiError(
                "Licence invalide, expirée ou installation non activée. "
                "Activez la licence via POST /license/activate.",
                status_code=403,
                code="license_invalid",
            )
        return None

    @app.after_request
    def finalize_response(response):
        request_id = g.get("request_id") or uuid.uuid4().hex
        response.headers["X-Request-Id"] = request_id
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["Cache-Control"] = "no-store"
        started = g.get("request_start")
        duration_ms = (time.perf_counter() - started) * 1000 if started else 0.0
        app.logger.info(
            "request id=%s method=%s path=%s status=%s duration_ms=%.1f",
            request_id,
            request.method,
            request.path,
            response.status_code,
            duration_ms,
        )
        return response


def _register_error_handlers(app: Flask) -> None:
    def _error_response(
        message: str, code: str, status_code: int, details: list[dict[str, Any]] | None = None
    ):
        payload = ErrorResponse(
            error=message,
            code=code,
            request_id=g.get("request_id") or uuid.uuid4().hex,
            details=details,
        ).model_dump()
        return jsonify(payload), status_code

    @app.errorhandler(ApiError)
    def handle_api_error(exc: ApiError):
        return _error_response(exc.message, exc.code, exc.status_code, exc.details)

    @app.errorhandler(404)
    def handle_not_found(_exc):
        return _error_response("Ressource introuvable.", "not_found", 404)

    @app.errorhandler(405)
    def handle_method_not_allowed(_exc):
        return _error_response("Méthode HTTP non autorisée.", "method_not_allowed", 405)

    @app.errorhandler(413)
    def handle_too_large(_exc):
        return _error_response("Corps de requête trop volumineux.", "payload_too_large", 413)

    @app.errorhandler(HTTPException)
    def handle_http_exception(exc: HTTPException):
        return _error_response(
            exc.description or "Erreur HTTP.",
            exc.name.lower().replace(" ", "_"),
            exc.code or 500,
        )

    @app.errorhandler(Exception)
    def handle_unexpected(exc: Exception):
        if app.config.get("TESTING"):
            raise exc
        app.logger.exception("unhandled_error request_id=%s", g.get("request_id") or "unknown")
        return _error_response(
            "Erreur interne du service.",
            "internal_error",
            500,
        )


def create_app(config: dict[str, Any] | None = None) -> Flask:
    """Fabrique d'application, utilisée par les tests et le serveur WSGI."""

    app = Flask(__name__)
    app.config.from_mapping(
        JSON_SORT_KEYS=False,
        MAX_CONTENT_LENGTH=1_000_000,
        PROPAGATE_EXCEPTIONS=False,
        USE_LLM=_env_bool("MINO_USE_LLM", False),
        MODEL_NAME=os.environ.get("MINO_MODEL", DEFAULT_MODEL),
        LOAD_IN_4BIT=_env_bool("MINO_LOAD_IN_4BIT", True),
        LOAD_LLM_ON_STARTUP=False,
    )
    if config:
        app.config.update(config)

    app.logger.setLevel(os.environ.get("MINO_LOG_LEVEL", "INFO").upper())
    engine = LLMEngine(
        model_name=str(app.config["MODEL_NAME"]),
        enabled=bool(app.config["USE_LLM"]),
        adapter_dir=app.config.get("ADAPTER_DIR"),
        load_in_4bit=bool(app.config["LOAD_IN_4BIT"]),
    )
    if app.config.get("LOAD_LLM_ON_STARTUP"):
        engine.load()
    app.extensions["llm"] = engine

    _register_middleware(app)
    _register_routes(app)
    _register_error_handlers(app)
    return app


app = create_app()


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="API Mino-IA")
    parser.add_argument("--host", default=os.environ.get("MINO_HOST", "127.0.0.1"))
    parser.add_argument("--port", type=int, default=int(os.environ.get("MINO_PORT", "5000")))
    parser.add_argument("--model", default=os.environ.get("MINO_MODEL", DEFAULT_MODEL))
    parser.add_argument(
        "--use-llm",
        action="store_true",
        default=_env_bool("MINO_USE_LLM", False),
        help="Active la rédaction par LLM (désactivée par défaut)",
    )
    parser.add_argument(
        "--no-4bit",
        action="store_true",
        help="Désactive la quantification 4 bits sur GPU",
    )
    parser.add_argument("--debug", action="store_true")
    parser.add_argument("--log-level", default=os.environ.get("MINO_LOG_LEVEL", "INFO"))
    args = parser.parse_args(argv)

    logging.basicConfig(
        level=getattr(logging, str(args.log_level).upper(), logging.INFO),
        format="%(asctime)s %(levelname)s %(name)s %(message)s",
    )

    application = create_app(
        {
            "USE_LLM": args.use_llm,
            "MODEL_NAME": args.model,
            "LOAD_IN_4BIT": not args.no_4bit,
            "LOAD_LLM_ON_STARTUP": args.use_llm,
        }
    )
    if not license_keys_configured():
        application.logger.warning(
            "Aucune clé de licence configurée. Définissez MINO_LICENSE_KEYS "
            "ou MINO_LICENSE_KEYS_FILE avant d'exposer l'API."
        )
    application.run(host=args.host, port=args.port, debug=args.debug)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
