# Données de Mino-IA

## Fichiers

| Fichier | Contenu |
|---------|---------|
| `dataset_synthetique.csv` | 4 000 échantillons d'entraînement (graine 42) |
| `dataset_test.csv` | 1 000 échantillons de test (graine 42) |
| `fiches_maladies/` | Fiches documentaires par maladie |
| `patients_reels.json` | Base locale vide, ignorée par Git, à remplir par le médecin |

Les deux CSV sont générés par le moteur déterministe :

```bash
python scripts/generation_dataset.py --samples 5000 --seed 42
```

Ils ne contiennent aucune donnée patient : ce sont des trios simulés.

## Colonnes

- `id` : identifiant de l'échantillon ;
- `origine`, `age_pere`, `age_mere`, `antecedents_familiaux` : contexte simulé ;
- `maladies_evaluees` : identifiants séparés par `|`, dans l'ordre de
  `core.diseases.DISEASE_IDS` ;
- `{maladie}_parent1`, `{maladie}_parent2`, `{maladie}_enfant` : génotypes
  observés (éventuellement `inconnu`) ;
- `{maladie}_sexe_enfant` : `M`, `F` ou `inconnu` ;
- `{maladie}_statut` : statut calculé par `core.genetics.predict` ;
- `{maladie}_proba` : probabilité d'être atteint, ou vide si les données sont
  insuffisantes (jamais `0.0` par défaut) ;
- `{maladie}_methode` : `genotype`, `mendelian` ou `insufficient_data` ;
- `prompt_entree` : liste JSON de prompts, un par maladie évaluée ;
- `prompt_sortie` : liste JSON de cibles, alignées sur `prompt_entree`.

## Validation

```bash
python scripts/validate_dataset.py \
  data/dataset_synthetique.csv \
  data/dataset_test.csv
```

Le validateur vérifie la structure, la cohérence des longueurs, les statuts, les
probabilités et le recalcul complet par le moteur. Il retourne un code non nul
en cas d'erreur.

## Fréquences de simulation

Les fréquences alléliques de `core/simulation.py` sont des ordres de grandeur
destinés à produire des trios variés. Elles ne doivent pas être citées comme
données épidémiologiques.
