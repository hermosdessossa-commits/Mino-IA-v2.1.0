"""Simulation de trios parentaux cohérents avec le moteur mendélien.

Ce module est utilisé par le générateur de dataset et par les tests. Il tire
des génotypes parentaux dans des fréquences de population, puis un génotype
d'enfant par transmission mendélienne réelle. Un mode « enrichi » permet de
produire suffisamment de cas positifs pour l'entraînement, sans jamais créer de
génotype impossible.

Les fréquences sont des ordres de grandeur destinés à la simulation. Elles ne
doivent pas être utilisées comme données épidémiologiques de référence.
"""

from __future__ import annotations

from dataclasses import dataclass

from core.diseases import DISEASES, Disease, get_disease
from core.genetics import (
    format_alpha,
    format_autosomal,
    format_xlinked,
    interpret_autosomal,
    predict,
)

__all__ = [
    "POPULATION_NAMES",
    "POPULATIONS",
    "Population",
    "apply_missingness",
    "choose_population",
    "generate_evaluation",
    "generate_trio",
    "get_population",
    "validate_population_data",
]


@dataclass(frozen=True)
class Population:
    """Fréquences alléliques d'une population simulée."""

    name: str
    weight: float
    allele_freq: dict[str, dict[str, float]]


def _alpha(a_minus: float, zero: float) -> dict[str, float]:
    return {"AA": round(1.0 - a_minus - zero, 6), "A-": a_minus, "--": zero}


# Les clés correspondent aux allèles du registre core.diseases.
_POPULATION_DATA: dict[str, tuple[float, dict[str, dict[str, float]]]] = {
    "Afrique de l'Ouest": (
        0.18,
        {
            "drepanocytose": {"S": 0.12, "C": 0.03},
            "mucoviscidose": {"MUT": 0.02},
            "thalassemie_alpha": _alpha(0.25, 0.005),
            "thalassemie_beta": {"B0": 0.03, "B+": 0.02},
            "phenylcetonurie": {"SEV": 0.004, "MILD": 0.002},
            "amyotrophie_spinale": {"DEL": 0.011},
            "huntington": {"IM": 0.003, "RP": 0.0003, "PP": 0.0001},
            "marfan": {"MUT": 0.0001},
            "neurofibromatose1": {"MUT": 0.0004},
            "polykystose_renale": {"MUT": 0.0008},
            "hemophilie_A": {"MUT": 0.0002},
            "hemophilie_B": {"MUT": 0.00006},
        },
    ),
    "Afrique Centrale": (
        0.14,
        {
            "drepanocytose": {"S": 0.10, "C": 0.02},
            "mucoviscidose": {"MUT": 0.015},
            "thalassemie_alpha": _alpha(0.22, 0.004),
            "thalassemie_beta": {"B0": 0.04, "B+": 0.03},
            "phenylcetonurie": {"SEV": 0.003, "MILD": 0.001},
            "amyotrophie_spinale": {"DEL": 0.014},
            "huntington": {"IM": 0.003, "RP": 0.0003, "PP": 0.0001},
            "marfan": {"MUT": 0.0001},
            "neurofibromatose1": {"MUT": 0.0004},
            "polykystose_renale": {"MUT": 0.0008},
            "hemophilie_A": {"MUT": 0.0002},
            "hemophilie_B": {"MUT": 0.00006},
        },
    ),
    "Méditerranée": (
        0.16,
        {
            "drepanocytose": {"S": 0.03, "C": 0.005},
            "mucoviscidose": {"MUT": 0.017},
            "thalassemie_alpha": _alpha(0.04, 0.02),
            "thalassemie_beta": {"B0": 0.04, "B+": 0.05},
            "phenylcetonurie": {"SEV": 0.010, "MILD": 0.005},
            "amyotrophie_spinale": {"DEL": 0.020},
            "huntington": {"IM": 0.004, "RP": 0.0004, "PP": 0.0002},
            "marfan": {"MUT": 0.0002},
            "neurofibromatose1": {"MUT": 0.0004},
            "polykystose_renale": {"MUT": 0.0008},
            "hemophilie_A": {"MUT": 0.0002},
            "hemophilie_B": {"MUT": 0.00006},
        },
    ),
    "Europe du Nord": (
        0.18,
        {
            "drepanocytose": {"S": 0.001, "C": 0.0005},
            "mucoviscidose": {"MUT": 0.020},
            "thalassemie_alpha": _alpha(0.005, 0.0005),
            "thalassemie_beta": {"B0": 0.002, "B+": 0.004},
            "phenylcetonurie": {"SEV": 0.010, "MILD": 0.004},
            "amyotrophie_spinale": {"DEL": 0.020},
            "huntington": {"IM": 0.005, "RP": 0.0006, "PP": 0.0003},
            "marfan": {"MUT": 0.0002},
            "neurofibromatose1": {"MUT": 0.0004},
            "polykystose_renale": {"MUT": 0.0008},
            "hemophilie_A": {"MUT": 0.0002},
            "hemophilie_B": {"MUT": 0.00006},
        },
    ),
    "Asie": (
        0.16,
        {
            "drepanocytose": {"S": 0.005, "C": 0.002},
            "mucoviscidose": {"MUT": 0.008},
            "thalassemie_alpha": _alpha(0.18, 0.03),
            "thalassemie_beta": {"B0": 0.03, "B+": 0.05},
            "phenylcetonurie": {"SEV": 0.005, "MILD": 0.008},
            "amyotrophie_spinale": {"DEL": 0.015},
            "huntington": {"IM": 0.003, "RP": 0.0001, "PP": 0.0001},
            "marfan": {"MUT": 0.0002},
            "neurofibromatose1": {"MUT": 0.0004},
            "polykystose_renale": {"MUT": 0.0008},
            "hemophilie_A": {"MUT": 0.0002},
            "hemophilie_B": {"MUT": 0.00006},
        },
    ),
    "Amériques": (
        0.18,
        {
            "drepanocytose": {"S": 0.06, "C": 0.015},
            "mucoviscidose": {"MUT": 0.015},
            "thalassemie_alpha": _alpha(0.10, 0.005),
            "thalassemie_beta": {"B0": 0.02, "B+": 0.03},
            "phenylcetonurie": {"SEV": 0.007, "MILD": 0.004},
            "amyotrophie_spinale": {"DEL": 0.018},
            "huntington": {"IM": 0.004, "RP": 0.0004, "PP": 0.0002},
            "marfan": {"MUT": 0.0002},
            "neurofibromatose1": {"MUT": 0.0004},
            "polykystose_renale": {"MUT": 0.0008},
            "hemophilie_A": {"MUT": 0.0002},
            "hemophilie_B": {"MUT": 0.00006},
        },
    ),
}

POPULATIONS: dict[str, Population] = {
    name: Population(name=name, weight=weight, allele_freq=freqs)
    for name, (weight, freqs) in _POPULATION_DATA.items()
}
POPULATION_NAMES: tuple[str, ...] = tuple(POPULATIONS)


def get_population(name: str) -> Population:
    try:
        return POPULATIONS[name]
    except KeyError as exc:
        raise ValueError(f"Population inconnue : {name!r}.") from exc


def choose_population(rng) -> Population:
    names = list(POPULATIONS)
    weights = [POPULATIONS[name].weight for name in names]
    return POPULATIONS[rng.choices(names, weights=weights, k=1)[0]]


def _freqs(population: Population, disease: Disease) -> dict[str, float]:
    try:
        return dict(population.allele_freq[disease.id])
    except KeyError as exc:
        raise ValueError(
            f"Fréquences manquantes pour {disease.id} dans {population.name}."
        ) from exc


def _normal(disease: Disease) -> str:
    if not disease.normal_alleles:
        raise ValueError(f"{disease.id} n'a pas d'allèle normal déclaré.")
    return disease.normal_alleles[0]


def _draw_allele(freqs: dict[str, float], normal: str, rng) -> str:
    alleles = list(freqs) + [normal]
    weights = [max(0.0, freqs[allele]) for allele in freqs] + [
        max(0.0, 1.0 - sum(max(0.0, value) for value in freqs.values()))
    ]
    if sum(weights) <= 0:
        raise ValueError("Fréquences alléliques invalides.")
    return rng.choices(alleles, weights=weights, k=1)[0]


def _draw_autosomal(disease: Disease, freqs: dict[str, float], rng) -> tuple[str, str]:
    normal = _normal(disease)
    return tuple(sorted((_draw_allele(freqs, normal, rng), _draw_allele(freqs, normal, rng))))


def _child_autosomal(parent1: tuple[str, str], parent2: tuple[str, str], rng) -> tuple[str, str]:
    return tuple(sorted((rng.choice(parent1), rng.choice(parent2))))


def _draw_xlinked_father(freqs: dict[str, float], rng) -> dict:
    mutated = rng.random() < freqs.get("MUT", 0.0)
    return {
        "sex": "M",
        "alleles": ("mut",) if mutated else ("normal",),
        "status": "malade" if mutated else "sain",
    }


def _draw_xlinked_mother(freqs: dict[str, float], rng) -> dict:
    q = freqs.get("MUT", 0.0)
    alleles = tuple("mut" if rng.random() < q else "normal" for _ in range(2))
    n_mut = alleles.count("mut")
    status = "malade" if n_mut == 2 else "porteuse" if n_mut == 1 else "saine"
    return {"sex": "F", "alleles": alleles, "status": status}


def _child_xlinked(father: dict, mother: dict, rng) -> dict:
    sex = "M" if rng.random() < 0.5 else "F"
    if sex == "M":
        allele = rng.choice(mother["alleles"])
        return {
            "sex": "M",
            "alleles": (allele,),
            "status": "malade" if allele == "mut" else "sain",
        }
    paternal = rng.choice(father["alleles"])
    maternal = rng.choice(mother["alleles"])
    n_mut = int(paternal == "mut") + int(maternal == "mut")
    status = "malade" if n_mut == 2 else "porteuse" if n_mut == 1 else "saine"
    return {"sex": "F", "alleles": (paternal, maternal), "status": status}


def _draw_alpha_chromosome(freqs: dict[str, float], rng) -> str:
    types = ["AA", "A-", "--"]
    weights = [max(0.0, freqs.get(kind, 0.0)) for kind in types]
    if sum(weights) <= 0:
        raise ValueError("Fréquences alpha invalides.")
    return rng.choices(types, weights=weights, k=1)[0]


def _draw_alpha(freqs: dict[str, float], rng) -> tuple[str, str]:
    return (_draw_alpha_chromosome(freqs, rng), _draw_alpha_chromosome(freqs, rng))


def _child_alpha(parent1: tuple[str, str], parent2: tuple[str, str], rng) -> tuple[str, str]:
    return (rng.choice(parent1), rng.choice(parent2))


def _pick_pathogenic(disease: Disease, freqs: dict[str, float], rng) -> str:
    candidates = [allele for allele in disease.pathogenic_alleles if freqs.get(allele, 0) > 0]
    if not candidates:
        candidates = list(disease.pathogenic_alleles)
    weights = [max(freqs.get(allele, 0.0), 1e-9) for allele in candidates]
    return rng.choices(candidates, weights=weights, k=1)[0]


def _recessive_trio(
    disease: Disease, freqs: dict[str, float], rng, scenario: str
) -> tuple[tuple[str, str], tuple[str, str], tuple[str, str]]:
    normal = _normal(disease)
    if scenario == "affected":
        allele1 = _pick_pathogenic(disease, freqs, rng)
        allele2 = _pick_pathogenic(disease, freqs, rng)
        parent1 = (
            (normal, allele1)
            if rng.random() < 0.8
            else tuple(sorted((allele1, _pick_pathogenic(disease, freqs, rng))))
        )
        parent2 = (
            (normal, allele2)
            if rng.random() < 0.8
            else tuple(sorted((allele2, _pick_pathogenic(disease, freqs, rng))))
        )
        child = tuple(sorted((allele1, allele2)))
        return parent1, parent2, child

    if scenario == "carrier":
        allele = _pick_pathogenic(disease, freqs, rng)
        parent1 = tuple(sorted((normal, allele)))
        parent2 = (normal, normal)
        child = tuple(sorted((normal, allele)))
        return parent1, parent2, child

    # Enfant sain : tirage naturel, avec repli sur des parents normaux.
    for _ in range(100):
        parent1 = _draw_autosomal(disease, freqs, rng)
        parent2 = _draw_autosomal(disease, freqs, rng)
        child = _child_autosomal(parent1, parent2, rng)
        if interpret_autosomal(child, disease)[0] == "sain":
            return parent1, parent2, child
    return (normal, normal), (normal, normal), (normal, normal)


def _dominant_trio(
    disease: Disease, freqs: dict[str, float], rng, scenario: str
) -> tuple[tuple[str, str], tuple[str, str], tuple[str, str]]:
    normal = _normal(disease)
    if scenario == "affected":
        if disease.id == "huntington":
            allele = "PP"
        else:
            allele = disease.pathogenic_alleles[0]
        parent1 = tuple(sorted((normal, allele)))
        parent2 = (normal, normal)
        child = tuple(sorted((normal, allele)))
        return parent1, parent2, child

    if scenario == "a_risque" and disease.id == "huntington":
        parent1 = (normal, "RP")
        parent2 = (normal, normal)
        child = (normal, "RP")
        return parent1, parent2, child

    if scenario == "intermediate" and disease.id == "huntington":
        parent1 = (normal, "IM")
        parent2 = (normal, normal)
        child = (normal, "IM")
        return parent1, parent2, child

    for _ in range(100):
        parent1 = _draw_autosomal(disease, freqs, rng)
        parent2 = _draw_autosomal(disease, freqs, rng)
        child = _child_autosomal(parent1, parent2, rng)
        if interpret_autosomal(child, disease)[0] == "sain":
            return parent1, parent2, child
    return (normal, normal), (normal, normal), (normal, normal)


def _xlinked_trio(
    disease: Disease, freqs: dict[str, float], rng, scenario: str
) -> tuple[dict, dict, dict]:
    father = _draw_xlinked_father(freqs, rng)
    mother = _draw_xlinked_mother(freqs, rng)

    if scenario == "affected_son":
        if mother["status"] == "saine":
            mother = {"sex": "F", "alleles": ("normal", "mut"), "status": "porteuse"}
        child = {"sex": "M", "alleles": ("mut",), "status": "malade"}
        return father, mother, child

    if scenario == "carrier_daughter":
        if rng.random() < 0.5:
            father = {"sex": "M", "alleles": ("mut",), "status": "malade"}
            mother = {"sex": "F", "alleles": ("normal", "normal"), "status": "saine"}
            child = {"sex": "F", "alleles": ("mut", "normal"), "status": "porteuse"}
        else:
            father = {"sex": "M", "alleles": ("normal",), "status": "sain"}
            mother = {"sex": "F", "alleles": ("normal", "mut"), "status": "porteuse"}
            child = {"sex": "F", "alleles": ("normal", "mut"), "status": "porteuse"}
        return father, mother, child

    if scenario == "affected_daughter":
        father = {"sex": "M", "alleles": ("mut",), "status": "malade"}
        if mother["status"] == "saine":
            mother = {"sex": "F", "alleles": ("normal", "mut"), "status": "porteuse"}
        child = {"sex": "F", "alleles": ("mut", "mut"), "status": "malade"}
        return father, mother, child

    for _ in range(100):
        father = _draw_xlinked_father(freqs, rng)
        mother = _draw_xlinked_mother(freqs, rng)
        child = _child_xlinked(father, mother, rng)
        if child["status"] in {"sain", "saine"}:
            return father, mother, child
    return (
        {"sex": "M", "alleles": ("normal",), "status": "sain"},
        {"sex": "F", "alleles": ("normal", "normal"), "status": "saine"},
        {"sex": "F", "alleles": ("normal", "normal"), "status": "saine"},
    )


def _alpha_parent_with(chromosome: str, rng) -> tuple[str, str]:
    options = {
        "A-": [("AA", "A-"), ("A-", "A-"), ("A-", "--")],
        "--": [("A-", "--"), ("--", "--")],
        "AA": [("AA", "AA"), ("AA", "A-")],
    }[chromosome]
    return rng.choice(options)


def _alpha_trio(
    freqs: dict[str, float], rng, scenario: str
) -> tuple[tuple[str, str], tuple[str, str], tuple[str, str]]:
    if scenario == "hbH":
        return _alpha_parent_with("A-", rng), _alpha_parent_with("--", rng), ("A-", "--")
    if scenario == "bart":
        return _alpha_parent_with("--", rng), _alpha_parent_with("--", rng), ("--", "--")
    if scenario == "trait":
        return _alpha_parent_with("A-", rng), _alpha_parent_with("A-", rng), ("A-", "A-")
    if scenario == "carrier":
        return _alpha_parent_with("A-", rng), ("AA", "AA"), ("AA", "A-")
    return ("AA", "AA"), ("AA", "AA"), ("AA", "AA")


def _format_trio(
    disease: Disease,
    parent1,
    parent2,
    child,
    sexe_enfant: str,
) -> dict[str, str]:
    if disease.is_alpha:
        return {
            "parent1": format_alpha(parent1),
            "parent2": format_alpha(parent2),
            "enfant": format_alpha(child),
            "sexe_enfant": sexe_enfant,
        }
    if disease.is_xlinked:
        return {
            "parent1": format_xlinked(parent1),
            "parent2": format_xlinked(parent2),
            "enfant": format_xlinked(child),
            "sexe_enfant": child["sex"],
        }
    return {
        "parent1": format_autosomal(parent1, disease),
        "parent2": format_autosomal(parent2, disease),
        "enfant": format_autosomal(child, disease),
        "sexe_enfant": sexe_enfant,
    }


def generate_trio(
    disease_id: str,
    population: Population,
    rng,
    case_rate: float = 0.35,
) -> dict[str, str]:
    """Génère un trio parent-enfant cohérent pour une maladie.

    ``case_rate`` est la probabilité de passer par un scénario enrichi. Les
    scénarios enrichis ne violent jamais les lois de Mendel : ils choisissent
    simplement des combinaisons parentales qui peuvent produire le phénotype
    cible.
    """

    disease = get_disease(disease_id)
    freqs = _freqs(population, disease)
    enriched = rng.random() < case_rate

    if disease.is_alpha:
        if enriched:
            scenario = rng.choices(
                ["hbH", "bart", "trait", "carrier", "healthy"],
                weights=[0.25, 0.05, 0.30, 0.25, 0.15],
                k=1,
            )[0]
            parent1, parent2, child = _alpha_trio(freqs, rng, scenario)
        else:
            parent1 = _draw_alpha(freqs, rng)
            parent2 = _draw_alpha(freqs, rng)
            child = _child_alpha(parent1, parent2, rng)
        sexe_enfant = "M" if rng.random() < 0.5 else "F"
        return _format_trio(disease, parent1, parent2, child, sexe_enfant)

    if disease.is_xlinked:
        if enriched:
            scenario = rng.choices(
                ["affected_son", "carrier_daughter", "affected_daughter", "healthy"],
                weights=[0.45, 0.25, 0.10, 0.20],
                k=1,
            )[0]
            father, mother, child = _xlinked_trio(disease, freqs, rng, scenario)
        else:
            father = _draw_xlinked_father(freqs, rng)
            mother = _draw_xlinked_mother(freqs, rng)
            child = _child_xlinked(father, mother, rng)
        return _format_trio(disease, father, mother, child, child["sex"])

    if disease.is_recessive:
        if enriched:
            scenario = rng.choices(
                ["affected", "carrier", "healthy"], weights=[0.55, 0.30, 0.15], k=1
            )[0]
            parent1, parent2, child = _recessive_trio(disease, freqs, rng, scenario)
        else:
            parent1 = _draw_autosomal(disease, freqs, rng)
            parent2 = _draw_autosomal(disease, freqs, rng)
            child = _child_autosomal(parent1, parent2, rng)
    else:
        if enriched:
            scenarios = ["affected", "healthy"]
            weights = [0.65, 0.35]
            if disease.id == "huntington":
                scenarios = ["affected", "a_risque", "intermediate", "healthy"]
                weights = [0.35, 0.15, 0.15, 0.35]
            scenario = rng.choices(scenarios, weights=weights, k=1)[0]
            parent1, parent2, child = _dominant_trio(disease, freqs, rng, scenario)
        else:
            parent1 = _draw_autosomal(disease, freqs, rng)
            parent2 = _draw_autosomal(disease, freqs, rng)
            child = _child_autosomal(parent1, parent2, rng)

    if rng.random() < 0.5:
        parent1, parent2 = parent2, parent1
    sexe_enfant = "M" if rng.random() < 0.5 else "F"
    return _format_trio(disease, parent1, parent2, child, sexe_enfant)


def apply_missingness(
    trio: dict[str, str],
    rng,
    missing_rate: float = 0.15,
) -> dict[str, str]:
    """Masque aléatoirement des génotypes, sans jamais tout masquer."""

    result = dict(trio)
    for key in ("parent1", "parent2", "enfant"):
        if rng.random() < missing_rate:
            result[key] = "inconnu"

    if all(result[key] == "inconnu" for key in ("parent1", "parent2", "enfant")):
        result["enfant"] = trio["enfant"]

    if rng.random() < missing_rate * 0.5:
        result["sexe_enfant"] = "inconnu"

    return result


def generate_evaluation(
    disease_id: str,
    population: Population,
    rng,
    case_rate: float = 0.35,
    missing_rate: float = 0.15,
) -> dict:
    """Génère un trio, applique le bruit et calcule la vérité terrain."""

    trio = generate_trio(disease_id, population, rng, case_rate=case_rate)
    observed = apply_missingness(trio, rng, missing_rate=missing_rate)
    prediction = predict(
        disease_id,
        observed["parent1"],
        observed["parent2"],
        observed["enfant"],
        observed["sexe_enfant"],
    )
    return {"genotypes": observed, "prediction": prediction, "truth": trio}


def validate_population_data() -> None:
    """Vérifie la cohérence des fréquences simulées."""

    total_weight = sum(population.weight for population in POPULATIONS.values())
    if abs(total_weight - 1.0) > 1e-9:
        raise ValueError(f"Les poids de population ne totalisent pas 1 : {total_weight}.")

    for population in POPULATIONS.values():
        for disease_id, disease in DISEASES.items():
            if disease_id not in population.allele_freq:
                raise ValueError(f"Fréquences manquantes : {population.name}/{disease_id}.")
            freqs = population.allele_freq[disease_id]
            if disease.is_alpha:
                if set(freqs) != {"AA", "A-", "--"}:
                    raise ValueError(f"Clés alpha invalides : {population.name}/{disease_id}.")
                if abs(sum(freqs.values()) - 1.0) > 1e-6:
                    raise ValueError(
                        f"Fréquences alpha non normalisées : {population.name}/{disease_id}."
                    )
            elif disease.is_xlinked:
                if not 0 <= freqs.get("MUT", 0) <= 1:
                    raise ValueError(f"Fréquence X invalide : {population.name}/{disease_id}.")
            else:
                allowed = (
                    set(disease.normal_alleles)
                    | set(disease.pathogenic_alleles)
                    | set(disease.intermediate_alleles)
                )
                if not set(freqs).issubset(allowed):
                    raise ValueError(
                        f"Allèles inconnus : {population.name}/{disease_id} : {set(freqs) - allowed}."
                    )
                if sum(freqs.values()) > 1:
                    raise ValueError(f"Fréquences > 1 : {population.name}/{disease_id}.")


validate_population_data()
