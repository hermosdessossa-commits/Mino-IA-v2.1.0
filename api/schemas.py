"""Schémas Pydantic de l'API Mino-IA."""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel, ConfigDict, Field, field_validator

from core.diseases import normalize_disease_id
from core.genetics import GenotypeError, normalize_sex


class RequestModel(BaseModel):
    """Base des requêtes : champs inconnus refusés, espaces normalisés."""

    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)


class ResponseModel(BaseModel):
    """Base des réponses : tolérante aux champs additionnels."""

    model_config = ConfigDict(extra="ignore")


class PredictRequest(RequestModel):
    """Requête de prédiction génétique.

    ``genotype_enfant`` est optionnel : si les deux parents sont connus, le
    moteur calcule une distribution mendélienne. ``sexe_enfant`` est utile pour
    les maladies liées à l'X.
    """

    maladie: str = Field(..., min_length=1, max_length=64)
    genotype_parent1: str | None = Field(default="inconnu", max_length=80)
    genotype_parent2: str | None = Field(default="inconnu", max_length=80)
    genotype_enfant: str | None = Field(default="inconnu", max_length=80)
    sexe_enfant: str | None = Field(default="inconnu", max_length=20)
    origine: str = Field(default="", max_length=120)
    age_pere: int = Field(default=0, ge=0, le=120)
    age_mere: int = Field(default=0, ge=0, le=120)
    antecedents_familiaux: str = Field(default="non", max_length=500)

    @field_validator("maladie")
    @classmethod
    def valider_maladie(cls, value: str) -> str:
        try:
            return normalize_disease_id(value)
        except ValueError as exc:
            raise ValueError(str(exc)) from exc

    @field_validator(
        "genotype_parent1",
        "genotype_parent2",
        "genotype_enfant",
        mode="before",
    )
    @classmethod
    def valider_genotype(cls, value: object) -> str:
        if value is None:
            return "inconnu"
        if not isinstance(value, str):
            raise ValueError("Le génotype doit être une chaîne de caractères.")
        return value.strip() or "inconnu"

    @field_validator("sexe_enfant", mode="before")
    @classmethod
    def valider_sexe(cls, value: object) -> str:
        if value is None:
            return "inconnu"
        if not isinstance(value, str):
            raise ValueError("Le sexe doit être une chaîne de caractères.")
        try:
            sex = normalize_sex(value)
        except GenotypeError as exc:
            raise ValueError(str(exc)) from exc
        return sex or "inconnu"


class PredictResponse(ResponseModel):
    """Réponse de prédiction génétique."""

    maladie: str
    probabilite: float | None = Field(default=None, ge=0.0, le=1.0)
    statut: str
    rapport: str
    recommandations: str
    disclaimer: str
    methode: str
    genotype_enfant: str | None = None
    distribution: dict[str, float] = Field(default_factory=dict)
    details: dict[str, Any] = Field(default_factory=dict)
    model_used: str
    llm_used: bool = False
    inference_time_s: float = 0.0
    request_id: str


class BatchPredictRequest(RequestModel):
    """Requête de prédiction en lot, bornée pour protéger le service."""

    predictions: list[PredictRequest] = Field(..., min_length=1, max_length=50)


class BatchItemError(ResponseModel):
    """Erreur isolée dans une requête en lot."""

    index: int
    maladie: str = ""
    error: str
    code: str


class BatchPredictResponse(ResponseModel):
    """Réponse d'une prédiction en lot."""

    predictions: list[PredictResponse]
    errors: list[BatchItemError] = Field(default_factory=list)
    count: int
    request_id: str


class LicenseActivateRequest(RequestModel):
    """Requête d'activation de licence."""

    license_key: str = Field(..., min_length=8, max_length=128)
    installation_id: str = Field(
        ...,
        min_length=3,
        max_length=128,
        pattern=r"^[A-Za-z0-9._:-]+$",
    )
    machine_name: str = Field(default="", max_length=120)


class LicenseDeactivateRequest(RequestModel):
    """Requête de désactivation de licence."""

    license_key: str = Field(..., min_length=8, max_length=128)
    installation_id: str = Field(
        ...,
        min_length=3,
        max_length=128,
        pattern=r"^[A-Za-z0-9._:-]+$",
    )


class LicenseStatusRequest(LicenseDeactivateRequest):
    """Requête de consultation du statut de licence."""


class LicenseResponse(ResponseModel):
    """Réponse des endpoints de licence."""

    valid: bool
    message: str
    code: str
    installation_id: str = ""
    machines_active: int = 0
    country: str = ""
    type: str = ""
    expires: str | None = None
    active: bool = False


class HealthResponse(ResponseModel):
    """Réponse du health check."""

    status: str
    version: str
    deterministic_engine: str
    llm_enabled: bool
    llm_loaded: bool
    model_loaded: bool
    model_name: str
    device: str
    environment: str
    license_configured: bool
    llm_error: str | None = None


class ErrorResponse(ResponseModel):
    """Réponse d'erreur normalisée."""

    error: str
    code: str
    request_id: str
    details: list[dict[str, Any]] | None = None
