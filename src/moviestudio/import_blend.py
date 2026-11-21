
"""Blend file import operator for MovieStudio."""

import uuid

import bpy
from mathutils import Matrix, Vector

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

            imported_set = set(imported_objects)

            # Link retained objects to the current scene.
            for obj in imported_objects:
                if obj.name not in scene.objects:
                    scene.collection.objects.link(obj)

            context.view_layer.update()

            # Save original world matrices and parent relationships.
            original_matrices = {
                obj: obj.matrix_world.copy()
                for obj in imported_objects
            }

            original_parents = {
                obj: obj.parent
                for obj in imported_objects
            }

            # Calculate the complete object's world-space bounds.
            depsgraph = context.evaluated_depsgraph_get()
            bounding_points = []

            for obj in imported_objects:
                evaluated_obj = obj.evaluated_get(depsgraph)
                world_matrix = evaluated_obj.matrix_world

                for corner in evaluated_obj.bound_box:
                    bounding_points.append(
                        world_matrix @ Vector(corner)
                    )

            if not bounding_points:
                self.report(
                    {"WARNING"},
                    "Impossible de calculer les dimensions de l'objet.",
                )
                return {"CANCELLED"}

            min_x = min(point.x for point in bounding_points)
            max_x = max(point.x for point in bounding_points)
            min_y = min(point.y for point in bounding_points)
            max_y = max(point.y for point in bounding_points)
            min_z = min(point.z for point in bounding_points)

            # Center of the bottom face of the complete object.
            base_center = Vector((
                (min_x + max_x) / 2,
                (min_y + max_y) / 2,
                min_z,
            ))

            # Translate every component by the same world-space offset.
            translation = Matrix.Translation(-base_center)

            # Create the MovieStudio root at the world origin.
            root = bpy.data.objects.new(
                "MovieStudio_Object",
                None,
            )
            scene.collection.objects.link(root)

            root.empty_display_type = "PLAIN_AXES"
            root.empty_display_size = 0.5
            root.location = (0, 0, 0)
            root.rotation_euler = (0, 0, 0)
            root.scale = (1, 1, 1)

            # Find the nearest retained ancestor for each component.
            new_parents = {}

            for obj in imported_objects:
                parent = original_parents[obj]

                while parent is not None and parent not in imported_set:
                    parent = parent.parent

                new_parents[obj] = parent if parent in imported_set else root

            # Process parents before their children.
            def hierarchy_depth(obj):
                depth = 0
                parent = original_parents[obj]
                visited = set()

                while parent is not None and parent not in visited:
                    visited.add(parent)
                    depth += 1
                    parent = parent.parent

                return depth

            ordered_objects = sorted(
                imported_objects,
                key=hierarchy_depth,
            )

            # Rebuild the hierarchy and preserve world transformations.
            for obj in ordered_objects:
                target_world = (
                    translation @ original_matrices[obj]
                )

                obj.parent = new_parents[obj]
                obj.parent_type = "OBJECT"
                obj.parent_bone = ""
                obj.matrix_parent_inverse = Matrix.Identity(4)

                context.view_layer.update()

                obj.matrix_world = target_world

                context.view_layer.update()

            # Remove excluded objects after rebuilding the hierarchy.
            for obj in ignored_objects:
                bpy.data.objects.remove(
                    obj,
                    do_unlink=True,
                )

            context.view_layer.update()

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
                f"origine placée au centre de la base."
            ),
        )

        return {"FINISHED"}

    def invoke(self, context, event):
        context.window_manager.fileselect_add(self)
        return {"RUNNING_MODAL"}
