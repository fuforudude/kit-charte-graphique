# 0001. Les modèles Office sont générés par un script Python à partir de charte.toml

Date : 2026-11-19
Statut : acceptée

## Contexte
L'équipe doit produire des modèles Word et PowerPoint conformes à la charte graphique relevée. Les valeurs (couleurs, polices, tailles) peuvent changer après un nouveau relevé, et la conformité doit pouvoir se vérifier sans ouvrir Office.

## Décision
Un script Python (python-docx, python-pptx) génère `modeles/dossier.dotx` et `modeles/presentation.potx`. Toutes les valeurs viennent de `charte.toml`, seule source, lu et validé par `kit_charte.charte.lire_charte`. Les valeurs absentes de la charte (tailles des diapositives) y figurent aussi, marquées « choix de l'équipe ». Les modèles Google sont obtenus par import des fichiers Office.

## Options écartées
- Modèles faits à la main dans Office : rapides pour la mise en page, mais illisibles dans Git et vérifiables seulement à l'œil.
- Hybride couverture manuelle et styles par script : deux sources à garder cohérentes.
- JavaScript (docx, pptxgenjs) : moins adapté à la fabrication de vrais modèles avec styles et masques.
- API Google : compte de service et autorisations, beaucoup plus de travail pour un rendu « proche » suffisant.

## Conséquences
- Changer une valeur de la charte revient à modifier `charte.toml` et lancer `python -m kit_charte`.
- Chaque style est testé automatiquement.
- python-pptx ne sait pas créer de dispositions de masque : le générateur réécrit le XML des dispositions par défaut. Un fichier qui s'ouvre sans message de réparation ne se vérifie qu'à la main dans Word et PowerPoint.
- Les modèles Google ne sont pas reproductibles automatiquement.
