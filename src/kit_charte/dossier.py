"""Génération du modèle de dossier Word (.dotx) à partir de la charte."""
import zipfile
from datetime import datetime
from io import BytesIO
from pathlib import Path

from docx import Document
from docx.enum.style import WD_STYLE_TYPE
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml import OxmlElement, parse_xml
from docx.oxml.ns import nsdecls, qn
from docx.shared import Cm, Pt, RGBColor

from kit_charte.charte import Charte, Style

TYPE_DOCUMENT = "application/vnd.openxmlformats-officedocument.wordprocessingml.document.main+xml"
TYPE_MODELE = "application/vnd.openxmlformats-officedocument.wordprocessingml.template.main+xml"
NOM_STYLE_TABLEAU = "Tableau charte"
_ALIGNEMENTS = {
    "gauche": WD_ALIGN_PARAGRAPH.LEFT,
    "centre": WD_ALIGN_PARAGRAPH.CENTER,
    "droite": WD_ALIGN_PARAGRAPH.RIGHT,
    "justifie": WD_ALIGN_PARAGRAPH.JUSTIFY,
}


class LogoIntrouvableError(FileNotFoundError):
    """Le logo de la couverture n'existe pas au chemin attendu."""


def _hexa(couleur: str) -> str:
    return couleur.lstrip("#").upper()


def _polices(rpr, nom: str) -> None:
    """Police sur les quatre jeux (ascii, hAnsi, eastAsia, cs), sans attribut de thème."""
    for ancien in rpr.findall(qn("w:rFonts")):
        rpr.remove(ancien)
    rfonts = OxmlElement("w:rFonts")
    for attr in ("ascii", "hAnsi", "eastAsia", "cs"):
        rfonts.set(qn(f"w:{attr}"), nom)
    rpr.insert(0, rfonts)


def _appliquer(st, s: Style) -> None:
    f = st.font
    f.name = s.police
    _polices(st.element.get_or_add_rPr(), s.police)
    f.size = Pt(s.taille)
    f.bold = s.gras
    f.italic = False
    f.all_caps = s.capitales
    f.underline = s.souligne
    f.color.rgb = RGBColor.from_string(_hexa(s.couleur))
    if st.type == WD_STYLE_TYPE.PARAGRAPH:
        if s.interligne is not None:
            st.paragraph_format.line_spacing = s.interligne
        if s.alignement:
            st.paragraph_format.alignment = _ALIGNEMENTS[s.alignement]


def _style(doc, nom: str, type_, s: Style, galerie: bool = False) -> None:
    try:
        st = doc.styles[nom]
    except KeyError:
        st = doc.styles.add_style(nom, type_)
        if type_ == WD_STYLE_TYPE.PARAGRAPH:
            st.base_style = doc.styles["Normal"]
    _appliquer(st, s)
    if galerie:
        st.quick_style = True


def _style_tableau(doc, charte: Charte) -> None:
    t = charte.tableau
    st = doc.styles.add_style(NOM_STYLE_TABLEAU, WD_STYLE_TYPE.TABLE)
    filets = "".join(
        f'<w:{c} w:val="single" w:sz="4" w:space="0" w:color="{_hexa(t.filets)}"/>'
        for c in ("top", "left", "bottom", "right", "insideH", "insideV")
    )
    gras = "<w:b/>" if t.entete_gras else ""
    st.element.append(parse_xml(
        f'<w:tblPr {nsdecls("w")}><w:tblBorders>{filets}</w:tblBorders>'
        '<w:tblCellMar><w:top w:w="60" w:type="dxa"/><w:left w:w="100" w:type="dxa"/>'
        '<w:bottom w:w="60" w:type="dxa"/><w:right w:w="100" w:type="dxa"/></w:tblCellMar></w:tblPr>'
    ))
    st.element.append(parse_xml(
        f'<w:tblStylePr {nsdecls("w")} w:type="firstRow"><w:rPr>'
        f'<w:rFonts w:ascii="{t.entete_police}" w:hAnsi="{t.entete_police}" '
        f'w:eastAsia="{t.entete_police}" w:cs="{t.entete_police}"/>{gras}'
        f'<w:color w:val="{_hexa(t.entete_texte)}"/></w:rPr>'
        f'<w:tcPr><w:shd w:val="clear" w:color="auto" w:fill="{_hexa(t.entete_fond)}"/></w:tcPr>'
        '</w:tblStylePr>'
    ))


def _champ(paragraphe, instruction: str, resultat: str) -> None:
    """Champ Word complexe (begin / instrText / separate / résultat / end)."""
    def fldchar(type_):
        fc = OxmlElement("w:fldChar")
        fc.set(qn("w:fldCharType"), type_)
        paragraphe.add_run()._r.append(fc)

    fldchar("begin")
    it = OxmlElement("w:instrText")
    it.set(qn("xml:space"), "preserve")
    it.text = f" {instruction} "
    paragraphe.add_run()._r.append(it)
    fldchar("separate")
    paragraphe.add_run(resultat)
    fldchar("end")


def _couverture(doc, charte: Charte, logo: Path) -> None:
    image = doc.add_picture(str(logo), width=Cm(6))
    # Zone de protection (charte §04) : un vide au moins égal à x, la hauteur du logo, sous le logo.
    doc.paragraphs[-1].paragraph_format.space_after = image.height
    doc.add_paragraph("[Titre du document]", style="Titre du document")
    for ligne in (
        "[Sous-titre]",
        "Date : [JJ/MM/AAAA]",
        "Version : [x.y]",
        "Auteurs : [Nom, rôle]",
        charte.document.societe,
        "Statut : [Brouillon / Validé]",
        "Diffusion : [Destinataires]",
    ):
        doc.add_paragraph(ligne)
    doc.add_page_break()


def _sommaire_et_exemple(doc) -> None:
    doc.add_paragraph().add_run("Sommaire").bold = True
    _champ(doc.add_paragraph(), 'TOC \\o "1-3" \\h \\z \\u', "Clic droit, Mettre à jour le champ")
    doc.add_paragraph().add_run("EXEMPLE DE CONTENU : à remplacer par le contenu du dossier.").bold = True
    doc.add_heading("Titre 1 d'exemple", 1)
    doc.add_heading("Titre 2 d'exemple", 2)
    doc.add_heading("Titre 3 d'exemple", 3)
    p = doc.add_paragraph("Paragraphe de corps d'exemple, avec un ")
    p.add_run("lien d'exemple", style="Lien")
    p.add_run(".")
    tableau = doc.add_table(rows=3, cols=3, style=NOM_STYLE_TABLEAU)
    for i, ligne in enumerate(tableau.rows):
        for j, cellule in enumerate(ligne.cells):
            cellule.text = f"Colonne {j + 1}" if i == 0 else f"Valeur {i}.{j + 1}"
    doc.add_paragraph("Légende d'exemple du tableau", style="Caption")
    doc.add_paragraph("42 %", style="Chiffre clé")


def _entete_pied(doc, charte: Charte) -> None:
    section = doc.sections[0]
    section.different_first_page_header_footer = True
    section.header.paragraphs[0].text = "[Titre du document]"
    pied = section.footer.paragraphs[0]
    pied.text = f"{charte.document.societe}  |  Page "
    _champ(pied, "PAGE", "1")


def _metadonnees(doc, charte: Charte) -> None:
    p = doc.core_properties
    p.title = "Modèle de dossier"
    p.author = charte.document.societe
    p.comments = ""
    p.created = p.modified = datetime.now()


def _retirer_styles_with_effects(doc) -> None:
    """Supprime la partie héritée de Word 2010 : relation retirée, la partie et son type ne sont plus écrits."""
    rels = doc.part.rels
    for rid in [r for r, rel in rels.items() if rel.reltype.endswith("/stylesWithEffects")]:
        rels.pop(rid)


def generer_dossier(charte: Charte, sortie: Path, racine: Path) -> Path:
    logo = Path(racine) / charte.document.logo
    if not logo.is_file():
        raise LogoIntrouvableError(f"Logo introuvable : {logo} (attendu d'après charte.document.logo)")

    doc = Document()
    s = charte.styles
    _style(doc, "Normal", WD_STYLE_TYPE.PARAGRAPH, s["corps"])
    _style(doc, "Titre du document", WD_STYLE_TYPE.PARAGRAPH, s["titre_document"], galerie=True)
    for n, cle in ((1, "titre1"), (2, "titre2"), (3, "titre3")):
        _style(doc, f"Heading {n}", WD_STYLE_TYPE.PARAGRAPH, s[cle])
        _style(doc, f"Heading {n} Char", WD_STYLE_TYPE.CHARACTER, s[cle])
    _style(doc, "Lien", WD_STYLE_TYPE.CHARACTER, s["lien"], galerie=True)
    _style(doc, "Caption", WD_STYLE_TYPE.PARAGRAPH, s["legende"])
    _style(doc, "Chiffre clé", WD_STYLE_TYPE.PARAGRAPH, s["chiffre_cle"], galerie=True)
    _style_tableau(doc, charte)

    section = doc.sections[0]
    section.page_width, section.page_height = Cm(21), Cm(29.7)
    section.left_margin = section.right_margin = section.top_margin = section.bottom_margin = Cm(2.5)

    _couverture(doc, charte, logo)
    _sommaire_et_exemple(doc)
    _entete_pied(doc, charte)

    _metadonnees(doc, charte)
    _retirer_styles_with_effects(doc)

    sortie = Path(sortie)
    sortie.parent.mkdir(parents=True, exist_ok=True)
    doc.save(sortie)
    _remplacer_type(sortie, TYPE_DOCUMENT, TYPE_MODELE)
    return sortie


def _reecrire_type(source, destination, ancien: str, nouveau: str) -> None:
    with zipfile.ZipFile(source) as src, zipfile.ZipFile(destination, "w", zipfile.ZIP_DEFLATED) as dst:
        for info in src.infolist():
            data = src.read(info)
            if info.filename == "[Content_Types].xml":
                data = data.replace(ancien.encode(), nouveau.encode())
            dst.writestr(info, data)


def _remplacer_type(chemin: Path, ancien: str, nouveau: str) -> None:
    tampon = BytesIO()
    _reecrire_type(chemin, tampon, ancien, nouveau)
    chemin.write_bytes(tampon.getvalue())


def ouvrir_modele_pour_test(chemin: Path):
    """Recharge un .dotx en mémoire : python-docx refuse le type « modèle »."""
    tampon = BytesIO()
    _reecrire_type(chemin, tampon, TYPE_MODELE, TYPE_DOCUMENT)
    tampon.seek(0)
    return Document(tampon)
