
"""Selection operators for MovieStudio import groups."""

import bpy

from .utils import (
    IMPORT_GROUP_PROPERTY,
    select_import_group,
)


class MOVIESTUDIO_OT_select_import_group(bpy.types.Operator):
    """Select all objects from the same FBX import."""

    bl_idname = "moviestudio.select_import_group"
    bl_label = "Sélectionner les objets communs"
    bl_description = (
        "Sélectionner tous les objets provenant du même import FBX"
    )
    bl_options = {"REGISTER", "UNDO"}

    @classmethod
    def poll(cls, context):
        obj = context.active_object

        return (
            obj is not None
            and obj.get(IMPORT_GROUP_PROPERTY) is not None
        )

    def execute(self, context):
        active_object = context.active_object

        group_objects = select_import_group(
            active_object,
            context,
        )

        if not group_objects:
            self.report(
                {"WARNING"},
                "Aucun objet commun trouvé.",
            )
            return {"CANCELLED"}

        self.report(
            {"INFO"},
            f"{len(group_objects)} objet(s) sélectionné(s).",
        )

        return {"FINISHED"}
