# Neurofibromatose Type 1 (NF1 - Maladie de von Recklinghausen)

## Gène concerné
- **Gène** : *NF1* (Neurofibromine 1)
- **Chromosome** : 17q11.2
- **Position GRCh38** : chr17:29,500,000-29,800,000
- **Protéine** : Neurofibromine (GAP pour RAS, suppresseur de tumeur, régulation signalisation RAS/MAPK)
- **Référence** : OMIM #162200, NM_000267.3

## Mode de transmission
**Autosomique dominante** — Un allèle muté suffit. **Pénétrance complète** (quasi 100% à l'âge adulte), **expressivité très variable** (même mutation, phénotypes très différents). ~50% cas *de novo* (mutation nouvelle, parents sains).

## Types de mutations NF1 (>3000 variantes décrites)

| Type | Fréquence | Mécanisme | Notes |
|------|-----------|-----------|-------|
| Nonsense / Frameshift | ~40-50% | Haploinsuffisance (NMD) | Phénotype classique |
| Délétion génique complète (1.4 Mb) | ~5-10% | Haploinsuffisance + gènes voisins | **Phénotype plus sévère** : retard mental, dysmorphisme facial, neurofibromes plexiformes multiples, risque MPNST ↑ |
| Splicing | ~10-15% | Exon skipping | Variable |
| Missense | ~10-15% | Fonction résiduelle partielle | Souvent plus léger (ex: p.Arg1809Cys → phénotype "spinal" / sans neurofibromes cutanés) |
| Délétion/insertion partielle | ~5% | Dommage structural | Variable |
| Mosaïcisme | ~10-20% des *de novo* | Mutation post-zygotique | Phénotype segmentaire / atténué |

> **Corrélation génotype-phénotype limitée** :
> - Délétion 1.4 Mb → phénotype sévère (retard mental, neurofibromes plexiformes précoces, risque MPNST 10-15%)
> - Missense p.Arg1809Cys / p.Arg1809His → "NF1 spinal" ou "NF1 sans neurofibromes cutanés" (phénotype atténué)
> - Majority des mutations → phénotype classique variable

## Critères diagnostiques (NIH Consensus 1987, toujours standard)

**Diagnostic si ≥2 critères présents** :
1. **≥6 taches café-au-lait** (>5 mm prépubère, >15 mm postpubère)
2. **≥2 neurofibromes cutanés** (ou 1 neurofibrome plexiforme)
3. **Éphelides axillaires/inguinales** (taches de rousseur)
4. **Gliome optique** (voie visuelle)
5. **≥2 hamartomes de Lisch** (nodules iris)
6. **Lésion osseuse caractéristique** (dysplasie sphénoïde, amincissement cortical tibia)
7. **Parent au 1er degré atteint** (critère familial)

## Génotypes pour dataset

| Génotype | Statut | Probabilité phénotype NF1 | Notes |
|----------|--------|---------------------------|-------|
| WT / WT | Normal | 0% | - |
| WT / MUT (pathogène) | **Hétérozygote muté** | **~99-100%** (pénétrance complète) | Expressivité très variable. 50% *de novo* |
| MUT / MUT | Homozygote (extrêmement rare) | Létal embryonnaire probable | Non viable |
| WT / DEL_1.4Mb | **Hétérozygote délétion** | 100% | Phénotype sévère (voir ci-dessus) |

> Pour dataset : binaire **mutation NF1 pathogène présente (OUI/NON)** + **type mutation** (classique vs délétion 1.4Mb vs missense atténué). Si OUI → probabilité maladie = 1.0.

## Probabilités de transmission

### Parent atteint (hétérozygote NF1 muté) × Parent sain

| Enfant hérite allèle | Probabilité | Statut |
|---------------------|-------------|--------|
| Allèle muté | 0.50 | **Atteint** (pénétrance ~100%) |
| Allèle normal | 0.50 | Sain |

### Mutation *de novo* (parents sains)
- Taux mutation *de novo* NF1 : **~2.7 × 10⁻⁵ par gamète** (l'un des plus élevés génome humain)
- Taille gène grande (280 kb, 60 exons), taux mutation élevé
- ~50% cas sporadiques = *de novo*
- Enfant atteint, parents non porteurs → risque récurrence fratrie :
  - **~1-2%** (mosaïcisme gonadique parental possible)
  - Si mosaïcisme somatique détecté chez un parent → risque jusqu'à 50%

### Parent avec mosaïcisme
- Si mosaïcisme détecté (sanguin ou cutané) : risque transmission = fraction cellules germinales mutées (inconnu, estimé 10-50%)

## Fréquence dans la population

| Population | Prévalence (1/~) | Incidence (1/~) | Source |
|------------|------------------|-----------------|--------|
| Général (tous groupes) | 1/2,500 - 1/3,000 | 1/2,500 - 1/3,000 | Orphanet, registres nationaux |
| Aucune différence ethnique majeure | - | - | Gène grand, mutation rate élevé universel |

## Complications majeures (pour rapport clinique)
- Neurofibromes plexiformes (20-50%) → risque transformation MPNST (8-13% vie)
- Gliomes optiques (15-20%, meist <7 ans)
- Retard développement / troubles apprentissage (50-60%)
- Scoliose (10-20%)
- Hypertension (sténose artère rénale, phéochromocytome rare)
- Risque cancer global accru (x2-3 population générale)

## Sources
- OMIM #162200 — Neurofibromatosis Type 1
- GeneReviews: Neurofibromatosis 1 (Gutmann & Ferner, 2023)
- Orphanet: ORPHA636 — Neurofibromatose type 1
- Gutmann DH, Ferner RE. "Neurofibromatosis type 1." Nat Rev Dis Primers 2022.
- Friedman JM. "Neurofibromatosis 1." GeneReviews 1998 (updated 2023).
- Legius E et al. "NF1 microdeletion syndrome." Hum Mutat 2011.
- UpToDate: Neurofibromatosis type 1.