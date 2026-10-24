# Syndrome de Marfan

## Gène concerné
- **Gène** : *FBN1* (Fibrilline-1)
- **Chromosome** : 15q21.1
- **Position GRCh38** : chr15:48,700,000-48,950,000
- **Protéine** : Fibrilline-1 (glycoprotéine matrice extracellulaire, microfibrilles, régulation TGF-β)
- **Référence** : OMIM #154700, NM_000138.4

## Mode de transmission
**Autosomique dominante** — Un allèle muté suffit. **Pénétrance complète** (presque 100% à l'âge adulte), mais **expressivité variable** (intra- et inter-familiale). ~25-30% cas *de novo* (mutation nouvelle, parents sains).

## Types de mutations FBN1 (>3000 variantes décrites)

| Type | Fréquence | Mécanisme | Phénotype typique |
|------|-----------|-----------|-------------------|
| Missens (Cys-substitution) | ~40% | Perturbation liaison Ca²⁺/disulfure, folding incorrect | Classique, souvent sévère |
| Missens (autres) | ~25% | Dommage domaine EGF-like/TB | Variable |
| Nonsense / Frameshift | ~15% | Haploinsuffisance (NMD) | Souvent plus léger |
| Splicing | ~10% | Exon skipping, intron retention | Variable |
| Délétion/insertion partielle | ~5% | Dommage structural | Variable |
| Délétion génique complète | <1% | Haploinsuffisance | Phénotype complet |
| Mosaïcisme | Rare | Mutation post-zygotique | Phénotype segmentaire/atténué |

> **Corrélation génotype-phénotype imparfaite** : Même mutation = phénotypes différents dans une famille. Facteurs : modificateurs génétiques (*FBN2*, *TGFBR1/2*, *LTBP*), épigénétique, environnement.

## Critères diagnostiques (Ghent nosology 2010 révisé)

**Diagnostic confirmé si** :
1. **Antécédent familial** + **1 critère majeur** (cardiovasculaire, oculaire, squelettique) + **système 2ème atteint**
2. **Sans antécédent familial** : **2 critères majeurs** (différents systèmes) + **1 système 3ème atteint** + **mutation FBN1 pathogène**
3. **Mutation FBN1 connue** + **phénotype compatible** (même sans critères complets)

### Systèmes et critères majeurs
| Système | Critère majeur |
|---------|----------------|
| Cardiovasculaire | Dilatation racine aortique (Z-score ≥2) OU dissection aortique |
| Oculaire | Ectopie cristallinienne (luxation lentille) |
| Squelettique | ≥4 critères sur : dolichosténie, arachnodactylie, pectus excavatum/carinatum, scoliose >20°, protrusio acetabuli, etc. |

## Génotypes pour dataset

| Génotype | Statut | Probabilité phénotype Marfan | Notes |
|----------|--------|------------------------------|-------|
| WT / WT | Normal | 0% | - |
| WT / MUT (pathogène) | **Hétérozygote muté** | **~95-100%** (pénétrance complète à l'âge adulte) | Expressivité variable. 25-30% *de novo* |
| MUT / MUT | Homozygote (très rare) | 100% | Phénotype néonatal sévère, létal précoce |

> Pour dataset : binaire **mutation FBN1 pathogène présente (OUI/NON)**. Si OUI → probabilité maladie = 1.0 (pénétrance complète), mais sévérité variable.

## Probabilités de transmission

### Parent atteint (hétérozygote FBN1 muté) × Parent sain

| Enfant hérite allèle | Probabilité | Statut |
|---------------------|-------------|--------|
| Allèle muté | 0.50 | **Atteint** (pénétrance ~100%) |
| Allèle normal | 0.50 | Sain |

### Parent atteint × Parent atteint (très rare)
- 25% WT/WT → Sain
- 50% WT/MUT → Atteint
- 25% MUT/MUT → Sévère néonatal (souvent létal)

### Mutation *de novo* (parents sains)
- Probabilité mutation *de novo* par gamète : ~1.2 × 10⁻⁸ par base / génération
- Pour FBN1 (65 exons, ~230 kb) : taux ~1/10,000 - 1/20,000 naissances
- Enfant atteint, parents non porteurs → risque récurrence fratrie faible (~1% pour mosaïcisme parental gonadique)

## Fréquence dans la population

| Population | Prévalence (1/~) | Incidence (1/~) | Source |
|------------|------------------|-----------------|--------|
| Général (Caucasiens) | 1/5,000 - 1/10,000 | 1/15,000 - 1/20,000 | Orphanet, registres nationaux |
| Tous groupes ethniques | Similaire | Similaire | Pas d'effet fondateur majeur connu |

## Sources
- OMIM #154700 — Marfan Syndrome
- GeneReviews: Marfan Syndrome (Loeys & Dietz, 2023)
- Orphanet: ORPHA558 — Syndrome de Marfan
- Loeys BL et al. "The revised Ghent nosology for Marfan syndrome." J Med Genet 2010.
- Faivre L et al. "FBN1 mutations and genotype-phenotype correlations." Hum Mutat 2007.
- Judge DP, Dietz HC. "Marfan's syndrome." Lancet 2005.
- Registre Français Marfan (RFM) / Montalcino Aortic Consortium.