
bl_info = {
    "name": "MovieStudio",
    "author": "MovieStudio",
    "version": (0, 1, 0),
    "blender": (5, 1, 0),
    "location": "View3D > Sidebar > MovieStudio",
    "description": "Base simple pour importer des personnages FBX dans une scène",
    "category": "3D View",
}

import bpy
from mathutils import Vector


# --------------------------------------------------
# CONFIGURATION
# --------------------------------------------------

COLLECTION_NAME = "MovieStudio_Scene"
FLOOR_NAME = "MovieStudio_Floor"
MODEL_COLLECTION_NAME = "MovieStudio_Model"


# --------------------------------------------------
# COLLECTIONS
# --------------------------------------------------

def get_or_create_collection(name, parent=None):
    collection = bpy.data.collections.get(name)

    if collection is None:
        collection = bpy.data.collections.new(name)

    if parent is None:
        parent = bpy.context.scene.collection

    if collection.name not in parent.children:
        parent.children.link(collection)

    return collection


def move_object_to_collection(obj, collection):
    for current_collection in list(obj.users_collection):
        current_collection.objects.unlink(obj)

    if obj.name not in collection.objects:
        collection.objects.link(obj)


# --------------------------------------------------
# SCENE
# --------------------------------------------------

def create_scene():
    scene_collection = get_or_create_collection(COLLECTION_NAME)

    # Créer le sol uniquement s'il n'existe pas déjà.
    floor = bpy.data.objects.get(FLOOR_NAME)

    if floor is None:
        mesh = bpy.data.meshes.new("MovieStudio_FloorMesh")

        size = 200.0
        vertices = [
            (-size, -size, 0.0),
            (size, -size, 0.0),
            (size, size, 0.0),
            (-size, size, 0.0),
        ]
        faces = [(0, 1, 2, 3)]

        mesh.from_pydata(vertices, [], faces)
        mesh.update()

        floor = bpy.data.objects.new(FLOOR_NAME, mesh)
        scene_collection.objects.link(floor)

        material = bpy.data.materials.new("MovieStudio_FloorMaterial")
        material.diffuse_color = (0.22, 0.22, 0.22, 1.0)
        floor.data.materials.append(material)

    floor.location = (0.0, 0.0, 0.0)
    floor.display_type = 'WIRE'
    floor.hide_select = True

    return scene_collection


# --------------------------------------------------
# FBX IMPORT
# --------------------------------------------------

def import_fbx(filepath):
    if not filepath.lower().endswith(".fbx"):
        raise ValueError("Le fichier sélectionné doit être un fichier FBX.")

    # Préparer une collection dédiée au personnage.
    model_collection = get_or_create_collection(
        MODEL_COLLECTION_NAME
    )

    # Mémoriser les objets présents avant l'importation.
    objects_before = set(bpy.data.objects)

    # Importer le FBX avec les réglages de Blender.
    bpy.ops.import_scene.fbx(
        filepath=filepath,
        use_manual_orientation=False,
        global_scale=1.0,
        bake_space_transform=False,
        use_anim=True,
    )

    # Identifier les objets nouvellement importés.
    imported_objects = [
        obj for obj in bpy.data.objects
        if obj not in objects_before
    ]

    if not imported_objects:
        raise RuntimeError("Aucun objet n'a été importé depuis le FBX.")

    # Regrouper les objets importés sans modifier
    # leurs transformations ni leur hiérarchie.
    for obj in imported_objects:
        move_object_to_collection(obj, model_collection)

    # Sélectionner les objets importés.
    bpy.ops.object.select_all(action='DESELECT')

    for obj in imported_objects:
        obj.select_set(True)

    active_object = next(
        (obj for obj in imported_objects if obj.type == 'ARMATURE'),
        imported_objects[0],
    )
    bpy.context.view_layer.objects.active = active_object

    # Recentrer uniquement la vue sur le modèle.
    bpy.ops.view3d.camera_to_view_selected if False else None

    return len(imported_objects)


# --------------------------------------------------
# FILE SELECTOR
# --------------------------------------------------

class MOVIESTUDIO_OT_import_fbx(bpy.types.Operator):
    bl_idname = "moviestudio.import_fbx"
    bl_label = "Importer un FBX"
    bl_description = "Importer un personnage depuis un fichier FBX"
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
            self.report({'ERROR'}, f"Échec de l'importation : {error}")
            return {'CANCELLED'}

        self.report(
            {'INFO'},
            f"Importation terminée : {count} objets importés.",
        )

        return {'FINISHED'}

    def invoke(self, context, event):
        context.window_manager.fileselect_add(self)
        return {'RUNNING_MODAL'}


# --------------------------------------------------
# CREATE SCENE BUTTON
# --------------------------------------------------

class MOVIESTUDIO_OT_create_scene(bpy.types.Operator):
    bl_idname = "moviestudio.create_scene"
    bl_label = "Créer le sol et la grille"
    bl_description = "Préparer le sol de la scène MovieStudio"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        create_scene()
        self.report({'INFO'}, "Sol MovieStudio créé ou vérifié.")
        return {'FINISHED'}


# --------------------------------------------------
# USER INTERFACE
# --------------------------------------------------

class MOVIESTUDIO_PT_panel(bpy.types.Panel):
    bl_label = "MovieStudio"
    bl_idname = "MOVIESTUDIO_PT_panel"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "MovieStudio"

    def draw(self, context):
        layout = self.layout

        layout.label(text="Préparation de la scène")
        layout.operator(
            "moviestudio.create_scene",
            icon='GRID',
        )

        layout.separator()

        layout.label(text="Personnage")
        layout.operator(
            "moviestudio.import_fbx",
            icon='IMPORT',
        )


# --------------------------------------------------
# REGISTER
# --------------------------------------------------

CLASSES = (
    MOVIESTUDIO_OT_import_fbx,
    MOVIESTUDIO_OT_create_scene,
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
