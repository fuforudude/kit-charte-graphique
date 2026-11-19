"""Lecture de charte.toml : structure typée, couleurs des styles résolues en hexadécimal."""
import re
import tomllib
from dataclasses import dataclass
from pathlib import Path

CHARTE_PAR_DEFAUT = Path(__file__).resolve().parents[2] / "charte.toml"
_HEX = re.compile(r"#[0-9A-Fa-f]{6}")


class CharteError(ValueError):
    """charte.toml est invalide."""


@dataclass(frozen=True)
class Polices:
    texte: str
    titre: str
    medium: str
    repli: str


@dataclass(frozen=True)
class Style:
    police: str
    taille: float
    couleur: str  # hexadécimal #RRGGBB, déjà résolu
    gras: bool = False
    capitales: bool = False
    souligne: bool = False
    interligne: float | None = None
    alignement: str | None = None


@dataclass(frozen=True)
class Tableau:
    entete_fond: str
    entete_texte: str
    entete_police: str
    entete_gras: bool
    filets: str


@dataclass(frozen=True)
class Presentation:
    format: str
    titres_police: str
    titres_gras: bool
    titres_couleur: str
    texte_police: str
    texte_couleur: str
    chiffres_police: str
    chiffres_gras: bool
    chiffres_couleur: str


@dataclass(frozen=True)
class Document:
    societe: str
    logo: str


@dataclass(frozen=True)
class Formes:
    rayon_carte: int
    rayon_bouton: int


@dataclass(frozen=True)
class Charte:
    couleurs: dict[str, str]
    interdites_texte: tuple[str, ...]
    polices: Polices
    styles: dict[str, Style]
    tableau: Tableau
    presentation: Presentation
    document: Document
    formes: Formes


def _couleur(couleurs: dict[str, str], nom: str, ou: str) -> str:
    if nom not in couleurs:
        raise CharteError(f"{ou} : couleur inconnue « {nom} »")
    return couleurs[nom]


def _couleur_texte(couleurs: dict[str, str], interdites: tuple[str, ...], nom: str, ou: str) -> str:
    hexa = _couleur(couleurs, nom, ou)
    if nom in interdites:
        raise CharteError(f"{ou} : la couleur « {nom} » est interdite en texte")
    return hexa


def lire_charte(chemin: Path | str = CHARTE_PAR_DEFAUT) -> Charte:
    with open(chemin, "rb") as f:
        brut = tomllib.load(f)
    try:
        couleurs = brut["couleurs"]
        interdites = tuple(brut["interdites_texte"])
        for nom, valeur in couleurs.items():
            if not isinstance(valeur, str) or not _HEX.fullmatch(valeur):
                raise CharteError(f"couleur « {nom} » : format #RRGGBB attendu, reçu {valeur!r}")
        for nom in interdites:
            _couleur(couleurs, nom, "interdites_texte")

        styles = {}
        for nom, s in brut["styles"].items():
            s = dict(s)
            hexa = _couleur_texte(couleurs, interdites, s.pop("couleur"), f"style « {nom} »")
            styles[nom] = Style(couleur=hexa, **s)

        t = dict(brut["tableau"])
        for cle in ("entete_fond", "entete_texte", "filets"):
            t[cle] = _couleur(couleurs, t[cle], f"tableau.{cle}")
        p = dict(brut["presentation"])
        for cle in ("titres_couleur", "texte_couleur", "chiffres_couleur"):
            p[cle] = _couleur_texte(couleurs, interdites, p[cle], f"presentation.{cle}")

        return Charte(
            couleurs=dict(couleurs),
            interdites_texte=interdites,
            polices=Polices(**brut["polices"]),
            styles=styles,
            tableau=Tableau(**t),
            presentation=Presentation(**p),
            document=Document(**brut["document"]),
            formes=Formes(**brut["formes"]),
        )
    except KeyError as e:
        raise CharteError(f"charte.toml : clé manquante {e}") from e
    except TypeError as e:
        raise CharteError(f"charte.toml : clé inattendue ou manquante ({e})") from e
