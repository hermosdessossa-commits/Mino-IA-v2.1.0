"""Prompts uniques du projet.

Le moteur mendélien calcule les faits cliniques. Le LLM ne doit jamais les
recalculer : il reçoit ces faits et rédige uniquement le compte rendu et les
recommandations. Ce module est importé par l'API et par l'entraînement afin
d'éviter toute divergence entre les deux.
"""

from __future__ import annotations

import json
from typing import Any

from core.diseases import TRANSMISSION_LABELS, get_disease
from core.genetics import Prediction
from core.report import DISCLAIMER

__all__ = [
    "DISCLAIMER",
    "SYSTEM_PROMPT",
    "build_facts_block",
    "build_training_target",
    "build_user_prompt",
    "format_prompt",
    "format_prompt_for_llama",
    "format_prompt_for_mistral",
    "is_llama3_model",
    "parse_json_object",
]

SYSTEM_PROMPT = f"""Tu es un assistant de rédaction médicale intégré à un logiciel de conseil génétique destiné aux professionnels de santé.

RÈGLE ABSOLUE : un moteur mendélien déterministe a déjà calculé le statut, la probabilité et la méthode. Tu ne dois JAMAIS recalculer, modifier ou contredire ces valeurs. Ton rôle se limite à rédiger un compte rendu clinique et des recommandations à partir des faits fournis.

CONSIGNES DE RÉDACTION :
- Registre clinique, professionnel, sobre, au vouvoiement.
- Ne pas inventer d'antécédent, d'âge, de résultat de laboratoire ni de diagnostic.
- Si la probabilité est « non calculable », écrire explicitement que les données sont insuffisantes ; ne jamais la remplacer par 0 %.
- Distinguer clairement « porteur sain » et « atteint ».
- Ne jamais promettre un diagnostic : rappeler qu'une confirmation par un test certifié est nécessaire.
- Ne pas inclure de données identifiantes (nom, adresse, numéro de dossier).
- Inclure systématiquement le disclaimer médical obligatoire, mot pour mot.

FORMAT DE SORTIE (JSON strict, aucun texte avant ou après) :
{{
  "probabilite": <nombre entre 0.0 et 1.0, ou null>,
  "statut": "<statut fourni par le moteur>",
  "rapport": "<compte rendu clinique>",
  "recommandations": "<recommandations adaptées>",
  "disclaimer": "{DISCLAIMER}"
}}

Les champs "probabilite" et "statut" doivent être recopiés exactement depuis le bloc « Résultat déterministe ».
"""


def _pct(value: float | None) -> str:
    if value is None:
        return "non calculable (données insuffisantes)"
    return f"{value * 100:.1f} %"


def _format_distribution(distribution: dict[str, float]) -> str:
    if not distribution:
        return "non disponible"
    return " ; ".join(
        f"{label} : {_pct(probability)}" for label, probability in distribution.items()
    )


def build_facts_block(prediction: Prediction) -> str:
    """Bloc de faits déterministes transmis au LLM."""

    lines = [
        "Résultat déterministe (source de vérité, ne pas recalculer) :",
        f"- Statut : {prediction.status}",
        f"- Probabilité : {_pct(prediction.probability)}",
        f"- Méthode : {prediction.method}",
        f"- Génotype de l'enfant : {prediction.genotype_enfant or 'inconnu'}",
    ]
    if prediction.risk_distribution:
        lines.append(f"- Distribution : {_format_distribution(prediction.risk_distribution)}")
    if prediction.message:
        lines.append(f"- Message : {prediction.message}")
    return "\n".join(lines)


def build_user_prompt(
    maladie: str,
    genotype_parent1: str,
    genotype_parent2: str,
    genotype_enfant: str = "inconnu",
    origine: str = "",
    age_pere: int = 0,
    age_mere: int = 0,
    antecedents: str = "non",
    sexe_enfant: str = "inconnu",
    prediction: Prediction | None = None,
    draft_report: str = "",
    draft_recommendations: str = "",
) -> str:
    """Construit le prompt utilisateur.

    ``prediction`` est fournie par le moteur déterministe. Elle est incluse
    dans le prompt pour que le LLM rédige sans inventer de probabilité.
    """

    try:
        disease = get_disease(maladie)
        disease_label = f"{disease.name} ({disease.id})"
        transmission = TRANSMISSION_LABELS[disease.transmission]
    except ValueError:
        disease_label = maladie
        transmission = "non précisé"

    lines = [
        f"Maladie à évaluer : {disease_label}",
        f"Mode de transmission : {transmission}",
    ]
    if origine:
        lines.append(f"Origine géographique déclarée : {origine}")
    if age_pere:
        lines.append(f"Âge du père : {age_pere} ans")
    if age_mere:
        lines.append(f"Âge de la mère : {age_mere} ans")
    if antecedents and antecedents.lower() != "non":
        lines.append(f"Antécédents familiaux déclarés : {antecedents}")

    lines.extend(
        [
            f"Génotype du père : {genotype_parent1 or 'inconnu'}",
            f"Génotype de la mère : {genotype_parent2 or 'inconnu'}",
            f"Génotype de l'enfant : {genotype_enfant or 'inconnu'}",
            f"Sexe de l'enfant : {sexe_enfant or 'inconnu'}",
        ]
    )

    if prediction is not None:
        lines.extend(["", build_facts_block(prediction)])

    if draft_report:
        lines.extend(
            [
                "",
                "Compte rendu déterministe à reformuler sans en changer le sens :",
                draft_report,
            ]
        )
    if draft_recommendations:
        lines.extend(
            [
                "",
                "Recommandations déterministes à reformuler sans en changer le sens :",
                draft_recommendations,
            ]
        )

    lines.extend(
        [
            "",
            "Rédige le compte rendu et les recommandations en respectant strictement "
            "les faits ci-dessus. Réponds uniquement par un objet JSON valide.",
        ]
    )
    return "\n".join(lines)


def build_training_target(
    prediction: Prediction,
    report: str,
    recommendations: str,
) -> str:
    """Construit la cible JSON d'entraînement, cohérente avec le moteur."""

    payload: dict[str, Any] = {
        "probabilite": prediction.probability,
        "statut": prediction.status,
        "rapport": report,
        "recommandations": recommendations,
        "disclaimer": DISCLAIMER,
    }
    return json.dumps(payload, ensure_ascii=False, indent=2)


def format_prompt_for_mistral(user_prompt: str) -> str:
    """Formate le prompt pour Mistral Instruct."""

    return f"<s>[INST] {SYSTEM_PROMPT}\n\n{user_prompt} [/INST]"


def format_prompt_for_llama(user_prompt: str) -> str:
    """Formate le prompt pour Llama 3 Instruct."""

    return (
        "<|begin_of_text|><|start_header_id|>system<|end_header_id|>\n\n"
        f"{SYSTEM_PROMPT}<|eot_id|>"
        "<|start_header_id|>user<|end_header_id|>\n\n"
        f"{user_prompt}<|eot_id|>"
        "<|start_header_id|>assistant<|end_header_id|>\n\n"
    )


def is_llama3_model(model_name: str) -> bool:
    """Indique si le modèle utilise le template Llama 3.

    Les modèles Llama 1/2 et TinyLlama utilisent le template Mistral
    ``<s>[INST] ... [/INST]``. Seuls les modèles Llama 3+ attendent les jetons
    ``<|begin_of_text|>`` et ``<|eot_id|>``.
    """

    name = (model_name or "").lower()
    return any(marker in name for marker in ("llama-3", "llama3", "llama_3"))


def format_prompt(model_name: str, user_prompt: str) -> str:
    """Sélectionne le template de chat selon le modèle."""

    if is_llama3_model(model_name):
        return format_prompt_for_llama(user_prompt)
    return format_prompt_for_mistral(user_prompt)


def parse_json_object(text: str) -> dict[str, Any] | None:
    """Extrait le premier objet JSON d'une sortie de LLM.

    Tolère les blocs Markdown et le texte parasite autour de l'objet. Retourne
    ``None`` si aucun objet exploitable n'est trouvé.
    """

    if not text or not text.strip():
        return None
    cleaned = text.strip()
    if cleaned.startswith("```"):
        lines = cleaned.splitlines()
        if lines and lines[0].startswith("```"):
            lines = lines[1:]
        if lines and lines[-1].strip().startswith("```"):
            lines = lines[:-1]
        cleaned = "\n".join(lines).strip()

    start = cleaned.find("{")
    if start == -1:
        return None

    decoder = json.JSONDecoder()
    try:
        value, _ = decoder.raw_decode(cleaned[start:])
    except json.JSONDecodeError:
        end = cleaned.rfind("}")
        if end <= start:
            return None
        try:
            value = json.loads(cleaned[start : end + 1])
        except json.JSONDecodeError:
            return None

    return value if isinstance(value, dict) else None
