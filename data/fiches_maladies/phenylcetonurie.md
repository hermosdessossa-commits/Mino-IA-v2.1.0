# Phénylcétonurie (PKU)

## Gène concerné
- **Gène** : *PAH* (Phénylalanine Hydroxylase)
- **Chromosome** : 12q23.2
- **Position GRCh38** : chr12:103,262,000-103,345,000
- **Protéine** : Phénylalanine hydroxylase (convertit Phe → Tyr, cofacteur BH4)
- **Référence** : OMIM #261600, NM_000277.2

## Mode de transmission
**Autosomique récessive** — Deux allèles *PAH* mutés requis. >1000 mutations décrites, très hétérogènes alléliques.

## Classification génotypique et phénotypique

| Génotype | Activité résiduelle PAH | Phénotype | Phe sanguin (sans régime) | Traitement |
|----------|------------------------|-----------|---------------------------|------------|
| **Sévère / Sévère** | <1% | **PKU classique** | >1200 μmol/L (20 mg/dL) | Régime strict vie entière |
| **Sévère / Modéré** | 1-5% | **PKU modérée** | 600-1200 μmol/L | Régime modéré |
| **Modéré / Modéré** | 5-15% | **PKU légère / HPA** | 360-600 μmol/L | Régime léger / surveillance |
| **Sévère / Léger** | Variable | **PKU modérée à légère** | Variable | Selon phénotype |
| **Léger / Léger** | >15% | **Hyperphénylalaninémie (HPA) bénigne** | 120-360 μmol/L | Souvent aucun, surveillance |
| **Normal / Muté** | 50% (hétérozygote) | **Porteur sain** | Normal (<120 μmol/L) | Aucun |

> **Note** : La corrélation génotype-phénotype n'est pas parfaite (modificateurs génétiques, BH4). Pour le dataset : on utilise 3 catégories alléliques : `WT` (normal), `SEV` (sévère: <1% activité, ex: R408W, IVS10-11G>A, Y414C), `MILD` (modéré/léger: >1% activité, ex: R261Q, R158Q, V388M).

## Mutations fréquentes (Caucasiens/Européens)

| Mutation | Notation cDNA | Protéine | Fréquence allélique | Phénotype |
|----------|---------------|----------|---------------------|-----------|
| R408W | c.1222C>T | p.Arg408Trp | 15-30% | Sévère (classique) |
| IVS10-11G>A | c.1066-11G>A | Splicing | 10-15% | Sévère |
| Y414C | c.1241A>G | p.Tyr414Cys | 5-10% | Sévère |
| R261Q | c.782G>A | p.Arg261Gln | 5-15% | Modéré |
| R158Q | c.473G>A | p.Arg158Gln | 2-8% | Modéré |
| V388M | c.1162G>A | p.Val388Met | 2-5% | Léger |
| I65T | c.194T>C | p.Ile65Thr | 1-3% | Léger |
| P281L | c.842C>T | p.Pro281Leu | <1% | Modéré |
| L48S | c.143T>C | p.Leu48Ser | <1% | Sévère |
| R241C | c.721C>T | p.Arg241Cys | Rare | Variable |

## Génotypes simplifiés pour dataset

| Allèle 1 | Allèle 2 | Catégorie | Phénotype attendu |
|----------|----------|-----------|-------------------|
| WT | WT | Normal | Sain |
| WT | SEV | Porteur | Sain |
| WT | MILD | Porteur | Sain |
| SEV | SEV | Malade | PKU classique |
| SEV | MILD | Malade | PKU modérée |
| MILD | MILD | Malade | PKU légère / HPA |

## Probabilités de transmission

| Parent 1 | Parent 2 | WT/WT | WT/SEV | SEV/SEV | WT/MILD | SEV/MILD | MILD/MILD |
|----------|----------|-------|--------|---------|---------|----------|-----------|
| WT/WT | WT/WT | 1.0 | 0 | 0 | 0 | 0 | 0 |
| WT/WT | WT/SEV | 0.5 | 0.5 | 0 | 0 | 0 | 0 |
| WT/WT | SEV/SEV | 0 | 1.0 | 0 | 0 | 0 | 0 |
| WT/WT | WT/MILD | 0.5 | 0 | 0 | 0.5 | 0 | 0 |
| WT/WT | SEV/MILD | 0 | 0.5 | 0 | 0 | 0.5 | 0 |
| WT/WT | MILD/MILD | 0 | 0 | 0 | 1.0 | 0 | 0 |
| WT/SEV | WT/SEV | 0.25 | 0.5 | 0.25 | 0 | 0 | 0 |
| WT/SEV | SEV/SEV | 0 | 0.5 | 0.5 | 0 | 0 | 0 |
| WT/SEV | WT/MILD | 0.25 | 0.25 | 0 | 0.25 | 0.25 | 0 |
| WT/SEV | SEV/MILD | 0 | 0.25 | 0.25 | 0 | 0.25 | 0.25 |
| WT/SEV | MILD/MILD | 0 | 0 | 0 | 0.5 | 0.5 | 0 |
| SEV/SEV | SEV/SEV | 0 | 0 | 1.0 | 0 | 0 | 0 |
| SEV/SEV | WT/MILD | 0 | 0.5 | 0 | 0 | 0.5 | 0 |
| SEV/SEV | SEV/MILD | 0 | 0 | 0.5 | 0 | 0.5 | 0 |
| SEV/SEV | MILD/MILD | 0 | 0 | 0 | 0 | 1.0 | 0 |
| WT/MILD | WT/MILD | 0.25 | 0 | 0 | 0.5 | 0 | 0.25 |
| WT/MILD | SEV/MILD | 0 | 0 | 0 | 0.25 | 0.25 | 0.5 |
| WT/MILD | MILD/MILD | 0 | 0 | 0 | 0.5 | 0 | 0.5 |
| SEV/MILD | SEV/MILD | 0 | 0.25 | 0.25 | 0 | 0.5 | 0 |
| SEV/MILD | MILD/MILD | 0 | 0 | 0 | 0 | 0.5 | 0.5 |
| MILD/MILD | MILD/MILD | 0 | 0 | 0 | 0 | 0 | 1.0 |

## Fréquences porteurs par population

| Population | Fréquence porteurs (1/~) | Incidence (1/~) | Mutations fondatrices |
|------------|---------------------------|-----------------|----------------------|
| Caucasiens (Europe Nord) | 1/50 | 1/10,000 | R408W, IVS10-11G>A |
| Irlandais | 1/45 | 1/4,500 | R408W (haute fréquence) |
| Turcs | 1/30 | 1/4,000 | IVS10-11G>A, R261Q |
| Italiens | 1/50 | 1/8,000 | IVS10-11G>A, R408W |
| Africains (USA) | 1/60 | 1/15,000 | Différentes (R408W rare) |
| Asiatiques (Japon, Chine) | 1/60-1/100 | 1/50,000-1/100,000 | R261Q, R158Q, V388M |
| Juifs Ashkénazes | 1/50 | 1/8,000 | R408W, Y414C |

## Sources
- OMIM #261600 — Phenylketonuria
- GeneReviews: Phenylalanine Hydroxylase Deficiency (Blau & van Spronsen, 2023)
- Orphanet: ORPHA79246 — Phénylcétonurie
- PAHdb (PAH Mutation Database) — www.pahdb.mcgill.ca
- Blau N et al. "Phenylketonuria." Lancet 2011.
- van Spronsen FJ et al. "Phenylketonuria." Nat Rev Dis Primers 2021.