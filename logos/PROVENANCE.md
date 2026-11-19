# Provenance des logos

E.Leclerc est une marque déposée. Logo utilisé pour un projet d'étude, document non officiel, dépôt privé.

Récupération le 2026-11-19, depuis le site officiel `www.e.leclerc` (seule source utilisée).

## e-leclerc-horizontal.svg

- URL : https://www.e.leclerc/assets/images/e-leclerc-small.svg
- Fichier servi par le site, sans aucune modification (130 x 32, 7373 octets).
- Contenu : initiale E et point orange, nom Leclerc, symbole rond. Couleurs `#0066CC` et `#FF6633`.
- Attention : le fichier contient en plus deux rectangles de fond (`#1A1A1A` puis `#FFFFFF`) issus de la maquette Sketch d'origine. Il s'affiche donc sur fond blanc.

## e-leclerc-horizontal.png

- Dérivé du SVG ci-dessus, 2000 x 493 px, RGBA, fond transparent, proportions conservées.
- Méthode : copie du SVG dont seuls les deux rectangles de fond ont été retirés, affichée à 2000 px de large dans une page HTML locale à fond transparent, puis capturée avec Microsoft Edge sans interface :
  `msedge --headless --hide-scrollbars --default-background-color=00000000 --force-device-scale-factor=1 --window-size=2000,493 --screenshot=... page.html`
- Aucune dépendance ajoutée au projet.

## Écartés

`https://www.mouvement.leclerc/build/images/logo-leclerc.png` (126 x 30) et `logo-lemouvement.jpg` (210 x 53) : trop petits, et le second est le logo « Le Mouvement ».
