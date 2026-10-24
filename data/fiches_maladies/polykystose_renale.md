# Polykystose Rénale Autosomique Dominante (ADPKD)

## Gènes concernés
| Gène | Chromosome | Position GRCh38 | Protéine | % cas | Référence |
|------|------------|-----------------|----------|-------|-----------|
| **PKD1** | 16p13.3 | chr16:2,070,000-2,120,000 | Polycystine-1 | **~85%** | OMIM #601313, NM_000296.4 |
| **PKD2** | 4q22.1 | chr4:89,100,000-89,200,000 | Polycystine-2 | **~15%** | OMIM #173910, NM_000297.3 |

## Mode de transmission
**Autosomique dominante** — Un allèle muté suffit. **Pénétrance quasi-complète** à l'âge adulte (>95% à 80 ans), mais **expressivité variable** (âge début, sévérité rénale, extra-rénale). **Pas de corrélation génotype-phénotype forte** au niveau individuel (même mutation, phénotypes différents), mais différences statistiques PKD1 vs PKD2.

## Gènes et phénotypes

| Paramètre | PKD1 | PKD2 |
|-----------|------|------|
| Âge médian ESRD (stade terminal) | ~55 ans | ~75 ans |
| Taille kystes / nombre | Plus nombreux, plus gros | Moins nombreux, plus petits |
| Hypertension (prévalence) | ~80% avant 35 ans | ~60% avant 45 ans |
| Kystes hépatiques | Fréquents, plus gros | Fréquents, plus petits |
| Anévrismes intracrâniens | ~10-12% | ~6-8% |
| Valvulopathies (MVP, regurg mitral) | ~25% | ~15% |
| Hérnies inguinales / diverticules | Fréquents | Fréquents |

## Types de mutations

| Type | PKD1 | PKD2 |
|------|------|------|
| Truncantes (nonsense, frameshift, splicing canonique) | ~60% | ~50% |
| Missense | ~30% | ~40% |
| Délétions/insertions partielles | ~10% | ~10% |
| Mosaïcisme | Rare | Rare |

> **Note** : PKD1 a 6 pseudogènes homologues (PKD1P1-6) → analyses complexes (NGS ciblé ou long-read requis). PKD2 plus simple.

## Génotypes pour dataset

| Gène | Génotype | Statut | Probabilité phénotype ADPKD | Âge médian ESRD |
|------|----------|--------|----------------------------|-----------------|
| PKD1 | WT / WT | Normal | 0% | - |
| PKD1 | WT / MUT | **Hétérozygote PKD1** | **~99%** (pénétrance quasi-complète) | ~55 ans |
| PKD2 | WT / MUT | **Hétérozygote PKD2** | **~95%** (pénétrance légèrement réduite) | ~75 ans |
| PKD1 | MUT / MUT | Homozygote (rare) | Létal périnatal / néonatal | - |
| PKD2 | MUT / MUT | Homozygote (rare) | Phénotype sévère néonatal | - |

> **Pour dataset simplifié** : on modélise **un seul gène causal par famille** (PKD1 OU PKD2). Probabilité mutation PKD1 = 0.85, PKD2 = 0.15. Binaire : mutation présente OUI/NON + gène concerné.

## Probabilités de transmission

### Parent atteint (hétérozygote PKD1 ou PKD2) × Parent sain

| Enfant hérite allèle | Probabilité | Statut |
|---------------------|-------------|--------|
| Allèle muté (PKD1 ou PKD2) | 0.50 | **Atteint** (pénétrance ~95-99%) |
| Allèle normal | 0.50 | Sain |

### Mutation *de novo*
- Taux *de novo* estimé : **~5-10% des cas** (plus faible que NF1)
- Enfant atteint, parents sains → risque récurrence fratrie : **~1-2%** (mosaïcisme gonadique parental possible)

### Parent PKD1 muté × Parent PKD2 muté (extrêmement rare)
- 25% PKD1 mut / PKD2 WT → Phénotype PKD1
- 25% PKD1 WT / PKD2 mut → Phénotype PKD2
- 25% PKD1 mut / PKD2 mut → **Double hétérozygote** (phénotype très sévère, ESRD précoce ~30-40 ans)
- 25% WT/WT → Sain

## Fréquence dans la population

| Population | Prévalence (1/~) | PKD1 % | PKD2 % | Source |
|------------|------------------|--------|--------|--------|
| Général (Caucasiens) | 1/400 - 1/1,000 | 85% | 15% | Registres dialyse, études populationnelles |
| Japon | 1/1,000 - 1/2,000 | 70% | 30% | Études japonaises (PKD2 plus fréquent) |
| Afrique | Similaire | 80% | 20% | Données limitées |

## Critères diagnostiques (Pei et al. / Unified criteria 2009)

**Individu à risque (parent atteint) — Nombre kystes rénaux total (deux reins) par âge :**

| Âge | PKD1 : Kystes pour diagnostic | PKD2 : Kystes pour diagnostic |
|-----|-------------------------------|-------------------------------|
| 15-29 ans | ≥2 | ≥2 |
| 30-39 ans | ≥2 | ≥2 |
| 40-59 ans | ≥2 | ≥2 |
| ≥60 ans | ≥4 | ≥2 |

**Exclusion** : Si < critères ci-dessus à âge donné → ADPKD exclu (sensibilité >95% pour PKD1, ~85% PKD2).

## Sources
- OMIM #173900 (PKD1), #613095 (PKD2) — Polycystic Kidney Disease, Autosomal Dominant
- GeneReviews: Autosomal Dominant Polycystic Kidney Disease (Harris & Torres, 2023)
- Orphanet: ORPHA731 — Polykystose rénale autosomique dominante
- Pei Y et al. "Unified criteria for ultrasonographic diagnosis of ADPKD." JASN 2009.
- Harris PC, Torres VE. "Polycystic kidney disease." Annu Rev Med 2023.
- Cornec-Le Gall E et al. "Type of PKD1 mutation influences renal outcome." JASN 2013.
- Audit Français ADPKD / Registre ADPKD (KDIGO).