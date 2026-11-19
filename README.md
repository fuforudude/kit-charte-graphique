# Kit de modèles de la charte graphique

Modèles Word (.dotx) et PowerPoint (.potx) générés à partir de `charte.toml`.
La notice utilisateur complète viendra avec la commande de génération.

## Développement

Depuis la racine du dépôt (PowerShell) :

```
python -m venv .venv
.venv\Scripts\python -m pip install -e ".[dev]"
.venv\Scripts\python -m pytest
```

Commande de génération des modèles (à venir, tâche 5) : `.venv\Scripts\python -m kit_charte`
