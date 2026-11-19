# Architecture

## Vue d'ensemble
Le kit contient deux modèles à la charte, déclinés pour chaque logiciel de l'équipe :
- un modèle de dossier (cahier des charges, DAT, comptes rendus, questionnaires) ;
- un modèle de présentation de comité.

Logiciels couverts : Microsoft Office (Word, PowerPoint) et Google (Docs, Slides). La police Roboto est fournie avec une notice d'installation.

Les modèles Office sont générés par un script Python depuis `charte.toml` (ADR 0001) et versionnés dans `modeles/` (ADR 0002). Les modèles Google s'obtiennent par import (procédure dans le README).

## Organisation du code
| Dossier | Rôle |
|---|---|
| `charte.toml` | Seule source des valeurs de la charte (et choix de l'équipe marqués) |
| `src/kit_charte/charte.py` | Lecture et validation de `charte.toml` |
| `src/kit_charte/dossier.py` | Génération du modèle Word `.dotx` |
| `src/kit_charte/presentation.py` | Génération du modèle PowerPoint `.potx` |
| `src/kit_charte/__main__.py` | Commande `python -m kit_charte` |
| `modeles/` | Modèles générés, commités |
| `polices/`, `logos/` | Polices Roboto (OFL) et logo E.Leclerc, avec provenance |
| `tests/` | Tests des styles, de la charte et de la fraîcheur des modèles |
| `docs/specs/` | Specs des fonctionnalités |
| `docs/adr/` | Décisions d'architecture |

## Points d'attention
- La charte (`charte-graphique.pdf`) est la seule source des valeurs de couleur, de police et de taille.
- Les logos E.Leclerc sont réservés aux livrables du projet d'étude : ne jamais rendre le dépôt public.
