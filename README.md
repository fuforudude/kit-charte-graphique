# Kit de modèles de la charte graphique

## À quoi sert ce kit

Ce kit permet de produire des documents aux couleurs de la charte graphique E.Leclerc sans rien régler à la main : mêmes polices, mêmes couleurs, mêmes tailles de titres partout. Il contient :

| Élément | Où | Usage |
|---|---|---|
| Modèle de dossier Word | `modeles/dossier.dotx` | Cahier des charges, DAT, comptes rendus, questionnaires |
| Modèle de présentation PowerPoint | `modeles/presentation.potx` | Présentations de comité |
| Polices Roboto | `polices/` | À installer avant d'utiliser les modèles |
| Logo | `logos/` | Déjà intégré aux modèles |
| Réglages de la charte | `charte.toml` | Seule source des couleurs, polices et tailles |

## 1. Installer les polices

Les modèles utilisent Roboto, Roboto Medium et Roboto Condensed. Installez-les une fois sur chaque ordinateur en suivant `polices/LISEZMOI.md`, puis redémarrez Word et PowerPoint. Sans cela, les modèles s'affichent avec une police de remplacement (Arial).

## 2. Utiliser le modèle de dossier dans Word

1. Dans l'Explorateur de fichiers, faites un **double-clic** sur `modeles/dossier.dotx` : Word crée un **nouveau document** (le modèle lui-même n'est pas modifié).
2. Sur la couverture, remplacez chaque champ entre crochets : `[Titre du document]`, `[Sous-titre]`, `[JJ/MM/AAAA]`, `[x.y]`, `[Nom, rôle]`, `[Statut]`, `[Destinataires]`.
3. Écrivez vos titres avec les styles **Titre 1**, **Titre 2** et **Titre 3** (onglet Accueil, galerie de styles). Les styles « Titre du document », « Lien » et « Chiffre clé » sont aussi dans la galerie.
4. Pour **mettre à jour le sommaire** : clic droit dessus, puis « Mettre à jour les champs », puis « Mettre à jour toute la table ».
5. **Supprimez la page d'exemple** qui suit le sommaire quand vous n'en avez plus besoin.

## 3. Utiliser le modèle de présentation dans PowerPoint

1. Double-clic sur `modeles/presentation.potx` : PowerPoint crée une nouvelle présentation.
2. Onglet Accueil, **Nouvelle diapositive** : choisissez la disposition adaptée.

| Disposition | Usage |
|---|---|
| Titre | Première diapositive : titre, sous-titre, date, logo |
| Intercalaire | Début d'une nouvelle partie (bande bleue) |
| Contenu | Titre et texte à puces |
| Chiffres clés | Trois chiffres avec leur libellé |
| Tableau | Titre et tableau (l'en-tête bleu à texte blanc est appliqué) |
| Fin | Remerciements et contact, logo centré |

3. **Supprimez les diapositives « [Exemple à supprimer] »** livrées avec le modèle.

## 4. Exporter en PDF avec la police intégrée

Dans Word comme dans PowerPoint :

1. Fichier, **Options**, **Enregistrement**.
2. Cochez **Incorporer les polices dans le fichier**.
3. Fichier, **Enregistrer sous**, type **PDF**.

## 5. Importer dans Google Docs et Google Slides

Google ne lit pas directement les modèles Word et PowerPoint : on les importe une fois, puis on les réutilise.

1. Ouvrez Google Drive et glissez-y `dossier.dotx` (ou `presentation.potx`).
2. Clic droit sur le fichier, **Ouvrir avec**, **Google Docs** (ou **Google Slides**).
3. **Vérifiez le rendu** (liste de contrôle ci-dessous : couleurs, polices, tailles de titres). Google propose Roboto nativement.
4. Choisissez l'une des deux façons de le réutiliser :
   - **Modèle** : Google Docs, menu Fichier, enregistrer comme modèle si votre organisation le permet ; sinon, utilisez la copie ci-dessous.
   - **Partage en lecture** : cliquez sur Partager, donnez l'accès « Lecteur » ; chaque personne fait ensuite Fichier, **Créer une copie** et travaille sur sa copie.
5. Les champs du sommaire doivent être remis à jour dans Google Docs (Insertion, Table des matières) après saisie des titres.

## 6. Changer le nom de la société

Le nom « [Nom de la société] » est provisoire. Ouvrez `charte.toml`, section `[document]`, remplacez la valeur de `societe`, puis régénérez les modèles (section « Développement ») et recommitez les fichiers de `modeles/`.

## 7. Liste de contrôle visuel

À cocher après chaque régénération des modèles : les tests automatiques ne voient pas ces points.

- [ ] Le dossier et la présentation s'ouvrent sans message de réparation dans Word et PowerPoint.
- [ ] La couverture du dossier n'a ni en-tête ni pied de page.
- [ ] Le sommaire se met à jour (clic droit, « Mettre à jour les champs »).
- [ ] Le logo respecte la zone de protection : un vide au moins égal à la hauteur du symbole rond du logo l'entoure (charte, §04).
- [ ] Un PDF exporté contient Roboto (Fichier, Propriétés, Polices dans Acrobat ou un lecteur PDF).
- [ ] Après import dans Google, les couleurs, les polices et les tailles de titres sont conservées.
- [ ] Le numéro de diapositive s'affiche dans Google Slides.
- [ ] L'en-tête des tableaux est bleu à texte blanc dans PowerPoint et dans Google.

## Mentions

E.Leclerc est une marque déposée. Le logo est réservé aux livrables du projet d'étude ; ce dépôt est privé et ne doit pas être rendu public.


## Développement

Depuis la racine du dépôt (PowerShell) :

```
python -m venv .venv
.venv\Scripts\python -m pip install -e ".[dev]"
.venv\Scripts\python -m pytest
```

Régénérer les modèles (après toute modification de `charte.toml`, puis commiter `modeles/`) : `.venv\Scripts\python -m kit_charte`. Le test `tests/test_modeles_a_jour.py` échoue si les modèles ne correspondent plus à la charte.
