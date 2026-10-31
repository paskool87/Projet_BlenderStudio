
"""User interface for the MovieStudio Blender add-on."""

import bpy

from .utils import IMPORT_GROUP_PROPERTY


class MOVIESTUDIO_PT_panel(bpy.types.Panel):
    """MovieStudio tools in the 3D View sidebar."""

    bl_label = "MovieStudio"
    bl_idname = "MOVIESTUDIO_PT_panel"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "MovieStudio"

    def draw(self, context):
        layout = self.layout
        active_object = context.active_object

        # ----------------------------------------------------
        # IMPORT
        # ----------------------------------------------------

        layout.label(text="Importation")

        layout.operator(
            "moviestudio.import_fbx",
            text="Importer un FBX",
            icon="IMPORT",
        )

        # ----------------------------------------------------
        # CHARACTER ANALYSIS
        # ----------------------------------------------------

        layout.separator()
        layout.label(text="Personnage")

        layout.operator(
            "moviestudio.analyze_character",
            text="Analyser le personnage",
            icon="ARMATURE_DATA",
        )

        # ----------------------------------------------------
        # IMPORT GROUP SELECTION
        # ----------------------------------------------------

        layout.separator()
        layout.label(text="Groupe d'importation")

        if (
            active_object is not None
            and active_object.get(IMPORT_GROUP_PROPERTY) is not None
        ):
            layout.label(
                text=f"Objet actif : {active_object.name}",
                icon="OBJECT_DATA",
            )

            layout.operator(
                "moviestudio.select_import_group",
                text="Sélectionner les objets communs",
                icon="RESTRICT_SELECT_OFF",
            )
        else:
            layout.label(
                text="Sélectionne un objet importé par MovieStudio.",
                icon="INFO",
            )

        # ----------------------------------------------------
        # TRANSFORMATION PREPARATION
        # ----------------------------------------------------

        layout.separator()
        layout.label(text="Préparation des objets")

        layout.operator(
            "moviestudio.validate_transforms",
            text="Valider les transformations",
            icon="CHECKMARK",
        )

        layout.operator(
            "moviestudio.mark_unprepared",
            text="Annuler la validation",
            icon="LOOP_BACK",
        )

        # ----------------------------------------------------
        # ANIMATION
        # ----------------------------------------------------

        layout.separator()
        layout.label(text="Animation")

        layout.operator(
            "moviestudio.insert_transform_keyframes",
            text="Insérer des images clés",
            icon="KEY_HLT",
        )

        # ----------------------------------------------------
        # TIMELINE VISIBILITY
        # ----------------------------------------------------

        layout.separator()
        layout.label(text="Visibilité sur la timeline")

        if (
            active_object is not None
            and active_object.get(IMPORT_GROUP_PROPERTY) is not None
        ):
            visibility_box = layout.box()

            visibility_box.label(
                text="Groupe d'importation",
                icon="OBJECT_DATA",
            )

            visibility_box.prop(
                active_object,
                "moviestudio_visibility_start",
                text="Apparition",
            )

            visibility_box.prop(
                active_object,
                "moviestudio_visibility_end",
                text="Disparition",
            )

            visibility_box.label(
                text="0 = aucune disparition."
            )

            visibility_box.label(
                text="Les réglages s'appliquent au groupe entier."
            )
        else:
            layout.label(
                text="Sélectionne un objet importé par MovieStudio.",
                icon="INFO",
            )

        # ----------------------------------------------------
        # ENVIRONMENT
        # ----------------------------------------------------

        layout.separator()
        layout.label(text="Environnement")

        layout.operator(
            "moviestudio.create_floor",
            text="Créer le sol quadrillé",
            icon="MESH_GRID",
        )
