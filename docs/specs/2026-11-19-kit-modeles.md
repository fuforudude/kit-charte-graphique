# Kit de modèles à la charte : dossier et présentation

Statut : validée
Date : 2026-11-19

## Besoin
L'équipe du projet d'étude E.Leclerc (développeurs et chef de projet) doit envoyer au client des documents présentés de façon professionnelle, à la charte graphique relevée (`charte-graphique.pdf`). Aujourd'hui chacun met en forme à sa façon, et un questionnaire est parti en .odt brut. Le kit fournit des modèles prêts à remplir, utilisables sans compétence technique, avant le second envoi au client (début décembre).

## Périmètre
- Dedans :
  - un modèle de dossier Word (`.dotx`) : cahier des charges, DAT, comptes rendus, questionnaires ;
  - un modèle de présentation PowerPoint (`.potx`) pour les comités ;
  - un script Python qui génère ces deux modèles à partir d'un fichier de réglages TOML, seule source des valeurs de la charte ;
  - les polices Roboto et Roboto Condensed, leur licence et une notice d'installation ;
  - une notice utilisateur : installer la police, utiliser les modèles, exporter en PDF avec la police intégrée, importer les modèles dans Google Docs et Google Slides ;
  - une liste de contrôle visuel pour ce que les tests ne voient pas.
- Hors périmètre :
  - l'appli web de conversion des documents existants (second temps, avec son propre entretien) ;
  - les modèles LibreOffice, courrier, signature de mail et tableur ;
  - la création des modèles Google eux-mêmes : c'est une procédure manuelle décrite dans la notice, faite par l'étudiant ;
  - le nom définitif de la société prestataire : un champ provisoire en tient lieu.

## Critères d'acceptation
Valeurs reprises de la charte, page « Hiérarchie du texte » et page « Couleurs ».

Modèle de dossier :
- [ ] Le style « Titre du document » est en Roboto Condensed, gras, capitales, 28 pt, couleur `#0066CC`.
- [ ] Le style « Titre 1 » est en Roboto, gras, capitales, 18 pt, `#0066CC`.
- [ ] Le style « Titre 2 » est en Roboto, gras, 14 pt, `#0A3561`.
- [ ] Le style « Titre 3 » est en Roboto Medium, 12 pt, `#212529`.
- [ ] Le style « Corps » (style normal) est en Roboto, 11 pt, interligne 1,3, `#212529`, aligné à gauche.
- [ ] Le style « Lien » est en Roboto, 11 pt, `#0066CC`, souligné.
- [ ] Le style « Légende » est en Roboto, 9 pt, `#606060`.
- [ ] Le style « Chiffre clé » est en Roboto Condensed, gras, 36 pt, `#0066CC`.
- [ ] Le style de tableau a un en-tête sur fond `#0066CC` avec texte blanc en Roboto gras, et des filets `#E7E7E7`.
- [ ] Aucun style n'utilise l'orange `#FF6633` ni l'orange foncé `#DD390E` comme couleur de texte.
- [ ] La première page est une couverture avec : le logo E.Leclerc complet, le titre, la date, la version, les auteurs et leurs rôles, le nom de la société prestataire (champ provisoire « [Nom de la société] »), le statut et la diffusion.
- [ ] Le logo n'apparaît que sur la couverture.
- [ ] À partir de la deuxième page, l'en-tête affiche le titre du document, et le pied de page affiche le nom de la société et le numéro de page.
- [ ] Le modèle contient un sommaire automatique basé sur les titres 1 à 3.

Modèle de présentation :
- [ ] Les diapositives sont au format 16:9.
- [ ] Le masque propose au moins ces dispositions : titre, intercalaire de section, contenu, chiffres clés, tableau, fin.
- [ ] Les titres de diapositive sont en Roboto gras `#0066CC` (sauf l'intercalaire : titre blanc gras sur bande bleue), le texte en Roboto `#212529`, les chiffres clés en Roboto Condensed gras `#0066CC`.
- [ ] Le logo n'apparaît que sur la diapositive de titre et la diapositive de fin.
- [ ] Aucun texte n'utilise l'orange comme couleur.

Génération et livraison :
- [ ] Une seule commande régénère les deux modèles dans `modeles/` à partir de `charte.toml`.
- [ ] Changer une couleur dans `charte.toml` puis régénérer change cette couleur dans les styles des deux modèles.
- [ ] Un test échoue si les modèles commités dans `modeles/` ne correspondent plus à `charte.toml` (comparaison des valeurs de styles, pas des octets).
- [ ] Les modèles s'ouvrent sans message d'erreur ni de réparation dans Word et PowerPoint.
- [ ] La suite de tests passe.

Contrôle visuel (liste à cocher par l'étudiant, dans la notice) :
- [ ] La couverture respecte la zone de protection du logo.
- [ ] Un PDF exporté depuis Word avec l'option « Incorporer les polices » contient Roboto.
- [ ] Après import dans Google Docs et Google Slides, les couleurs, polices et tailles de titres sont conservées.

## Décisions techniques
Prises par l'étudiant (skill `decision-technique`), avec ses mots.
| Question | Options envisagées | Choix | Raison |
|---|---|---|---|
| Forme du premier livrable | Modèles d'abord, conversion d'abord, tout ensemble | Modèles d'abord | Recommandation suivie : utilisable tout de suite, sans code pour l'équipe. |
| Logiciels couverts | Un .docx partout, un modèle par logiciel | Un modèle par logiciel (Office et Google, sans LibreOffice) | Choix de l'étudiant ; le chef de projet passe à Google. |
| Fidélité dans Google | Rendu proche accepté, rendu identique exigé | Rendu proche accepté | Recommandation suivie. |
| Fabrication des modèles Office | Script versionné, à la main, hybride | Script versionné | Recommandation suivie : reproductible et testable. |
| Langage du script | Python, JavaScript | Python (python-docx, python-pptx) | Recommandation suivie. |
| Modèles Google | Import des fichiers Office, script avec l'API Google | Import des fichiers Office | Recommandation suivie : procédure écrite, sans code. |
| Vérification | Tests automatiques et contrôle visuel, contrôle visuel seul | Tests automatiques et contrôle visuel | Recommandation suivie. |
| Format des réglages | TOML, YAML, code Python | TOML | Recommandation suivie : lisible, sans dépendance. |
| Livraison des modèles | Versionnés dans le dépôt, Release GitHub, générés par chacun | Versionnés dans `modeles/` | Recommandation suivie. |
| Police | Dans le dépôt, lien Google Fonts | Dans le dépôt, avec la licence OFL | Recommandation suivie. |
| Tailles des diapositives (absentes de la charte) | Dans charte.toml, constantes dans le code | Dans charte.toml, marquées « choix de l'équipe » | Recommandation suivie : source unique. |
| Styles caractère liés aux titres (revue) | Les mettre à la charte, supprimer le lien | Les mettre à la charte | Recommandation suivie : Word garde son comportement habituel. |
| Ancienne copie des styles stylesWithEffects.xml (revue) | La retirer, la garder avec contrôle visuel | La retirer | Recommandation suivie : aucun risque de vieux styles repris. |
| Style du tableau de présentation (revue) | Style personnalisé depuis charte.toml, couleurs sur l'exemple, garder le style PowerPoint | Style personnalisé, déclaré par défaut | Recommandation suivie : source unique, s'applique aux nouveaux tableaux. |
| Titre de l'intercalaire (revue) | Blanc sur bande bleue, bleu sur fond blanc | Blanc sur bande bleue | Recommandation suivie : lisible, signe distinctif de la charte. Exception au critère « titres en bleu ». |
| Exemples dans les modèles (revue) | Garder, retirer | Garder, marqués « à supprimer » | Recommandation suivie : montre l'usage de chaque style. |

## Tâches
1. Socle : `pyproject.toml` (dépendances python-docx, python-pptx, pytest), `charte.toml` avec toutes les valeurs des pages « Couleurs » et « Hiérarchie du texte » de la charte, module de lecture des réglages et ses tests. Durée estimée : 30 min
2. Polices : dossier `polices/` avec Roboto (Regular, Medium, Bold) et Roboto Condensed (Bold), la licence OFL et la notice d'installation Windows et macOS. En parallèle de la tâche 1. Durée estimée : 20 min
3. Générateur du modèle de dossier `.dotx` : styles, style de tableau, couverture, en-tête et pied de page, sommaire, et tests des critères du modèle de dossier. Après la tâche 1. Durée estimée : 40 min
4. Générateur du modèle de présentation `.potx` : masque 16:9, dispositions, styles de texte, et tests des critères du modèle de présentation. En parallèle de la tâche 3. Durée estimée : 40 min
5. Commande de génération unique, test « modèles à jour », modèles générés commités dans `modeles/`, notice utilisateur (`README.md`) avec la procédure d'import Google et la liste de contrôle visuel. Après les tâches 2, 3 et 4. Durée estimée : 30 min

Durée estimée du jalon : 2 h 30, contrôles, QA et livraison compris.

## Impacts
- Données / migrations : aucune.
- API : aucune.
- Écrans : aucun ; les livrables sont des fichiers de modèles.

## Questions ouvertes
- Logo : le dossier `logos/` cité par la charte n'est pas dans le dépôt. Il faut au minimum `e-leclerc-horizontal.svg`. Word et PowerPoint gèrent mal le SVG depuis python-docx et python-pptx : une version PNG en haute définition est nécessaire. À fournir par l'étudiant, ou à convertir.
- Polices : récupérer les fichiers Roboto demande un téléchargement depuis le dépôt officiel Google Fonts. Il faut l'accord de l'étudiant avant de lancer la tâche 2.
- Python 3.14 est installé, mais pas python-docx, python-pptx ni pytest : la tâche 1 les installe dans un environnement virtuel du projet.
