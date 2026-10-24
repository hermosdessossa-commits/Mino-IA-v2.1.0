# Maladie de Huntington

## Gène concerné
- **Gène** : *HTT* (Huntingtine)
- **Chromosome** : 4p16.3
- **Position GRCh38** : chr4:3,074,000-3,244,000
- **Mutation** : Expansion de répétitions **CAG** dans l'exon 1 (codant polyglutamine)
- **Protéine** : Huntingtine (protéine ubiquitinaire, fonction neuroprotectrice)
- **Référence** : OMIM #143100, NM_002111.8

## Mode de transmission
**Autosomique dominante à pénétrance complète (selon taille expansion)** — Un seul allèle étendu suffit. Phénomène d'**anticipation** : expansion lors de la méiose (surtout transmission paternelle) → début plus précoce, plus sévère chez la descendance.

## Allèles selon nombre de répétitions CAG

| Répétitions CAG | Allèle | Statut | Pénétrance | Âge moyen début | Transmission |
|-----------------|--------|--------|------------|-----------------|--------------|
| **< 27** | Normal | Non pathogène | 0% | - | Stable |
| **27-35** | Intermédiaire (IM) | Non pathogène* | 0% | - | **Instable** : peut s'étendre vers pathogène à la méiose (surtout paternelle) |
| **36-39** | **Réduit pénétrance (RP)** | Pathogène à pénétrance réduite | ~30-60% (âge-dépendante) | >60 ans si symptomatique | Instable, expansion possible |
| **≥ 40** | **Pleinement pénétrant (PP)** | Pathogène | **100%** (à vie suffisante) | 35-45 ans (moyenne) | Très instable, forte expansion paternelle |

> **Note** : 36-39 = "zone grise". Certains restent asymptomatiques toute leur vie. Pénétrance à 65 ans ~40%, à 80 ans ~60-80%.

## Corrélation CAG / Âge début (modèle prédictif)

| CAG | Âge médian début (ans) | Intervalle 95% |
|-----|------------------------|----------------|
| 40 | ~55 | 40-70 |
| 41 | ~50 | 35-65 |
| 42 | ~45 | 30-60 |
| 43 | ~42 | 28-55 |
| 44 | ~38 | 25-50 |
| 45 | ~35 | 22-48 |
| 46 | ~32 | 20-44 |
| 47 | ~30 | 18-42 |
| 48 | ~28 | 16-40 |
| 49 | ~26 | 15-38 |
| 50 | ~24 | 14-35 |
| 55 | ~15 | 8-25 |
| 60 | ~10 | 5-18 |
| >60 | **Forme juvénile** | <20 ans |

Formule approximative (Langbehn et al. 2004) :
```
Âge début ≈ exp(9.556 - 0.146 × CAG)  [ans]
```
R² ≈ 0.70. Grande variabilité interindividuelle (facteurs modificateurs : *MSH3*, *FAN1*, *RRM2B*, etc.).

## Génotypes pour dataset

| Allèle 1 (CAG) | Allèle 2 (CAG) | Statut | Risque développer maladie |
|----------------|----------------|--------|---------------------------|
| <27 | <27 | Normal | 0% |
| <27 | 27-35 (IM) | Porteur IM | 0% (mais risque expansion descendance) |
| <27 | 36-39 (RP) | **À risque** | 30-60% (âge-dépendant) |
| <27 | ≥40 (PP) | **Atteint** | 100% |
| 27-35 | 27-35 | IM homozygote | 0% |
| 27-35 | 36-39 | À risque (RP) | 30-60% |
| 27-35 | ≥40 | Atteint | 100% |
| 36-39 | 36-39 | RP homozygote | 30-60% (plus précoce possible) |
| 36-39 | ≥40 | Atteint | 100% |
| ≥40 | ≥40 | PP homozygote | 100% (pas plus sévère que hétérozygote) |

> **Point clé** : L'homozygotie pour allèle PP ne change pas la sévérité vs hétérozygote (pas d'effet de dose). L'âge début corrèle avec l'allèle le plus long.

## Probabilités de transmission (expansion méiotique)

### Modèle d'expansion (basé sur données empiriques)

| Allèle parent | Transmission maternelle | Transmission paternelle |
|---------------|------------------------|-------------------------|
| **Normal (<27)** | Stable (±1) | Stable (±1) |
| **IM (27-35)** | Expansion rare (+1 à +5) | Expansion modérée (+1 à +10, peut atteindre ≥36) |
| **RP (36-39)** | Expansion modérée (±5) | Expansion marquée (+5 à +20, souvent ≥40) |
| **PP (≥40)** | Expansion modérée (±10) | **Forte expansion** (+10 à +50, forme juvénile possible) |

### Probabilités simplifiées pour dataset

Pour un parent atteint (CAG ≥40) × parent sain (<27) :
- **50%** enfant hérite allèle normal → **sain**
- **50%** enfant hérite allèle étendu → **atteint**
  - CAG enfant = CAG parent + Δ (expansion)
  - Δ maternel : distribution centrée sur +5 (écart-type ~8)
  - Δ paternel : distribution centrée sur +15 (écart-type ~15), queue longue

Pour un parent IM (27-35) × parent sain :
- 50% hérite IM → risque expansion descendance future
- 50% hérite normal

## Fréquence dans la population

| Population | Prévalence (1/~) | Fréquence allèle ≥36 | Source |
|------------|------------------|----------------------|--------|
| Europe (Caucasiens) | 1/10,000 - 1/20,000 | ~0.0005 | Euro-HD Network |
| Amérique du Nord (Caucasiens) | 1/10,000 - 1/15,000 | ~0.0007 | HDSA |
| Japon | 1/100,000 - 1/500,000 | ~0.00005 | Études japonaises |
| Afrique sub-saharienne | Très rare | <0.00001 | Études limitées |
| Amérindiens (Venezuela, lac Maracaibo) | 1/1,000 (cluster) | Cluster familial | Études fondatrices |

## Sources
- OMIM #143100 — Huntington Disease
- GeneReviews: Huntington Disease (Roos, 2023)
- Orphanet: ORPHA399 — Maladie de Huntington
- Langbehn DR et al. "CAG-repeat length predicts age of onset." Am J Hum Genet 2004.
- MacDonald ME et al. "Huntington disease." Nat Rev Dis Primers 2021.
- Genetic Modifiers of Huntington's Disease (GeM-HD) Consortium.
- European Huntington's Disease Network (EHDN) Registry.