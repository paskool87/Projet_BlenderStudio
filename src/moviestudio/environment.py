"""Environment creation operators for MovieStudio."""

import bpy


class MOVIESTUDIO_OT_create_floor(bpy.types.Operator):
    """Create a solid floor with a visible grid."""

    bl_idname = "moviestudio.create_floor"
    bl_label = "Créer le sol quadrillé"
    bl_options = {"REGISTER", "UNDO"}

    size: bpy.props.FloatProperty(
        name="Taille",
        description="Taille du sol",
        default=20.0,
        min=1.0,
    )

    subdivisions: bpy.props.IntProperty(
        name="Subdivisions",
        description="Nombre de subdivisions du quadrillage",
        default=20,
        min=1,
        max=200,
    )

    def execute(self, context):
        bpy.ops.mesh.primitive_plane_add(
            size=self.size,
            location=(0.0, 0.0, 0.0),
        )

        floor = context.object
        floor.name = "MovieStudio_Floor"

        bpy.ops.object.mode_set(mode="EDIT")
        bpy.ops.mesh.subdivide(
            number_cuts=self.subdivisions - 1,
        )
        bpy.ops.object.mode_set(mode="OBJECT")

        floor.display_type = "SOLID"
        floor.show_wire = True
        floor.show_all_edges = True

        self.report(
            {"INFO"},
            "Sol quadrillé créé.",
        )

        return {"FINISHED"}