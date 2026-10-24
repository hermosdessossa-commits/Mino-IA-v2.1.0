# Notebooks

## Fine-tuning LoRA de Mistral 7B — Colab / Kaggle

[![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/hermosdessossa-commits/Mino-IA-v2.1.0/blob/main/notebooks/finetuning_lora_colab_kaggle.ipynb)

Fichier : [`finetuning_lora_colab_kaggle.ipynb`](finetuning_lora_colab_kaggle.ipynb)

Ce notebook automatise :

1. la vérification du GPU et de la VRAM ;
2. le clonage du dépôt et l'installation de `requirements-ml.txt` ;
3. la connexion Hugging Face optionnelle ;
4. la validation du dataset par le moteur déterministe ;
5. le choix entre un mode `smoke` rapide et un mode `full` ;
6. le fine-tuning LoRA 4 bits de Mistral 7B ;
7. l'évaluation sur le jeu de test ;
8. l'export propre de l'adaptateur, sans checkpoints d'entraînement ;
9. la copie vers Google Drive ou `/kaggle/working` ;
10. l'export optionnel d'un modèle fusionné autonome ;
11. une vérification optionnelle de rechargement de l'adaptateur.

### Ouvrir le notebook

- **Colab** : utiliser le badge ci-dessus, puis activer un GPU T4 ou A100.
- **Kaggle** : *File → Import Notebook → GitHub*, puis coller l'URL du fichier.

### Matériel recommandé

| Configuration | Usage |
|---------------|-------|
| T4 16 Go | Mode `smoke`, ou `full` avec `MAX_SEQ_LENGTH=1024` |
| A100 40 Go | Mode `full` confortable, `MAX_SEQ_LENGTH=2048` |
| P100 16 Go | Non recommandé : `bitsandbytes` 4 bits peut être incompatible |

Le mode `smoke` (200 paires, 1 époque) sert à vérifier la chaîne. Le mode
`full` (4 000 paires, 3 époques) produit l'adaptateur destiné à une évaluation
sérieuse. Sur Colab gratuit, le mode `full` peut dépasser la durée de session ;
préférer Colab Pro/A100 ou Kaggle.

### Sortie : adaptateur LoRA

Le notebook exporte par défaut :

- `adapter_config.json`
- `adapter_model.safetensors`
- les fichiers du tokenizer
- `training_metadata.json`

Les checkpoints (`optimizer.pt`, `rng_state.pth`, etc.) restent dans
`model/lora-adapter/` et ne sont pas inclus dans l'archive.

### Modèle fusionné (optionnel)

La cellule 10 peut fusionner l'adaptateur avec Mistral 7B et sauvegarder un
modèle autonome d'environ **14,5 Go**. L'adaptateur reste recommandé pour
l'usage courant : il est beaucoup plus léger.

| Ressource | Minimum |
|-----------|---------|
| VRAM GPU | 20 Go (A100 40 Go, L4 24 Go) |
| ou RAM système | 24 Go (Colab high-RAM, Kaggle) |
| Disque libre | 18 Go (34 Go avec archive ZIP) |

Sur un Colab T4 standard (16 Go de VRAM, 12,7 Go de RAM), la fusion n'est pas
possible : conserver l'adaptateur. Sur Kaggle, elle se fait sur CPU avec environ
30 Go de RAM ; c'est lent mais fonctionnel.

Pour récupérer le modèle fusionné :

- **Hugging Face Hub** (recommandé) : activer `PUSH_MERGED_TO_HUB` et renseigner
  un dépôt privé dans `HUB_REPO_ID` ;
- **archive ZIP** : activer `ZIP_MERGED_MODEL` ;
- **Google Drive** : à éviter avec un compte gratuit (15 Go au total).

Pour servir le modèle fusionné avec Mino-IA, pointer `MINO_MODEL` vers le dossier
exporté. Si `model/lora-adapter/` contient encore l'adaptateur, le retirer ou le
renommer : sinon il serait appliqué une seconde fois.

Le modèle fusionné reste soumis à la licence du modèle de base.

### Sécurité

- Ne jamais écrire un token Hugging Face dans une cellule ou un commit.
- Colab : utiliser le champ masqué `getpass`.
- Kaggle : utiliser *Add-ons → Secrets* avec la clé `HF_TOKEN`.
- L'adaptateur reste un artefact expérimental : le moteur mendélien demeure la
  source de vérité et aucune donnée patient ne doit être utilisée.

Voir le [README principal](../README.md) et [`SECURITY.md`](../SECURITY.md).
