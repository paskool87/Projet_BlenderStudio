
"""Blend file import operator for MovieStudio."""

import uuid

import bpy
from mathutils import Vector

from .utils import (
    IMPORTED_PROPERTY,
    IMPORT_GROUP_PROPERTY,
    PREPARED_PROPERTY,
)
from . import visibility


class MOVIESTUDIO_OT_import_blend(bpy.types.Operator):
    """Import a Blender file as one MovieStudio object."""

    bl_idname = "moviestudio.import_blend"
    bl_label = "Importer un objet"
    bl_options = {"REGISTER", "UNDO"}

    filepath: bpy.props.StringProperty(
        name="Fichier Blender",
        description="Fichier Blender à importer",
        subtype="FILE_PATH",
    )

    filter_glob: bpy.props.StringProperty(
        default="*.blend",
        options={"HIDDEN"},
    )

    def execute(self, context):
        scene = context.scene
        current_frame = scene.frame_current
        import_group_id = uuid.uuid4().hex

        try:
            # Import all objects from the Blender file.
            with bpy.data.libraries.load(
                self.filepath,
                link=False,
            ) as (data_from, data_to):
                data_to.objects = list(data_from.objects)

            all_imported_objects = [
                obj
                for obj in data_to.objects
                if obj is not None
            ]

            if not all_imported_objects:
                self.report(
                    {"WARNING"},
                    "Aucun objet trouvé dans ce fichier.",
                )
                return {"CANCELLED"}

            # Exclude cameras, lights, empties and armatures.
            ignored_types = {
                "EMPTY",
                "CAMERA",
                "LIGHT",
                "ARMATURE",
            }

            imported_objects = [
                obj
                for obj in all_imported_objects
                if obj.type not in ignored_types
            ]

            ignored_objects = [
                obj
                for obj in all_imported_objects
                if obj.type in ignored_types
            ]

            if not imported_objects:
                self.report(
                    {"WARNING"},
                    "Aucun objet exploitable dans ce fichier.",
                )
                return {"CANCELLED"}

            # Link only the retained objects to the current scene.
            for obj in imported_objects:
                if obj.name not in scene.objects:
                    scene.collection.objects.link(obj)

            bpy.context.view_layer.update()

            # Calculate the world-space bounds using evaluated geometry.
            depsgraph = context.evaluated_depsgraph_get()
            bounding_points = []

            for obj in imported_objects:
                evaluated_obj = obj.evaluated_get(depsgraph)
                world_matrix = evaluated_obj.matrix_world

                for corner in evaluated_obj.bound_box:
                    bounding_points.append(
                        world_matrix @ Vector(corner)
                    )

            if bounding_points:
                min_x = min(point.x for point in bounding_points)
                max_x = max(point.x for point in bounding_points)
                min_y = min(point.y for point in bounding_points)
                max_y = max(point.y for point in bounding_points)
                min_z = min(point.z for point in bounding_points)

                base_center = Vector((
                    (min_x + max_x) / 2,
                    (min_y + max_y) / 2,
                    min_z,
                ))
            else:
                base_center = Vector((0, 0, 0))

            # Create the MovieStudio root at the world origin.
            root = bpy.data.objects.new(
                "MovieStudio_Object",
                None,
            )

            scene.collection.objects.link(root)

            root.empty_display_type = "PLAIN_AXES"
            root.empty_display_size = 0.5

            # Preserve the original world transformations.
            imported_set = set(imported_objects)

            for obj in imported_objects:
                if obj.parent not in imported_set:
                    world_matrix = obj.matrix_world.copy()

                    obj.parent = root
                    obj.matrix_world = world_matrix

            # Remove excluded objects from the Blender scene data.
            for obj in ignored_objects:
                bpy.data.objects.remove(
                    obj,
                    do_unlink=True,
                )

            # Move the entire imported object as one block.
            root.location = -base_center

            # Identify the complete MovieStudio object.
            root[IMPORTED_PROPERTY] = True
            root[PREPARED_PROPERTY] = False
            root[IMPORT_GROUP_PROPERTY] = import_group_id

            visibility.save_original_visibility(root)
            root.moviestudio_visibility_start = current_frame
            root.moviestudio_visibility_end = 0

            for obj in imported_objects:
                obj[IMPORTED_PROPERTY] = True
                obj[PREPARED_PROPERTY] = False
                obj[IMPORT_GROUP_PROPERTY] = import_group_id

                visibility.save_original_visibility(obj)
                obj.moviestudio_visibility_start = current_frame
                obj.moviestudio_visibility_end = 0

        except Exception as exc:
            self.report(
                {"ERROR"},
                f"Échec de l'importation : {exc}",
            )
            return {"CANCELLED"}

        # Select only the MovieStudio root.
        for obj in context.selected_objects:
            obj.select_set(False)

        root.select_set(True)
        context.view_layer.objects.active = root

        visibility.update_scene_visibility(scene)

        self.report(
            {"INFO"},
            (
                f"Objet importé avec {len(imported_objects)} composant(s), "
                f"{len(ignored_objects)} élément(s) ignoré(s), "
                f"et posé au sol à partir de l'image {current_frame}."
            ),
        )

        return {"FINISHED"}

    def invoke(self, context, event):
        context.window_manager.fileselect_add(self)
        return {"RUNNING_MODAL"}
