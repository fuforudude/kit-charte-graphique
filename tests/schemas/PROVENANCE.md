# Provenance des schémas XSD

Schémas XSD de la norme ISO/IEC 29500-4:2016 (Office Open XML, variante transitionnelle) et d'OPC (ECMA-376, 4e édition), plus `mce/mc.xsd` (compatibilité de balisage), copiés tels quels depuis les schémas livrés avec la skill `pptx` de Claude (`pptx/scripts/office/schemas`).

Fichiers retenus : ceux qu'importent, de proche en proche, PresentationML (`pml.xsd`), DrawingML (`dml-main.xsd`), WordprocessingML (`wml.xsd`), les propriétés étendues (`shared-documentPropertiesExtended.xsd`), les types de contenu (`opc-contentTypes.xsd`) et les relations (`opc-relationships.xsd`).

Utilisés uniquement par `tests/test_schemas.py`. Ne pas les modifier.
