
bl_info = {
    "name": "MovieStudio",
    "author": "MovieStudio",
    "version": (0, 2, 0),
    "blender": (5, 1, 0),
    "location": "Vue 3D > Barre latérale > MovieStudio",
    "description": "Sol, importation FBX et rotation du personnage",
    "category": "3D View",
}

import bpy
import math
from mathutils import Matrix, Vector


COLLECTION_NAME = "MovieStudio_Scene"
FLOOR_NAME = "MovieStudio_Floor"
MODEL_COLLECTION_NAME = "MovieStudio_Model"


# --------------------------------------------------
# COLLECTIONS
# --------------------------------------------------

def get_or_create_collection(name):
    collection = bpy.data.collections.get(name)

    if collection is None:
        collection = bpy.data.collections.new(name)
        bpy.context.scene.collection.children.link(collection)

    return collection


def move_object_to_collection(obj, collection):
    for current_collection in list(obj.users_collection):
        current_collection.objects.unlink(obj)

    if obj.name not in collection.objects:
        collection.objects.link(obj)


# --------------------------------------------------
# SOL
# --------------------------------------------------

def create_floor():
    collection = get_or_create_collection(COLLECTION_NAME)
    floor = bpy.data.objects.get(FLOOR_NAME)

    if floor is not None:
        return floor

    size = 200.0

    vertices = [
        (-size, -size, 0.0),
        (size, -size, 0.0),
        (size, size, 0.0),
        (-size, size, 0.0),
    ]

    mesh = bpy.data.meshes.new("MovieStudio_FloorMesh")
    mesh.from_pydata(vertices, [], [(0, 1, 2, 3)])
    mesh.update()

    floor = bpy.data.objects.new(FLOOR_NAME, mesh)
    collection.objects.link(floor)

    material = bpy.data.materials.new("MovieStudio_FloorMaterial")
    material.diffuse_color = (0.22, 0.22, 0.22, 1.0)
    floor.data.materials.append(material)

    floor.display_type = 'WIRE'
    floor.hide_select = True
    floor.location = (0.0, 0.0, 0.0)

    return floor


# --------------------------------------------------
# IMPORTATION FBX
# --------------------------------------------------

def import_fbx(filepath):
    if not filepath.lower().endswith(".fbx"):
        raise ValueError("Le fichier doit être au format FBX.")

    collection = get_or_create_collection(MODEL_COLLECTION_NAME)
    objects_before = set(bpy.data.objects)

    bpy.ops.import_scene.fbx(
        filepath=filepath,
        global_scale=1.0,
        use_manual_orientation=False,
        bake_space_transform=False,
        use_anim=True,
    )

    imported_objects = [
        obj for obj in bpy.data.objects
        if obj not in objects_before
    ]

    if not imported_objects:
        raise RuntimeError("Aucun objet n'a été importé.")

    for obj in imported_objects:
        move_object_to_collection(obj, collection)

    # Enregistrer les transformations initiales.
    for obj in imported_objects:
        obj["moviestudio_imported"] = True
        obj["moviestudio_initial_matrix"] = [
            value
            for row in obj.matrix_world
            for value in row
        ]

    # Déterminer le centre du personnage dans le monde.
    corners = []

    for obj in imported_objects:
        if obj.type == 'MESH':
            for corner in obj.bound_box:
                corners.append(obj.matrix_world @ Vector(corner))

    if corners:
        min_x = min(point.x for point in corners)
        max_x = max(point.x for point in corners)
        min_y = min(point.y for point in corners)
        max_y = max(point.y for point in corners)
        min_z = min(point.z for point in corners)

        center = Vector((
            (min_x + max_x) / 2.0,
            (min_y + max_y) / 2.0,
            min_z,
        ))
    else:
        center = Vector((0.0, 0.0, 0.0))

    # Enregistrer les données de rotation sur la scène.
    scene = bpy.context.scene
    scene.moviestudio_pivot = tuple(center)
    scene.moviestudio_rotation = '0'

    scene["moviestudio_object_names"] = [
        obj.name for obj in imported_objects
    ]

    bpy.ops.object.select_all(action='DESELECT')

    for obj in imported_objects:
        obj.select_set(True)

    bpy.context.view_layer.objects.active = imported_objects[0]

    return len(imported_objects)


# --------------------------------------------------
# ROTATION DIRECTE DES OBJETS IMPORTÉS
# --------------------------------------------------

def apply_rotation(context, angle_degrees):
    scene = context.scene
    object_names = scene.get("moviestudio_object_names", [])

    if not object_names:
        return False

    pivot = Vector(scene.moviestudio_pivot)
    angle = math.radians(angle_degrees)

    rotation_matrix = Matrix.Rotation(angle, 4, 'Z')
    to_origin = Matrix.Translation(-pivot)
    to_pivot = Matrix.Translation(pivot)

    transform = to_pivot @ rotation_matrix @ to_origin

    for name in object_names:
        obj = bpy.data.objects.get(name)

        if obj is None:
            continue

        values = obj.get("moviestudio_initial_matrix")

        if not values or len(values) != 16:
            continue

        initial_matrix = Matrix((
            values[0:4],
            values[4:8],
            values[8:12],
            values[12:16],
        ))

        # Rotation de la transformation mondiale initiale.
        obj.matrix_world = transform @ initial_matrix

    context.view_layer.update()
    return True


def update_rotation(self, context):
    angles = {
        '0': 0,
        '90': 90,
        '-90': -90,
        '180': 180,
    }

    angle = angles.get(context.scene.moviestudio_rotation, 0)
    apply_rotation(context, angle)


# --------------------------------------------------
# OPÉRATEURS
# --------------------------------------------------

class MOVIESTUDIO_OT_create_floor(bpy.types.Operator):
    bl_idname = "moviestudio.create_floor"
    bl_label = "Créer le sol"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        create_floor()
        return {'FINISHED'}


class MOVIESTUDIO_OT_import_fbx(bpy.types.Operator):
    bl_idname = "moviestudio.import_fbx"
    bl_label = "Importer un FBX"
    bl_options = {'REGISTER', 'UNDO'}

    filepath: bpy.props.StringProperty(
        name="Fichier FBX",
        subtype='FILE_PATH',
    )

    filter_glob: bpy.props.StringProperty(
        default="*.fbx",
        options={'HIDDEN'},
    )

    def execute(self, context):
        try:
            count = import_fbx(self.filepath)
        except Exception as error:
            self.report({'ERROR'}, f"Importation impossible : {error}")
            return {'CANCELLED'}

        self.report({'INFO'}, f"{count} objets importés.")
        return {'FINISHED'}

    def invoke(self, context, event):
        context.window_manager.fileselect_add(self)
        return {'RUNNING_MODAL'}


class MOVIESTUDIO_OT_reset_rotation(bpy.types.Operator):
    bl_idname = "moviestudio.reset_rotation"
    bl_label = "Réinitialiser"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        scene = context.scene

        if not scene.get("moviestudio_object_names", []):
            self.report({'WARNING'}, "Aucun personnage importé.")
            return {'CANCELLED'}

        scene.moviestudio_rotation = '0'
        apply_rotation(context, 0)

        self.report({'INFO'}, "Rotation réinitialisée.")
        return {'FINISHED'}


# --------------------------------------------------
# PANNEAU
# --------------------------------------------------

class MOVIESTUDIO_PT_panel(bpy.types.Panel):
    bl_label = "MovieStudio"
    bl_idname = "MOVIESTUDIO_PT_panel"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "MovieStudio"

    def draw(self, context):
        layout = self.layout

        layout.label(text="Environnement")
        layout.operator(
            "moviestudio.create_floor",
            icon='GRID',
        )

        layout.separator()

        layout.label(text="Personnage")
        layout.operator(
            "moviestudio.import_fbx",
            icon='IMPORT',
        )

        layout.separator()
        layout.label(text="Rotation autour de Z")

        layout.prop(
            context.scene,
            "moviestudio_rotation",
            text="Angle",
            expand=True,
        )

        layout.operator(
            "moviestudio.reset_rotation",
            icon='LOOP_BACK',
        )


# --------------------------------------------------
# ENREGISTREMENT
# --------------------------------------------------

CLASSES = (
    MOVIESTUDIO_OT_create_floor,
    MOVIESTUDIO_OT_import_fbx,
    MOVIESTUDIO_OT_reset_rotation,
    MOVIESTUDIO_PT_panel,
)


def register():
    for cls in CLASSES:
        bpy.utils.register_class(cls)

    bpy.types.Scene.moviestudio_rotation = bpy.props.EnumProperty(
        name="Rotation",
        items=[
            ('0', "0°", "Orientation initiale"),
            ('90', "+90°", "Rotation de 90 degrés"),
            ('-90', "-90°", "Rotation de -90 degrés"),
            ('180', "180°", "Rotation de 180 degrés"),
        ],
        default='0',
        update=update_rotation,
    )

    bpy.types.Scene.moviestudio_pivot = bpy.props.FloatVectorProperty(
        name="Pivot",
        size=3,
        subtype='TRANSLATION',
        options={'HIDDEN'},
    )


def unregister():
    if hasattr(bpy.types.Scene, "moviestudio_rotation"):
        del bpy.types.Scene.moviestudio_rotation

    if hasattr(bpy.types.Scene, "moviestudio_pivot"):
        del bpy.types.Scene.moviestudio_pivot

    for cls in reversed(CLASSES):
        bpy.utils.unregister_class(cls)


if __name__ == "__main__":
    register()
