import pytest

from kit_charte.charte import CharteError, lire_charte

ATTENDUS = {
    "titre_document": ("Roboto Condensed", 28, "#0066CC", True, True),
    "titre1": ("Roboto", 18, "#0066CC", True, True),
    "titre2": ("Roboto", 14, "#0A3561", True, False),
    "titre3": ("Roboto Medium", 12, "#212529", False, False),
    "corps": ("Roboto", 11, "#212529", False, False),
    "lien": ("Roboto", 11, "#0066CC", False, False),
    "legende": ("Roboto", 9, "#606060", False, False),
    "chiffre_cle": ("Roboto Condensed", 36, "#0066CC", True, False),
}


@pytest.mark.parametrize("nom", ATTENDUS)
def test_styles_du_vrai_charte(nom):
    s = lire_charte().styles[nom]
    assert (s.police, s.taille, s.couleur, s.gras, s.capitales) == ATTENDUS[nom]


def test_details_du_vrai_charte():
    c = lire_charte()
    assert len(c.styles) == 8
    assert c.styles["corps"].interligne == 1.3
    assert c.styles["corps"].alignement == "gauche"
    assert c.styles["lien"].souligne
    assert c.tableau.entete_fond == "#0066CC"
    assert c.tableau.entete_texte == "#FFFFFF"
    assert c.tableau.filets == "#E7E7E7"
    assert c.presentation.titres_couleur == "#0066CC"
    assert c.couleurs["orange"] == "#FF6633"
    assert c.document.societe == "[Nom de la société]"


def _toml(tmp_path, couleurs_extra="", style_couleur="bleu"):
    p = tmp_path / "charte.toml"
    p.write_text(
        f"""
interdites_texte = ["orange"]
[couleurs]
bleu = "#0066CC"
orange = "#FF6633"
blanc = "#FFFFFF"
{couleurs_extra}
[polices]
texte = "Roboto"
titre = "Roboto"
medium = "Roboto"
repli = "Arial"
[styles.corps]
police = "Roboto"
taille = 11
couleur = "{style_couleur}"
[tableau]
entete_fond = "bleu"
entete_texte = "blanc"
entete_police = "Roboto"
entete_gras = true
filets = "bleu"
[presentation]
format = "16:9"
titres_police = "Roboto"
titres_gras = true
titres_couleur = "bleu"
texte_police = "Roboto"
texte_couleur = "bleu"
chiffres_police = "Roboto"
chiffres_gras = true
chiffres_couleur = "bleu"
[document]
societe = "X"
logo = "x.png"
[formes]
rayon_carte = 6
rayon_bouton = 999
""",
        encoding="utf-8",
    )
    return p


def test_fichier_minimal_valide(tmp_path):
    assert lire_charte(_toml(tmp_path)).styles["corps"].couleur == "#0066CC"


def test_couleur_inconnue(tmp_path):
    with pytest.raises(CharteError, match="couleur inconnue « violet »"):
        lire_charte(_toml(tmp_path, style_couleur="violet"))


def test_format_invalide(tmp_path):
    with pytest.raises(CharteError, match="#RRGGBB"):
        lire_charte(_toml(tmp_path, couleurs_extra='rouge = "red"'))


def test_couleur_interdite(tmp_path):
    with pytest.raises(CharteError, match="interdite"):
        lire_charte(_toml(tmp_path, style_couleur="orange"))
