# Polices de la charte graphique

La charte utilise la famille **Roboto**. Ce dossier contient les quatre fichiers à installer pour que les modèles Word et PowerPoint s'affichent comme prévu.

| Fichier | Nom vu dans Word | Usage |
|---|---|---|
| `Roboto-Regular.ttf` | Roboto | Texte courant |
| `Roboto-Medium.ttf` | Roboto Medium | Sous-titres et accents |
| `Roboto-Bold.ttf` | Roboto (en gras) | Titres et texte en gras |
| `RobotoCondensed-Bold.ttf` | Roboto Condensed (en gras) | Titres étroits |

## Installer sous Windows

1. Ouvrez ce dossier `polices` dans l'Explorateur de fichiers.
2. Sélectionnez les quatre fichiers `.ttf` (touche Ctrl enfoncée, ou Ctrl + A).
3. Faites un clic droit sur la sélection, puis **Installer pour tous les utilisateurs** (si le choix n'apparaît pas, cliquez d'abord sur « Afficher plus d'options »). Acceptez la demande d'autorisation.
4. Fermez complètement Word et PowerPoint, puis rouvrez-les.

## Installer sous macOS

1. Ouvrez l'application **Livre des polices** (Font Book).
2. Glissez les quatre fichiers `.ttf` dans la fenêtre, ou menu **Fichier**, **Ajouter des polices à l'ordinateur**, puis choisissez les fichiers.
3. Si macOS affiche un avertissement de validation, choisissez de garder les polices.
4. Quittez Word et PowerPoint (Cmd + Q), puis rouvrez-les.

## Vérifier que Word voit les polices

1. Ouvrez un document Word vide, tapez quelques mots et sélectionnez-les.
2. Cliquez dans la liste des polices de l'onglet **Accueil** et tapez `Roboto`.
3. La liste doit proposer **Roboto**, **Roboto Medium** et **Roboto Condensed**.
4. Appliquez chacune des trois : l'aspect du texte doit changer. Pour Roboto Condensed, activez aussi le gras (Ctrl + B) : seule la version grasse est fournie.

Si une police manque : vérifiez que Word a bien été fermé puis rouvert, puis réinstallez le fichier correspondant.

## Provenance et licence

- Source : dépôt officiel `googlefonts/roboto-3-classic`, publication **v3.016**
  https://github.com/googlefonts/roboto-3-classic/releases/tag/v3.016
  (archive `Roboto_v3.016.zip`, dossier `hinted/static/`).
- Les fichiers sont des polices TrueType **statiques** (une par graisse), sans modification, car Word et PowerPoint gèrent mal les polices variables.
- Licence : **SIL Open Font License 1.1**, texte complet dans `OFL.txt` (copié depuis le dépôt officiel). Elle autorise l'usage, la copie et la redistribution, y compris dans une société, à condition de conserver ce fichier de licence avec les polices et de ne pas les vendre seules.
