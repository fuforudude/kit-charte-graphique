# 0002. Les modèles générés sont versionnés dans le dépôt, avec un test de fraîcheur

Date : 2026-11-19
Statut : acceptée

## Contexte
Le chef de projet et les développeurs non concernés par le script doivent récupérer les modèles sans installer Python. Il n'y a pas encore de CI pour publier des versions.

## Décision
Les fichiers générés sont commités dans `modeles/`. Le test `tests/test_modeles_a_jour.py` régénère les modèles et compare les valeurs des styles (pas les octets, qui changent à chaque génération) avec les fichiers commités ; il échoue si `charte.toml` a changé sans régénération.

## Options écartées
- Publication GitHub (Release) : plus propre, mais demande une CI qui n'existe pas.
- Génération par chacun : inutilisable pour un non-développeur.

## Conséquences
- Téléchargement direct depuis GitHub ou le dossier partagé.
- Des fichiers binaires dans Git : chaque régénération ajoute une version complète.
- Côté présentation, le test compare le thème, les styles de texte, les dispositions et le style de tableau, mais pas la géométrie des dispositions ni les diapositives d'exemple.
- À reconsidérer si une CI de publication est mise en place.
