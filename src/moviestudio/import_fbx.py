"""FBX import operator for MovieStudio."""

import bpy

from .utils import (
    IMPORTED_PROPERTY,
    PREPARED_PROPERTY,
)


class MOVIESTUDIO_OT_import_fbx(bpy.types.Operator):
    """Import an FBX file and mark its objects as MovieStudio objects."""

    bl_idname = "moviestudio.import_fbx"
    bl_label = "Importer un FBX"
    bl_options = {"REGISTER", "UNDO"}

    filepath: bpy.props.StringProperty(
        name="Fichier FBX",
        description="Fichier FBX à importer",
        subtype="FILE_PATH",
    )

    filter_glob: bpy.props.StringProperty(
        default="*.fbx",
        options={"HIDDEN"},
    )

    def execute(self, context):
        objects_before = set(context.scene.objects)

        try:
            bpy.ops.import_scene.fbx(filepath=self.filepath)
        except Exception as exc:
            self.report(
                {"ERROR"},
                f"Échec de l'importation FBX : {exc}",
            )
            return {"CANCELLED"}

        objects_after = set(context.scene.objects)
        imported_objects = list(objects_after - objects_before)

        if not imported_objects:
            self.report(
                {"WARNING"},
                "Aucun nouvel objet n'a été importé.",
            )
            return {"FINISHED"}

        for obj in imported_objects:
            obj[IMPORTED_PROPERTY] = True
            obj[PREPARED_PROPERTY] = False

        for obj in context.selected_objects:
            obj.select_set(False)

        for obj in imported_objects:
            obj.select_set(True)

        context.view_layer.objects.active = imported_objects[0]

        self.report(
            {"INFO"},
            f"{len(imported_objects)} objet(s) importé(s).",
        )

        return {"FINISHED"}

    def invoke(self, context, event):
        context.window_manager.fileselect_add(self)
        return {"RUNNING_MODAL"}