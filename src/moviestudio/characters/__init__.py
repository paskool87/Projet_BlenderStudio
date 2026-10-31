
"""Character tools for MovieStudio."""

from .rig_analyzer import MOVIESTUDIO_OT_analyze_character
from .rig_comparator import MOVIESTUDIO_OT_compare_rigs

from .metarig_template import (
    get_reference_metarig,
    create_working_copy,
)


__all__ = (
    "MOVIESTUDIO_OT_analyze_character",
    "MOVIESTUDIO_OT_compare_rigs",
    "get_reference_metarig",
    "create_working_copy",
)
