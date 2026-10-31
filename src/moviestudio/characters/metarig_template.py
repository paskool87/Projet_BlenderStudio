
"""Load and duplicate the MovieStudio Rigify reference Meta-Rig."""

from pathlib import Path

import bpy


REFERENCE_FILENAME = "reference_metarig.blend"
REFERENCE_OBJECT_NAME = "MovieStudio_Reference_MetaRig"
REFERENCE_COLLECTION_NAME = "MovieStudio_Reference"
WORKING_COLLECTION_NAME = "MovieStudio_Characters"

REFERENCE_MARKER = "moviestudio_is_reference_metarig"
COPY_MARKER = "moviestudio_metarig_copy_id"


def get_resource_path():
    """Return the absolute path to the reference Blender file."""

    return (
        Path(__file__).resolve().parent.parent
        / "resources"
        / REFERENCE_FILENAME
    )


def get_or_create_collection(scene, name):
    """Get a collection or create and link it to the scene."""

    collection = bpy.data.collections.get(name)

    if collection is None:
        collection = bpy.data.collections.new(name)

    if collection.name not in {
        child.name for child in scene.collection.children
    }:
        scene.collection.children.link(collection)

    return collection


def get_reference_metarig(context):
    """Load the immutable reference Meta-Rig if necessary."""

    collection = get_or_create_collection(
        context.scene,
        REFERENCE_COLLECTION_NAME,
    )

    for obj in collection.objects:
        if (
            obj.type == "ARMATURE"
            and obj.get(REFERENCE_MARKER)
        ):
            return obj

    filepath = get_resource_path()

    if not filepath.is_file():
        raise FileNotFoundError(
            f"Meta-Rig de référence introuvable : {filepath}"
        )

    with bpy.data.libraries.load(
        str(filepath),
        link=False,
    ) as (data_from, data_to):

        if "metarig" not in data_from.objects:
            raise RuntimeError(
                "Le fichier de référence ne contient pas "
                "d'objet nommé 'metarig'."
            )

        data_to.objects = ["metarig"]

    loaded_objects = [
        obj for obj in data_to.objects
        if obj is not None
    ]

    if not loaded_objects:
        raise RuntimeError(
            "Impossible de charger le Meta-Rig de référence."
        )

    reference = loaded_objects[0]

    if reference.type != "ARMATURE":
        bpy.data.objects.remove(reference, do_unlink=True)
        raise RuntimeError(
            "L'objet 'metarig' chargé n'est pas une armature."
        )

    reference.name = REFERENCE_OBJECT_NAME
    reference.data.name = REFERENCE_OBJECT_NAME + "_Data"
    reference[REFERENCE_MARKER] = True

    collection.objects.link(reference)

    # Keep the reference out of the user's normal workflow.
    reference.hide_set(True)
    reference.hide_select = True
    reference.hide_render = True

    return reference


def create_working_copy(context, copy_id, name=None):
    """Create or retrieve an independent working Meta-Rig copy.

    copy_id must uniquely identify the character being prepared.
    Calling this function again with the same ID returns the
    existing copy instead of creating another one.
    """

    if not copy_id:
        raise ValueError(
            "Un identifiant de personnage est obligatoire."
        )

    working_collection = get_or_create_collection(
        context.scene,
        WORKING_COLLECTION_NAME,
    )

    for obj in working_collection.objects:
        if (
            obj.type == "ARMATURE"
            and obj.get(COPY_MARKER) == copy_id
        ):
            return obj

    reference = get_reference_metarig(context)

    working_copy = reference.copy()
    working_copy.data = reference.data.copy()

    working_copy.name = name or f"MetaRig_{copy_id}"
    working_copy.data.name = working_copy.name + "_Data"

    working_copy[REFERENCE_MARKER] = False
    working_copy[COPY_MARKER] = copy_id

    working_collection.objects.link(working_copy)

    working_copy.hide_set(False)
    working_copy.hide_select = False
    working_copy.hide_render = False

    return working_copy
