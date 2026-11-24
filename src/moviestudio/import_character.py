"""MakeHuman character import operator for MovieStudio."""

import uuid

import bpy
from mathutils import Matrix, Vector

from .utils import (
    IMPORTED_PROPERTY,
    IMPORT_GROUP_PROPERTY,
    PREPARED_PROPERTY,
)
from . import visibility


class MOVIESTUDIO_OT_import_character(bpy.types.Operator):
    """Import a prepared MakeHuman character from a Blender file."""

    bl_idname = "moviestudio.import_character"
    bl_label = "Importer un personnage"
    bl_options = {"REGISTER", "UNDO"}

    filepath: bpy.props.StringProperty(
        name="Fichier du personnage",
        description="Fichier Blender préparé depuis MakeHuman / MPFB2",
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
        imported_objects = []
        root = None

        try:
            with bpy.data.libraries.load(self.filepath, link=False) as (
                data_from,
                data_to,
            ):
                data_to.objects = list(data_from.objects)

            imported_objects = [
                obj for obj in data_to.objects if obj is not None
            ]

            if not imported_objects:
                self.report({"WARNING"}, "Aucun objet trouvé dans ce fichier.")
                return {"CANCELLED"}

            # Cameras and lights are not part of a character. Keep EMPTY
            # objects because a rig may use them as controls or helpers.
            ignored_objects = [
                obj for obj in imported_objects
                if obj.type in {"CAMERA", "LIGHT"}
            ]
            character_objects = [
                obj for obj in imported_objects
                if obj.type not in {"CAMERA", "LIGHT"}
            ]

            has_armature = any(obj.type == "ARMATURE" for obj in character_objects)
            has_mesh = any(obj.type == "MESH" for obj in character_objects)

            if not has_armature or not has_mesh:
                for obj in imported_objects:
                    bpy.data.objects.remove(obj, do_unlink=True)
                self.report(
                    {"WARNING"},
                    "Ce fichier ne contient pas à la fois une armature et un mesh.",
                )
                return {"CANCELLED"}

            character_set = set(character_objects)

            for obj in character_objects:
                if obj.name not in scene.objects:
                    scene.collection.objects.link(obj)

            context.view_layer.update()

            # Use mesh geometry only to find the character's ground centre.
            depsgraph = context.evaluated_depsgraph_get()
            bounding_points = []

            for obj in character_objects:
                if obj.type != "MESH":
                    continue

                evaluated_obj = obj.evaluated_get(depsgraph)
                world_matrix = evaluated_obj.matrix_world

                for corner in evaluated_obj.bound_box:
                    bounding_points.append(world_matrix @ Vector(corner))

            if not bounding_points:
                raise RuntimeError("Impossible de calculer les dimensions du personnage.")

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
            translation = Matrix.Translation(-base_center)

            # Keep the imported character's internal hierarchy untouched.
            # Only its top-level objects become children of the MovieStudio root.
            top_level_objects = [
                obj for obj in character_objects
                if obj.parent not in character_set
            ]
            original_matrices = {
                obj: obj.matrix_world.copy()
                for obj in top_level_objects
            }

            root = bpy.data.objects.new("MovieStudio_Character", None)
            scene.collection.objects.link(root)
            root.empty_display_type = "PLAIN_AXES"
            root.empty_display_size = 0.7
            root.location = (0, 0, 0)
            root.rotation_euler = (0, 0, 0)
            root.scale = (1, 1, 1)

            for obj in top_level_objects:
                obj.parent = root
                obj.parent_type = "OBJECT"
                obj.parent_bone = ""
                obj.matrix_parent_inverse = Matrix.Identity(4)
                obj.matrix_world = translation @ original_matrices[obj]

            for obj in ignored_objects:
                bpy.data.objects.remove(obj, do_unlink=True)

            context.view_layer.update()

            # Register the root and every character component as one group.
            group_objects = [root] + character_objects
            for obj in group_objects:
                obj[IMPORTED_PROPERTY] = True
                obj[PREPARED_PROPERTY] = False
                obj[IMPORT_GROUP_PROPERTY] = import_group_id
                visibility.save_original_visibility(obj)
                obj.moviestudio_visibility_start = current_frame
                obj.moviestudio_visibility_end = 0

        except Exception as exc:
            if root is not None and root.name in bpy.data.objects:
                bpy.data.objects.remove(root, do_unlink=True)
            for obj in imported_objects:
                if obj is not None and obj.name in bpy.data.objects:
                    bpy.data.objects.remove(obj, do_unlink=True)
            self.report({"ERROR"}, f"Échec de l'importation du personnage : {exc}")
            return {"CANCELLED"}

        for obj in context.selected_objects:
            obj.select_set(False)

        root.select_set(True)
        context.view_layer.objects.active = root
        visibility.update_scene_visibility(scene)

        armature_count = sum(obj.type == "ARMATURE" for obj in character_objects)
        mesh_count = sum(obj.type == "MESH" for obj in character_objects)
        self.report(
            {"INFO"},
            f"Personnage importé : {armature_count} armature(s), "
            f"{mesh_count} mesh(es).",
        )
        return {"FINISHED"}

    def invoke(self, context, event):
        context.window_manager.fileselect_add(self)
        return {"RUNNING_MODAL"}
