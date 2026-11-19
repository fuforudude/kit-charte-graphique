# Kit charte graphique

Kit de modèles de documents (dossier et présentation) à la charte graphique E.Leclerc relevée par l'équipe, pour Microsoft Office et Google, utilisé par l'équipe du projet d'étude M1 « Plateforme décisionnelle de pilotage commercial ». Une appli web de conversion des documents existants viendra dans un second temps.

## Commandes
- Lancer, compiler, tester : à définir avec les décisions techniques de la première spec (`docs/specs/`).
- Les commandes lourdes (génération de tous les modèles, suite de tests) se lancent via `lourd` (plugin `socle`) : `lourd <commande>`.

## Référence
- La charte graphique fait foi : `charte-graphique.pdf` (relevé du 18/11/2026). Couleurs, polices, tailles de texte et règles d'usage du logo en viennent ; aucune valeur inventée.
- Valeurs principales : bleu `#0066CC`, bleu survol `#0059B3`, bleu nuit `#0A3561`, orange `#FF6633` (accent seulement, jamais en couleur de texte), noir doux `#212529`, gris texte `#606060`, gris de fond `#E7E7E7`. Polices : Roboto (texte), Roboto Condensed Bold (titre du document, chiffres clés).

## Architecture
Voir `docs/architecture.md`. Les décisions structurantes sont dans `docs/adr/`, les specs dans `docs/specs/`.

## Conventions
- Tout en français : documents, commentaires, messages de commit.
- Le logo E.Leclerc et ses fichiers ne servent qu'aux livrables du projet d'étude (charte, §13) : le dépôt reste privé.
- Un seul logo par page (en couverture), un seul accent orange par page.

## Git
- Branche principale : `main`, protégée. Le travail passe par une branche `agents/<slug>` et une PR.
- Commits au nom de l'utilisateur (identité git configurée), message en français, sans mention de Claude.

## Agents de l'équipe
Ce projet utilise les plugins du marketplace `equipe` :
- En mode « Projet dev » (choisi à la création de la conversation, ou avec `/mode`), le chef de projet mène l'entretien et pilote les agents `dev`, `reviewer`, `qa`.
- En mode « Création d'assets », le chef de projet assets pilote `createur-2d`, `createur-3d` et `controle-assets` ; les assets sont suivis dans `.claude/assets.json`.
- Toute nouvelle fonctionnalité a une spec dans `docs/specs/`, toute décision structurante un ADR dans `docs/adr/`.
