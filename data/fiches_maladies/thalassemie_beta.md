# Thalassémie β

## Gène concerné
- **Gène** : *HBB* (Hémoglobine sous-unité bêta)
- **Chromosome** : 11p15.4 (même locus que drépanocytose)
- **Position GRCh38** : chr11:5,227,001-5,227,500
- **Protéine** : Hémoglobine bêta-globine
- **Référence** : OMIM #613985, NM_000518.5

## Mode de transmission
**Autosomique récessive** — Deux allèles β mutés requis. Sévérité selon type de mutation (β⁰ = pas de production, β⁺ = production réduite).

## Types de mutations β-thalassémie

| Type | Production β-globine | Mutations exemples | Phénotype homozygote |
|------|---------------------|-------------------|---------------------|
| **β⁰ (beta-zéro)** | Aucune (nonsense, frameshift, splicing canonique) | Codon 39 (C>T), IVS1-1 (G>T), IVS1-110 (G>A), IVS2-1 (G>A), W15X | Thalassémie majeure (transfusion-dépendante) |
| **β⁺ (beta-plus)** | Réduite (promoteur, splicing non-canonique, 5'UTR) | -28 (A>G), -29 (A>G), -87 (C>G), IVS1-6 (T>C), IVS1-110 (G>A) | Thalassémie intermédiaire |
| **β⁺⁺ (silencieuse)** | Très légèrement réduite | -101 (C>T), Cap site +1 (A>C) | Porteur asymptomatique, microcytose seulement |

> **Note** : >300 mutations β-thal décrites. Fréquences variables selon population. Pour dataset : on regroupe en 3 allèles : `B` (normal), `B0` (β⁰), `B+` (β⁺).

## Génotypes et phénotypes

| Génotype | Phénotype | Description clinique | Transfusions |
|----------|-----------|---------------------|--------------|
| B / B | Normal | HbA >95%, HbA₂ 2-3% | Non |
| B / B0 | Porteur β⁰-thal (trait) | Microcytose (MCV 60-70), HbA₂ ↑ (4-8%), HbF ↑ (1-5%) | Non |
| B / B+ | Porteur β⁺-thal (trait) | Microcytose légère, HbA₂ normal-légèrement ↑ | Non |
| B0 / B0 | **Thalassémie majeure (β⁰/β⁰)** | Anémie sévère dès 6-12 mois, hépatosplénomégalie, expansion médullaire, surcharge ferrique. Déficit de croissance | **Vie entière, toutes les 2-4 sem** |
| B+ / B+ | **Thalassémie intermédiaire (β⁺/β⁺)** | Anémie modérée (Hb 7-10 g/dL), splénomégalie, extramédullaire. Diagnostic plus tardif (enfant/adulte) | Occasionnelles / aucune |
| B0 / B+ | **Thalassémie intermédiaire à majeure** | Phénotype variable selon mutation B+ spécifique. Souvent transfusion-dépendant ou intermittent | Variables (régulières à occasionnelles) |
| B / (silencieuse) | Porteur silencieux | Microcytose très légère, HbA₂ normal | Non |

## Probabilités de transmission

### Allèles : B (normal), B0 (β⁰), B+ (β⁺)

| Parent 1 | Parent 2 | B/B | B/B0 | B0/B0 | B/B+ | B0/B+ | B+/B+ |
|----------|----------|-----|------|-------|------|-------|-------|
| B/B | B/B | 1.0 | 0 | 0 | 0 | 0 | 0 |
| B/B | B/B0 | 0.5 | 0.5 | 0 | 0 | 0 | 0 |
| B/B | B0/B0 | 0 | 1.0 | 0 | 0 | 0 | 0 |
| B/B | B/B+ | 0.5 | 0 | 0 | 0.5 | 0 | 0 |
| B/B | B0/B+ | 0 | 0.5 | 0 | 0 | 0.5 | 0 |
| B/B | B+/B+ | 0 | 0 | 0 | 1.0 | 0 | 0 |
| B/B0 | B/B0 | 0.25 | 0.5 | 0.25 | 0 | 0 | 0 |
| B/B0 | B0/B0 | 0 | 0.5 | 0.5 | 0 | 0 | 0 |
| B/B0 | B/B+ | 0.25 | 0.25 | 0 | 0.25 | 0.25 | 0 |
| B/B0 | B0/B+ | 0 | 0.25 | 0.25 | 0 | 0.25 | 0.25 |
| B/B0 | B+/B+ | 0 | 0 | 0 | 0.5 | 0.5 | 0 |
| B0/B0 | B0/B0 | 0 | 0 | 1.0 | 0 | 0 | 0 |
| B0/B0 | B/B+ | 0 | 0.5 | 0 | 0 | 0.5 | 0 |
| B0/B0 | B0/B+ | 0 | 0 | 0.5 | 0 | 0.5 | 0 |
| B0/B0 | B+/B+ | 0 | 0 | 0 | 0 | 1.0 | 0 |
| B/B+ | B/B+ | 0.25 | 0 | 0 | 0.5 | 0 | 0.25 |
| B/B+ | B0/B+ | 0 | 0 | 0 | 0.25 | 0.25 | 0.5 |
| B/B+ | B+/B+ | 0 | 0 | 0 | 0.5 | 0 | 0.5 |
| B0/B+ | B0/B+ | 0 | 0.25 | 0.25 | 0 | 0.5 | 0 |
| B0/B+ | B+/B+ | 0 | 0 | 0 | 0 | 0.5 | 0.5 |
| B+/B+ | B+/B+ | 0 | 0 | 0 | 0 | 0 | 1.0 |

## Fréquences par population (porteurs β-thal)

| Population | Fréquence porteurs (1/~) | Mutations principales | Source |
|------------|---------------------------|----------------------|--------|
| Chypre | 1/7 | IVS1-110, IVS1-1 | Orphanet |
| Grèce (îles) | 1/10-1/15 | IVS1-110, Codon 39 | Orphanet |
| Italie (Sardaigne, Sicile, Pouilles) | 1/10-1/20 | Codon 39, IVS1-110, IVS1-1 | Registre italien |
| Turquie | 1/20-1/30 | IVS1-110, IVS1-1, Codon 8 | Orphanet |
| Moyen-Orient | 1/20-1/50 | IVS1-5, IVS1-1, Codon 8/39 | Études locales |
| Asie du Sud-Est | 1/20-1/50 | Codon 41/42, -28, IVS1-5 | Études locales |
| Afrique du Nord | 1/30-1/50 | Codon 39, IVS1-110, IVS1-1 | Orphanet |
| Europe du Nord | 1/100-1/300 | Rare | gnomAD |
| Ashkénazes | 1/30 | IVS1-110, Codon 39 | Études génétiques |

## Sources
- OMIM #613985 — Beta-Thalassemia
- GeneReviews: Beta-Thalassemia (Galanello & Origa, 2023)
- Orphanet: ORPHA848 — Bêta-thalassémie
- Galanello R, Origa R. "Beta-thalassemia." Orphanet J Rare Dis 2010.
- Thein SL. "Molecular basis of β-thalassemia." Blood Rev 2018.
- Registre Italien Thalassémie / Registre Chypriote