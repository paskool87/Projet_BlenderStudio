"""User interface for the MovieStudio Blender add-on."""

import bpy


class MOVIESTUDIO_PT_panel(bpy.types.Panel):
    """MovieStudio tools in the 3D View sidebar."""

    bl_label = "MovieStudio"
    bl_idname = "MOVIESTUDIO_PT_panel"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "MovieStudio"

    def draw(self, context):
        layout = self.layout

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
        # TIMELINE
        # ----------------------------------------------------

        layout.separator()
        layout.label(text="Animation")

        layout.operator(
            "moviestudio.insert_transform_keyframes",
            text="Insérer des images clés",
            icon="KEY_HLT",
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