# Mino-IA 2.1.0

Moteur de conseil génétique **déterministe** pour 12 maladies héréditaires, exposé par une API REST sous licence. Les probabilités sont calculées par les lois de Mendel dans `core/` ; un LLM peut ensuite **rédiger** le compte rendu, mais il ne calcule jamais les valeurs cliniques.

> **AVERTISSEMENT MÉDICAL** — Mino-IA est une aide à la décision fondée sur des données synthétiques et sur les lois de Mendel. Il ne remplace en aucun cas un conseil génétique professionnel ni un test de laboratoire certifié. Toute décision médicale doit être confirmée par un médecin généticien ou un conseiller en génétique. Ce logiciel n'est pas un dispositif médical certifié.

---

## 1. Principe

| Composant | Rôle | Dépendances |
|-----------|------|-------------|
| `core/` | Registre des maladies, moteur mendélien, simulation, comptes rendus, métriques | Python standard uniquement |
| `api/` | API Flask, validation Pydantic, licences, rédaction LLM optionnelle | Flask, Pydantic |
| `scripts/` | Génération et validation du dataset synthétique | `core/` |
| `training/` | Fine-tuning LoRA du modèle de rédaction | PyTorch, Transformers, PEFT |
| `notebooks/` | Notebook de fine-tuning GPU pour Colab/Kaggle | GPU, PyTorch |
| `tests/` | 114 tests unitaires et d'intégration | pytest |

**Règle d'architecture :** `core.genetics.predict()` est l'unique source de vérité pour `probabilite`, `statut`, `methode` et `distribution`. L'API appelle toujours ce moteur en premier. Le LLM, s'il est activé, reçoit les faits déjà calculés et se contente de reformuler le rapport et les recommandations.

Conséquences directes :

- une donnée manquante renvoie `probabilite: null` et `statut: "inconnu"` — **jamais `0.0`** ;
- le mode déterministe fonctionne sans GPU, sans modèle et sans connexion réseau ;
- une panne du LLM dégrade la rédaction, pas la prédiction ;
- les tests du moteur s'exécutent sans PyTorch ni Transformers.

## 2. Maladies couvertes

| Identifiant | Maladie | Transmission | Gène(s) |
|-------------|---------|--------------|---------|
| `drepanocytose` | Drépanocytose | autosomique récessive | HBB |
| `mucoviscidose` | Mucoviscidose | autosomique récessive | CFTR |
| `thalassemie_alpha` | Thalassémie alpha | dosage des 4 gènes alpha | HBA1/HBA2 |
| `thalassemie_beta` | Thalassémie bêta | autosomique récessive | HBB |
| `phenylcetonurie` | Phénylcétonurie | autosomique récessive | PAH |
| `amyotrophie_spinale` | Amyotrophie spinale | autosomique récessive | SMN1/SMN2 |
| `huntington` | Maladie de Huntington | autosomique dominante | HTT |
| `marfan` | Syndrome de Marfan | autosomique dominante | FBN1 |
| `neurofibromatose1` | Neurofibromatose de type 1 | autosomique dominante | NF1 |
| `polykystose_renale` | Polykystose rénale autosomique dominante | autosomique dominante | PKD1/PKD2 |
| `hemophilie_A` | Hémophilie A | liée à l'X récessive | F8 |
| `hemophilie_B` | Hémophilie B | liée à l'X récessive | F9 |

Les noms accentués et les alias courants (`Hémophilie A`, `NF1`, `PKU`, `PKD`, `maladie de Huntington`, etc.) sont normalisés automatiquement.

## 3. Démarrage rapide

Prérequis : **Python 3.10 ou supérieur**.

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements-api.txt

cp .env.example .env
# Éditer .env : MINO_LICENSE_KEYS ou MINO_LICENSE_KEYS_FILE, MINO_IP_HASH_SALT
set -a && source .env && set +a

python -m api.app
# ou : gunicorn --bind 127.0.0.1:5000 --workers 2 wsgi:app
```

L'API écoute par défaut sur `http://127.0.0.1:5000`. Sans clé de licence configurée, `/health` et `/` restent accessibles, mais l'activation de licence répond `503` tant qu'aucune clé n'est configurée.

### Configurer une licence

Le serveur ne contient aucune clé en dur. Deux variables sont acceptées :

```bash
# 1) JSON directement dans l'environnement
export MINO_LICENSE_KEYS='[{"key":"MINO-EXEMPLE-CLE-0001","type":"standard","max_machines":2,"expires":"2027-12-31"}]'

# 2) ou fichier JSON lisible uniquement par le service
export MINO_LICENSE_KEYS_FILE=/etc/mino-ia/licenses.json
```

Le fichier peut contenir une liste :

```json
[
  {
    "key": "MINO-EXEMPLE-CLE-0001",
    "type": "standard",
    "max_machines": 2,
    "expires": "2027-12-31"
  }
]
```

ou un dictionnaire `{"clé": {"type": "...", "max_machines": 2, "expires": "..."}}`.

### Activer une installation

```bash
curl -sS -X POST http://127.0.0.1:5000/license/activate \
  -H 'Content-Type: application/json' \
  -d '{
    "license_key": "MINO-EXEMPLE-CLE-0001",
    "installation_id": "poste-cabinet-01",
    "machine_name": "Poste consultation"
  }'
```

La réponse contient `valid`, `machines_active`, `type`, `expires` et `country`. L'identifiant d'installation doit être stable et unique par poste.

### Première prédiction

```bash
curl -sS -X POST http://127.0.0.1:5000/predict \
  -H 'Content-Type: application/json' \
  -H 'X-License-Key: MINO-EXEMPLE-CLE-0001' \
  -H 'X-Installation-Id: poste-cabinet-01' \
  -d '{
    "maladie": "drepanocytose",
    "genotype_parent1": "A/S",
    "genotype_parent2": "A/S",
    "genotype_enfant": "S/S"
  }'
```

Réponse (extrait) :

```json
{
  "maladie": "drepanocytose",
  "probabilite": 1.0,
  "statut": "malade",
  "methode": "genotype",
  "genotype_enfant": "S/S",
  "distribution": {},
  "rapport": "Compte rendu de conseil génétique — Drépanocytose…",
  "recommandations": "Consultation en hématologie spécialisée…",
  "disclaimer": "AVERTISSEMENT MÉDICAL : …",
  "model_used": "deterministic",
  "llm_used": false,
  "request_id": "…"
}
```

Sans génotype d'enfant, mais avec les deux parents connus, le moteur renvoie la distribution mendélienne :

```bash
curl -sS -X POST http://127.0.0.1:5000/predict \
  -H 'Content-Type: application/json' \
  -H 'X-License-Key: MINO-EXEMPLE-CLE-0001' \
  -H 'X-Installation-Id: poste-cabinet-01' \
  -d '{"maladie":"drepanocytose","genotype_parent1":"A/S","genotype_parent2":"A/S"}'
```

```json
{
  "probabilite": 0.25,
  "statut": "risque",
  "methode": "mendelian",
  "distribution": {"A/A": 0.25, "A/S": 0.5, "S/S": 0.25}
}
```

## 4. API

| Méthode | Chemin | Licence | Description |
|---------|--------|---------|-------------|
| `GET` | `/` | non | Documentation et liste des maladies |
| `GET` | `/health` | non | État du service, du LLM et de la configuration de licence |
| `POST` | `/license/activate` | non | Active une installation |
| `POST` | `/license/status` | non | Statut d'une installation |
| `POST` | `/license/deactivate` | non | Libère une machine |
| `POST` | `/predict` | oui | Prédiction pour une maladie |
| `POST` | `/predict/batch` | oui | Jusqu'à 50 prédictions, erreurs isolées par élément |

Les routes protégées exigent les en-têtes `X-License-Key` et `X-Installation-Id`. Les erreurs sont renvoyées en JSON avec `error`, `code`, `request_id` et éventuellement `details`. Chaque réponse porte un `X-Request-Id` (repris s'il est fourni et valide) et `Cache-Control: no-store`.

### Champs de `/predict`

| Champ | Type | Obligatoire | Remarque |
|-------|------|-------------|----------|
| `maladie` | string | oui | Identifiant, nom ou alias |
| `genotype_parent1` | string | non | Père ; `"inconnu"` par défaut |
| `genotype_parent2` | string | non | Mère ; `"inconnu"` par défaut |
| `genotype_enfant` | string | non | Si absent, calcul à partir des parents |
| `sexe_enfant` | string | non | `M`, `F` ou `inconnu` ; indispensable pour l'X-linked |
| `origine` | string | non | Contexte, sans valeur diagnostique |
| `age_pere`, `age_mere` | int | non | 0 à 120 |
| `antecedents_familiaux` | string | non | Texte libre, sans données identifiantes |

Notations acceptées :

- autosomique : `A/S`, `AS`, `A / S`, `S/C` ;
- dominant : `WT`, `MUT`, `A/PP`, `A/RP`, `A/IM` ;
- polykystose : `PKD1:WT`, `PKD1:MUT` ;
- lié à l'X : `XY:sain`, `XY:malade`, `XX:saine`, `XX:porteuse`, `XX:malade` ;
- alpha : `AA/AA`, `AA/A-`, `A-/A-`, `A-/--`, `--/--` ou le nombre d'allèles fonctionnels `4`, `3`, `2`, `1`, `0`.

### Sémantique des résultats

- `probabilite` est la probabilité que l'enfant soit **atteint** (0 à 1).
- `probabilite: null` signifie **données insuffisantes** ; ce n'est pas une absence de risque.
- `methode` vaut `genotype` (génotype de l'enfant fourni), `mendelian` (calcul parental) ou `insufficient_data`.
- `statut` peut valoir `sain`, `saine`, `porteur`, `porteuse`, `porteur_im`, `a_risque`, `trait`, `malade`, `risque` ou `inconnu`.
- `distribution` détaille les génotypes attendus (ou les combinaisons sexe/statut pour l'X-linked).
- `details.risques_par_sexe` expose le risque masculin et féminin pour les maladies liées à l'X.

### Exemples remarquables

```bash
# Hémophilie A : mère porteuse, père sain, enfant de sexe masculin
curl -sS -X POST http://127.0.0.1:5000/predict \
  -H 'Content-Type: application/json' \
  -H 'X-License-Key: MINO-EXEMPLE-CLE-0001' \
  -H 'X-Installation-Id: poste-cabinet-01' \
  -d '{
    "maladie": "hemophilie_A",
    "genotype_parent1": "XY:sain",
    "genotype_parent2": "XX:porteuse",
    "sexe_enfant": "M"
  }'
# probabilite = 0.5, distribution = {"M:malade": 0.5, "M:sain": 0.5}

# Données insuffisantes : null, jamais 0.0
curl -sS -X POST http://127.0.0.1:5000/predict \
  -H 'Content-Type: application/json' \
  -H 'X-License-Key: MINO-EXEMPLE-CLE-0001' \
  -H 'X-Installation-Id: poste-cabinet-01' \
  -d '{"maladie":"drepanocytose"}'
# probabilite = null, statut = "inconnu", methode = "insufficient_data"
```

## 5. Dataset synthétique

Le dataset est généré à partir de trios parent-enfant cohérents, puis étiqueté par le moteur. Les CSV versionnés contiennent 4 000 échantillons d'entraînement et 1 000 de test (5 000 au total, graine 42).

```bash
# Régénérer (sauvegarde automatique dans data/backups/)
python scripts/generation_dataset.py --samples 5000 --seed 42

# Valider et afficher les statistiques
python scripts/validate_dataset.py data/dataset_synthetique.csv data/dataset_test.csv

# Vérifier la compatibilité avec l'entraînement, sans dépendance ML
python training/finetuning_lora.py --check-dataset
```

Chaque ligne contient les variables contextuelles, un trio par maladie évaluée (`{maladie}_parent1`, `_parent2`, `_enfant`, `_sexe_enfant`, `_statut`, `_proba`, `_methode`) et les listes JSON `prompt_entree` / `prompt_sortie`. Les prompts incluent les faits déterministes et un brouillon de rapport ; la cible JSON reprend exactement la probabilité et le statut du moteur.

Options utiles :

- `--case-rate` : proportion de scénarios enrichis en cas positifs (les lois de Mendel restent respectées) ;
- `--missing-rate` : taux de génotypes masqués, pour apprendre à gérer l'incertitude ;
- `--strict` : échec si la validation post-génération détecte une incohérence.

## 6. Rédaction par LLM (optionnel)

Le LLM ne sert qu'à reformuler. Il est désactivé par défaut et n'est chargé que si `MINO_USE_LLM=1`.

```bash
pip install -r requirements-ml.txt

# Vérifier le dataset
python training/finetuning_lora.py --check-dataset

# Fine-tuning LoRA (GPU recommandé ; CPU possible mais lent)
python training/finetuning_lora.py \
  --model mistralai/Mistral-7B-Instruct-v0.3 \
  --epochs 3 \
  --batch-size 1 \
  --gradient-accumulation 16

# Servir l'API avec rédaction LLM
MINO_USE_LLM=1 gunicorn --bind 0.0.0.0:8000 --workers 1 --timeout 120 wsgi:app
```

L'adaptateur est cherché dans `model/lora-adapter/`. Le prompt est masqué dans la loss (`-100`), le padding est dynamique, et l'évaluation calcule MAE, RMSE, accuracy, sensibilité, spécificité et AUROC, avec une baseline « toujours 0 % ». Toute sortie LLM non JSON, trop courte ou incohérente est ignorée : l'API renvoie alors le rapport déterministe.

### Fine-tuning sur GPU (Colab/Kaggle)

Un notebook prêt à exécuter automatise l'installation, la validation du dataset, le choix entre un mode `smoke` rapide et un mode `full`, l'entraînement LoRA 4 bits, l'évaluation et l'export de l'adaptateur :

[![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/hermosdessossa-commits/Mino-IA-v2.1.0/blob/main/notebooks/finetuning_lora_colab_kaggle.ipynb)

- **T4 16 Go** : mode `smoke`, ou `full` avec `MAX_SEQ_LENGTH=1024` ;
- **A100 40 Go** : mode `full` confortable en 2 048 tokens ;
- **Kaggle** : importer `notebooks/finetuning_lora_colab_kaggle.ipynb` depuis GitHub.

Voir [`notebooks/README.md`](notebooks/README.md) pour les prérequis, les durées indicatives et le dépannage.

## 7. Tests et qualité

```bash
pip install -r requirements-dev.txt

pytest -q                 # 114 tests
pytest --cov=core --cov=api --cov-report=term-missing
ruff format --check .
ruff check .
python -m compileall -q core api scripts training tests wsgi.py

# Tout en une commande
make check
```

La CI GitHub Actions exécute le lint, le formatage, la compilation et les tests sur Python 3.10 et 3.12, puis génère et valide un dataset de démonstration. Le workflow vérifie aussi que le dataset versionné reste cohérent avec le moteur.

## 8. Docker

```bash
docker build -t mino-ia:2.1.0 .
docker run --rm -p 8000:8000 --env-file .env mino-ia:2.1.0
```

L'image ne contient que l'API déterministe (pas de PyTorch). Elle tourne avec un utilisateur non privilégié, expose `8000` et possède un healthcheck sur `/health`. Montez un volume pour `var/` si la base de licences doit survivre aux redémarrages :

```bash
docker run --rm -p 8000:8000 --env-file .env \
  -v "$PWD/var:/app/var" mino-ia:2.1.0
```

## 9. Sécurité et données personnelles

- Aucune clé de licence n'est stockée en clair : seules les empreintes SHA-256 sont conservées en mémoire.
- La base des installations est écrite de façon atomique, avec verrou inter-processus et permissions `600`.
- Les adresses IP sont hachées avec `MINO_IP_HASH_SALT` avant stockage ; aucun géocodage externe n'est effectué. Les adresses privées sont marquées `Local`, les autres `Inconnu`.
- Les logs ne contiennent ni génotype, ni nom, ni adresse. Le `request_id` sert à la traçabilité.
- Les secrets doivent être fournis par l'environnement ou un fichier protégé, jamais commités.
- `data/patients_reels.json` est ignoré par Git et destiné à rester local.

Voir [`SECURITY.md`](SECURITY.md) pour la procédure de signalement.

## 10. Limites

- Les fréquences alléliques de simulation sont des ordres de grandeur, pas des données épidémiologiques de référence.
- Le moteur suppose une transmission mendélienne classique : pas de mutation *de novo*, pas de consanguinité, pas d'interaction entre gènes, pénétrance incomplète modélisée de façon simplifiée.
- La thalassémie alpha est modélisée par dosage génique, sans distinction des sous-types moléculaires.
- Le projet n'est pas un dispositif médical certifié et ne doit pas être utilisé seul pour une décision clinique.
- Le LLM peut reformuler maladroitement ; ses sorties sont contrôlées mais ne remplacent pas une relecture professionnelle.

## 11. Licence

Le code est distribué sous licence propriétaire Mino-IA. Voir [`LICENSE`](LICENSE). Toute utilisation clinique, redistribution ou intégration commerciale nécessite une autorisation écrite de l'éditeur.

## 12. Historique

Voir [`CHANGELOG.md`](CHANGELOG.md). La version 2.1.0 remplace le cœur « LLM qui estime une probabilité » par un moteur mendélien déterministe et corrige les bugs critiques de la version précédente.
