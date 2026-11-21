
"""MovieStudio Blender add-on."""

bl_info = {
    "name": "MovieStudio",
    "author": "MovieStudio",
    "version": (0, 9, 3),
    "blender": (5, 1, 0),
    "location": "View3D > Sidebar > MovieStudio",
    "description": (
        "Import objects and animate their transformations "
        "on Blender timeline"
    ),
    "category": "3D View",
}

import bpy

from .import_blend import MOVIESTUDIO_OT_import_blend
from .preparation import (
    MOVIESTUDIO_OT_validate_transforms,
    MOVIESTUDIO_OT_mark_unprepared,
)
from .timeline import MOVIESTUDIO_OT_insert_transform_keyframes
from .environment import MOVIESTUDIO_OT_create_floor
from .selection import (
    MOVIESTUDIO_OT_select_import_group,
    register_selection_handler,
    unregister_selection_handler,
)
from . import visibility
from .visibility import (
    MOVIESTUDIO_OT_set_visibility_start,
    MOVIESTUDIO_OT_set_visibility_end,
)
from .interface import MOVIESTUDIO_PT_panel


CLASSES = (
    MOVIESTUDIO_OT_import_blend,
    MOVIESTUDIO_OT_validate_transforms,
    MOVIESTUDIO_OT_mark_unprepared,
    MOVIESTUDIO_OT_insert_transform_keyframes,
    MOVIESTUDIO_OT_create_floor,
    MOVIESTUDIO_OT_select_import_group,
    MOVIESTUDIO_OT_set_visibility_start,
    MOVIESTUDIO_OT_set_visibility_end,
    MOVIESTUDIO_PT_panel,
)


def register():
    """Register MovieStudio classes and handlers."""

    visibility.register_properties()
    registered_classes = []

    try:
        for cls in CLASSES:
            bpy.utils.register_class(cls)
            registered_classes.append(cls)

        visibility.register_handler()
        register_selection_handler()

    except Exception:
        unregister_selection_handler()
        visibility.unregister_handler()

        for cls in reversed(registered_classes):
            bpy.utils.unregister_class(cls)

        visibility.unregister_properties()
        raise


def unregister():
    """Unregister MovieStudio classes and handlers."""

    unregister_selection_handler()
    visibility.unregister_handler()

    for cls in reversed(CLASSES):
        bpy.utils.unregister_class(cls)

    visibility.unregister_properties()


if __name__ == "__main__":
    register()
