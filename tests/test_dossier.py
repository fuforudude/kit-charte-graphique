import re
import shutil
import struct
import zipfile
import zlib

import pytest
from docx.shared import Pt

from kit_charte.charte import CHARTE_PAR_DEFAUT, lire_charte
from kit_charte.dossier import (
    LogoIntrouvableError,
    TYPE_MODELE,
    generer_dossier,
    ouvrir_modele_pour_test,
)

W = "{http://schemas.openxmlformats.org/wordprocessingml/2006/main}"


def _png_minimal() -> bytes:
    def bloc(type_, data):
        return struct.pack(">I", len(data)) + type_ + data + struct.pack(">I", zlib.crc32(type_ + data))

    ihdr = struct.pack(">IIBBBBB", 1, 1, 8, 2, 0, 0, 0)
    return (b"\x89PNG\r\n\x1a\n" + bloc(b"IHDR", ihdr)
            + bloc(b"IDAT", zlib.compress(b"\x00\xff\xff\xff")) + bloc(b"IEND", b""))


@pytest.fixture
def projet(tmp_path):
    (tmp_path / "logos").mkdir()
    (tmp_path / "logos" / "e-leclerc-horizontal.png").write_bytes(_png_minimal())
    shutil.copy(CHARTE_PAR_DEFAUT, tmp_path / "charte.toml")
    return tmp_path


@pytest.fixture
def modele(projet):
    charte = lire_charte(projet / "charte.toml")
    return charte, generer_dossier(charte, projet / "sortie" / "dossier.dotx", projet)


def _xml(chemin, partie):
    with zipfile.ZipFile(chemin) as z:
        return z.read(partie).decode()


def _verifie(st, police, taille, couleur, gras=False, capitales=False):
    assert st.font.name == police
    assert st.font.size == Pt(taille)
    assert str(st.font.color.rgb) == couleur
    assert bool(st.font.bold) is gras
    assert bool(st.font.all_caps) is capitales
    rfonts = st.element.rPr.find(f"{W}rFonts")
    assert {k.split("}")[1]: v for k, v in rfonts.attrib.items()} == {
        "ascii": police, "hAnsi": police, "eastAsia": police, "cs": police}


def test_styles(modele):
    st = ouvrir_modele_pour_test(modele[1]).styles
    _verifie(st["Titre du document"], "Roboto Condensed", 28, "0066CC", True, True)
    _verifie(st["Heading 1"], "Roboto", 18, "0066CC", True, True)
    _verifie(st["Heading 2"], "Roboto", 14, "0A3561", True)
    _verifie(st["Heading 3"], "Roboto Medium", 12, "212529")
    _verifie(st["Normal"], "Roboto", 11, "212529")
    assert st["Normal"].paragraph_format.line_spacing == 1.3
    assert st["Normal"].paragraph_format.alignment == 0
    _verifie(st["Lien"], "Roboto", 11, "0066CC")
    assert st["Lien"].font.underline is True
    _verifie(st["Caption"], "Roboto", 9, "606060")
    _verifie(st["Chiffre clé"], "Roboto Condensed", 36, "0066CC", True)


def test_style_tableau(modele):
    styles = _xml(modele[1], "word/styles.xml")
    bloc = re.search(r'<w:style [^>]*w:styleId="Tableaucharte".*?</w:style>', styles, re.S).group(0)
    ligne = re.search(r'<w:tblStylePr w:type="firstRow">.*?</w:tblStylePr>', bloc, re.S).group(0)
    assert 'w:fill="0066CC"' in ligne
    assert '<w:color w:val="FFFFFF"/>' in ligne and "<w:b/>" in ligne
    assert 'w:ascii="Roboto"' in ligne
    assert bloc.count('w:color="E7E7E7"') == 6


def test_pas_de_texte_orange(modele):
    for partie in ("word/styles.xml", "word/document.xml"):
        assert not re.search(r'<w:color w:val="(FF6633|DD390E)"', _xml(modele[1], partie), re.I)


def test_logo_unique_sur_la_couverture(modele):
    chemin = modele[1]
    with zipfile.ZipFile(chemin) as z:
        assert [n for n in z.namelist() if n.startswith("word/media/")] == ["word/media/image1.png"]
        autres = [n for n in z.namelist() if n.startswith("word/") and n.endswith(".xml") and n != "word/document.xml"]
        assert all("<w:drawing" not in z.read(n).decode() for n in autres)
    assert _xml(chemin, "word/document.xml").count("<w:drawing") == 1
    assert "<w:drawing" in ouvrir_modele_pour_test(chemin).paragraphs[0]._p.xml


def test_couverture(modele):
    charte, chemin = modele
    doc = ouvrir_modele_pour_test(chemin)
    textes = [p.text for p in doc.paragraphs[:10]]
    for attendu in ("[Titre du document]", "[Sous-titre]", "Date : [JJ/MM/AAAA]", "Version : [x.y]",
                    "Auteurs : [Nom, rôle]", charte.document.societe,
                    "Statut : [Brouillon / Validé]", "Diffusion : [Destinataires]"):
        assert attendu in textes
    assert doc.paragraphs[1].style.name == "Titre du document"


def test_en_tete_pied_et_premiere_page(modele):
    charte, chemin = modele
    section = ouvrir_modele_pour_test(chemin).sections[0]
    assert section.different_first_page_header_footer is True
    assert section.header.paragraphs[0].text == "[Titre du document]"
    pied = section.footer.paragraphs[0]
    assert charte.document.societe in pied.text
    assert "PAGE" in pied._p.xml
    assert section.first_page_header.is_linked_to_previous
    assert section.first_page_footer.is_linked_to_previous
    assert section.page_width.cm == pytest.approx(21, abs=0.01)
    assert section.page_height.cm == pytest.approx(29.7, abs=0.01)
    assert section.left_margin.cm == pytest.approx(2.5, abs=0.01)


def test_sommaire_et_exemple(modele):
    assert 'TOC \\o "1-3" \\h \\z \\u' in _xml(modele[1], "word/document.xml")
    assert "Clic droit, Mettre à jour le champ" in _xml(modele[1], "word/document.xml")
    doc = ouvrir_modele_pour_test(modele[1])
    assert {"Heading 1", "Heading 2", "Heading 3", "Caption", "Chiffre clé"} <= {p.style.name for p in doc.paragraphs}
    assert len(doc.tables) == 1 and len(doc.tables[0].rows) == 3
    assert doc.tables[0].style.name == "Tableau charte"


def test_type_de_contenu_modele(modele):
    assert f'PartName="/word/document.xml" ContentType="{TYPE_MODELE}"' in _xml(modele[1], "[Content_Types].xml")


def test_changer_une_couleur_change_le_style(projet):
    toml = projet / "charte.toml"
    toml.write_text(toml.read_text(encoding="utf-8").replace('bleu = "#0066CC"', 'bleu = "#123456"'), encoding="utf-8")
    chemin = generer_dossier(lire_charte(toml), projet / "d.dotx", projet)
    assert str(ouvrir_modele_pour_test(chemin).styles["Heading 1"].font.color.rgb) == "123456"
    assert 'w:fill="123456"' in _xml(chemin, "word/styles.xml")


def test_logo_absent(projet):
    (projet / "logos" / "e-leclerc-horizontal.png").unlink()
    with pytest.raises(LogoIntrouvableError, match="e-leclerc-horizontal.png"):
        generer_dossier(lire_charte(projet / "charte.toml"), projet / "d.dotx", projet)
