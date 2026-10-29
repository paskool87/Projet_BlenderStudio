
"""Utility functions and properties used by MovieStudio."""

import bpy


# ============================================================
# CUSTOM PROPERTY NAMES
# ============================================================

PREPARED_PROPERTY = "moviestudio_transformations_validated"
IMPORTED_PROPERTY = "moviestudio_imported_by_addon"
IMPORT_GROUP_PROPERTY = "moviestudio_import_group"


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

    valid_objects = [
        obj for obj in objects
        if obj is not None
    ]

    for obj in valid_objects:
        obj.select_set(True)

    if active_object is not None:
        bpy.context.view_layer.objects.active = active_object
    elif valid_objects:
        bpy.context.view_layer.objects.active = valid_objects[0]


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


def get_import_group(obj):
    """Return the import group identifier for an object."""

    if obj is None:
        return None

    return obj.get(IMPORT_GROUP_PROPERTY)


def get_import_group_objects(obj, scene=None):
    """Return all objects belonging to the same FBX import."""

    if obj is None:
        return []

    if scene is None:
        scene = bpy.context.scene

    group_id = get_import_group(obj)

    if group_id is None:
        return [obj]

    return [
        candidate
        for candidate in scene.objects
        if candidate.get(IMPORT_GROUP_PROPERTY) == group_id
    ]


def select_import_group(obj, context=None):
    """Select every object from the same FBX import as the given object."""

    if context is None:
        context = bpy.context

    if obj is None:
        return []

    group_objects = get_import_group_objects(
        obj,
        context.scene,
    )

    select_objects(
        group_objects,
        active_object=obj,
    )

    return group_objects


# ============================================================
# TRANSFORMATION VALIDATION
# ============================================================

def is_prepared(obj):
    """Return whether an object's transformations are validated."""

    return bool(obj.get(PREPARED_PROPERTY, False))


def mark_as_prepared(obj):
    """Mark an object's transformations as validated."""

    obj[PREPARED_PROPERTY] = True


def mark_as_unprepared(obj):
    """Mark an object's transformations as not validated."""

    obj[PREPARED_PROPERTY] = False
