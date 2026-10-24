# Hémophilie A et B

## Gènes concernés
| Maladie | Gène | Chromosome | Position GRCh38 | Protéine | % cas | Référence |
|---------|------|------------|-----------------|----------|-------|-----------|
| **Hémophilie A** | *F8* (Facteur VIII) | **Xq28** | chrX:154,800,000-155,000,000 | Facteur VIII (cofacteur FIXa) | **~80-85%** | OMIM #306700, NM_000132.4 |
| **Hémophilie B** | *F9* (Facteur IX) | **Xq27.1** | chrX:139,900,000-139,950,000 | Facteur IX (sérine protéase) | **~15-20%** | OMIM #306900, NM_000133.4 |

## Mode de transmission
**Liée à l'X récessive** — Gènes sur chromosome X.
- **Hommes (XY)** : Un allèle muté sur leur unique X → **malades**
- **Femmes (XX)** : Deux allèles → Porteuses (généralement asymptomatiques) ou atteintes si homozygotes / X-inactivation défavorable

## Niveaux de facteur et sévérité (identique A et B)

| Niveau facteur (UI/dL ou %) | Sévérité | Phénotype clinique | Hémorragies spontanées |
|----------------------------|----------|-------------------|------------------------|
| **< 1%** (< 1 UI/dL) | **Sévère** | Hémarthroses spontanées récurrentes, hématomes musculaires, hémorragies post-traumatiques majeures | Fréquentes (2-5/semaine sans prophylaxie) |
| **1-5%** | **Modérée** | Hémorragies post-traumatiques/chirurgicales, hémarthroses occasionnelles | Rares spontanées |
| **5-40%** | **Légère** | Hémorragies post-chirurgicales/traumatiques majeures seulement | Exceptionnelles |
| **> 40%** | Normal / Porteur asymptomatique | Asymptomatique | Aucune |

## Mutations fréquentes

### Hémophilie A (F8)
| Type | Fréquence | Exemples |
|------|-----------|----------|
| Inversion intron 22 (Inv22) | **~45% allèles sévères** | Récombinaison avec gène homologue *F8A* |
| Inversion intron 1 (Inv1) | ~5% allèles sévères | Récombinaison avec *F8B* |
| Délétions partielles | ~5% | Variables |
| Nonsense / Frameshift / Splicing | ~30% | Dispersées |
| Missense | ~15% | Souvent modérées/légères |

### Hémophilie B (F9)
| Type | Fréquence | Exemples |
|------|-----------|----------|
| Missense | ~60% | Dispersées |
| Nonsense / Frameshift / Splicing | ~25% | Dispersées |
| Délétions partielles | ~10% | Variables |
| Promoteur / 5'UTR (hémophilie B Leyden) | ~5% | Amélioration pubertaire (androgène-réponsif) |

## Génotypes et statuts (liés à l'X)

### Hommes (XY) — Un seul allèle
| Génotype F8/F9 | Statut | Sévérité |
|----------------|--------|----------|
| Normal | Sain | - |
| Muté (sévère) | **Malade sévère** | <1% |
| Muté (modéré) | **Malade modéré** | 1-5% |
| Muté (léger) | **Malade léger** | 5-40% |

### Femmes (XX) — Deux allèles
| Génotype | Statut | Niveau facteur moyen | Phénotype |
|----------|--------|---------------------|-----------|
| Normal / Normal | Sain | 100% | Asymptomatique |
| Normal / Muté (sévère) | **Porteuse** | ~50% (30-70% selon X-inactivation) | Généralement asymptomatique. ~10-30% : taux bas (symptomatiques légères) |
| Normal / Muté (modéré) | Porteuse | ~60-70% | Asymptomatique |
| Normal / Muté (léger) | Porteuse | ~70-85% | Asymptomatique |
| Muté (sévère) / Muté (sévère) | **Homozygote composée** | <1% | **Malade sévère** (très rare) |
| Muté / Muté (différents) | Composée | Variable | Malade (sévérité selon allèles) |
| Turner (XO) + Muté | **Malade** | <1% | Comme homme |

> **X-inactivation (lyonisation)** : Aléatoire. Si X muté inactivé dans >80% cellules → taux facteur bas → symptômes. Pour dataset : on modélise taux facteur porteuse ~ N(50%, 15%) tronqué [10%, 90%].

## Probabilités de transmission

### Notation
- **X^N** : X normal
- **X^A_s** : X avec mutation hémophilie A sévère
- **X^A_m** : X avec mutation hémophilie A modérée
- **X^A_l** : X avec mutation hémophilie A légère
- Idem pour B : **X^B_s**, **X^B_m**, **X^B_l**

### Croisements principaux

#### 1. Père malade (X^mut Y) × Mère saine (X^N X^N)
| Enfant | Génotype | Probabilité | Statut |
|--------|----------|-------------|--------|
| Fille | X^mut / X^N | 1.0 | **Porteuse obligée** |
| Garçon | X^N / Y | 1.0 | **Sain** |

#### 2. Père sain (X^N Y) × Mère porteuse (X^N / X^mut)
| Enfant | Génotype | Probabilité | Statut |
|--------|----------|-------------|--------|
| Fille | X^N / X^N | 0.25 | Sain |
| Fille | X^N / X^mut | 0.25 | **Porteuse** |
| Garçon | X^N / Y | 0.25 | **Sain** |
| Garçon | X^mut / Y | 0.25 | **Malade** (même sévérité que mère si connue) |

#### 3. Père malade (X^mut Y) × Mère porteuse (X^N / X^mut) — Rare
| Enfant | Génotype | Probabilité | Statut |
|--------|----------|-------------|--------|
| Fille | X^mut / X^N | 0.25 | Porteuse |
| Fille | X^mut / X^mut | 0.25 | **Malade (homozygote)** |
| Garçon | X^mut / Y | 0.25 | Malade |
| Garçon | X^N / Y | 0.25 | Sain |

#### 4. Mutation *de novo*
- **Hémophilie A** : ~30% cas *de novo* (taux mutation élevé, gène grand, inversions récurrentes)
- **Hémophilie B** : ~20-30% cas *de novo*
- Si *de novo* : mère non porteuse (sauf mosaïcisme). Risque récurrence fratrie : **~1-5%** (mosaïcisme gonadique maternel possible, surtout pour inversions F8).

## Fréquence dans la population

| Maladie | Incidence naissances mâles | Prévalence (hommes) | Porteuses femelles | Source |
|---------|---------------------------|---------------------|-------------------|--------|
| Hémophilie A | 1/5,000 - 1/10,000 | 1/12,000 | 1/2,500 - 1/5,000 | WFH Annual Global Survey |
| Hémophilie B | 1/25,000 - 1/30,000 | 1/40,000 | 1/12,000 - 1/15,000 | WFH |

## Sources
- OMIM #306700 (Hemophilia A), #306900 (Hemophilia B)
- GeneReviews: Hemophilia A (Gitschier, 2023), Hemophilia B (High, 2023)
- Orphanet: ORPHA448 (Hémophilie A), ORPHA449 (Hémophilie B)
- World Federation of Hemophilia (WFH) Guidelines 2020/2024.
- Gouw SC et al. "F8 mutation type and inhibitor risk." Blood 2012.
- Plug I et al. "Bleeding in carriers of hemophilia." Blood 2006.
- UKHCDO / FranceCoag / Registres nationaux hémophilie.