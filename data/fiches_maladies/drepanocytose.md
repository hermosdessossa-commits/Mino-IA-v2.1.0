# Drépanocytose (Maladie drépanocytaire)

## Gène concerné
- **Gène** : *HBB* (Hémoglobine sous-unité bêta)
- **Chromosome** : 11p15.4
- **Position GRCh38** : chr11:5,227,001-5,227,500
- **Protéine** : Hémoglobine bêta-globine
- **Référence** : OMIM #603903, NM_000518.5

## Mode de transmission
**Autosomique récessive** — Les deux allèles doivent être mutés pour exprimer la maladie. Les hétérozygotes sont porteurs asymptomatiques (sauf conditions extrêmes : déshydratation sévère, haute altitude).

## Allèles principaux
| Allèle | Mutation | Notation | Fréquence (Afrique sub-saharienne) | Fréquence (Méditerranée) |
|--------|----------|----------|-----------------------------------|--------------------------|
| HbA (normal) | — | A | ~0.85-0.95 | ~0.98 |
| HbS (drépanocytaire) | Glu6Val (GAG→GTG) | S | ~0.05-0.15 | ~0.01-0.05 |
| HbC | Glu6Lys (GAG→AAG) | C | ~0.01-0.05 | Rare |
| HbE | Glu26Lys | E | Rare | Rare (Asie du Sud-Est) |
| HbD-Punjab | Glu121Gln | D | Rare | Rare |

## Génotypes possibles et interprétation clinique

| Génotype | Phénotype | Sévérité | Description clinique |
|----------|-----------|----------|---------------------|
| AA | Sain | Aucune | Hémoglobine normale (HbA₂ > 95%) |
| AS | Porteur (trait drépanocytaire) | Asymptomatique* | ~40% HbS, 60% HbA. Résistance au paludisme. *Crises possibles en conditions extrêmes |
| SS | Drépanocytose homozygote (SS) | Sévère | Anémie hémolytique chronique, crises vaso-occlusives, syndrome thoracique aigu, AVC, infections récurrentes. Espérance de vie réduite sans prise en charge |
| AC | Porteur HbC | Asymptomatique | ~40% HbC, 60% HbA. Rarement symptomatique |
| SC | Drépanocytose hétérozygote composé (SC) | Modérée à sévère | ~50% HbS, 50% HbC. Phénotype intermédiaire : anémie moins sévère que SS, mais crises vaso-occlusives, rétinopathie proliférative, nécrose aseptique fémorale |
| CC | Maladie HbC homozygote | Légère | Anémie hémolytique légère, splénomégalie. Pas de crises vaso-occlusives typiques |
| SD | Drépanocytose SD | Modérée à sévère | Similaire à SC |
| SE | Drépanocytose SE | Variable | Rare |

> **Note** : Pour ce projet, on couvre les 6 génotypes principaux : AA, AS, SS, AC, SC, CC. Les variantes rares (D, E, O-Arab) sont regroupées en "autres variants" avec probabilité faible.

## Probabilités de transmission (lois de Mendel)

### Croisements parentaux → Probabilités génotypes enfant

| Parent 1 | Parent 2 | AA | AS | SS | AC | SC | CC |
|----------|----------|----|----|----|----|----|----|
| AA | AA | 1.0 | 0 | 0 | 0 | 0 | 0 |
| AA | AS | 0.5 | 0.5 | 0 | 0 | 0 | 0 |
| AA | SS | 0 | 1.0 | 0 | 0 | 0 | 0 |
| AA | AC | 0.5 | 0 | 0 | 0.5 | 0 | 0 |
| AA | SC | 0 | 0.5 | 0 | 0 | 0.5 | 0 |
| AA | CC | 0 | 0 | 0 | 1.0 | 0 | 0 |
| AS | AS | 0.25 | 0.5 | 0.25 | 0 | 0 | 0 |
| AS | SS | 0 | 0.5 | 0.5 | 0 | 0 | 0 |
| AS | AC | 0.25 | 0.25 | 0 | 0.25 | 0.25 | 0 |
| AS | SC | 0 | 0.25 | 0.25 | 0 | 0.25 | 0.25 |
| AS | CC | 0 | 0 | 0 | 0.5 | 0.5 | 0 |
| SS | SS | 0 | 0 | 1.0 | 0 | 0 | 0 |
| SS | AC | 0 | 0.5 | 0 | 0 | 0.5 | 0 |
| SS | SC | 0 | 0 | 0.5 | 0 | 0.5 | 0 |
| SS | CC | 0 | 0 | 0 | 0 | 1.0 | 0 |
| AC | AC | 0.25 | 0 | 0 | 0.5 | 0 | 0.25 |
| AC | SC | 0 | 0 | 0 | 0.25 | 0.25 | 0.5 |
| AC | CC | 0 | 0 | 0 | 0.5 | 0 | 0.5 |
| SC | SC | 0 | 0 | 0.25 | 0 | 0.5 | 0.25 |
| SC | CC | 0 | 0 | 0 | 0 | 0.5 | 0.5 |
| CC | CC | 0 | 0 | 0 | 0 | 0 | 1.0 |

## Fréquences alléliques par population (pour simulation réaliste)

| Population | Fréquence HbS | Fréquence HbC | Source |
|------------|---------------|---------------|--------|
| Afrique de l'Ouest (Yoruba) | 0.12 | 0.03 | 1000 Genomes |
| Afrique Centrale (Bantu) | 0.10 | 0.02 | 1000 Genomes |
| Caraïbes | 0.08 | 0.02 | Études locales |
| Méditerranée (Grèce, Sicile, Turquie) | 0.02-0.05 | <0.01 | Orphanet |
| Europe du Nord | <0.001 | <0.001 | gnomAD |
| Amérique du Nord (Afro-américains) | 0.07 | 0.02 | NHANES |

## Sources
- OMIM #603903 — Hemoglobin S
- GeneReviews: Sickle Cell Disease (Piel et al., 2017)
- Orphanet: ORPHA232 — Drépanocytose
- ClinVar: VCV000002275 (HbS), VCV000002276 (HbC)
- Piel FB et al. "Global burden of sickle cell disease." Lancet 2017.
- Rees DC et al. "Sickle cell disease." Lancet 2010.