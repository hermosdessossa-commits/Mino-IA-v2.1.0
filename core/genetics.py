"""Moteur mendélien déterministe.

Le moteur est volontairement indépendant de tout LLM : il calcule les
probabilités et interprète les génotypes à partir des lois de Mendel. Le LLM ne
doit servir qu'à rédiger le compte rendu, jamais à inventer une probabilité.

Conventions de génotypes
------------------------
- Autosomique : deux allèles séparés par ``/`` (``A/S``, ``A/A``, ``MUT/WT``).
  Un allèle seul est interprété comme hétérozygote s'il est pathogène, et comme
  homozygote normal s'il est normal.
- Lié à l'X : ``XY:sain``, ``XY:malade``, ``XX:saine``, ``XX:porteuse``,
  ``XX:malade`` (ou ``M:sain``, ``F:porteuse``).
- Alpha-thalassémie : nombre d'allèles fonctionnels (``0`` à ``4``) ou
  configuration ``AA/AA``, ``AA/A-``, ``AA/--``, ``A-/A-``, ``A-/--``, ``--/--``.
- ``inconnu`` (ou vide) signifie que le génotype n'est pas disponible.
"""

from __future__ import annotations

import re
from collections import defaultdict
from dataclasses import dataclass, field
from itertools import product

from core.diseases import Disease, get_disease

__all__ = [
    "GenotypeError",
    "Prediction",
    "alpha_count",
    "child_distribution_alpha",
    "child_distribution_autosomal",
    "child_distribution_xlinked",
    "format_alpha",
    "format_autosomal",
    "format_xlinked",
    "interpret_alpha",
    "interpret_autosomal",
    "interpret_xlinked",
    "normalize_sex",
    "parse_alpha",
    "parse_autosomal",
    "parse_xlinked",
    "predict",
]

UNKNOWN_VALUES = {
    "",
    "inconnu",
    "inconnue",
    "unknown",
    "?",
    "na",
    "n/a",
    "non teste",
    "non testé",
    "non_teste",
    "non_testé",
    "non testee",
    "non testée",
}


class GenotypeError(ValueError):
    """Génotype invalide ou incohérent avec la maladie."""


@dataclass
class Prediction:
    """Résultat du moteur mendélien."""

    disease: str
    status: str
    probability: float | None
    method: str
    genotype_enfant: str | None = None
    risk_distribution: dict[str, float] = field(default_factory=dict)
    details: dict = field(default_factory=dict)
    message: str = ""

    def to_dict(self) -> dict:
        return {
            "maladie": self.disease,
            "statut": self.status,
            "probabilite": self.probability,
            "methode": self.method,
            "genotype_enfant": self.genotype_enfant,
            "distribution": self.risk_distribution,
            "details": self.details,
            "message": self.message,
        }


def _clean(value: object) -> str:
    if value is None:
        return ""
    return str(value).strip().replace("~", "").replace("|", "/").replace(" ", "")


def _is_unknown(value: object) -> bool:
    return _clean(value).lower() in UNKNOWN_VALUES


def normalize_sex(value: object) -> str | None:
    """Normalise ``M``/``F``/``inconnu``."""

    if value is None:
        return None
    raw = str(value).strip().lower()
    if raw in {"", "inconnu", "inconnue", "unknown", "?", "na", "n/a"}:
        return None
    if raw in {"m", "masculin", "homme", "garcon", "garçon", "xy"}:
        return "M"
    if raw in {"f", "feminin", "féminin", "femme", "fille", "xx"}:
        return "F"
    raise GenotypeError("Sexe invalide : utilisez M, F ou inconnu.")


# ---------------------------------------------------------------------------
# Maladies autosomiques
# ---------------------------------------------------------------------------
def _map_allele(token: str, disease: Disease) -> str:
    token = token.strip().upper()
    normal = disease.normal_alleles[0]
    if token in {"WT", "NORMAL", "SAIN", "SAINE", "N"}:
        return normal
    if token in {"MUT", "MUTE", "MUTÉ"}:
        if len(disease.pathogenic_alleles) == 1:
            return disease.pathogenic_alleles[0]
        raise GenotypeError(
            f"Pour {disease.name}, précisez l'allèle pathogène : "
            f"{', '.join(disease.pathogenic_alleles)}."
        )
    if token in disease.normal_alleles or token in disease.pathogenic_alleles:
        return token
    if token in disease.intermediate_alleles:
        return token
    raise GenotypeError(
        f"Allèle inconnu pour {disease.name} : {token!r}. "
        f"Allèles acceptés : {', '.join((*disease.normal_alleles, *disease.pathogenic_alleles, *disease.intermediate_alleles))}."
    )


def parse_autosomal(value: object, disease: Disease) -> tuple[str, str] | None:
    """Parse un génotype autosomique et retourne deux allèles triés."""

    if not disease.normal_alleles:
        raise GenotypeError(f"{disease.name} n'utilise pas de génotype autosomique simple.")
    raw = _clean(value)
    if _is_unknown(raw):
        return None

    upper = raw.upper()
    # Notation PKD1:MUT / PKD2:WT
    pkd = re.fullmatch(r"(PKD[12]):(MUT|WT)", upper)
    if pkd:
        if disease.id != "polykystose_renale":
            raise GenotypeError(
                "La notation PKD1/PKD2 n'est valable que pour la polykystose rénale."
            )
        return (
            (disease.pathogenic_alleles[0], disease.normal_alleles[0])
            if pkd.group(2) == "MUT"
            else (
                disease.normal_alleles[0],
                disease.normal_alleles[0],
            )
        )

    if "/" in upper:
        parts = [part for part in upper.split("/") if part]
        if len(parts) != 2:
            raise GenotypeError(f"Génotype invalide : {value!r}. Format attendu : ALLELE/ALLELE.")
        alleles = [_map_allele(part, disease) for part in parts]
    else:
        token = (
            _map_allele(upper, disease)
            if upper
            in {
                *disease.normal_alleles,
                *disease.pathogenic_alleles,
                *disease.intermediate_alleles,
                "WT",
                "MUT",
            }
            else None
        )
        if token is not None:
            if token == disease.normal_alleles[0]:
                alleles = [token, token]
            else:
                # Un allèle pathogène seul = hétérozygote (porteur), jamais
                # homozygote par défaut : on ne veut pas diagnostiquer à tort.
                alleles = [token, disease.normal_alleles[0]]
        else:
            # Essayer de découper un génotype concaténé : AS, SS, B0B+, ...
            valid = (
                set(disease.normal_alleles)
                | set(disease.pathogenic_alleles)
                | set(disease.intermediate_alleles)
            )
            split: tuple[str, str] | None = None
            for index in range(1, len(upper)):
                left, right = upper[:index], upper[index:]
                if left in valid and right in valid:
                    split = (left, right)
                    break
            if split is None:
                raise GenotypeError(
                    f"Génotype invalide pour {disease.name} : {value!r}. "
                    "Utilisez la forme ALLELE/ALLELE (ex. A/S)."
                )
            alleles = list(split)

    return tuple(sorted(alleles))  # type: ignore[return-value]


def format_autosomal(genotype: tuple[str, str] | None, disease: Disease) -> str:
    if genotype is None:
        return "inconnu"
    a1, a2 = genotype
    normal = disease.normal_alleles[0]
    if disease.is_dominant and disease.id in {"marfan", "neurofibromatose1", "polykystose_renale"}:
        if a1 == normal and a2 == normal:
            return "WT"
        if a1 == a2:
            return f"{a1}/{a2}"
        return "MUT"
    return f"{a1}/{a2}"


def child_distribution_autosomal(
    parent1: tuple[str, str], parent2: tuple[str, str]
) -> dict[tuple[str, str], float]:
    distribution: dict[tuple[str, str], float] = defaultdict(float)
    for allele1, allele2 in product(parent1, parent2):
        distribution[tuple(sorted((allele1, allele2)))] += 0.25
    return dict(distribution)


def interpret_autosomal(genotype: tuple[str, str], disease: Disease) -> tuple[str, float]:
    """Retourne (statut, probabilité d'être atteint) pour un génotype connu."""

    pathogenic = set(disease.pathogenic_alleles)
    if disease.id == "huntington":
        alleles = set(genotype)
        if "PP" in alleles:
            return "malade", 1.0
        if "RP" in alleles:
            # Pénétrance réduite : 30-60 % selon la fiche. Valeur centrale 45 %.
            return "a_risque", 0.45
        if "IM" in alleles:
            return "porteur_im", 0.0
        return "sain", 0.0

    n_pathogenic = sum(1 for allele in genotype if allele in pathogenic)
    if disease.is_recessive:
        if n_pathogenic == 0:
            return "sain", 0.0
        if n_pathogenic == 1:
            return "porteur", 0.0
        return "malade", 1.0
    if n_pathogenic == 0:
        return "sain", 0.0
    return "malade", 1.0


# ---------------------------------------------------------------------------
# Maladies liées à l'X
# ---------------------------------------------------------------------------
def parse_xlinked(value: object, default_sex: str | None = None) -> dict | None:
    """Parse un génotype lié à l'X."""

    raw = _clean(value)
    if _is_unknown(raw):
        return None
    if ":" in raw:
        sex_token, status_token = raw.split(":", 1)
    elif default_sex:
        sex_token, status_token = default_sex, raw
    else:
        raise GenotypeError(
            "Pour une maladie liée à l'X, précisez le sexe : XY:sain, XY:malade, "
            "XX:saine, XX:porteuse ou XX:malade."
        )

    sex = normalize_sex(sex_token)
    status_token = status_token.strip().lower()
    if sex == "M":
        if status_token in {"sain", "saine", "normal"}:
            status = "sain"
        elif status_token in {"malade", "atteint"}:
            status = "malade"
        else:
            raise GenotypeError("Pour un homme XY, le statut doit être « sain » ou « malade ».")
    elif sex == "F":
        if status_token in {"saine", "sain", "normale", "normal"}:
            status = "saine"
        elif status_token in {"porteuse", "porteur"}:
            status = "porteuse"
        elif status_token in {"malade", "atteinte"}:
            status = "malade"
        else:
            raise GenotypeError(
                "Pour une femme XX, le statut doit être « saine », « porteuse » ou « malade »."
            )
    else:
        raise GenotypeError("Sexe invalide pour un génotype lié à l'X.")
    return {"sex": sex, "status": status}


def format_xlinked(genotype: dict | None) -> str:
    if genotype is None:
        return "inconnu"
    return f"{'XY' if genotype['sex'] == 'M' else 'XX'}:{genotype['status']}"


def child_distribution_xlinked(
    father: dict, mother: dict, sex: str | None = None
) -> dict[tuple[str, str], float]:
    """Distribution des enfants pour une maladie liée à l'X.

    ``sex`` peut valoir ``M``, ``F`` ou ``None``. Si ``None``, la distribution
    couvre les deux sexes à 50/50.
    """

    if father["sex"] != "M" or mother["sex"] != "F":
        raise GenotypeError("Pour une maladie liée à l'X, le père doit être XY et la mère XX.")

    paternal_x = "mut" if father["status"] == "malade" else "normal"
    maternal_x = {
        "saine": ("normal", "normal"),
        "porteuse": ("normal", "mut"),
        "malade": ("mut", "mut"),
    }[mother["status"]]

    distribution: dict[tuple[str, str], float] = defaultdict(float)
    if sex in (None, "M"):
        weight = 0.5 if sex == "M" else 0.25
        for x in maternal_x:
            status = "malade" if x == "mut" else "sain"
            distribution[("M", status)] += weight
    if sex in (None, "F"):
        weight = 0.5 if sex == "F" else 0.25
        for x in maternal_x:
            mutated = int(paternal_x == "mut") + int(x == "mut")
            status = "malade" if mutated == 2 else "porteuse" if mutated == 1 else "saine"
            distribution[("F", status)] += weight
    return dict(distribution)


def _xlinked_risk(distribution: dict[tuple[str, str], float], sex: str | None = None) -> float:
    return sum(
        probability
        for (child_sex, status), probability in distribution.items()
        if status == "malade" and (sex is None or child_sex == sex)
    )


def interpret_xlinked(genotype: dict) -> tuple[str, float]:
    if genotype["status"] == "malade":
        return "malade", 1.0
    return genotype["status"], 0.0


# ---------------------------------------------------------------------------
# Alpha-thalassémie (dosage)
# ---------------------------------------------------------------------------
def _normalize_alpha_chromosome(value: str) -> str:
    chromosome = value.strip().upper()
    if chromosome == "A":
        chromosome = "AA"
    elif chromosome == "-A":
        chromosome = "A-"
    elif chromosome == "-":
        chromosome = "--"
    if not re.fullmatch(r"[A-]{2}", chromosome):
        raise GenotypeError(f"Chromosome alpha invalide : {value!r}. Utilisez AA, A- ou --.")
    return chromosome


def _alpha_config_from_count(count: int) -> tuple[str, str]:
    configs = {
        4: ("AA", "AA"),
        3: ("AA", "A-"),
        2: ("A-", "A-"),
        1: ("A-", "--"),
        0: ("--", "--"),
    }
    if count not in configs:
        raise GenotypeError(
            "Le nombre d'allèles alpha fonctionnels doit être compris entre 0 et 4."
        )
    return configs[count]


def parse_alpha(value: object) -> tuple[str, str] | None:
    """Parse un génotype alpha en deux chromosomes."""

    raw = _clean(value)
    if _is_unknown(raw):
        return None
    if raw.isdigit():
        return _alpha_config_from_count(int(raw))
    if re.fullmatch(r"[A-]{4}", raw):
        return (_normalize_alpha_chromosome(raw[:2]), _normalize_alpha_chromosome(raw[2:]))
    if "/" in raw:
        parts = [part for part in raw.split("/") if part]
        if len(parts) != 2:
            raise GenotypeError(
                f"Génotype alpha invalide : {value!r}. Format attendu : AA/AA, AA/A-, A-/--, etc."
            )
        return (_normalize_alpha_chromosome(parts[0]), _normalize_alpha_chromosome(parts[1]))
    raise GenotypeError(
        f"Génotype alpha invalide : {value!r}. Utilisez 0-4 ou une configuration AA/AA."
    )


def alpha_count(genotype: tuple[str, str]) -> int:
    return sum(chromosome.count("A") for chromosome in genotype)


def format_alpha(genotype: tuple[str, str] | None) -> str:
    if genotype is None:
        return "inconnu"
    return f"{genotype[0]}/{genotype[1]}"


def child_distribution_alpha(
    parent1: tuple[str, str], parent2: tuple[str, str]
) -> dict[int, float]:
    distribution: dict[int, float] = defaultdict(float)
    for chromosome1, chromosome2 in product(parent1, parent2):
        distribution[chromosome1.count("A") + chromosome2.count("A")] += 0.25
    return dict(distribution)


def interpret_alpha(count: int) -> tuple[str, float]:
    if count == 4:
        return "sain", 0.0
    if count == 3:
        return "porteur", 0.0
    if count == 2:
        return "trait", 0.0
    if count == 1:
        return "malade", 1.0
    if count == 0:
        return "malade", 1.0
    raise GenotypeError("Le nombre d'allèles alpha fonctionnels doit être compris entre 0 et 4.")


# ---------------------------------------------------------------------------
# Point d'entrée
# ---------------------------------------------------------------------------
def _insufficient(disease: Disease, message: str) -> Prediction:
    return Prediction(
        disease=disease.id,
        status="inconnu",
        probability=None,
        method="insufficient_data",
        message=message,
    )


def predict(
    disease_id: str,
    genotype_parent1: object = "inconnu",
    genotype_parent2: object = "inconnu",
    genotype_enfant: object = "inconnu",
    sexe_enfant: object = "inconnu",
) -> Prediction:
    """Calcule le statut et la probabilité pour une maladie.

    - Si le génotype de l'enfant est connu : interprétation directe.
    - Sinon, si les deux parents sont connus : distribution mendélienne.
    - Sinon : résultat ``inconnu`` avec ``probabilite=None`` (jamais 0.0 par
      défaut, pour ne pas confondre « inconnu » et « pas de risque »).
    """

    disease = get_disease(disease_id)
    sex = normalize_sex(sexe_enfant)

    if disease.is_alpha:
        parent1 = parse_alpha(genotype_parent1)
        parent2 = parse_alpha(genotype_parent2)
        child = parse_alpha(genotype_enfant)
        if child is not None:
            count = alpha_count(child)
            status, probability = interpret_alpha(count)
            return Prediction(
                disease=disease.id,
                status=status,
                probability=probability,
                method="genotype",
                genotype_enfant=str(count),
                details={
                    "alleles_fonctionnels": count,
                    "configuration": format_alpha(child),
                },
            )
        if parent1 is not None and parent2 is not None:
            distribution = child_distribution_alpha(parent1, parent2)
            risk = sum(probability for count, probability in distribution.items() if count <= 1)
            return Prediction(
                disease=disease.id,
                status="risque",
                probability=risk,
                method="mendelian",
                risk_distribution={
                    str(count): probability for count, probability in sorted(distribution.items())
                },
                details={
                    "parents": {"parent1": format_alpha(parent1), "parent2": format_alpha(parent2)},
                    "risque_maladie": risk,
                    "risque_trait": distribution.get(2, 0.0),
                    "risque_porteur": distribution.get(3, 0.0),
                },
            )
        return _insufficient(
            disease,
            "Données insuffisantes : génotype de l'enfant inconnu et génotypes "
            "parentaux incomplets, impossible de calculer un risque alpha-thalassémique.",
        )

    if disease.is_xlinked:
        parent1 = parse_xlinked(genotype_parent1)
        parent2 = parse_xlinked(genotype_parent2)
        child = parse_xlinked(genotype_enfant, default_sex=sex)
        if child is not None:
            if sex is not None and child["sex"] != sex:
                raise GenotypeError(
                    f"Le génotype de l'enfant ({format_xlinked(child)}) est incompatible "
                    f"avec le sexe déclaré ({sex})."
                )
            status, probability = interpret_xlinked(child)
            return Prediction(
                disease=disease.id,
                status=status,
                probability=probability,
                method="genotype",
                genotype_enfant=format_xlinked(child),
                details={"sexe": child["sex"]},
            )
        if parent1 is not None and parent2 is not None:
            if parent1["sex"] == parent2["sex"]:
                raise GenotypeError(
                    "Pour une maladie liée à l'X, fournissez un père (XY) et une mère (XX)."
                )
            father = parent1 if parent1["sex"] == "M" else parent2
            mother = parent1 if parent1["sex"] == "F" else parent2
            distribution_all = child_distribution_xlinked(father, mother, None)
            distribution_male = child_distribution_xlinked(father, mother, "M")
            distribution_female = child_distribution_xlinked(father, mother, "F")
            if sex is None:
                distribution = distribution_all
                risk = _xlinked_risk(distribution_all, None)
            else:
                distribution = distribution_male if sex == "M" else distribution_female
                risk = _xlinked_risk(distribution, sex)
            details = {
                "pere": format_xlinked(father),
                "mere": format_xlinked(mother),
                "risques_par_sexe": {
                    "M": _xlinked_risk(distribution_male, "M"),
                    "F": _xlinked_risk(distribution_female, "F"),
                },
            }
            return Prediction(
                disease=disease.id,
                status="risque",
                probability=risk,
                method="mendelian",
                risk_distribution={
                    f"{child_sex}:{status}": probability
                    for (child_sex, status), probability in sorted(distribution.items())
                },
                details=details,
            )
        return _insufficient(
            disease,
            "Données insuffisantes : génotype de l'enfant inconnu et génotypes "
            "parentaux incomplets, impossible de calculer un risque lié à l'X.",
        )

    parent1 = parse_autosomal(genotype_parent1, disease)
    parent2 = parse_autosomal(genotype_parent2, disease)
    child = parse_autosomal(genotype_enfant, disease)

    if child is not None:
        status, probability = interpret_autosomal(child, disease)
        return Prediction(
            disease=disease.id,
            status=status,
            probability=probability,
            method="genotype",
            genotype_enfant=format_autosomal(child, disease),
            details={
                "genotype_parent1": format_autosomal(parent1, disease),
                "genotype_parent2": format_autosomal(parent2, disease),
            },
        )

    if parent1 is not None and parent2 is not None:
        distribution = child_distribution_autosomal(parent1, parent2)
        risk = sum(
            probability * interpret_autosomal(genotype, disease)[1]
            for genotype, probability in distribution.items()
        )
        return Prediction(
            disease=disease.id,
            status="risque",
            probability=risk,
            method="mendelian",
            risk_distribution={
                format_autosomal(genotype, disease): probability
                for genotype, probability in sorted(distribution.items())
            },
            details={
                "parents": {
                    "parent1": format_autosomal(parent1, disease),
                    "parent2": format_autosomal(parent2, disease),
                },
                "risque_maladie": risk,
                "risque_porteur": sum(
                    probability
                    for genotype, probability in distribution.items()
                    if interpret_autosomal(genotype, disease)[0]
                    in {"porteur", "porteuse", "porteur_im", "trait"}
                ),
            },
        )

    return _insufficient(
        disease,
        "Données insuffisantes : génotype de l'enfant inconnu et génotypes "
        "parentaux incomplets, impossible de calculer un risque mendélien.",
    )
