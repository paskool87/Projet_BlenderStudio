
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
            "moviestudio.import_blend",
            text="Importer un objet",
            icon="IMPORT",
        )

        layout.operator(
            "moviestudio.import_character",
            text="Importer un personnage",
            icon="ARMATURE_DATA",
        )

        # ----------------------------------------------------
        # IMPORT GROUP SELECTION
        # ----------------------------------------------------

        layout.separator()
        layout.label(text="Objet MovieStudio")

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
                text="Sélectionner tous les composants",
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
            text="Valider orientation et échelle",
            icon="CHECKMARK",
        )

        layout.operator(
            "moviestudio.mark_unprepared",
            text="Annuler la validation",
            icon="LOOP_BACK",
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
                text="Objet MovieStudio",
                icon="OBJECT_DATA",
            )

            visibility_box.operator(
                "moviestudio.set_visibility_start",
                text=(
                    f"Apparition : "
                    f"image {active_object.moviestudio_visibility_start}"
                ),
                icon="PLAY",
            )

            visibility_box.operator(
                "moviestudio.set_visibility_end",
                text=(
                    f"Disparition : "
                    f"image {active_object.moviestudio_visibility_end}"
                ),
                icon="TIME",
            )

            visibility_box.label(
                text="0 = aucune disparition."
            )

            visibility_box.label(
                text="Les réglages s'appliquent à l'objet entier."
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


class MOVIESTUDIO_PT_animation_panel(bpy.types.Panel):
    """Animation tools in a dedicated collapsible panel."""

    bl_label = "Animation"
    bl_idname = "MOVIESTUDIO_PT_animation_panel"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "MovieStudio"
    bl_parent_id = "MOVIESTUDIO_PT_panel"
    bl_options = {"DEFAULT_CLOSED"}

    def draw(self, context):
        layout = self.layout

        layout.label(text="Images clés", icon="KEY_HLT")
        layout.operator(
            "moviestudio.insert_transform_keyframes",
            text="Insérer les clés de transformation",
            icon="KEYFRAME",
        )

        layout.separator()
        layout.label(
            text="Trajectoires et animations avancées à venir.",
            icon="INFO",
        )
