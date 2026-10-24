"""Registre central des maladies génétiques supportées.

Ce module est la source unique de vérité pour les identifiants, les noms, les
modes de transmission et les allèles connus. L'API, le générateur de dataset et
le script d'entraînement doivent tous passer par ce registre.
"""

from __future__ import annotations

import re
import unicodedata
from dataclasses import dataclass


@dataclass(frozen=True)
class Disease:
    """Description d'une maladie supportée."""

    id: str
    name: str
    transmission: str
    normal_alleles: tuple[str, ...] = ()
    pathogenic_alleles: tuple[str, ...] = ()
    intermediate_alleles: tuple[str, ...] = ()
    aliases: tuple[str, ...] = ()
    description: str = ""

    @property
    def is_dominant(self) -> bool:
        return self.transmission == "autosomal_dominant"

    @property
    def is_recessive(self) -> bool:
        return self.transmission == "autosomal_recessive"

    @property
    def is_xlinked(self) -> bool:
        return self.transmission == "xlinked_recessive"

    @property
    def is_alpha(self) -> bool:
        return self.transmission == "alpha_dosage"


DISEASES: dict[str, Disease] = {
    "drepanocytose": Disease(
        id="drepanocytose",
        name="Drépanocytose",
        transmission="autosomal_recessive",
        normal_alleles=("A",),
        pathogenic_alleles=("S", "C"),
        aliases=("sickle_cell", "sickle_cell_disease", "drepanocytose"),
        description="Maladie de l'hémoglobine liée au gène HBB.",
    ),
    "mucoviscidose": Disease(
        id="mucoviscidose",
        name="Mucoviscidose",
        transmission="autosomal_recessive",
        normal_alleles=("A",),
        pathogenic_alleles=("MUT",),
        aliases=("cystic_fibrosis", "cf", "mucoviscidose"),
        description="Maladie liée au gène CFTR.",
    ),
    "thalassemie_alpha": Disease(
        id="thalassemie_alpha",
        name="Thalassémie alpha",
        transmission="alpha_dosage",
        aliases=("alpha_thalassemia", "thalassemie_a", "thalassemie_alpha"),
        description="Dosage des quatre gènes alpha (HBA1/HBA2).",
    ),
    "thalassemie_beta": Disease(
        id="thalassemie_beta",
        name="Thalassémie bêta",
        transmission="autosomal_recessive",
        normal_alleles=("A",),
        pathogenic_alleles=("B0", "B+"),
        aliases=("beta_thalassemia", "thalassemie_b", "thalassemie_beta"),
        description="Maladie liée au gène HBB.",
    ),
    "phenylcetonurie": Disease(
        id="phenylcetonurie",
        name="Phénylcétonurie",
        transmission="autosomal_recessive",
        normal_alleles=("A",),
        pathogenic_alleles=("SEV", "MILD"),
        aliases=("phenylketonuria", "pku", "phenylcetonurie", "phenylcetonurie"),
        description="Maladie liée au gène PAH.",
    ),
    "amyotrophie_spinale": Disease(
        id="amyotrophie_spinale",
        name="Amyotrophie spinale",
        transmission="autosomal_recessive",
        normal_alleles=("OK",),
        pathogenic_alleles=("DEL",),
        aliases=("sma", "spinal_muscular_atrophy", "amyotrophie_spinale"),
        description="Maladie liée aux gènes SMN1/SMN2.",
    ),
    "huntington": Disease(
        id="huntington",
        name="Maladie de Huntington",
        transmission="autosomal_dominant",
        normal_alleles=("A",),
        pathogenic_alleles=("PP", "RP"),
        intermediate_alleles=("IM",),
        aliases=("hd", "maladie_de_huntington", "huntington"),
        description="Expansion CAG du gène HTT.",
    ),
    "marfan": Disease(
        id="marfan",
        name="Syndrome de Marfan",
        transmission="autosomal_dominant",
        normal_alleles=("WT",),
        pathogenic_alleles=("MUT",),
        aliases=("syndrome_de_marfan", "marfan"),
        description="Maladie liée au gène FBN1.",
    ),
    "neurofibromatose1": Disease(
        id="neurofibromatose1",
        name="Neurofibromatose de type 1",
        transmission="autosomal_dominant",
        normal_alleles=("WT",),
        pathogenic_alleles=("MUT",),
        aliases=("nf1", "neurofibromatose_1", "neurofibromatose1"),
        description="Maladie liée au gène NF1.",
    ),
    "polykystose_renale": Disease(
        id="polykystose_renale",
        name="Polykystose rénale autosomique dominante",
        transmission="autosomal_dominant",
        normal_alleles=("WT",),
        pathogenic_alleles=("MUT",),
        aliases=("pkd", "adpkd", "polykystose_renale_ad", "polykystose_renale"),
        description="Maladie liée aux gènes PKD1/PKD2.",
    ),
    "hemophilie_A": Disease(
        id="hemophilie_A",
        name="Hémophilie A",
        transmission="xlinked_recessive",
        aliases=("hemophilia_a", "hemophilie_a", "hemophilie_a"),
        description="Déficit en facteur VIII lié au gène F8.",
    ),
    "hemophilie_B": Disease(
        id="hemophilie_B",
        name="Hémophilie B",
        transmission="xlinked_recessive",
        aliases=("hemophilia_b", "hemophilie_b", "hemophilie_b"),
        description="Déficit en facteur IX lié au gène F9.",
    ),
}

DISEASE_IDS: tuple[str, ...] = tuple(DISEASES)

STATUS_VALUES: tuple[str, ...] = (
    "sain",
    "saine",
    "porteur",
    "porteuse",
    "porteur_im",
    "a_risque",
    "trait",
    "malade",
    "risque",
    "inconnu",
)

TRANSMISSION_LABELS: dict[str, str] = {
    "autosomal_recessive": "autosomique récessive",
    "autosomal_dominant": "autosomique dominante",
    "xlinked_recessive": "liée à l'X récessive",
    "alpha_dosage": "dosage génique (alpha-thalassémie)",
}


def _strip_accents(value: str) -> str:
    return "".join(
        char for char in unicodedata.normalize("NFKD", value) if not unicodedata.combining(char)
    )


def _key(value: str) -> str:
    value = _strip_accents(value).strip().lower()
    value = re.sub(r"[^a-z0-9]+", "_", value)
    return re.sub(r"_+", "_", value).strip("_")


def _build_alias_index() -> dict[str, str]:
    index: dict[str, str] = {}
    for disease_id, disease in DISEASES.items():
        for candidate in (disease_id, disease.name, *disease.aliases):
            index[_key(candidate)] = disease_id
    return index


_ALIAS_INDEX = _build_alias_index()


def normalize_disease_id(value: str) -> str:
    """Normalise un nom de maladie vers son identifiant canonique.

    Accepte les accents, les espaces, les tirets, les majuscules et les alias
    courants (« Hémophilie A », « NF1 », « PKU », etc.).
    """

    if not isinstance(value, str) or not value.strip():
        raise ValueError("Le nom de la maladie est obligatoire.")
    key = _key(value)
    if key in _ALIAS_INDEX:
        return _ALIAS_INDEX[key]
    raise ValueError(
        f"Maladie non supportée : {value!r}. "
        f"Maladies disponibles : {', '.join(sorted(DISEASE_IDS))}."
    )


def get_disease(value: str) -> Disease:
    """Retourne la description canonique d'une maladie."""

    return DISEASES[normalize_disease_id(value)]
