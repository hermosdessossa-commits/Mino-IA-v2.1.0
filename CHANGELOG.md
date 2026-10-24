# Journal des modifications

Toutes les modifications notables de Mino-IA sont documentées ici.
Format inspiré de [Keep a Changelog](https://keepachangelog.com/fr/1.1.0/).
Versionnement [SemVer](https://semver.org/lang/fr/).

## [2.1.0] — 2026-10-24

### Ajouté

- Moteur mendélien déterministe `core.genetics` : autosomique récessif et
  dominant, lié à l'X conditionné au sexe, dosage alpha, pénétrance réduite et
  allèle intermédiaire de Huntington.
- Registre unique des 12 maladies (`core.diseases`) avec normalisation des
  noms, accents et alias.
- Simulation de trios cohérents (`core.simulation`), enrichissement contrôlé en
  cas positifs et masquage des génotypes.
- Générateur de dataset réécrit, validation post-génération et script
  `scripts/validate_dataset.py`.
- Format de dataset centralisé (`core.dataset`) avec écriture atomique,
  chargement des paires prompt/cible et validation croisée avec le moteur.
- API Flask : moteur déterministe en premier, LLM de rédaction optionnel,
  erreurs JSON normalisées, `X-Request-Id`, `/health` enrichi, `/predict/batch`.
- Endpoints de licence complets : activation, statut, désactivation.
- Tests unitaires et d'intégration (114 tests), configuration Ruff, CI GitHub
  Actions, Dockerfile, Makefile et fichiers de dépendances séparés.
- Documentation : README réécrit, `SECURITY.md`, `CHANGELOG.md`, `LICENSE`,
  `.env.example`.
- Notebook Colab/Kaggle pour le fine-tuning LoRA de Mistral 7B, avec modes
  `smoke`/`full`, export propre de l'adaptateur et vérification optionnelle.

### Modifié

- `genotype_enfant` est désormais **optionnel** : sans lui, le moteur calcule la
  distribution mendélienne à partir des deux parents.
- Ajout de `sexe_enfant` pour les maladies liées à l'X ; le risque est
  conditionné au sexe et `details.risques_par_sexe` expose les deux valeurs.
- Les prompts incluent les faits déterministes et un brouillon de rapport ; le
  LLM ne doit plus recalculer la probabilité.
- Le dataset contient `{maladie}_sexe_enfant` et `{maladie}_methode`, et les
  cibles JSON reprennent exactement le statut et la probabilité du moteur.
- Les clés de licence sont lues depuis `MINO_LICENSE_KEYS` ou
  `MINO_LICENSE_KEYS_FILE`, plus aucune clé n'est codée en dur.
- La base de licences est stockée dans `var/`, écrite atomiquement et protégée
  par un verrou ; les IP sont hachées et salées.
- Le fine-tuning LoRA utilise toutes les paires, masque le prompt dans la loss
  (`-100`), applique un padding dynamique et calcule des métriques.
- Compatibilité Transformers 4.x/5.x : sélection automatique de
  `torch_dtype`/`dtype`, détection précise du template Llama 3, vérification du
  jeton `<|eot_id|>` et synchronisation du `pad_token_id`.

### Corrigé

- **P0** — L'activation de licence était inaccessible : les routes sont
  désormais publiques et la vérification est appliquée aux routes protégées.
- **P0** — L'hémophilie A et B étaient rejetées : le registre, le parseur
  X-linked et la validation Pydantic acceptent maintenant ces maladies.
- **P0** — Le mode démo renvoyait un faux `0,0 %` : une donnée insuffisante
  renvoie `probabilite: null` et `statut: "inconnu"`.
- **P0** — L'extraction Llama était cassée : seuls les tokens générés sont
  décodés, avec repli déterministe en cas d'échec.
- L'ordre `maladies_evaluees` / `prompt_entree` / `prompt_sortie` est stabilisé
  sur `DISEASE_IDS`.
- Huntington : distinction `PP` (pénétrance complète), `RP` (réduite) et `IM`
  (intermédiaire), au lieu d'un statut malade systématique.
- Alpha-thalassémie : le statut dépend du nombre d'allèles fonctionnels, et non
  d'une simple présence/absence.
- Le dataset historique (probabilités à `0.0` pour `inconnu`, colonnes
  manquantes) est remplacé par un dataset cohérent avec le moteur.

### Sécurité

- Aucune clé de licence en clair dans le code ou les logs.
- Permissions `600` sur la base de licences, verrou inter-processus.
- Hachage salé des adresses IP, aucun géocodage externe.
- Logs sans donnée patient ; `data/patients_reels.json` ignoré par Git.

### Ruptures de compatibilité

- `probabilite` peut être `null` ; les clients doivent gérer l'incertitude.
- `genotype_enfant` n'est plus obligatoire.
- Les CSV antérieurs à 2.1.0 ne passent pas le nouveau validateur.
- Les clés de licence ne sont plus lues depuis le code source.
