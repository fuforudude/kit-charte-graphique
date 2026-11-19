"""Génération du modèle de présentation PowerPoint (.potx) à partir de la charte.

python-pptx ne sait pas créer de dispositions : on part de la présentation par défaut,
on garde six de ses dispositions et on réécrit leur XML (nom, formes, styles).
"""
import io
import re
import zipfile
from pathlib import Path
from xml.sax.saxutils import escape

from lxml import etree
from pptx import Presentation
from pptx.opc.constants import CONTENT_TYPE as CT
from pptx.opc.constants import RELATIONSHIP_TYPE as RT
from pptx.oxml import parse_xml
from pptx.oxml.ns import nsdecls
from pptx.util import Emu

from kit_charte.charte import Charte

# Mise en page 16:9 (en EMU). Ces grandeurs ne sont pas dans la charte : ce sont des choix de gabarit.
LARGEUR, HAUTEUR = 12192000, 6858000
MARGE = 609600
Y_PIED, H_PIED = 6309360, 365760
H_LOGO, L_LOGO_MAX = 685800, 3657600

# Tailles en points ; la charte demande « 36 pt et plus » pour les chiffres clés.
TAILLE_TITRE, TAILLE_TITRE_COUVERTURE, TAILLE_INTERCALAIRE = 32, 40, 36
TAILLES_CORPS = (20, 18, 16, 14, 14)
TAILLE_CHIFFRE, TAILLE_LIBELLE, TAILLE_PIED = 54, 16, 10

MARQUE_EXEMPLE = "[Exemple à supprimer]"

_NS = nsdecls("a", "p", "r")
_A = "http://schemas.openxmlformats.org/drawingml/2006/main"
_P = "http://schemas.openxmlformats.org/presentationml/2006/main"


def _el(xml: str):
    """Analyse un fragment XML en ajoutant les espaces de noms à sa balise racine."""
    return parse_xml(re.sub(r"^<([\w:]+)", rf"<\1 {_NS}", xml, count=1))


def _rpr(balise: str, police: str, taille: float | None, couleur: str, gras: bool | None = None) -> str:
    attrs = ""
    if taille is not None:
        attrs += f' sz="{int(taille * 100)}"'
    if gras is not None:
        attrs += f' b="{int(gras)}"'
    return (f'<a:{balise}{attrs}><a:solidFill><a:srgbClr val="{couleur[1:]}"/></a:solidFill>'
            f'<a:latin typeface="{escape(police)}"/></a:{balise}>')


def _xfrm(x, y, cx, cy) -> str:
    return f'<a:xfrm><a:off x="{x}" y="{y}"/><a:ext cx="{cx}" cy="{cy}"/></a:xfrm>'


def _rect(x, y, cx, cy) -> str:
    return _xfrm(x, y, cx, cy) + '<a:prstGeom prst="rect"><a:avLst/></a:prstGeom>'


def _ph(nom, ph, pos=None, lst="", texte="", ancre=None) -> str:
    """Espace réservé ; sans position, il hérite de celle du masque."""
    sppr = _rect(*pos) if pos else ""
    bodypr = f' anchor="{ancre}"' if ancre else ""
    return (f'<p:sp><p:nvSpPr><p:cNvPr id="0" name="{nom}"/><p:cNvSpPr><a:spLocks noGrp="1"/></p:cNvSpPr>'
            f'<p:nvPr><p:ph {ph}/></p:nvPr></p:nvSpPr><p:spPr>{sppr}</p:spPr>'
            f'<p:txBody><a:bodyPr{bodypr}><a:normAutofit/></a:bodyPr><a:lstStyle>{lst}</a:lstStyle>'
            f'<a:p><a:r><a:rPr lang="fr-FR"/><a:t>{escape(texte)}</a:t></a:r></a:p></p:txBody></p:sp>')


def _niveau(algn="l", rpr="", puce=False) -> str:
    puces = "" if puce else '<a:buNone/>'
    return f'<a:lvl1pPr marL="0" indent="0" algn="{algn}">{puces}{rpr}</a:lvl1pPr>'


def _bande(couleur: str) -> str:
    y = HAUTEUR // 2 - 914400
    return (f'<p:sp><p:nvSpPr><p:cNvPr id="0" name="Bande"/><p:cNvSpPr/><p:nvPr userDrawn="1"/></p:nvSpPr>'
            f'<p:spPr>{_rect(0, y, LARGEUR, 1828800)}<a:solidFill><a:srgbClr val="{couleur[1:]}"/></a:solidFill>'
            f'<a:ln><a:noFill/></a:ln></p:spPr></p:sp>')


def _zone_texte(nom, pos, algn, contenu) -> str:
    return (f'<p:sp><p:nvSpPr><p:cNvPr id="0" name="{nom}"/><p:cNvSpPr txBox="1"/><p:nvPr userDrawn="1"/>'
            f'</p:nvSpPr><p:spPr>{_rect(*pos)}<a:noFill/></p:spPr><p:txBody>'
            f'<a:bodyPr wrap="square" lIns="0" rIns="0" anchor="ctr"/><a:lstStyle/>'
            f'<a:p><a:pPr algn="{algn}"/>{contenu}</a:p></p:txBody></p:sp>')


def _pied(charte: Charte) -> list[str]:
    """Nom de la société et numéro de diapositive (champ évalué sur chaque diapositive)."""
    rpr = _rpr("rPr", charte.presentation.texte_police, TAILLE_PIED, charte.couleurs["texte_secondaire"])
    rpr = rpr.replace("<a:rPr", '<a:rPr lang="fr-FR"', 1)
    societe = f'<a:r>{rpr}<a:t>{escape(charte.document.societe)}</a:t></a:r>'
    numero = f'<a:fld id="{{B6F15528-21DE-4FAA-801E-634DDDAF4B2B}}" type="slidenum">{rpr}<a:t>‹#›</a:t></a:fld>'
    larg_num = 1828800
    return [
        _zone_texte("Société", (MARGE, Y_PIED, 6096000, H_PIED), "l", societe),
        _zone_texte("Numéro de diapositive", (LARGEUR - MARGE - larg_num, Y_PIED, larg_num, H_PIED), "r", numero),
    ]


def _logo(disposition, chemin: Path, centre: bool) -> str:
    image, rid = disposition.part.get_or_add_image_part(str(chemin))
    cx, cy = image.scale(None, H_LOGO)
    if cx > L_LOGO_MAX:
        cx, cy = image.scale(L_LOGO_MAX, None)
    x = (LARGEUR - cx) // 2 if centre else MARGE
    return (f'<p:pic><p:nvPicPr><p:cNvPr id="0" name="Logo"/><p:cNvPicPr><a:picLocks noChangeAspect="1"/>'
            f'</p:cNvPicPr><p:nvPr userDrawn="1"/></p:nvPicPr><p:blipFill><a:blip r:embed="{rid}"/>'
            f'<a:stretch><a:fillRect/></a:stretch></p:blipFill><p:spPr>{_rect(x, MARGE, cx, cy)}</p:spPr></p:pic>')


def _remplacer_formes(element, formes: list[str]) -> None:
    """Remplace les formes d'un arbre (p:spTree) en numérotant les identifiants."""
    arbre = element.find(f"{{{_P}}}cSld/{{{_P}}}spTree")
    for enfant in list(arbre)[2:]:  # garde nvGrpSpPr et grpSpPr
        arbre.remove(enfant)
    for i, xml in enumerate(formes, start=2):
        arbre.append(_el(xml.replace('id="0"', f'id="{i}"', 1)))


def _theme(prs, charte: Charte) -> None:
    c, p = charte.couleurs, charte.presentation
    part = prs.slide_master.part.part_related_by(RT.THEME)
    theme = etree.fromstring(part.blob)
    schema = theme.find(f".//{{{_A}}}clrScheme")
    schema.set("name", "Charte")
    valeurs = {"dk1": c["texte"], "lt1": c["blanc"], "dk2": c["bleu_nuit"], "lt2": c["filet"],
               "accent1": c["bleu"], "accent2": c["orange"], "accent3": c["jaune"], "accent4": c["vert"],
               "accent5": c["bleu_survol"], "accent6": c["texte_secondaire"],
               "hlink": c["bleu"], "folHlink": c["bleu_nuit"]}
    for nom, hexa in valeurs.items():
        noeud = schema.find(f"{{{_A}}}{nom}")
        noeud.clear()
        etree.SubElement(noeud, f"{{{_A}}}srgbClr", val=hexa[1:])
    for balise, police in (("majorFont", p.titres_police), ("minorFont", p.texte_police)):
        theme.find(f".//{{{_A}}}{balise}/{{{_A}}}latin").set("typeface", police)
    part._blob = etree.tostring(theme, xml_declaration=True, encoding="UTF-8", standalone=True)


def _masque(prs, charte: Charte) -> None:
    p, c = charte.presentation, charte.couleurs
    masque = prs.slide_master._element
    fond = masque.find(f"{{{_P}}}cSld/{{{_P}}}bg")
    fond.getparent().replace(fond, _el(f'<p:bg><p:bgPr><a:solidFill><a:srgbClr val="{c["blanc"][1:]}"/></a:solidFill>'
                            f'<a:effectLst/></p:bgPr></p:bg>'))
    _remplacer_formes(masque, [
        _ph("Titre", 'type="title"', (MARGE, 365760, LARGEUR - 2 * MARGE, 914400), ancre="ctr",
            texte="Modifier le style du titre"),
        _ph("Texte", 'type="body" idx="1"', (MARGE, 1463040, LARGEUR - 2 * MARGE, 4572000),
            texte="Modifier les styles du texte"),
    ])
    titre = _rpr("defRPr", p.titres_police, TAILLE_TITRE, p.titres_couleur, p.titres_gras)
    niveaux = []
    for n in range(1, 10):
        taille = TAILLES_CORPS[min(n, len(TAILLES_CORPS)) - 1]
        retrait = 285750 + 457200 * (n - 1)
        niveaux.append(
            f'<a:lvl{n}pPr marL="{retrait}" indent="-285750" algn="l"><a:spcBef><a:spcPts val="600"/></a:spcBef>'
            f'<a:buFont typeface="Arial"/><a:buChar char="•"/>'
            f'{_rpr("defRPr", p.texte_police, taille, p.texte_couleur, False)}</a:lvl{n}pPr>')
    autre = _rpr("defRPr", p.texte_police, None, p.texte_couleur)
    styles = _el(
        f'<p:txStyles><p:titleStyle><a:lvl1pPr algn="l"><a:spcBef><a:spcPct val="0"/></a:spcBef><a:buNone/>'
        f'{titre}</a:lvl1pPr></p:titleStyle><p:bodyStyle>{"".join(niveaux)}</p:bodyStyle>'
        f'<p:otherStyle><a:lvl1pPr>{autre}</a:lvl1pPr></p:otherStyle></p:txStyles>')
    masque.replace(masque.find(f"{{{_P}}}txStyles"), styles)


def _dispositions(prs, charte: Charte, logo: Path) -> None:
    p, c = charte.presentation, charte.couleurs
    larg = LARGEUR - 2 * MARGE
    corps = (MARGE, 1463040, larg, 4572000)
    titre = _ph("Titre", 'type="title"', texte="Titre de la diapositive")
    gap = 457200
    col = (larg - 2 * gap) // 3
    chiffre = _niveau("ctr", _rpr("defRPr", p.chiffres_police, TAILLE_CHIFFRE, p.chiffres_couleur, p.chiffres_gras))
    libelle = _niveau("ctr", _rpr("defRPr", p.texte_police, TAILLE_LIBELLE, p.texte_couleur, False))
    chiffres = []
    for i in range(3):
        x = MARGE + i * (col + gap)
        chiffres.append(_ph(f"Chiffre {i + 1}", f'type="body" sz="quarter" idx="{10 + i}"',
                            (x, 2286000, col, 1280160), chiffre, "00 %", "b"))
        chiffres.append(_ph(f"Libellé {i + 1}", f'type="body" sz="quarter" idx="{13 + i}"',
                            (x, 3611880, col, 914400), libelle, "Libellé du chiffre", "t"))
    intercalaire = _niveau("l", _rpr("defRPr", p.titres_police, TAILLE_INTERCALAIRE, c["blanc"], True))
    y_bande = HAUTEUR // 2 - 914400

    # (indice dans la présentation par défaut, nom, type de disposition, formes)
    gardees = [
        (0, "Titre", "title", lambda d: [
            _logo(d, logo, centre=False),
            _ph("Titre", 'type="ctrTitle"', (MARGE, 2286000, larg, 1371600),
                _niveau("l", f'<a:defRPr sz="{TAILLE_TITRE_COUVERTURE * 100}"/>'), "Titre de la présentation", "b"),
            _ph("Sous-titre", 'type="subTitle" idx="1"', (MARGE, 3749040, larg, 1097280),
                _niveau("l"), "Sous-titre, date"),
        ]),
        (2, "Intercalaire", "secHead", lambda d: [
            _bande(c["bleu"]),
            _ph("Titre", 'type="title"', (MARGE, y_bande, larg, 1828800), intercalaire, "Titre de la partie", "ctr"),
            _ph("Texte", 'type="body" idx="1"', (MARGE, y_bande + 1965960, larg, 914400),
                _niveau("l"), "Description de la partie"),
        ]),
        (1, "Contenu", "obj", lambda d: [titre, _ph("Contenu", 'idx="1"', corps, texte="Texte")] + _pied(charte)),
        (5, "Chiffres clés", "cust", lambda d: [titre] + chiffres + _pied(charte)),
        (3, "Tableau", "tbl", lambda d: [titre, _ph("Tableau", 'type="tbl" idx="10"', corps)] + _pied(charte)),
        (6, "Fin", "cust", lambda d: [
            _logo(d, logo, centre=True),
            _ph("Titre", 'type="title"', (MARGE, 2743200, larg, 1371600), _niveau("ctr"), "Merci", "ctr"),
            _ph("Texte", 'type="body" idx="1"', (MARGE, 4206240, larg, 1097280), _niveau("ctr"), "Contact"),
        ]),
    ]
    defaut = list(prs.slide_layouts)
    ids = prs.slide_master._element.sldLayoutIdLst
    ordre = []
    for indice, nom, type_, formes in gardees:
        d = defaut[indice]
        d._element.set("type", type_)
        d._element.cSld.set("name", nom)
        _remplacer_formes(d._element, formes(d))
        ordre.append(ids[indice])
    for indice, d in enumerate(defaut):
        if indice not in {g[0] for g in gardees}:
            prs.slide_layouts.remove(d)
    for sid in ordre:  # remet les dispositions dans l'ordre d'usage
        ids.append(sid)


def _exemples(prs) -> None:
    """Une diapositive d'exemple par disposition, qui dit quoi y mettre."""
    m = MARQUE_EXEMPLE
    textes = {
        "Titre": {0: f"{m} Titre de la présentation", 1: "Sous-titre, comité, date"},
        "Intercalaire": {0: f"{m} Titre de la partie", 1: "Une phrase qui annonce la partie"},
        "Contenu": {0: f"{m} Titre de la diapositive", 1: "Une idée par puce\nPhrases courtes"},
        "Chiffres clés": {0: f"{m} Trois chiffres à retenir", 10: "42 %", 11: "1 200", 12: "3",
                          13: "Ce que mesure le chiffre", 14: "Ce que mesure le chiffre", 15: "Ce que mesure le chiffre"},
        "Tableau": {0: f"{m} Titre du tableau"},
        "Fin": {0: "Merci", 1: f"{m} Nom, rôle et adresse de contact"},
    }
    for disposition in prs.slide_layouts:
        diapo = prs.slides.add_slide(disposition)
        for idx, texte in textes[disposition.name].items():
            diapo.placeholders[idx].text_frame.text = texte
        if disposition.name == "Tableau":
            tableau = diapo.placeholders[10].insert_table(3, 3).table
            for j, entete in enumerate(("Indicateur", "Valeur", "Commentaire")):
                tableau.cell(0, j).text = entete


def _en_modele(chemin: Path, de: str, vers: str) -> bytes:
    """Contenu du paquet avec le type de contenu de /ppt/presentation.xml remplacé."""
    sortie = io.BytesIO()
    with zipfile.ZipFile(chemin) as zin, zipfile.ZipFile(sortie, "w", zipfile.ZIP_DEFLATED) as zout:
        for info in zin.infolist():
            donnees = zin.read(info.filename)
            if info.filename == "[Content_Types].xml":
                donnees = donnees.replace(de.encode(), vers.encode())
            zout.writestr(info, donnees)
    return sortie.getvalue()


def generer_presentation(charte: Charte, sortie: Path, racine: Path) -> Path:
    """Écrit le modèle .potx et renvoie son chemin."""
    logo = Path(racine) / charte.document.logo
    if not logo.is_file():
        raise FileNotFoundError(f"Logo introuvable : {logo} (chemin attendu d'après document.logo de charte.toml)")
    prs = Presentation()
    prs.slide_width, prs.slide_height = Emu(LARGEUR), Emu(HAUTEUR)
    _theme(prs, charte)
    _masque(prs, charte)
    _dispositions(prs, charte, logo)
    _exemples(prs)
    sortie = Path(sortie)
    sortie.parent.mkdir(parents=True, exist_ok=True)
    prs.save(sortie)
    sortie.write_bytes(_en_modele(sortie, CT.PML_PRESENTATION_MAIN, CT.PML_TEMPLATE_MAIN))
    return sortie


def ouvrir_modele(chemin: Path):
    """Ouvre un .potx avec python-pptx, qui refuse le type de contenu « template »."""
    return Presentation(io.BytesIO(_en_modele(Path(chemin), CT.PML_TEMPLATE_MAIN, CT.PML_PRESENTATION_MAIN)))
