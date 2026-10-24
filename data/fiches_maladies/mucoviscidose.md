# Mucoviscidose (Fibrose kystique)

## Gène concerné
- **Gène** : *CFTR* (Cystic Fibrosis Transmembrane conductance Regulator)
- **Chromosome** : 7q31.2
- **Position GRCh38** : chr7:117,559,593-117,712,319
- **Protéine** : Canal chlorure régulé par cAMP
- **Référence** : OMIM #602421, NM_000492.3

## Mode de transmission
**Autosomique récessive** — Deux allèles mutés (homozygote ou hétérozygote composé) requis pour la maladie. >2000 mutations répertoriées, classées en 6 classes fonctionnelles.

## Classes de mutations CFTR (classification fonctionnelle)

| Classe | Défaut | Exemples mutations fréquentes | Phénotype typique |
|--------|--------|------------------------------|-------------------|
| I | Pas de synthèse (nonsense, frameshift, splicing) | G542X, W1282X, 621+1G>T, 1717-1G>A | Sévère, pancréatique insuffisant |
| II | Pliage/maturation défectueux (rétention ER) | **F508del** (p.Phe508del, ~70% allèles), N1303K | Sévère, pancréatique insuffisant |
| III | Régulation défectueuse (canal ne s'ouvre pas) | G551D, G1349D, G178R, S549N | Variable, souvent pancréatique insuffisant |
| IV | Conductance chlorure réduite | R117H, R334W, R347P, D1152H | Plus léger, souvent pancréatique suffisant |
| V | Quantité réduite (splicing aberrant, promoteur) | 3849+10kbC>T, 5T/7T/9T (intron 9), A455E | Variable, souvent pancréatique suffisant |
| VI | Instabilité protéique à la membrane | c.120delI, c.3700A>G | Phénotype émergent |

## Mutations les plus fréquentes (Caucasiens)
| Mutation | Allèle | Fréquence allélique | Classe |
|----------|--------|---------------------|--------|
| F508del | c.1521_1523delCTT | 65-70% | II |
| G542X | c.1624G>T | 2-3% | I |
| G551D | c.1652G>A | 2-3% | III |
| N1303K | c.3909C>G | 1-2% | II |
| W1282X | c.3846G>A | 1-2% (Ashkénazes: 60%) | I |
| R117H | c.350G>A | 1-2% | IV |
| 3849+10kbC>T | c.3718-2477C>T | 1% | V |
| 621+1G>T | c.489+1G>T | 1-2% | I |
| 1717-1G>A | c.1585-1G>A | 1% | I |
| 2789+5G>A | c.2657+5G>A | <1% | I/V |

> **Note pour dataset** : On regroupe en 3 macro-génotypes pour simplification : `WT/WT` (sain), `WT/mut` (porteur), `mut/mut` (malade) où `mut` = toute mutation pathogène. Pour finesse : distinguer `F508del/F508del` (sévère) vs `F508del/R117H` (modéré) vs `R117H/R117H` (léger).

## Génotypes simplifiés et interprétation clinique

| Génotype (simplifié) | Phénotype | Statut pancréatique | Sévérité pulmonaire |
|----------------------|-----------|---------------------|---------------------|
| WT / WT | Sain | Normal | Aucune |
| WT / mut (toute classe) | Porteur sain | Normal | Aucune |
| F508del / F508del | Mucoviscidose classique | Insuffisant (PI) | Sévère, déclin précoce VEMS |
| F508del / Classe I-II-III | Mucoviscidose sévère | Insuffisant (PI) | Sévère |
| F508del / Classe IV-V (ex: R117H, 3849+10kbC>T) | Mucoviscidose modérée | Souvent suffisant (PS) | Modérée, diagnostic plus tardif |
| Classe IV-V / Classe IV-V | Mucoviscidose légère/atypique | Suffisant (PS) | Légère, souvent mono-symptomatique |

## Probabilités de transmission

### Modèle simplifié (3 allèles : WT, MUT_SEVERE, MUT_MILD)

| Parent 1 | Parent 2 | WT/WT | WT/MUT_SEV | MUT_SEV/MUT_SEV | WT/MUT_MILD | MUT_SEV/MUT_MILD | MUT_MILD/MUT_MILD |
|----------|----------|-------|------------|-----------------|-------------|------------------|-------------------|
| WT/WT | WT/WT | 1.0 | 0 | 0 | 0 | 0 | 0 |
| WT/WT | WT/MUT_SEV | 0.5 | 0.5 | 0 | 0 | 0 | 0 |
| WT/WT | MUT_SEV/MUT_SEV | 0 | 1.0 | 0 | 0 | 0 | 0 |
| WT/WT | WT/MUT_MILD | 0.5 | 0 | 0 | 0.5 | 0 | 0 |
| WT/WT | MUT_SEV/MUT_MILD | 0 | 0.5 | 0 | 0 | 0.5 | 0 |
| WT/WT | MUT_MILD/MUT_MILD | 0 | 0 | 0 | 1.0 | 0 | 0 |
| WT/MUT_SEV | WT/MUT_SEV | 0.25 | 0.5 | 0.25 | 0 | 0 | 0 |
| WT/MUT_SEV | MUT_SEV/MUT_SEV | 0 | 0.5 | 0.5 | 0 | 0 | 0 |
| WT/MUT_SEV | WT/MUT_MILD | 0.25 | 0.25 | 0 | 0.25 | 0.25 | 0 |
| WT/MUT_SEV | MUT_SEV/MUT_MILD | 0 | 0.25 | 0.25 | 0 | 0.25 | 0.25 |
| WT/MUT_SEV | MUT_MILD/MUT_MILD | 0 | 0 | 0 | 0.5 | 0.5 | 0 |
| MUT_SEV/MUT_SEV | MUT_SEV/MUT_SEV | 0 | 0 | 1.0 | 0 | 0 | 0 |
| MUT_SEV/MUT_SEV | WT/MUT_MILD | 0 | 0.5 | 0 | 0 | 0.5 | 0 |
| MUT_SEV/MUT_SEV | MUT_SEV/MUT_MILD | 0 | 0 | 0.5 | 0 | 0.5 | 0 |
| MUT_SEV/MUT_SEV | MUT_MILD/MUT_MILD | 0 | 0 | 0 | 0 | 1.0 | 0 |
| WT/MUT_MILD | WT/MUT_MILD | 0.25 | 0 | 0 | 0.5 | 0 | 0.25 |
| WT/MUT_MILD | MUT_SEV/MUT_MILD | 0 | 0 | 0 | 0.25 | 0.25 | 0.5 |
| WT/MUT_MILD | MUT_MILD/MUT_MILD | 0 | 0 | 0 | 0.5 | 0 | 0.5 |
| MUT_SEV/MUT_MILD | MUT_SEV/MUT_MILD | 0 | 0.25 | 0.25 | 0 | 0.5 | 0 |
| MUT_SEV/MUT_MILD | MUT_MILD/MUT_MILD | 0 | 0 | 0 | 0 | 0.5 | 0.5 |
| MUT_MILD/MUT_MILD | MUT_MILD/MUT_MILD | 0 | 0 | 0 | 0 | 0 | 1.0 |

### Fréquences porteurs par population
| Population | Fréquence porteurs (1/~) | Fréquence allélique F508del | Source |
|------------|---------------------------|----------------------------|--------|
| Europe du Nord (Caucasiens) | 1/25 - 1/30 | 0.013 - 0.015 | ECFS Registry |
| Europe du Sud (France, Italie) | 1/30 - 1/40 | 0.010 - 0.012 | Registre français |
| Ashkénazes | 1/25 | 0.012 (mais W1282X fréquent) | Études génétiques |
| Afro-américains | 1/65 | 0.004 | Cystic Fibrosis Foundation |
| Hispaniques (USA) | 1/46 | 0.007 | CFF |
| Asiatiques | 1/90 - 1/100 | Très rare | gnomAD |

## Sources
- OMIM #219700 — Cystic Fibrosis
- GeneReviews: Cystic Fibrosis (Farrell et al., 2023)
- Orphanet: ORPHA586 — Mucoviscidose
- CFTR2 Database (cftr2.org) — Classification fonctionnelle mutations
- Elborn JS. "Cystic fibrosis." Lancet 2016.
- Rowe SM et al. "Cystic fibrosis." NEJM 2005.
- Registre Européen CF (ECFS) / Registre Français de la Mucoviscidose