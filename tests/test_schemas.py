"""Chaque partie XML des modèles (commités et fraîchement générés) doit être valide contre les schémas XSD ISO 29500."""
import zipfile
from functools import cache
from pathlib import Path

import pytest
from lxml import etree

from kit_charte.__main__ import RACINE, generer_modeles

SCH = Path(__file__).parent / "schemas"
ISO = SCH / "ISO-IEC29500-4_2016"
OPC = SCH / "ecma" / "fouth-edition"
MC = "http://schemas.openxmlformats.org/markup-compatibility/2006"
XSD_PAR_ESPACE = {
    "http://schemas.openxmlformats.org/presentationml/2006/main": ISO / "pml.xsd",
    "http://schemas.openxmlformats.org/drawingml/2006/main": ISO / "dml-main.xsd",
    "http://schemas.openxmlformats.org/wordprocessingml/2006/main": ISO / "wml.xsd",
    "http://schemas.openxmlformats.org/officeDocument/2006/extended-properties": ISO / "shared-documentPropertiesExtended.xsd",
    "http://schemas.openxmlformats.org/package/2006/content-types": OPC / "opc-contentTypes.xsd",
    "http://schemas.openxmlformats.org/package/2006/relationships": OPC / "opc-relationships.xsd",
}
# Parties sans schéma disponible localement : exclues explicitement.
EXCLUES = {
    "docProps/core.xml": "importe Dublin Core depuis le web (schéma non embarqué)",
    "customXml/item1.xml": "contenu XML libre du modèle, sans schéma Office",
    "customXml/itemProps1.xml": "schéma customXmlDataProperties non embarqué",
}


@cache
def _schema(ns: str) -> etree.XMLSchema:
    return etree.XMLSchema(etree.parse(str(XSD_PAR_ESPACE[ns])))


def _sans_extensions_ignorables(racine):
    """Retire mc:Ignorable et les éléments/attributs de ses espaces de noms, comme le fait Office avant lecture (norme MCE)."""
    ignorables = racine.get(f"{{{MC}}}Ignorable")
    if ignorables is None:
        return racine
    espaces = {racine.nsmap[prefixe] for prefixe in ignorables.split()}
    del racine.attrib[f"{{{MC}}}Ignorable"]
    for el in list(racine.iter()):
        if not isinstance(el.tag, str):
            continue
        for cle in [c for c in el.attrib if etree.QName(c).namespace in espaces]:
            del el.attrib[cle]
        if etree.QName(el).namespace in espaces:
            el.getparent().remove(el)
    return racine


def _erreurs(chemin: Path) -> list[str]:
    erreurs = []
    with zipfile.ZipFile(chemin) as z:
        for nom in sorted(z.namelist()):
            if not nom.endswith((".xml", ".rels")) or nom in EXCLUES:
                continue
            racine = _sans_extensions_ignorables(etree.fromstring(z.read(nom)))
            ns =etree.QName(racine).namespace
            if ns not in XSD_PAR_ESPACE:
                erreurs.append(f"{nom} : aucun schéma pour l'espace de noms {ns} (à ajouter ou à exclure avec sa raison)")
                continue
            schema = _schema(ns)
            if not schema.validate(racine):
                erreurs += [f"{nom}:{e.line} : {e.message}" for e in schema.error_log]
    return erreurs


@pytest.fixture(scope="module")
def regeneres(tmp_path_factory):
    return generer_modeles(tmp_path_factory.mktemp("frais"))




@pytest.mark.parametrize("modele", ["dossier.dotx", "presentation.potx"])
def test_modele_commite_valide(modele):
    assert not _erreurs(RACINE / "modeles" / modele)


@pytest.mark.parametrize("indice", [pytest.param(0, id="dossier"), pytest.param(1, id="presentation")])
def test_modele_genere_valide(regeneres, indice):
    assert not _erreurs(regeneres[indice])
