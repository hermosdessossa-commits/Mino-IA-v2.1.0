# Thalassémie α

## Gènes concernés
- **HBA1** : Hémoglobine alpha-1 — Chromosome 16p13.3 (chr16:177,000-182,000)
- **HBA2** : Hémoglobine alpha-2 — Chromosome 16p13.3 (chr16:172,000-177,000)
- **Référence** : OMIM #141800, #141850
- **Note** : Deux gènes α par chromosome 16 → 4 allèles α au total par individu (αα/αα)

## Mode de transmission
**Autosomique récessive** — Mais dosage génique : la sévérité dépend du **nombre d'allèles α fonctionnels restants** (0 à 4).

## Types de mutations
| Type | Description | Notation | Effet |
|------|-------------|----------|-------|
| Déletion α⁺ | Perte d'un gène α (HBA1 ou HBA2) | -α/αα | 3 allèles fonctionnels |
| Déletion α⁰ | Perte des deux gènes α sur un chromosome | --/αα | 2 allèles fonctionnels |
| Mutation non-déletionnelle | Mutation ponctuelle (ex: Hb Constant Spring) | αᴺ/αα | 3 allèles (mais α instable) |

## Génotypes et phénotypes (selon nombre allèles α fonctionnels)

| Allèles α fonctionnels | Génotype (notation) | Phénotype | Description clinique |
|------------------------|---------------------|-----------|---------------------|
| 4 | αα/αα (WT) | Normal | HbA 95-98%, HbA₂ 2-3%, HbF <1% |
| 3 | -α/αα (hétérozygote α⁺) | Porteur silencieux / Trait α-thal mineur | Asymptomatique. Microcytose légère (MCV 70-80 fl). HbH <1% |
| 2 | --/αα (hétérozygote α⁰) OU -α/-α (homozygote α⁺) | Trait α-thalassémique (mineur) | Microcytose modérée (MCV 60-70 fl), anémie légère. HbH 1-5% |
| 1 | --/-α (hétérozygote composé α⁰/α⁺) | Maladie HbH | Anémie hémolytique modérée à sévère, splénomégalie, ictère, surcharge ferrique. HbH 10-40%. Nécessite transfusions occasionnelles |
| 0 | --/-- (homozygote α⁰) | Hydrops foetalis (Bart's) | Incompatible avec la vie. Hb Bart's (γ₄) 80-90%. Avortement tardif ou mort néonatale sans transfusion in utero |

## Allèles fréquents par population

| Population | α⁺ (-α) freq | α⁰ (--) freq | Hb Constant Spring freq |
|------------|--------------|--------------|------------------------|
| Afrique sub-saharienne | 0.20-0.30 | <0.01 | Rare |
| Méditerranée (Grèce, Chypre, Turquie) | 0.02-0.05 | 0.01-0.03 | Rare |
| Moyen-Orient | 0.03-0.08 | 0.01-0.02 | Rare |
| Asie du Sud-Est (Thaïlande, Malaisie) | 0.15-0.25 | 0.01-0.05 | 0.01-0.03 (Constant Spring) |
| Chine du Sud | 0.10-0.20 | 0.01-0.03 | 0.02-0.05 |
| Europe du Nord | <0.01 | <0.001 | Rare |

## Probabilités de transmission

### Notation simplifiée pour dataset
- **AAAA** : 4 allèles fonctionnels (normal)
- **AAA-** : 3 allèles (porteur silencieux, α⁺ het)
- **AA--** : 2 allèles (trait α-thal, α⁰ het OU α⁺ hom)
- **A---** : 1 allèle (maladie HbH)
- **----** : 0 allèle (hydrops foetalis)

### Table de transmission (simplifiée : on considère le nombre d'allèles fonctionnels transmis par chaque parent)

Chaque parent transmet 2 allèles (un par chromosome 16). Le nombre d'allèles fonctionnels transmis suit une distribution hypergéométrique selon son propre génotype.

| Parent 1 (allèles fonct.) | Parent 2 (allèles fonct.) | Enfant: 4 | Enfant: 3 | Enfant: 2 | Enfant: 1 | Enfant: 0 |
|---------------------------|---------------------------|-----------|-----------|-----------|-----------|-----------|
| 4 (AAAA) | 4 (AAAA) | 1.0 | 0 | 0 | 0 | 0 |
| 4 | 3 (AAA-) | 0.5 | 0.5 | 0 | 0 | 0 |
| 4 | 2 (AA--) | 0 | 1.0 | 0 | 0 | 0 |
| 4 | 1 (A---) | 0 | 0 | 1.0 | 0 | 0 |
| 4 | 0 (----) | 0 | 0 | 0 | 1.0 | 0 |
| 3 | 3 | 0.25 | 0.5 | 0.25 | 0 | 0 |
| 3 | 2 | 0 | 0.5 | 0.5 | 0 | 0 |
| 3 | 1 | 0 | 0 | 0.5 | 0.5 | 0 |
| 3 | 0 | 0 | 0 | 0 | 1.0 | 0 |
| 2 | 2 | 0 | 0.25 | 0.5 | 0.25 | 0 |
| 2 | 1 | 0 | 0 | 0.25 | 0.5 | 0.25 |
| 2 | 0 | 0 | 0 | 0 | 0.5 | 0.5 |
| 1 | 1 | 0 | 0 | 0 | 0.25 | 0.75 |
| 1 | 0 | 0 | 0 | 0 | 0 | 1.0 |
| 0 | 0 | 0 | 0 | 0 | 0 | 1.0 |

> **Note importante** : Un parent avec 2 allèles fonctionnels peut être soit --/αα (α⁰ het) soit -α/-α (α⁺ hom). La transmission est identique (transmet 1 allèle fonct. en moyenne), mais le risque de HbH diffère si l'autre parent a une α⁰ deletion. Pour simplicité dataset : on utilise le nombre d'allèles fonctionnels uniquement.

## Sources
- OMIM #141800, #141850 — Alpha-Thalassemia
- GeneReviews: Alpha-Thalassemia (Harteveld & Higgs, 2023)
- Orphanet: ORPHA853 — Alpha-thalassémie
- Weatherall DJ. "The thalassemias." Blood 2018.
- Harteveld CL, Higgs DR. "Alpha-thalassaemia." Orphanet J Rare Dis 2010.