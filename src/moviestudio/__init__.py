
"""MovieStudio Blender add-on."""

bl_info = {
    "name": "MovieStudio",
    "author": "MovieStudio",
    "version": (0, 9, 1),
    "blender": (5, 1, 0),
    "location": "View3D > Sidebar > MovieStudio",
    "description": (
        "Import objects and animate their transformations "
        "on Blender timeline"
    ),
    "category": "3D View",
}

import bpy

from .import_fbx import MOVIESTUDIO_OT_import_fbx
from .preparation import (
    MOVIESTUDIO_OT_validate_transforms,
    MOVIESTUDIO_OT_mark_unprepared,
)
from .timeline import MOVIESTUDIO_OT_insert_transform_keyframes
from .environment import MOVIESTUDIO_OT_create_floor
from .selection import MOVIESTUDIO_OT_select_import_group
from . import visibility
from .interface import MOVIESTUDIO_PT_panel


CLASSES = (
    MOVIESTUDIO_OT_import_fbx,
    MOVIESTUDIO_OT_validate_transforms,
    MOVIESTUDIO_OT_mark_unprepared,
    MOVIESTUDIO_OT_insert_transform_keyframes,
    MOVIESTUDIO_OT_create_floor,
    MOVIESTUDIO_OT_select_import_group,
    MOVIESTUDIO_PT_panel,
)


def register():
    """Register MovieStudio classes and timeline visibility."""

    visibility.register_properties()
    registered_classes = []

    try:
        for cls in CLASSES:
            bpy.utils.register_class(cls)
            registered_classes.append(cls)

        # Do not access bpy.context.scene during registration.
        # Blender may use a restricted context here.
        visibility.register_handler()

    except Exception:
        visibility.unregister_handler()

        for cls in reversed(registered_classes):
            bpy.utils.unregister_class(cls)

        visibility.unregister_properties()
        raise


def unregister():
    """Unregister MovieStudio classes and timeline visibility."""

    visibility.unregister_handler()

    for cls in reversed(CLASSES):
        bpy.utils.unregister_class(cls)

    visibility.unregister_properties()


if __name__ == "__main__":
    register()
