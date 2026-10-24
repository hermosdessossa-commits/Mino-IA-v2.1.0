# Politique de sécurité

## Versions supportées

| Version | Support de sécurité |
|---------|---------------------|
| 2.1.x | Oui |
| < 2.1 | Non |

## Signaler une vulnérabilité

Merci de **ne pas ouvrir d'issue publique** pour une vulnérabilité de sécurité.

Utilisez de préférence l'onglet *Security advisories* du dépôt GitHub
(`Report a vulnerability`) ou contactez le mainteneur par un canal privé.

Merci d'inclure :

- la version concernée et l'environnement (système, Python, navigateur/client) ;
- une description du problème et de son impact ;
- les étapes de reproduction, avec une requête ou un fichier minimal ;
- les journaux pertinents, **sans donnée patient ni clé de licence** ;
- toute mesure d'atténuation envisagée.

Accusé de réception sous 72 heures ouvrées. Une divulgation coordonnée est
préférée ; aucun détail exploitable ne sera publié avant correction.

## Périmètre

Sont notamment concernés :

- le contournement de la vérification de licence ou des limites de machines ;
- l'accès non authentifié à `/predict` ou `/predict/batch` ;
- l'injection, la fuite ou la corruption de données via l'API ;
- l'exposition de secrets, de clés ou de données personnelles ;
- les dépendances vulnérables.

Ne sont pas considérés comme des vulnérabilités :

- l'absence de rate limiting ou de WAF, qui relève du déploiement ;
- des résultats génétiques inexacts dus à des données d'entrée incohérentes,
  sauf contournement du moteur déterministe ;
- des rapports LLM maladroits, dès lors que les valeurs cliniques restent
  celles du moteur ;
- les avertissements de scanners sans impact démontré.

## Bonnes pratiques de déploiement

- Servir l'API derrière HTTPS (reverse proxy).
- Définir `MINO_LICENSE_KEYS_FILE` ou `MINO_LICENSE_KEYS` hors du dépôt.
- Générer un `MINO_IP_HASH_SALT` aléatoire et stable (`openssl rand -hex 32`).
- Restreindre l'accès à `var/license_db.json` au compte du service.
- Ne jamais journaliser de génotype, de nom ou de donnée identifiante.
- Mettre à jour Flask, Pydantic et Gunicorn régulièrement.
- Désactiver le LLM (`MINO_USE_LLM=0`) si la rédaction n'est pas nécessaire.
