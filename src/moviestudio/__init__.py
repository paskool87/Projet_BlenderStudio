"""MovieStudio Blender add-on."""

bl_info = {
    "name": "MovieStudio",
    "author": "MovieStudio",
    "version": (0, 6, 0),
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
from .interface import MOVIESTUDIO_PT_panel


# ============================================================
# CLASS REGISTRATION
# ============================================================

CLASSES = (
    MOVIESTUDIO_OT_import_fbx,
    MOVIESTUDIO_OT_validate_transforms,
    MOVIESTUDIO_OT_mark_unprepared,
    MOVIESTUDIO_OT_insert_transform_keyframes,
    MOVIESTUDIO_OT_create_floor,
    MOVIESTUDIO_PT_panel,
)


def register():
    """Register MovieStudio classes with Blender."""
    for cls in CLASSES:
        bpy.utils.register_class(cls)


def unregister():
    """Unregister MovieStudio classes in reverse order."""
    for cls in reversed(CLASSES):
        bpy.utils.unregister_class(cls)


if __name__ == "__main__":
    register()