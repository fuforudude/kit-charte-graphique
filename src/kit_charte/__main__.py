"""python -m kit_charte : régénère modeles/dossier.dotx et modeles/presentation.potx depuis charte.toml."""
import argparse
import sys
from pathlib import Path

from kit_charte.charte import CHARTE_PAR_DEFAUT, CharteError, lire_charte
from kit_charte.dossier import generer_dossier
from kit_charte.presentation import generer_presentation

RACINE = CHARTE_PAR_DEFAUT.parent


def generer_modeles(sortie: Path, charte_chemin: Path = CHARTE_PAR_DEFAUT, racine: Path = RACINE) -> list[Path]:
    charte = lire_charte(charte_chemin)
    return [
        generer_dossier(charte, sortie / "dossier.dotx", racine),
        generer_presentation(charte, sortie / "presentation.potx", racine),
    ]


def main(argv: list[str] | None = None) -> int:
    parseur = argparse.ArgumentParser(prog="kit-charte", description=__doc__)
    parseur.add_argument("--sortie", type=Path, default=RACINE / "modeles",
                         help="dossier d'écriture des modèles (défaut : modeles/ à la racine du dépôt)")
    args = parseur.parse_args(argv)
    try:
        for chemin in generer_modeles(args.sortie):
            print(chemin)
    except (CharteError, OSError) as e:  # LogoIntrouvableError est un FileNotFoundError, donc un OSError
        print(f"Erreur : {e}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
