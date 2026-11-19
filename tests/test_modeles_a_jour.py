"""Les modèles commités dans modeles/ doivent correspondre à charte.toml (comparaison des valeurs, pas des octets)."""
import re
import zipfile
from pathlib import Path

import pytest
from lxml import etree

from kit_charte.__main__ import RACINE, generer_modeles
from kit_charte.charte import CHARTE_PAR_DEFAUT

MESSAGE = "Les modèles de modeles/ ne correspondent plus à charte.toml : lancez python -m kit_charte et commitez"
A = "{http://schemas.openxmlformats.org/drawingml/2006/main}"
P = "{http://schemas.openxmlformats.org/presentationml/2006/main}"
W = "{http://schemas.openxmlformats.org/wordprocessingml/2006/main}"


def _canon(el) -> bytes:
    return etree.tostring(el, method="c14n")


def _valeurs_dossier(chemin: Path) -> dict:
    """Style par style : police, taille, gras, capitales, couleur (tout le XML du style, sans dates ni identifiants)."""
    with zipfile.ZipFile(chemin) as z:
        styles = etree.fromstring(z.read("word/styles.xml"))
    return {s.get(f"{W}styleId"): _canon(s) for s in styles.iter(f"{W}style")}


def _valeurs_presentation(chemin: Path) -> dict:
    with zipfile.ZipFile(chemin) as z:
        def lire(nom):
            return etree.fromstring(z.read(nom))

        theme = lire("ppt/theme/theme1.xml")
        masque = lire("ppt/slideMasters/slideMaster1.xml")
        # Ordre d'usage des dispositions = ordre de sldLayoutIdLst du masque, via ses relations.
        rels = {r.get("Id"): r.get("Target") for r in lire("ppt/slideMasters/_rels/slideMaster1.xml.rels")}
        rid = "{http://schemas.openxmlformats.org/officeDocument/2006/relationships}id"
        dispositions = [
            lire("ppt/slideLayouts/" + rels[i.get(rid)].rsplit("/", 1)[-1]).find(f"{P}cSld").get("name")
            for i in masque.find(f"{P}sldLayoutIdLst")
        ]
        return {
            "clrScheme": _canon(theme.find(f".//{A}clrScheme")),
            "fontScheme": _canon(theme.find(f".//{A}fontScheme")),
            "txStyles": _canon(masque.find(f"{P}txStyles")),
            "dispositions": dispositions,
            "tableStyles": _canon(lire("ppt/tableStyles.xml")),
        }


def _ecarts(a: dict, b: dict) -> list[str]:
    return sorted(k for k in a.keys() | b.keys() if a.get(k) != b.get(k))


@pytest.fixture
def regeneres(tmp_path):
    return generer_modeles(tmp_path / "frais")


def test_modeles_a_jour(regeneres):
    dossier, presentation = regeneres
    dossier_commite = RACINE / "modeles" / "dossier.dotx"
    presentation_commitee = RACINE / "modeles" / "presentation.potx"
    assert dossier_commite.is_file() and presentation_commitee.is_file(), MESSAGE
    assert not _ecarts(_valeurs_dossier(dossier), _valeurs_dossier(dossier_commite)), MESSAGE
    assert not _ecarts(_valeurs_presentation(presentation), _valeurs_presentation(presentation_commitee)), MESSAGE


def test_detecte_une_couleur_modifiee(tmp_path, regeneres):
    texte = CHARTE_PAR_DEFAUT.read_text(encoding="utf-8").replace('bleu = "#0066CC"', 'bleu = "#0066CD"')
    charte = tmp_path / "charte.toml"
    charte.write_text(texte, encoding="utf-8")
    dossier, presentation = generer_modeles(tmp_path / "modif", charte_chemin=charte)
    assert _ecarts(_valeurs_dossier(dossier), _valeurs_dossier(regeneres[0]))
    ecarts = _ecarts(_valeurs_presentation(presentation), _valeurs_presentation(regeneres[1]))
    assert "clrScheme" in ecarts and "txStyles" in ecarts
