"""Tests du moteur mendélien déterministe."""

from __future__ import annotations

import pytest

from core.diseases import get_disease
from core.genetics import (
    GenotypeError,
    format_alpha,
    format_autosomal,
    format_xlinked,
    parse_alpha,
    parse_autosomal,
    parse_xlinked,
    predict,
)


def test_recessive_risk_from_two_carriers():
    prediction = predict("drepanocytose", "A/S", "A/S")
    assert prediction.status == "risque"
    assert prediction.probability == pytest.approx(0.25)
    assert prediction.method == "mendelian"
    assert prediction.risk_distribution == {
        "A/A": 0.25,
        "A/S": 0.5,
        "S/S": 0.25,
    }
    assert prediction.details["risque_porteur"] == pytest.approx(0.5)


def test_recessive_child_genotypes():
    assert predict("drepanocytose", "A/S", "A/S", "S/S").status == "malade"
    assert predict("drepanocytose", "A/S", "A/S", "S/S").probability == 1.0
    assert predict("drepanocytose", "A/S", "A/S", "A/S").status == "porteur"
    assert predict("drepanocytose", "A/S", "A/S", "A/S").probability == 0.0
    assert predict("drepanocytose", "A/S", "A/S", "A/A").status == "sain"
    assert predict("drepanocytose", "A/S", "A/S", "A/A").probability == 0.0


def test_compound_heterozygous_is_affected():
    prediction = predict("drepanocytose", "S/C", "A/A", "S/C")
    assert prediction.status == "malade"
    assert prediction.probability == 1.0


def test_recessive_affected_parent_and_carrier_parent():
    prediction = predict("drepanocytose", "S/C", "A/S")
    assert prediction.probability == pytest.approx(0.5)
    assert prediction.risk_distribution == {
        "A/C": 0.25,
        "A/S": 0.25,
        "C/S": 0.25,
        "S/S": 0.25,
    }


def test_single_pathogenic_allele_is_carrier_not_homozygous():
    disease = get_disease("mucoviscidose")
    assert parse_autosomal("MUT", disease) == ("A", "MUT")
    assert parse_autosomal("WT", disease) == ("A", "A")
    assert predict("mucoviscidose", "MUT", "A").probability == 0.0


def test_dominant_risk_and_child_status():
    prediction = predict("marfan", "WT", "MUT")
    assert prediction.probability == pytest.approx(0.5)
    assert prediction.risk_distribution == {"MUT": 0.5, "WT": 0.5}
    assert predict("marfan", "WT", "WT", "MUT").status == "malade"
    assert predict("marfan", "WT", "WT", "WT").status == "sain"
    assert predict("marfan", "MUT", "MUT").probability == pytest.approx(0.75)


def test_polycystic_kidney_disease_notation():
    prediction = predict("polykystose_renale", "PKD1:MUT", "PKD1:WT")
    assert prediction.probability == pytest.approx(0.5)
    assert predict("polykystose_renale", "PKD1:MUT", "PKD1:WT", "PKD1:MUT").status == "malade"
    assert predict("polykystose_renale", "PKD1:MUT", "PKD1:WT", "PKD1:WT").status == "sain"


def test_huntington_intermediate_and_reduced_penetrance():
    assert predict("huntington", "A/IM", "A/A", "A/IM").status == "porteur_im"
    assert predict("huntington", "A/IM", "A/A", "A/IM").probability == 0.0
    reduced = predict("huntington", "A/RP", "A/A", "A/RP")
    assert reduced.status == "a_risque"
    assert reduced.probability == pytest.approx(0.45)
    assert predict("huntington", "A/PP", "A/A", "A/PP").status == "malade"
    assert predict("huntington", "A/PP", "A/A", "A/PP").probability == 1.0


def test_huntington_parental_risk():
    assert predict("huntington", "A/RP", "A/A").probability == pytest.approx(0.225)
    assert predict("huntington", "A/RP", "A/RP").probability == pytest.approx(0.3375)
    intermediate = predict("huntington", "A/IM", "A/A")
    assert intermediate.probability == 0.0
    assert intermediate.details["risque_porteur"] == pytest.approx(0.5)
    assert predict("huntington", "A/A", "A/A").probability == 0.0


def test_xlinked_risk_depends_on_child_sex():
    male = predict("hemophilie_A", "XY:sain", "XX:porteuse", sexe_enfant="M")
    female = predict("hemophilie_A", "XY:sain", "XX:porteuse", sexe_enfant="F")
    unknown = predict("hemophilie_A", "XY:sain", "XX:porteuse")
    assert male.probability == pytest.approx(0.5)
    assert female.probability == 0.0
    assert unknown.probability == pytest.approx(0.25)
    assert male.details["risques_par_sexe"] == {"M": 0.5, "F": 0.0}


def test_xlinked_affected_father_transmits_carrier_status_to_daughters():
    prediction = predict("hemophilie_A", "XY:malade", "XX:saine", sexe_enfant="F")
    assert prediction.probability == 0.0
    assert prediction.risk_distribution == {"F:porteuse": 1.0}
    son = predict("hemophilie_A", "XY:malade", "XX:saine", sexe_enfant="M")
    assert son.probability == 0.0


def test_xlinked_affected_daughter_requires_affected_father_and_carrier_mother():
    prediction = predict("hemophilie_A", "XY:malade", "XX:porteuse", sexe_enfant="F")
    assert prediction.probability == pytest.approx(0.5)
    affected = predict("hemophilie_A", "XY:malade", "XX:malade", sexe_enfant="F")
    assert affected.probability == 1.0


def test_xlinked_child_genotype():
    assert predict("hemophilie_A", "XY:sain", "XX:porteuse", "XY:malade").status == "malade"
    assert predict("hemophilie_A", "XY:sain", "XX:porteuse", "XX:porteuse").status == "porteuse"
    assert predict("hemophilie_A", "XY:sain", "XX:porteuse", "XX:malade").status == "malade"


def test_xlinked_sex_mismatch_is_rejected():
    with pytest.raises(GenotypeError, match="incompatible"):
        predict("hemophilie_A", "XY:sain", "XX:porteuse", "XY:malade", "F")


def test_xlinked_requires_one_father_and_one_mother():
    with pytest.raises(GenotypeError):
        predict("hemophilie_A", "XY:sain", "XY:sain")


def test_alpha_distribution_and_statuses():
    carrier = predict("thalassemie_alpha", "AA/AA", "AA/A-")
    assert carrier.probability == 0.0
    assert carrier.risk_distribution == {"3": 0.5, "4": 0.5}
    assert predict("thalassemie_alpha", "AA/AA", "AA/A-", "3").status == "porteur"
    assert predict("thalassemie_alpha", "AA/AA", "AA/A-", "2").status == "trait"
    assert predict("thalassemie_alpha", "AA/AA", "AA/A-", "1").status == "malade"
    assert predict("thalassemie_alpha", "AA/AA", "AA/A-", "0").status == "malade"


def test_alpha_hbh_risk():
    prediction = predict("thalassemie_alpha", "A-/--", "A-/--")
    assert prediction.probability == pytest.approx(0.75)
    assert prediction.risk_distribution == {"0": 0.25, "1": 0.5, "2": 0.25}
    assert prediction.details["risque_trait"] == pytest.approx(0.25)


def test_alpha_invalid_genotypes():
    with pytest.raises(GenotypeError):
        predict("thalassemie_alpha", "AA/AA", "AA/AA", "5")
    with pytest.raises(GenotypeError):
        predict("thalassemie_alpha", "AA/AA/AA", "AA/AA")


def test_insufficient_data_returns_none_not_zero():
    prediction = predict("drepanocytose", "inconnu", "inconnu", "inconnu")
    assert prediction.status == "inconnu"
    assert prediction.probability is None
    assert prediction.method == "insufficient_data"
    one_parent = predict("drepanocytose", "A/S", "inconnu", "inconnu")
    assert one_parent.probability is None


def test_parsing_tolerates_spaces_and_concatenated_alleles():
    disease = get_disease("drepanocytose")
    assert parse_autosomal("A / S", disease) == ("A", "S")
    assert parse_autosomal("AS", disease) == ("A", "S")
    assert parse_autosomal("S", disease) == ("A", "S")
    assert parse_autosomal("A~S", disease) == ("A", "S")
    with pytest.raises(GenotypeError):
        parse_autosomal("A/X", disease)


def test_xlinked_and_alpha_parsing():
    assert parse_xlinked("XY:malade") == {"sex": "M", "status": "malade"}
    assert parse_xlinked("malade", default_sex="M") == {"sex": "M", "status": "malade"}
    assert parse_xlinked("XX:porteuse") == {"sex": "F", "status": "porteuse"}
    assert parse_xlinked("inconnu") is None
    assert parse_alpha("AA/A-") == ("AA", "A-")
    assert parse_alpha("3") == ("AA", "A-")
    assert parse_alpha("--/--") == ("--", "--")


def test_formatting_helpers():
    disease = get_disease("drepanocytose")
    assert format_autosomal(("A", "S"), disease) == "A/S"
    assert format_xlinked({"sex": "M", "status": "malade"}) == "XY:malade"
    assert format_alpha(("AA", "A-")) == "AA/A-"
    assert format_autosomal(None, disease) == "inconnu"
