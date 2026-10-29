
"""Timeline-based object visibility for MovieStudio."""

import bpy
from bpy.app.handlers import persistent

from .utils import IMPORT_GROUP_PROPERTY, IMPORTED_PROPERTY


ORIGINAL_VIEWPORT_PROPERTY = "moviestudio_visibility_original_viewport"
ORIGINAL_RENDER_PROPERTY = "moviestudio_visibility_original_render"
STATE_SAVED_PROPERTY = "moviestudio_visibility_state_saved"

_SYNCING_VISIBILITY = False


def save_original_visibility(obj):
    """Save original visibility before timeline management starts."""

    if obj.get(STATE_SAVED_PROPERTY, False):
        return

    obj[ORIGINAL_VIEWPORT_PROPERTY] = obj.hide_viewport
    obj[ORIGINAL_RENDER_PROPERTY] = obj.hide_render
    obj[STATE_SAVED_PROPERTY] = True


def get_visibility_group(obj, scene=None):
    """Return all objects belonging to the same import group."""

    if obj is None:
        return []

    if scene is None:
        context = bpy.context
        scene = getattr(context, "scene", None)

    if scene is None:
        return [obj]

    group_id = obj.get(IMPORT_GROUP_PROPERTY)

    if group_id is None:
        return [obj]

    return [
        candidate
        for candidate in scene.objects
        if candidate.get(IMPORT_GROUP_PROPERTY) == group_id
    ]


def is_visible_at_frame(obj, frame):
    """Return whether an object should be visible at a frame."""

    start_frame = obj.moviestudio_visibility_start
    end_frame = obj.moviestudio_visibility_end

    return frame >= start_frame and (
        end_frame == 0 or frame < end_frame
    )


def update_scene_visibility(scene):
    """Update visibility for MovieStudio-imported objects."""

    if scene is None:
        return

    for obj in scene.objects:
        if not obj.get(IMPORTED_PROPERTY, False):
            continue

        save_original_visibility(obj)
        visible = is_visible_at_frame(obj, scene.frame_current)

        obj.hide_viewport = (
            obj.get(ORIGINAL_VIEWPORT_PROPERTY, False) or not visible
        )
        obj.hide_render = (
            obj.get(ORIGINAL_RENDER_PROPERTY, False) or not visible
        )


@persistent
def moviestudio_visibility_frame_handler(scene, depsgraph=None):
    """Update visibility whenever the current frame changes."""

    update_scene_visibility(scene)


def update_visibility_properties(self, context):
    """Synchronize visibility limits across the import group."""

    global _SYNCING_VISIBILITY

    if _SYNCING_VISIBILITY:
        return

    # Blender may provide a restricted context without a scene.
    scene = getattr(context, "scene", None)

    if scene is None:
        return

    group_objects = get_visibility_group(self, scene)

    if not group_objects:
        return

    _SYNCING_VISIBILITY = True

    try:
        start_frame = self.moviestudio_visibility_start
        end_frame = self.moviestudio_visibility_end

        for obj in group_objects:
            if obj == self:
                continue

            obj.moviestudio_visibility_start = start_frame
            obj.moviestudio_visibility_end = end_frame
    finally:
        _SYNCING_VISIBILITY = False

    update_scene_visibility(scene)


def register_properties():
    """Register MovieStudio timeline visibility properties."""

    if not hasattr(bpy.types.Object, "moviestudio_visibility_start"):
        bpy.types.Object.moviestudio_visibility_start = (
            bpy.props.IntProperty(
                name="Apparition",
                description="Première image où l'objet est visible",
                default=1,
                min=1,
                update=update_visibility_properties,
            )
        )

    if not hasattr(bpy.types.Object, "moviestudio_visibility_end"):
        bpy.types.Object.moviestudio_visibility_end = (
            bpy.props.IntProperty(
                name="Disparition",
                description="Première image invisible, 0 pour aucune",
                default=0,
                min=0,
                update=update_visibility_properties,
            )
        )


def unregister_properties():
    """Remove MovieStudio timeline visibility properties."""

    for property_name in (
        "moviestudio_visibility_end",
        "moviestudio_visibility_start",
        "moviestudio_visibility_enabled",
    ):
        if hasattr(bpy.types.Object, property_name):
            delattr(bpy.types.Object, property_name)


def register_handler():
    """Register the timeline handler once."""

    if (
        moviestudio_visibility_frame_handler
        not in bpy.app.handlers.frame_change_post
    ):
        bpy.app.handlers.frame_change_post.append(
            moviestudio_visibility_frame_handler
        )


def unregister_handler():
    """Remove the timeline handler."""

    for handler in list(bpy.app.handlers.frame_change_post):
        if handler.__name__ == "moviestudio_visibility_frame_handler":
            bpy.app.handlers.frame_change_post.remove(handler)
