import struct
import zipfile
import zlib

import pytest
from lxml import etree
from pptx.enum.shapes import PP_PLACEHOLDER
from pptx.opc.constants import CONTENT_TYPE as CT
from pptx.opc.constants import RELATIONSHIP_TYPE as RT

from kit_charte.charte import CHARTE_PAR_DEFAUT, lire_charte
from kit_charte.presentation import ID_STYLE_TABLEAU, MARQUE_EXEMPLE, generer_presentation, ouvrir_modele

A = "{http://schemas.openxmlformats.org/drawingml/2006/main}"
P = "{http://schemas.openxmlformats.org/presentationml/2006/main}"
DISPOSITIONS = ["Titre", "Intercalaire", "Contenu", "Chiffres clés", "Tableau", "Fin"]


def png_minimal() -> bytes:
    """PNG valide de 1 × 1 pixel, construit sans Pillow."""
    def bloc(type_, donnees):
        return struct.pack(">I", len(donnees)) + type_ + donnees + struct.pack(">I", zlib.crc32(type_ + donnees))
    return (b"\x89PNG\r\n\x1a\n" + bloc(b"IHDR", struct.pack(">IIBBBBB", 1, 1, 8, 2, 0, 0, 0))
            + bloc(b"IDAT", zlib.compress(b"\x00\x00\x66\xcc")) + bloc(b"IEND", b""))


@pytest.fixture
def racine(tmp_path):
    logo = tmp_path / lire_charte().document.logo
    logo.parent.mkdir(parents=True)
    logo.write_bytes(png_minimal())
    return tmp_path


@pytest.fixture
def modele(racine):
    return generer_presentation(lire_charte(), racine / "modele.potx", racine)


@pytest.fixture
def prs(modele):
    return ouvrir_modele(modele)


def dispositions(prs):
    return {d.name: d for d in prs.slide_layouts}


def def_rpr(niveau):
    """(police, taille en pt, couleur, gras) d'un a:lvlNpPr."""
    rpr = niveau.find(f"{A}defRPr")
    return (rpr.find(f"{A}latin").get("typeface"), int(rpr.get("sz")) / 100,
            "#" + rpr.find(f"{A}solidFill/{A}srgbClr").get("val"), rpr.get("b") == "1")


def tous_les_xml(prs):
    elements = [prs.slide_master._element] + [d._element for d in prs.slide_layouts] + [s._element for s in prs.slides]
    from lxml import etree
    return [etree.tostring(e, encoding="unicode").upper() for e in elements]


def test_format_16_9(prs):
    assert (prs.slide_width, prs.slide_height) == (12192000, 6858000)
    assert prs._element.sldSz.get("type") is None


def test_six_dispositions_nommees(prs):
    assert [d.name for d in prs.slide_layouts] == DISPOSITIONS


def test_type_de_contenu_modele(modele):
    with zipfile.ZipFile(modele) as z:
        types = z.read("[Content_Types].xml").decode()
    assert CT.PML_TEMPLATE_MAIN in types
    assert CT.PML_PRESENTATION_MAIN not in types


def test_styles_du_masque(prs):
    styles = prs.slide_master._element.find(f"{P}txStyles")
    assert def_rpr(styles.find(f"{P}titleStyle/{A}lvl1pPr")) == ("Roboto", 32, "#0066CC", True)
    for niveau in styles.find(f"{P}bodyStyle"):
        police, _, couleur, gras = def_rpr(niveau)
        assert (police, couleur, gras) == ("Roboto", "#212529", False)


def test_theme(prs):
    from lxml import etree
    theme = etree.fromstring(prs.slide_master.part.part_related_by(RT.THEME).blob)
    couleurs = {e.tag.replace(A, ""): e[0].get("val") for e in theme.find(f".//{A}clrScheme")}
    assert couleurs["dk1"] == "212529" and couleurs["lt1"] == "FFFFFF"
    assert couleurs["dk2"] == "0A3561" and couleurs["lt2"] == "E7E7E7"
    assert couleurs["accent1"] == "0066CC" and couleurs["accent2"] == "FF6633"
    assert theme.find(f".//{A}majorFont/{A}latin").get("typeface") == "Roboto"
    assert theme.find(f".//{A}minorFont/{A}latin").get("typeface") == "Roboto"


def test_fond_blanc(prs):
    fond = prs.slide_master._element.find(f"{P}cSld/{P}bg//{A}srgbClr")
    assert fond.get("val") == "FFFFFF"


def test_chiffres_cles(prs):
    d = dispositions(prs)["Chiffres clés"]
    phs = {ph.placeholder_format.idx: ph for ph in d.placeholders}
    assert phs[0].placeholder_format.type == PP_PLACEHOLDER.TITLE
    for idx in (10, 11, 12):
        niveau = phs[idx]._element.find(f".//{A}lstStyle/{A}lvl1pPr")
        assert def_rpr(niveau) == ("Roboto Condensed", 54, "#0066CC", True)
    for idx in (13, 14, 15):
        police, _, couleur, _ = def_rpr(phs[idx]._element.find(f".//{A}lstStyle/{A}lvl1pPr"))
        assert (police, couleur) == ("Roboto", "#212529")


def test_tableau(prs):
    types = {ph.placeholder_format.type.name for ph in dispositions(prs)["Tableau"].placeholders}
    assert {"TITLE", "TABLE"} <= types


def test_intercalaire_bande_bleue_titre_blanc_gras(prs):
    d = dispositions(prs)["Intercalaire"]
    bande = next(s for s in d.shapes if s.name == "Bande")
    assert bande.width == prs.slide_width
    assert bande._element.find(f".//{A}solidFill/{A}srgbClr").get("val") == "0066CC"
    titre = next(ph for ph in d.placeholders if ph.placeholder_format.idx == 0)
    _, _, couleur, gras = def_rpr(titre._element.find(f".//{A}lstStyle/{A}lvl1pPr"))
    assert (couleur, gras) == ("#FFFFFF", True)


def test_aucune_couleur_interdite(prs):
    charte = lire_charte()
    interdites = [charte.couleurs[nom][1:].upper() for nom in charte.interdites_texte]
    assert interdites
    for xml in tous_les_xml(prs):
        for hexa in interdites:
            assert hexa not in xml
        assert 'VAL="ACCENT2"' not in xml


def test_titre_de_couverture_herite_du_masque(prs):
    titre = next(ph for ph in dispositions(prs)["Titre"].placeholders
                 if ph.placeholder_format.type == PP_PLACEHOLDER.CENTER_TITLE)
    assert not titre._element.findall(f".//{A}solidFill")
    assert all(e.get("b") is None for e in titre._element.iter(f"{A}defRPr", f"{A}rPr"))


def generer_avec(racine, de, vers):
    """Génère le modèle depuis une copie de charte.toml où `de` est remplacé par `vers`."""
    texte = CHARTE_PAR_DEFAUT.read_text(encoding="utf-8")
    assert texte.count(de) == 1, de
    toml = racine / "charte.toml"
    toml.write_text(texte.replace(de, vers), encoding="utf-8")
    return generer_presentation(lire_charte(toml), racine / "modele.potx", racine)


def styles_de_tableau(modele):
    with zipfile.ZipFile(modele) as z:
        return etree.fromstring(z.read("ppt/tableStyles.xml"))


def test_style_de_tableau_par_defaut(modele, prs):
    liste = styles_de_tableau(modele)
    assert liste.get("def") == ID_STYLE_TABLEAU
    style = liste.find(f"{A}tblStyle[@styleId='{ID_STYLE_TABLEAU}']")
    entete = style.find(f"{A}firstRow")
    assert entete.find(f"{A}tcStyle/{A}fill//{A}srgbClr").get("val") == "0066CC"
    texte = entete.find(f"{A}tcTxStyle")
    assert (texte.find(f"{A}srgbClr").get("val"), texte.get("b")) == ("FFFFFF", "on")
    assert texte.find(f"{A}font/{A}latin").get("typeface") == "Roboto"
    filets = style.findall(f"{A}wholeTbl/{A}tcStyle/{A}tcBdr/*//{A}srgbClr")
    assert filets and {f.get("val") for f in filets} == {"E7E7E7"}
    assert style.find(f"{A}band1H") is None and style.find(f"{A}band1V") is None
    tableau = next(s for s in prs.slides[DISPOSITIONS.index("Tableau")].shapes if s.has_table).table
    assert tableau._tbl.tblPr.find(f"{A}tableStyleId").text == ID_STYLE_TABLEAU
    assert tableau.first_row and not tableau.horz_banding


def test_changer_entete_fond_change_le_style_de_tableau(racine):
    modele = generer_avec(racine, 'entete_fond = "bleu"', 'entete_fond = "bleu_nuit"')
    entete = styles_de_tableau(modele).find(f"{A}tblStyle/{A}firstRow")
    assert entete.find(f"{A}tcStyle/{A}fill//{A}srgbClr").get("val") == "0A3561"


def test_changer_une_taille_change_le_titre(racine):
    prs = ouvrir_modele(generer_avec(racine, "titre = 32", "titre = 30"))
    titre = prs.slide_master._element.find(f"{P}txStyles/{P}titleStyle/{A}lvl1pPr")
    assert def_rpr(titre)[1] == 30


def test_metadonnees(modele, prs):
    cp = prs.core_properties
    assert cp.title == "Modèle de présentation"
    assert cp.author == lire_charte().document.societe
    assert not cp.last_modified_by and not cp.comments
    assert cp.created.year >= 2026
    with zipfile.ZipFile(modele) as z:
        noms = z.namelist()
        assert "docProps/thumbnail.jpeg" not in noms
        assert b"thumbnail" not in z.read("_rels/.rels")
        for nom in (n for n in noms if n.startswith("docProps/")):
            contenu = z.read(nom)
            assert b"python-pptx" not in contenu and b"Steve Canny" not in contenu, nom
        assert b"4:3" not in z.read("docProps/app.xml")
    theme = etree.fromstring(prs.slide_master.part.part_related_by(RT.THEME).blob)
    assert theme.get("name") == theme.find(f".//{A}clrScheme").get("name") == "Charte E.Leclerc"


def test_puces_en_police_de_repli(prs):
    puces = prs.slide_master._element.findall(f"{P}txStyles/{P}bodyStyle/*/{A}buFont")
    assert puces and {b.get("typeface") for b in puces} == {lire_charte().polices.repli}


def test_logo_seulement_sur_titre_et_fin(prs):
    def images(objet):
        return [r for r in objet.part.rels.values() if r.reltype == RT.IMAGE]
    assert not images(prs.slide_master)
    for nom, d in dispositions(prs).items():
        assert bool(images(d)) == (nom in ("Titre", "Fin")), nom
        assert bool(d._element.findall(f".//{P}pic")) == (nom in ("Titre", "Fin")), nom
    for diapo in prs.slides:
        assert not images(diapo)


def test_pied_de_page_des_dispositions_de_contenu(prs):
    for nom in ("Contenu", "Chiffres clés", "Tableau"):
        xml = tous_les_xml(prs)[1 + DISPOSITIONS.index(nom)]
        assert "[NOM DE LA SOCIÉTÉ]" in xml and 'TYPE="SLIDENUM"' in xml, nom


def test_une_diapositive_exemple_par_disposition(prs):
    assert [s.slide_layout.name for s in prs.slides] == DISPOSITIONS
    for diapo in prs.slides:
        textes = " ".join(sh.text_frame.text for sh in diapo.shapes if sh.has_text_frame)
        assert MARQUE_EXEMPLE in textes


def test_changer_une_couleur_change_le_style(racine):
    toml = racine / "charte.toml"
    toml.write_text(CHARTE_PAR_DEFAUT.read_text(encoding="utf-8").replace('bleu = "#0066CC"', 'bleu = "#123456"'),
                    encoding="utf-8")
    prs = ouvrir_modele(generer_presentation(lire_charte(toml), racine / "modele.potx", racine))
    titre = prs.slide_master._element.find(f"{P}txStyles/{P}titleStyle/{A}lvl1pPr")
    assert def_rpr(titre)[2] == "#123456"


def test_logo_absent(tmp_path):
    with pytest.raises(FileNotFoundError, match="e-leclerc-horizontal.png"):
        generer_presentation(lire_charte(), tmp_path / "modele.potx", tmp_path)


@pytest.mark.parametrize("nom", ["Titre", "Fin"])
def test_zone_de_protection_du_logo(prs, nom):
    """Charte §04 : vide d'au moins x (hauteur du logo) autour du logo, bords de la diapositive compris."""
    formes = list(dispositions(prs)[nom].shapes)
    logo = next(f for f in formes if f.name == "Logo")
    x = logo.height
    assert logo.left >= x and logo.top >= x
    gauche, haut, droite, bas = logo.left - x, logo.top - x, logo.left + logo.width + x, logo.top + logo.height + x
    for f in formes:
        if f is not logo:
            assert not (f.left < droite and f.left + f.width > gauche and f.top < bas and f.top + f.height > haut), f.name
