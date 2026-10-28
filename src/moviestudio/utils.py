"""Utility functions and properties used by MovieStudio."""

import bpy


# ============================================================
# CUSTOM PROPERTY NAMES
# ============================================================

PREPARED_PROPERTY = "moviestudio_transformations_validated"
IMPORTED_PROPERTY = "moviestudio_imported_by_addon"


# ============================================================
# OBJECT SELECTION
# ============================================================

def deselect_all_objects():
    """Deselect all currently selected objects."""
    for obj in bpy.context.selected_objects:
        obj.select_set(False)


def select_objects(objects, active_object=None):
    """Select the given objects and optionally set the active object."""
    deselect_all_objects()

    for obj in objects:
        if obj is not None:
            obj.select_set(True)

    if active_object is not None:
        bpy.context.view_layer.objects.active = active_object
    elif objects:
        bpy.context.view_layer.objects.active = objects[0]


def get_selected_objects():
    """Return the currently selected objects."""
    return list(bpy.context.selected_objects)


# ============================================================
# MOVIESTUDIO OBJECTS
# ============================================================

def get_imported_objects():
    """Return objects marked as imported by MovieStudio."""
    return [
        obj
        for obj in bpy.context.scene.objects
        if obj.get(IMPORTED_PROPERTY, False)
    ]


def is_prepared(obj):
    """Return whether an object's transformations are validated."""
    return bool(obj.get(PREPARED_PROPERTY, False))


def mark_as_prepared(obj):
    """Mark an object's transformations as validated."""
    obj[PREPARED_PROPERTY] = True


def mark_as_unprepared(obj):
    """Mark an object's transformations as not validated."""
    obj[PREPARED_PROPERTY] = False