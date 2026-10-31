
import bpy
from mathutils import Vector

from .rig_analyzer import (
    extract_skeleton_data,
    get_character_objects,
)
from .metarig_template import create_working_copy


MIXAMO_TO_METARIG = {
    "mixamorig:Hips": "spine",
    "mixamorig:Spine": "spine.001",
    "mixamorig:Spine1": "spine.002",
    "mixamorig:Spine2": "spine.003",
    "mixamorig:Neck": "spine.004",
    "mixamorig:Head": "spine.006",

    "mixamorig:LeftShoulder": "shoulder.L",
    "mixamorig:LeftArm": "upper_arm.L",
    "mixamorig:LeftForeArm": "forearm.L",
    "mixamorig:LeftHand": "hand.L",

    "mixamorig:RightShoulder": "shoulder.R",
    "mixamorig:RightArm": "upper_arm.R",
    "mixamorig:RightForeArm": "forearm.R",
    "mixamorig:RightHand": "hand.R",

    "mixamorig:LeftUpLeg": "thigh.L",
    "mixamorig:LeftLeg": "shin.L",
    "mixamorig:LeftFoot": "foot.L",
    "mixamorig:LeftToeBase": "toe.L",

    "mixamorig:RightUpLeg": "thigh.R",
    "mixamorig:RightLeg": "shin.R",
    "mixamorig:RightFoot": "foot.R",
    "mixamorig:RightToeBase": "toe.R",
}


def is_mixamo_armature(obj):
    """Vérifie si un objet est une armature Mixamo."""

    if obj is None or obj.type != "ARMATURE":
        return False

    return any(
        bone.name.startswith("mixamorig:")
        for bone in obj.data.bones
    )


def find_mixamo_armature(objects, context=None):
    """
    Recherche une armature Mixamo dans les objets fournis,
    puis dans la scène active si nécessaire.
    """

    for obj in objects:
        if is_mixamo_armature(obj):
            return obj

    if context is not None:
        for obj in context.scene.objects:
            if is_mixamo_armature(obj):
                return obj

    raise RuntimeError(
        "Aucune armature Mixamo détectée dans le groupe "
        "ni dans la scène active."
    )


def validate_mapping(skeleton, metarig):
    """Vérifie les correspondances entre Mixamo et Meta-Rig."""

    missing_mixamo = []
    missing_metarig = []

    for mixamo_name, metarig_name in MIXAMO_TO_METARIG.items():
        if mixamo_name not in skeleton["bones"]:
            missing_mixamo.append(mixamo_name)

        if metarig.data.bones.get(metarig_name) is None:
            missing_metarig.append(metarig_name)

    return {
        "missing_mixamo": missing_mixamo,
        "missing_metarig": missing_metarig,
        "mapping_count": len(MIXAMO_TO_METARIG),
        "valid": not missing_mixamo and not missing_metarig,
    }


def world_to_local(metarig, world_position):
    """Convertit une position monde dans le repère local du Meta-Rig."""

    position = Vector(world_position)

    return tuple(
        metarig.matrix_world.inverted() @ position
    )


def get_target_bone_positions(skeleton, metarig):
    """Prépare les positions cibles des os du Meta-Rig."""

    positions = {}

    for mixamo_name, metarig_name in MIXAMO_TO_METARIG.items():
        source_bone = skeleton["bones"].get(mixamo_name)

        if source_bone is None:
            continue

        positions[metarig_name] = {
            "head": world_to_local(
                metarig,
                source_bone["head"],
            ),
            "tail": world_to_local(
                metarig,
                source_bone["tail"],
            ),
            "source": mixamo_name,
        }

    return positions


def prepare_metarig_adaptation(context, copy_id=None):
    """Prépare une copie du Meta-Rig sans déplacer aucun os."""

    objects = get_character_objects(context)

    armature = find_mixamo_armature(
        objects,
        context,
    )

    skeleton = extract_skeleton_data(
        armature,
        objects,
    )

    if copy_id is None:
        copy_id = armature.get(
            "moviestudio_metarig_copy_id",
            armature.name,
        )

    metarig = create_working_copy(
        context,
        copy_id,
    )

    validation = validate_mapping(
        skeleton,
        metarig,
    )

    if not validation["valid"]:
        raise RuntimeError(
            f"Correspondances invalides : {validation}"
        )

    positions = get_target_bone_positions(
        skeleton,
        metarig,
    )

    return {
        "armature": armature,
        "skeleton": skeleton,
        "metarig": metarig,
        "positions": positions,
        "validation": validation,
    }


def format_adaptation_report(result):
    """Génère un rapport lisible de préparation."""

    lines = [
        "MOVIESTUDIO - PREPARATION METARIG",
        "=" * 42,
        f"Personnage : {result['armature'].name}",
        f"Meta-Rig : {result['metarig'].name}",
        f"Os Mixamo : {result['skeleton']['bone_count']}",
        f"Correspondances : {result['validation']['mapping_count']}",
        f"Positions préparées : {len(result['positions'])}",
        "",
        "Correspondances :",
    ]

    for mixamo_name, metarig_name in MIXAMO_TO_METARIG.items():
        lines.append(
            f"  {mixamo_name} -> {metarig_name}"
        )

    lines.extend([
        "",
        "Aucune modification géométrique effectuée.",
    ])

    return "\n".join(lines)


def test_metarig_adapter(context):
    """Lance un test de préparation sans modifier les os."""

    result = prepare_metarig_adaptation(context)

    print(format_adaptation_report(result))

    return result
