"""Transformation preparation operators for MovieStudio."""

import bpy

from .utils import (
    get_selected_objects,
    mark_as_prepared,
    mark_as_unprepared,
)


class MOVIESTUDIO_OT_validate_transforms(bpy.types.Operator):
    """Apply rotation and scale to selected objects."""

    bl_idname = "moviestudio.validate_transforms"
    bl_label = "Valider les transformations"
    bl_options = {"REGISTER", "UNDO"}

    @classmethod
    def poll(cls, context):
        return bool(context.selected_objects)

    def execute(self, context):
        selected_objects = get_selected_objects()

        bpy.ops.object.transform_apply(
            location=False,
            rotation=True,
            scale=True,
        )

        for obj in selected_objects:
            mark_as_prepared(obj)

        self.report(
            {"INFO"},
            f"Transformations validées pour {len(selected_objects)} objet(s).",
        )

        return {"FINISHED"}


class MOVIESTUDIO_OT_mark_unprepared(bpy.types.Operator):
    """Mark selected objects as not prepared."""

    bl_idname = "moviestudio.mark_unprepared"
    bl_label = "Annuler la validation"
    bl_options = {"REGISTER", "UNDO"}

    @classmethod
    def poll(cls, context):
        return bool(context.selected_objects)

    def execute(self, context):
        selected_objects = get_selected_objects()

        for obj in selected_objects:
            mark_as_unprepared(obj)

        self.report(
            {"INFO"},
            f"Validation annulée pour {len(selected_objects)} objet(s).",
        )

        return {"FINISHED"}