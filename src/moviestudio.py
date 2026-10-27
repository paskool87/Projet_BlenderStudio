
bl_info = {
    "name": "MovieStudio",
    "author": "MovieStudio",
    "version": (0, 5, 0),
    "blender": (5, 1, 0),
    "location": "View3D > Sidebar > MovieStudio",
    "description": "Import FBX and manually validate object transformations",
    "category": "3D View",
}

import bpy


# ============================================================
# CONSTANTS
# ============================================================

PREPARED_PROPERTY = "moviestudio_transformations_validated"
IMPORTED_PROPERTY = "moviestudio_imported_by_addon"


# ============================================================
# OBJECT HELPERS
# ============================================================

def deselect_all_objects():
    """Deselect every currently selected object."""
    bpy.ops.object.select_all(action="DESELECT")


def select_objects(context, objects):
    """Select the given objects and make the first one active."""
    deselect_all_objects()

    valid_objects = [
        obj for obj in objects
        if obj is not None and obj.name in bpy.data.objects
    ]

    for obj in valid_objects:
        obj.select_set(True)

    if valid_objects:
        context.view_layer.objects.active = valid_objects[0]


def get_selected_objects(context):
    """Return the current selection."""
    return list(context.selected_objects)


def get_imported_objects(context, previous_objects):
    """Find objects created by the latest FBX import."""
    return [
        obj
        for obj in bpy.data.objects
        if obj not in previous_objects
    ]


def is_prepared(obj):
    """Check whether an object has been marked as prepared."""
    return bool(obj.get(PREPARED_PROPERTY, False))


def mark_as_prepared(objects):
    """Mark objects as having had their transformations validated."""
    for obj in objects:
        obj[PREPARED_PROPERTY] = True


def mark_as_unprepared(objects):
    """Clear the validation status after further manual changes."""
    for obj in objects:
        obj[PREPARED_PROPERTY] = False


# ============================================================
# FBX IMPORT
# ============================================================

class MOVIESTUDIO_OT_import_fbx(bpy.types.Operator):
    """Import an FBX and select all newly imported objects."""

    bl_idname = "moviestudio.import_fbx"
    bl_label = "Importer un FBX"
    bl_description = "Import an FBX and select its newly created objects"
    bl_options = {"REGISTER", "UNDO"}

    filepath: bpy.props.StringProperty(
        name="Fichier FBX",
        description="Fichier FBX à importer",
        subtype="FILE_PATH",
    )

    filter_glob: bpy.props.StringProperty(
        default="*.fbx",
        options={"HIDDEN"},
    )

    def invoke(self, context, event):
        context.window_manager.fileselect_add(self)
        return {"RUNNING_MODAL"}

    def execute(self, context):
        if context.mode != "OBJECT":
            try:
                bpy.ops.object.mode_set(mode="OBJECT")
            except RuntimeError:
                self.report(
                    {"ERROR"},
                    "Impossible de passer en mode Objet.",
                )
                return {"CANCELLED"}

        previous_objects = set(bpy.data.objects)

        try:
            bpy.ops.import_scene.fbx(
                filepath=self.filepath,
            )
        except Exception as error:
            self.report(
                {"ERROR"},
                f"Échec de l'import FBX : {error}",
            )
            return {"CANCELLED"}

        imported_objects = get_imported_objects(
            context,
            previous_objects,
        )

        if not imported_objects:
            self.report(
                {"WARNING"},
                "L'import n'a créé aucun nouvel objet.",
            )
            return {"CANCELLED"}

        # Record that these objects were imported through MovieStudio.
        for obj in imported_objects:
            obj[IMPORTED_PROPERTY] = True
            obj[PREPARED_PROPERTY] = False

        # Select the entire newly imported set.
        select_objects(context, imported_objects)

        self.report(
            {"INFO"},
            (
                f"{len(imported_objects)} objet(s) importé(s) "
                "et sélectionné(s). Réglez-les puis validez."
            ),
        )

        return {"FINISHED"}


# ============================================================
# VALIDATE TRANSFORMATIONS
# ============================================================

class MOVIESTUDIO_OT_validate_transforms(bpy.types.Operator):
    """
    Apply location, rotation and scale to the current selection.

    The operator deliberately uses Blender's standard Apply
    Transforms operation rather than implementing custom transforms.
    """

    bl_idname = "moviestudio.validate_transforms"
    bl_label = "Valider les transformations"
    bl_description = (
        "Apply location, rotation and scale to the selected objects"
    )
    bl_options = {"REGISTER", "UNDO"}

    @classmethod
    def poll(cls, context):
        return (
            context.mode == "OBJECT"
            and context.view_layer.objects.active is not None
            and len(context.selected_objects) > 0
        )

    def execute(self, context):
        selected_objects = get_selected_objects(context)

        if not selected_objects:
            self.report(
                {"WARNING"},
                "Sélectionnez les objets à préparer.",
            )
            return {"CANCELLED"}

        # Blender's Apply Transforms operation works on the current
        # selection. It is intentionally not applied to the whole scene.
        try:
            bpy.ops.object.transform_apply(
                location=True,
                rotation=True,
                scale=True,
            )
        except RuntimeError as error:
            self.report(
                {"ERROR"},
                f"Impossible de valider les transformations : {error}",
            )
            return {"CANCELLED"}

        mark_as_prepared(selected_objects)

        self.report(
            {"INFO"},
            (
                f"Transformations validées pour "
                f"{len(selected_objects)} objet(s)."
            ),
        )

        return {"FINISHED"}


# ============================================================
# RESET VALIDATION STATUS
# ============================================================

class MOVIESTUDIO_OT_mark_unprepared(bpy.types.Operator):
    """Mark selected objects as requiring validation again."""

    bl_idname = "moviestudio.mark_unprepared"
    bl_label = "Reprendre les réglages"
    bl_description = (
        "Mark the selected objects as needing transformation validation"
    )
    bl_options = {"REGISTER", "UNDO"}

    @classmethod
    def poll(cls, context):
        return (
            context.mode == "OBJECT"
            and len(context.selected_objects) > 0
        )

    def execute(self, context):
        selected_objects = get_selected_objects(context)

        mark_as_unprepared(selected_objects)

        self.report(
            {"INFO"},
            (
                f"{len(selected_objects)} objet(s) "
                "marqué(s) comme non validé(s)."
            ),
        )

        return {"FINISHED"}


# ============================================================
# CREATE FLOOR AND GRID
# ============================================================

class MOVIESTUDIO_OT_create_floor(bpy.types.Operator):
    """Create a reference floor and grid at ground level."""

    bl_idname = "moviestudio.create_floor"
    bl_label = "Créer le sol et la grille"
    bl_description = "Create a reference floor at Z = 0"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        floor_name = "MovieStudio_Floor"
        grid_name = "MovieStudio_Grid"

        # Create the floor if it does not already exist.
        if bpy.data.objects.get(floor_name) is None:
            bpy.ops.mesh.primitive_plane_add(
                size=200.0,
                location=(0.0, 0.0, 0.0),
            )

            floor = context.object
            floor.name = floor_name
            floor.hide_select = True

        # Create the reference grid if it does not already exist.
        if bpy.data.objects.get(grid_name) is None:
            vertices = []
            edges = []

            extent = 50
            spacing = 1.0
            z = 0.002

            for index in range(-extent, extent + 1):
                coordinate = index * spacing
                start_index = len(vertices)

                vertices.extend([
                    (-extent * spacing, coordinate, z),
                    (extent * spacing, coordinate, z),
                    (coordinate, -extent * spacing, z),
                    (coordinate, extent * spacing, z),
                ])

                edges.extend([
                    (start_index, start_index + 1),
                    (start_index + 2, start_index + 3),
                ])

            mesh = bpy.data.meshes.new(
                "MovieStudio_GridMesh",
            )

            mesh.from_pydata(
                vertices,
                edges,
                [],
            )

            mesh.update()

            grid = bpy.data.objects.new(
                grid_name,
                mesh,
            )

            context.collection.objects.link(grid)
            grid.display_type = "WIRE"
            grid.hide_select = True
            grid.hide_render = True

        self.report(
            {"INFO"},
            "Sol et grille créés ou déjà présents.",
        )

        return {"FINISHED"}


# ============================================================
# USER INTERFACE
# ============================================================

class MOVIESTUDIO_PT_panel(bpy.types.Panel):
    """Main MovieStudio panel in the 3D View sidebar."""

    bl_label = "MovieStudio"
    bl_idname = "MOVIESTUDIO_PT_panel"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "MovieStudio"

    def draw(self, context):
        layout = self.layout

        selected_objects = get_selected_objects(context)

        layout.label(
            text="Import",
            icon="IMPORT",
        )

        layout.operator(
            "moviestudio.import_fbx",
            text="Importer un FBX",
            icon="FILE_3D",
        )

        layout.separator()

        layout.label(
            text="Préparation de la sélection",
            icon="OBJECT_DATA",
        )

        if not selected_objects:
            layout.label(
                text="Aucun objet sélectionné",
                icon="INFO",
            )
        else:
            layout.label(
                text=f"{len(selected_objects)} objet(s) sélectionné(s)",
            )

            prepared_count = sum(
                1 for obj in selected_objects
                if is_prepared(obj)
            )

            layout.label(
                text=(
                    f"{prepared_count}/{len(selected_objects)} "
                    "objet(s) marqué(s) validé(s)"
                ),
            )

            layout.separator()

            layout.label(
                text="Réglages manuels dans Blender",
                icon="TOOL_SETTINGS",
            )

            layout.label(text="Déplacement : G")
            layout.label(text="Rotation : R")
            layout.label(text="Échelle : S")

            layout.separator()

            layout.label(
                text="Repères souhaités :",
            )

            layout.label(text="Avant : Y+")
            layout.label(text="Haut : Z+")
            layout.label(text="Sol conseillé : Z = 0")

            layout.separator()

            layout.operator(
                "moviestudio.validate_transforms",
                text="Valider les transformations",
                icon="CHECKMARK",
            )

            layout.operator(
                "moviestudio.mark_unprepared",
                text="Reprendre les réglages",
                icon="LOOP_BACK",
            )

        layout.separator()

        layout.label(
            text="Scène",
            icon="GRID",
        )

        layout.operator(
            "moviestudio.create_floor",
            text="Créer le sol et la grille",
            icon="MESH_PLANE",
        )


# ============================================================
# REGISTER / UNREGISTER
# ============================================================

CLASSES = (
    MOVIESTUDIO_OT_import_fbx,
    MOVIESTUDIO_OT_validate_transforms,
    MOVIESTUDIO_OT_mark_unprepared,
    MOVIESTUDIO_OT_create_floor,
    MOVIESTUDIO_PT_panel,
)


def register():
    for cls in CLASSES:
        bpy.utils.register_class(cls)


def unregister():
    for cls in reversed(CLASSES):
        bpy.utils.unregister_class(cls)


if __name__ == "__main__":
    register()
