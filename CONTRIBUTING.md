# Contribuer à Mino-IA

Merci de votre intérêt. Ce projet touche à la santé : la prudence, les tests et
la traçabilité priment sur la vitesse.

## Mise en place

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements-dev.txt
pytest -q
```

Pour le LLM (optionnel) : `pip install -r requirements-ml.txt`.

## Règles de contribution

1. **Le moteur déterministe est la source de vérité.** Ne jamais faire calculer
   une probabilité ou un statut par un LLM, un script de génération ou un test.
   Toute valeur clinique doit venir de `core.genetics.predict()`.
2. **Pas de donnée patient** dans les issues, les tests, les captures ou les
   commits. Utiliser uniquement des données synthétiques.
3. **Pas de secret** dans le dépôt : clés, sel d'IP, fichiers `.env` réels.
4. **Tests obligatoires** pour toute modification du moteur, du format de
   dataset, de l'API ou des licences.
5. **Compatibilité** : Python 3.10 minimum, pas de dépendance ML dans `core/`.

## Avant de proposer une modification

```bash
ruff format .
ruff check .
pytest -q
python -m compileall -q core api scripts training tests wsgi.py
```

Si le format du dataset change, régénérer un petit jeu et valider :

```bash
python scripts/generation_dataset.py --samples 120 --seed 42 \
  --output-dir /tmp/mino-data --no-backup
python scripts/validate_dataset.py \
  /tmp/mino-data/dataset_synthetique.csv \
  /tmp/mino-data/dataset_test.csv
```

## Style

- Français pour les docstrings, messages d'erreur et documentation.
- Identifiants et noms de fonctions en anglais ou en français, mais rester
  cohérent avec le module modifié.
- Lignes de 100 caractères maximum, formatage Ruff.
- Erreurs explicites : préférer une exception ou un `None` documenté à une
  valeur par défaut trompeuse (`0.0` pour une probabilité inconnue).
- Les commentaires expliquent le *pourquoi*, pas le *comment*.

## Commits et pull requests

- Un commit par intention, message à l'impératif.
- Décrire le comportement avant/après et les tests ajoutés.
- Lier l'issue concernée si elle existe.
- Ne pas mélanger refactorisation et correction fonctionnelle.

## Signalement de sécurité

Voir [`SECURITY.md`](SECURITY.md). Ne pas ouvrir d'issue publique.
