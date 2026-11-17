
"""Timeline operators for MovieStudio."""

import bpy


class MOVIESTUDIO_OT_insert_transform_keyframes(bpy.types.Operator):
    """Insert transformation keyframes for selected objects."""

    bl_idname = "moviestudio.insert_transform_keyframes"
    bl_label = "Insérer des images clés"
    bl_options = {"REGISTER", "UNDO"}

    @classmethod
    def poll(cls, context):
        return bool(context.selected_objects)

    def execute(self, context):
        selected_objects = list(context.selected_objects)
        current_frame = context.scene.frame_current

        for obj in selected_objects:
            obj.keyframe_insert(
                data_path="location",
                frame=current_frame,
                group="Transformations",
            )

            if obj.rotation_mode == "QUATERNION":
                obj.keyframe_insert(
                    data_path="rotation_quaternion",
                    frame=current_frame,
                    group="Transformations",
                )
            elif obj.rotation_mode == "AXIS_ANGLE":
                obj.keyframe_insert(
                    data_path="rotation_axis_angle",
                    frame=current_frame,
                    group="Transformations",
                )
            else:
                obj.keyframe_insert(
                    data_path="rotation_euler",
                    frame=current_frame,
                    group="Transformations",
                )

            obj.keyframe_insert(
                data_path="scale",
                frame=current_frame,
                group="Transformations",
            )

        self.report(
            {"INFO"},
            (
                f"Images clés insérées pour {len(selected_objects)} objet(s) "
                f"à l'image {current_frame}."
            ),
        )

        return {"FINISHED"}
