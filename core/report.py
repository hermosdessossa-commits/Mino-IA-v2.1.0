"""Rédaction des comptes rendus et des recommandations.

Le texte est déterministe et vérifiable. Il peut ensuite être reformulé par un
LLM, mais les valeurs cliniques (statut, probabilité) ne doivent jamais être
modifiées par le modèle.
"""

from __future__ import annotations

from core.diseases import TRANSMISSION_LABELS, get_disease
from core.genetics import Prediction

DISCLAIMER = (
    "AVERTISSEMENT MÉDICAL : Cette estimation est une aide à la décision fondée sur "
    "les informations génétiques fournies et sur les lois de Mendel. Elle ne remplace "
    "en aucun cas un conseil génétique professionnel ni un test de laboratoire certifié. "
    "Toute décision médicale doit être confirmée par un médecin généticien ou un "
    "conseiller en génétique."
)

_STATUS_LABELS = {
    "sain": "sain",
    "saine": "saine",
    "porteur": "porteur sain",
    "porteuse": "porteuse saine",
    "porteur_im": "porteur d'un allèle intermédiaire",
    "a_risque": "porteur d'un allèle à pénétrance réduite",
    "trait": "trait thalassémique",
    "malade": "atteint",
    "risque": "risque estimé",
    "inconnu": "indéterminé",
}


def _pct(value: float | None) -> str:
    if value is None:
        return "non calculable"
    return f"{value * 100:.1f} %"


def _format_distribution(distribution: dict[str, float]) -> str:
    if not distribution:
        return ""
    parts = [f"{label} : {_pct(probability)}" for label, probability in distribution.items()]
    return "Distribution attendue : " + " ; ".join(parts) + "."


def build_report(
    prediction: Prediction,
    parent1: str = "inconnu",
    parent2: str = "inconnu",
    enfant: str = "inconnu",
    sexe_enfant: str = "inconnu",
    meta: dict | None = None,
) -> str:
    """Construit un compte rendu clinique structuré."""

    disease = get_disease(prediction.disease)
    meta = meta or {}
    lines = [f"Compte rendu de conseil génétique — {disease.name}", ""]
    lines.append(f"Mode de transmission : {TRANSMISSION_LABELS[disease.transmission]}.")

    if meta.get("origine"):
        lines.append(f"Origine géographique déclarée : {meta['origine']}.")
    if meta.get("age_pere"):
        lines.append(f"Âge du père : {meta['age_pere']} ans.")
    if meta.get("age_mere"):
        lines.append(f"Âge de la mère : {meta['age_mere']} ans.")
    if meta.get("antecedents"):
        lines.append(f"Antécédents familiaux déclarés : {meta['antecedents']}.")

    lines.append(
        f"Génotypes fournis : père {parent1 or 'inconnu'} ; mère {parent2 or 'inconnu'} ; "
        f"enfant {enfant or 'inconnu'}."
    )
    if sexe_enfant and sexe_enfant != "inconnu":
        lines.append(f"Sexe de l'enfant : {sexe_enfant}.")
    lines.append("")

    if prediction.method == "genotype":
        status = _STATUS_LABELS.get(prediction.status, prediction.status)
        if prediction.status == "malade":
            lines.append(
                f"Le génotype de l'enfant ({prediction.genotype_enfant}) est en faveur d'un "
                f"phénotype atteint de {disease.name}. La probabilité d'être atteint est de "
                f"{_pct(prediction.probability)}. Une confirmation par un test biologique "
                "certifié est impérative."
            )
        elif prediction.status in {"porteur", "porteuse"}:
            lines.append(
                f"Le génotype de l'enfant ({prediction.genotype_enfant}) est compatible avec "
                f"un statut de {status} de {disease.name}. La probabilité de développer la "
                "maladie est de 0 %. Le porteur ne développe pas la maladie mais peut la "
                "transmettre à sa descendance."
            )
        elif prediction.status == "porteur_im":
            lines.append(
                "Le génotype de l'enfant comporte un allèle intermédiaire (IM) pour "
                f"{disease.name}. Cet allèle n'est pas pathogène pour l'enfant, mais il peut "
                "s'étendre lors de la méiose et devenir pathogène dans la descendance. "
                "Un conseil génétique est recommandé avant tout projet d'enfant."
            )
        elif prediction.status == "a_risque":
            lines.append(
                f"Le génotype de l'enfant comporte un allèle à pénétrance réduite (RP) pour "
                f"{disease.name}. Le risque de développer la maladie est estimé à "
                f"{_pct(prediction.probability)} (fourchette de 30 à 60 % selon l'âge). "
                "Une surveillance neurologique et un conseil génétique sont recommandés."
            )
        elif prediction.status == "trait":
            lines.append(
                "Le génotype est compatible avec un trait alpha-thalassémique (deux allèles "
                "alpha fonctionnels). Il s'agit d'un porteur généralement asymptomatique, "
                "avec une microcytose possible. La probabilité de développer une maladie "
                "alpha-thalassémique est de 0 %."
            )
        elif prediction.status in {"sain", "saine"}:
            lines.append(
                f"Les informations génétiques disponibles ({prediction.genotype_enfant}) ne "
                f"révèlent aucun risque de {disease.name} pour l'enfant. La probabilité "
                "estimée est de 0 %."
            )
        else:
            lines.append(
                f"Les informations génétiques fournies sont insuffisantes pour estimer le "
                f"risque de {disease.name}. Un test génétique complet est nécessaire."
            )
    elif prediction.method == "mendelian":
        lines.append(
            f"À partir des génotypes parentaux, le risque estimé qu'un enfant à venir soit "
            f"atteint de {disease.name} est de {_pct(prediction.probability)}."
        )
        if prediction.risk_distribution:
            if disease.id == "thalassemie_alpha":
                parts = [
                    f"{count} allèles fonctionnels : {_pct(probability)}"
                    for count, probability in prediction.risk_distribution.items()
                ]
                lines.append(
                    "Distribution attendue du nombre d'allèles alpha fonctionnels : "
                    + " ; ".join(parts)
                    + "."
                )
            else:
                lines.append(_format_distribution(prediction.risk_distribution))
        risks_by_sex = prediction.details.get("risques_par_sexe")
        if risks_by_sex:
            lines.append(
                "Risque selon le sexe de l'enfant : garçon "
                f"{_pct(risks_by_sex.get('M'))} ; fille {_pct(risks_by_sex.get('F'))}."
            )
        if prediction.details.get("risque_porteur") is not None:
            lines.append(
                f"Risque que l'enfant soit porteur sain : "
                f"{_pct(prediction.details['risque_porteur'])}."
            )
        if disease.id == "thalassemie_alpha":
            lines.append(
                f"Risque de trait alpha-thalassémique : "
                f"{_pct(prediction.details.get('risque_trait'))}."
            )
        lines.append(
            "Ce calcul suppose une transmission mendélienne classique, sans mutation de novo, "
            "sans consanguinité et sans interaction entre gènes. Il doit être confirmé par "
            "un test biologique certifié."
        )
    else:
        lines.append(
            prediction.message
            or "Les informations fournies sont insuffisantes pour calculer un risque."
        )

    return "\n".join(lines).strip()


_RECOMMENDATIONS: dict[str, dict[str, str]] = {
    "drepanocytose": {
        "malade": "Consultation en hématologie spécialisée. Bilan d'hémolyse et de surcharge ferrique. Vaccination anti-pneumococcique et anti-méningococcique. Prévention des crises vaso-occlusives.",
        "porteur": "Aucun suivi médical spécialisé nécessaire. Dépistage du partenaire recommandé avant un projet d'enfant. Conseil génétique préconceptionnel.",
        "sain": "Aucune recommandation particulière.",
    },
    "mucoviscidose": {
        "malade": "Prise en charge en centre de référence de la mucoviscidose. Test de la sueur, bilan pulmonaire et digestif. Consultation en conseil génétique.",
        "porteur": "Aucun suivi médical nécessaire. Dépistage du partenaire recommandé. Conseil génétique préconceptionnel.",
        "sain": "Aucune recommandation particulière.",
    },
    "thalassemie_alpha": {
        "malade": "Hémogramme complet, électrophorèse de l'hémoglobine. Consultation en hématologie. Surveillance de la surcharge en fer si maladie HbH.",
        "trait": "Aucun suivi spécialisé nécessaire. Une microcytose isolée peut être observée. Dépistage du partenaire recommandé avant un projet d'enfant.",
        "porteur": "Aucun suivi spécialisé nécessaire. Dépistage du partenaire recommandé.",
        "sain": "Aucune recommandation particulière.",
    },
    "thalassemie_beta": {
        "malade": "Électrophorèse de l'hémoglobine, ferritine. Consultation en hématologie spécialisée. Dépistage du partenaire impératif.",
        "porteur": "Aucun suivi spécialisé nécessaire. Microcytose sans conséquence clinique. Dépistage du partenaire recommandé avant un projet d'enfant.",
        "sain": "Aucune recommandation particulière.",
    },
    "phenylcetonurie": {
        "malade": "Bilan plasmatique de la phénylalanine. Régime pauvre en phénylalanine dès la naissance. Suivi nutritionnel et neurologique régulier.",
        "porteur": "Aucun suivi nécessaire. Dépistage du partenaire recommandé. Conseil génétique préconceptionnel.",
        "sain": "Aucune recommandation particulière.",
    },
    "amyotrophie_spinale": {
        "malade": "IRM médullaire, électromyographie. Consultation en neuromusculaire. Prise en charge précoce (nusinersen, risdiplam, onasemnogene).",
        "porteur": "Aucun suivi nécessaire. Dépistage du partenaire recommandé avant un projet d'enfant.",
        "sain": "Aucune recommandation particulière.",
    },
    "huntington": {
        "malade": "IRM cérébrale, bilan neuropsychologique. Consultation en neurologie spécialisée. Accompagnement psychologique. Conseil génétique et test prédictif si souhaité.",
        "a_risque": "Surveillance neurologique régulière. Conseil génétique et information sur le test prédictif. Accompagnement psychologique si nécessaire.",
        "porteur_im": "Aucun symptôme attendu. Conseil génétique pour le projet de filiation en raison du risque d'expansion de l'allèle.",
        "sain": "Aucune recommandation particulière.",
    },
    "marfan": {
        "malade": "Échocardiographie transthoracique avec mesure de la racine aortique. Examen ophtalmologique. Bilan squelettique. Surveillance cardiologique à vie.",
        "sain": "Aucune recommandation particulière.",
    },
    "neurofibromatose1": {
        "malade": "Examen dermatologique complet. IRM cérébrale si symptômes. Examen ophtalmologique (hamartomes de Lisch). Surveillance à vie des neurofibromes.",
        "sain": "Aucune recommandation particulière.",
    },
    "polykystose_renale": {
        "malade": "Échographie rénale et bilan de fonction rénale (DFG, créatinine). Contrôle de la pression artérielle. IRM abdominale selon le stade. Surveillance néphrologique à vie.",
        "sain": "Aucune recommandation particulière.",
    },
    "hemophilie_A": {
        "malade": "Dosage du facteur VIII. Coagulogramme. Consultation en hématologie spécialisée. Prophylaxie selon le niveau. Dépistage des porteurs familiaux.",
        "porteuse": "Dosage du facteur VIII et temps de céphaline. Aucun traitement si taux normal. Projet d'enfant à discuter avec un hématologue.",
        "sain": "Aucune recommandation particulière.",
    },
    "hemophilie_B": {
        "malade": "Dosage du facteur IX. Coagulogramme. Consultation en hématologie spécialisée. Prophylaxie selon le niveau. Dépistage des porteurs familiaux.",
        "porteuse": "Dosage du facteur IX. Aucun traitement si taux normal. Projet d'enfant à discuter avec un hématologue.",
        "sain": "Aucune recommandation particulière.",
    },
}


def build_recommendations(disease_id: str, status: str, probability: float | None = None) -> str:
    """Retourne des recommandations adaptées au statut et au risque."""

    disease = get_disease(disease_id)
    if status == "risque":
        if probability is None:
            return "Consultation en conseil génétique recommandée."
        if probability >= 0.25:
            return (
                "Consultation en conseil génétique préconceptionnel. Discuter du dépistage "
                "du partenaire, des options de diagnostic prénatal et du suivi de grossesse."
            )
        if probability > 0:
            return (
                "Conseil génétique recommandé avant un projet d'enfant. Discuter du "
                "dépistage du partenaire et des options de diagnostic prénatal."
            )
        return (
            "Le risque d'être atteint est nul d'après les génotypes fournis. Vérifier "
            "néanmoins le statut de porteur éventuel et confirmer par un test génétique "
            "certifié avant toute conclusion."
        )

    if status == "inconnu":
        return (
            "Les informations sont insuffisantes. Un test génétique complet et une "
            "consultation en conseil génétique sont recommandés."
        )

    disease_recommendations = _RECOMMENDATIONS.get(disease.id, {})
    if status in disease_recommendations:
        return disease_recommendations[status]
    if status in {"porteur", "porteuse"}:
        return (
            "Aucun suivi médical spécialisé nécessaire. Dépistage du partenaire recommandé "
            "avant un projet d'enfant. Conseil génétique préconceptionnel."
        )
    if status in {"sain", "saine"}:
        return "Aucune recommandation particulière."
    return "Consultation médicale recommandée."
