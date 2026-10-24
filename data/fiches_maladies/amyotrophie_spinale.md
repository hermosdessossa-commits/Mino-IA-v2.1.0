# Amyotrophie Spinale (SMA - Spinal Muscular Atrophy)

## Gènes concernés
- **SMN1** (Survival of Motor Neuron 1) — **Gène principal**, Chromosome 5q13.2
  - Position GRCh38 : chr5:70,924,000-70,951,000
  - Protéine : SMN (complexe snRNP, biogenèse spliceosome)
  - Référence : OMIM #600354, NM_000344.3
- **SMN2** (Survival of Motor Neuron 2) — **Gène modificateur**, Chromosome 5q13.2
  - Presque identique à SMN1 (5 nucléotides diffèrent)
  - Différence critique : exon 7 (c.840C>T dans SMN2 → skipping exon 7)
  - SMN2 produit ~10-15% protéine SMN fonctionnelle (flux exon 7 inclus)
  - **Nombre de copies SMN2 variable (0-8)** → détermine la sévérité

## Mode de transmission
**Autosomique récessive** (SMN1) — Deux allèles SMN1 non-fonctionnels requis.
- 95-98% cas : **déletion homozygous exons 7-8 SMN1** (conversion génique SMN2→SMN1)
- 2-5% cas : **déletion + mutation ponctuelle** (composé hétérozygote)
- SMN2 = modificateur de sévérité (pas causatif seul)

## Copies SMN2 et phénotype (corrélation forte mais pas absolue)

| Copies SMN1 fonctionnelles | Copies SMN2 | Phénotype (type SMA) | Âge début | Jalons moteurs | Espérance de vie |
|---------------------------|-------------|---------------------|-----------|----------------|------------------|
| 2 (normal) | 0-8 | **Normal** | - | Marche normale | Normale |
| 1 (porteur) | 0-8 | **Porteur asymptomatique** | - | Normal | Normale |
| 0 (homoz délétion) | **1-2** | **Type 0 (prénatal)** | In utero | Aucun (akinesie fœtale) | Mort néonatale |
| 0 | **2** | **Type 1 (Werdnig-Hoffmann)** | <6 mois | Ne s'assoit jamais | <2 ans sans traitement |
| 0 | **3** | **Type 2 (Dubowitz)** | 6-18 mois | S'assoit, ne marche pas | Adulte (avec soins) |
| 0 | **3-4** | **Type 3 (Kugelberg-Welander)** | >18 mois | Marche, puis perte progressive | Normale |
| 0 | **≥4** | **Type 4 (adulte)** | >30 ans | Marche préservée longtemps | Normale |

> **Note importante** : La corrélation SMN2/phénotype a des exceptions (2 copies → Type 2 possible ; 4 copies → Type 2 possible). Facteurs modificateurs : plastine 3, NCALD, ZPR1, épigénétique.

## Génotypes pour dataset (simplifié)

On modélise : **copies SMN1** (0, 1, 2) + **copies SMN2** (0-6, típico 1-4)

| SMN1 copies | SMN2 copies | Statut | Phénotype probable |
|-------------|-------------|--------|-------------------|
| 2 | 0-6 | Normal / Porteur* | Sain |
| 1 | 0-6 | Porteur | Asymptomatique |
| 0 | 1-2 | Malade | Type 0/1 (sévère) |
| 0 | 3 | Malade | Type 2 (intermédiaire) |
| 0 | 4 | Malade | Type 3 (modéré) |
| 0 | ≥5 | Malade | Type 3/4 (léger) |

*Si 1 copie SMN1 + 0 SMN2 = porteur ; mais 0 SMN2 est rare (<1% population)

## Probabilités de transmission

### Transmission SMN1 (déletion homozygote = 0 copie, hétérozygote = 1 copie, normal = 2 copies)

Chaque parent transmet 1 allèle SMN1 (présent ou délété). Fréquence délétion SMN1 ~1/40-1/60 selon population.

| Parent 1 SMN1 | Parent 2 SMN1 | Enfant: 2 copies | Enfant: 1 copie | Enfant: 0 copie |
|---------------|---------------|------------------|-----------------|-----------------|
| 2 (normal) | 2 (normal) | 1.0 | 0 | 0 |
| 2 | 1 (porteur) | 0.5 | 0.5 | 0 |
| 2 | 0 (malade) | 0 | 1.0 | 0 |
| 1 | 1 | 0.25 | 0.5 | 0.25 |
| 1 | 0 | 0 | 0.5 | 0.5 |
| 0 | 0 | 0 | 0 | 1.0 |

### Copies SMN2 : transmission indépendante (gènes distincts mais liés)

SMN1 et SMN2 sont en tandem (97% identité). Transmission liée mais recombination possible.
Pour simplicité dataset : **SMN2 copies transmis = échantillonnage selon copies parentales**.

Si parent a N copies SMN2 → transmet k copies selon distribution binomiale (N essais, p=0.5 par copie).
Mais copies SMN2 sont sur 2 chromosomes → chaque chromosome a un certain nombre de copies.

Modèle réaliste simplifié :
- Chaque chromosome 5 a 0-3 copies SMN2
- Parent transmet un de ses 2 chromosomes → enfant reçoit copies SMN2 de ce chromosome
- Total SMN2 enfant = copies chr5 paternel + copies chr5 maternel

### Fréquences haplotypes SMN1/SMN2 par population

| Population | Fréquence délétion SMN1 (porteurs 1/~) | Copies SMN2 médianes | Source |
|------------|----------------------------------------|---------------------|--------|
| Caucasiens (Europe) | 1/40 - 1/50 | 2 (mode), 1-3 fréquent | gnomAD, études SMA |
| Ashkénazes | 1/30 - 1/40 | 2 | Études ciblées |
| Asiatiques (Chine, Japon) | 1/50 - 1/70 | 2-3 | Études locales |
| Africains | 1/60 - 1/100 | 2-3 | gnomAD |
| Hispaniques | 1/50 - 1/70 | 2 | Études US |

## Probabilités conjointes (SMN1 + SMN2)

Pour un couple de porteurs (SMN1: 1 copy each) :
- 25% enfant 0 SMN1 (malade)
  - Parmi eux : distribution SMN2 selon copies parentales
  - Ex: si chaque parent a 2 copies SMN2 (1 par chr) → enfant 0-4 copies SMN2
  - Probabilité Type 1 (1-2 copies SMN2) ≈ 30-40%
  - Probabilité Type 2 (3 copies) ≈ 40-50%
  - Probabilité Type 3 (≥4 copies) ≈ 10-20%

## Sources
- OMIM #253300 — Spinal Muscular Atrophy
- GeneReviews: Spinal Muscular Atrophy (Darras & Kunkel, 2023)
- Orphanet: ORPHA70 — Amyotrophie spinale
- Darras BT. "Spinal muscular atrophies." Pediatr Clin North Am 2015.
- Farrar MA et al. "Emerging therapies for SMA." Nat Rev Neurol 2017.
- Prior TW et al. "SMN2 copy number predicts phenotype." Neurology 2020.