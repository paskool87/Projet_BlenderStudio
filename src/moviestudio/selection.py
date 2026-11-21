
"""Selection operators and automatic selection for MovieStudio."""

import bpy

from .utils import (
    IMPORT_GROUP_PROPERTY,
    get_import_group_root,
    select_import_group,
)


_SELECTION_UPDATE_RUNNING = False


class MOVIESTUDIO_OT_select_import_group(bpy.types.Operator):
    """Select the common root of a MovieStudio import."""

    bl_idname = "moviestudio.select_import_group"
    bl_label = "Sélectionner l'objet MovieStudio"
    bl_description = (
        "Sélectionner la racine de l'objet MovieStudio"
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

        root = get_import_group_root(
            active_object,
            context.scene,
        )

        if root is None:
            self.report(
                {"WARNING"},
                "Racine MovieStudio introuvable.",
            )
            return {"CANCELLED"}

        select_import_group(
            active_object,
            context,
        )

        self.report(
            {"INFO"},
            "Objet MovieStudio sélectionné.",
        )

        return {"FINISHED"}


def automatic_object_selection(scene, depsgraph):
    """Redirect component selection to its MovieStudio root."""

    global _SELECTION_UPDATE_RUNNING

    if _SELECTION_UPDATE_RUNNING:
        return

    context = bpy.context
    active_object = context.view_layer.objects.active

    if active_object is None:
        return

    if active_object.get(IMPORT_GROUP_PROPERTY) is None:
        return

    root = get_import_group_root(
        active_object,
        context.scene,
    )

    if root is None or root == active_object:
        return

    _SELECTION_UPDATE_RUNNING = True

    try:
        select_import_group(
            active_object,
            context,
        )
    finally:
        _SELECTION_UPDATE_RUNNING = False


def register_selection_handler():
    """Register automatic MovieStudio object selection."""

    if automatic_object_selection not in bpy.app.handlers.depsgraph_update_post:
        bpy.app.handlers.depsgraph_update_post.append(
            automatic_object_selection
        )


def unregister_selection_handler():
    """Unregister automatic MovieStudio object selection."""

    if automatic_object_selection in bpy.app.handlers.depsgraph_update_post:
        bpy.app.handlers.depsgraph_update_post.remove(
            automatic_object_selection
        )
