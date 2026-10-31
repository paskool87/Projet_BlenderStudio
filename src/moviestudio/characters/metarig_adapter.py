
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


FINGER_MAPPING = {
    "Thumb": "thumb",
    "Index": "f_index",
    "Middle": "f_middle",
    "Ring": "f_ring",
    "Pinky": "f_pinky",
}

FINGER_SEGMENTS = (1, 2, 3)


def is_mixamo_armature(obj):
    """Vérifie si un objet est une armature Mixamo."""

    if obj is None or obj.type != "ARMATURE":
        return False

    return any(
        bone.name.startswith("mixamorig:")
        for bone in obj.data.bones
    )


def find_mixamo_armature(objects, context=None):
    """Recherche une armature Mixamo dans le groupe ou la scène."""

    for obj in objects:
        if is_mixamo_armature(obj):
            return obj

    if context is not None:
        for obj in context.scene.objects:
            if is_mixamo_armature(obj):
                return obj

    raise RuntimeError(
        "Aucune armature Mixamo détectée dans la scène."
    )


def validate_mapping(skeleton, metarig):
    """Vérifie les correspondances principales."""

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
    """Convertit une position monde en position locale."""

    return metarig.matrix_world.inverted() @ Vector(world_position)


def get_finger_mapping(skeleton, metarig):
    """Construit les correspondances disponibles pour les doigts."""

    mapping = {}

    for side in ("Left", "Right"):
        rigify_side = "L" if side == "Left" else "R"

        for mixamo_finger, rigify_finger in FINGER_MAPPING.items():
            for segment in FINGER_SEGMENTS:
                mixamo_name = (
                    f"mixamorig:{side}Hand{mixamo_finger}{segment}"
                )

                metarig_name = (
                    f"{rigify_finger}.{segment:02d}.{rigify_side}"
                )

                if mixamo_name not in skeleton["bones"]:
                    continue

                if metarig.data.bones.get(metarig_name) is None:
                    continue

                mapping[mixamo_name] = metarig_name

    return mapping


def get_target_bone_positions(skeleton, metarig):
    """Prépare les positions cibles des os principaux et des doigts."""

    complete_mapping = dict(MIXAMO_TO_METARIG)
    complete_mapping.update(get_finger_mapping(skeleton, metarig))

    positions = {}

    for mixamo_name, metarig_name in complete_mapping.items():
        source_bone = skeleton["bones"].get(mixamo_name)

        if source_bone is None:
            continue

        positions[metarig_name] = {
            "head": world_to_local(metarig, source_bone["head"]),
            "tail": world_to_local(metarig, source_bone["tail"]),
            "source": mixamo_name,
        }

    return positions


def prepare_metarig_adaptation(context, copy_id=None):
    """Prépare les données nécessaires à l'adaptation."""

    objects = get_character_objects(context)

    armature = find_mixamo_armature(objects, context)

    skeleton = extract_skeleton_data(armature, objects)

    if copy_id is None:
        copy_id = armature.name

    metarig = create_working_copy(context, copy_id)

    validation = validate_mapping(skeleton, metarig)

    if not validation["valid"]:
        raise RuntimeError(
            f"Correspondances invalides : {validation}"
        )

    positions = get_target_bone_positions(skeleton, metarig)

    finger_count = len(positions) - len(MIXAMO_TO_METARIG)

    return {
        "armature": armature,
        "skeleton": skeleton,
        "metarig": metarig,
        "positions": positions,
        "validation": validation,
        "finger_count": finger_count,
    }


def remove_palm_bones(edit_bones):
    """
    Supprime les os palm et rattache leurs enfants
    directement aux mains correspondantes.
    """

    removed = []

    for side in ("L", "R"):
        hand = edit_bones.get(f"hand.{side}")

        if hand is None:
            continue

        for index in range(1, 5):
            name = f"palm.{index:02d}.{side}"
            palm = edit_bones.get(name)

            if palm is None:
                continue

            children = list(palm.children)

            for child in children:
                child.parent = hand
                child.use_connect = False

            edit_bones.remove(palm)

            # On mémorise le nom avant toute autre opération.
            removed.append(name)

    return removed


def adapt_metarig_geometry(result):
    """
    Adapte géométriquement la copie du Meta-Rig.

    Les positions des os sont appliquées en mode Édition.
    Les os palm sont ensuite supprimés automatiquement.
    L'armature Mixamo originale reste intacte.
    """

    metarig = result["metarig"]
    positions = result["positions"]

    if metarig.mode != "OBJECT":
        bpy.ops.object.mode_set(mode="OBJECT")

    bpy.ops.object.select_all(action="DESELECT")

    metarig.select_set(True)
    bpy.context.view_layer.objects.active = metarig

    bpy.ops.object.mode_set(mode="EDIT")

    edit_bones = metarig.data.edit_bones

    original_positions = {}

    for bone_name in positions:
        bone = edit_bones.get(bone_name)

        if bone is None:
            continue

        original_positions[bone_name] = {
            "head": bone.head.copy(),
            "tail": bone.tail.copy(),
        }

    ordered_names = [
        "spine",
        "spine.001",
        "spine.002",
        "spine.003",
        "spine.004",
        "spine.006",

        "shoulder.L",
        "upper_arm.L",
        "forearm.L",
        "hand.L",

        "shoulder.R",
        "upper_arm.R",
        "forearm.R",
        "hand.R",

        "thigh.L",
        "shin.L",
        "foot.L",
        "toe.L",

        "thigh.R",
        "shin.R",
        "foot.R",
        "toe.R",
    ]

    # Ajouter les doigts après les mains.
    for side in ("L", "R"):
        for finger in FINGER_MAPPING.values():
            for segment in FINGER_SEGMENTS:
                bone_name = f"{finger}.{segment:02d}.{side}"

                if bone_name in positions:
                    ordered_names.append(bone_name)

    adapted = []
    skipped = []

    for bone_name in ordered_names:
        bone = edit_bones.get(bone_name)

        if bone is None or bone_name not in positions:
            skipped.append(bone_name)
            continue

        bone.use_connect = False

    for bone_name in ordered_names:
        bone = edit_bones.get(bone_name)
        target = positions.get(bone_name)

        if bone is None or target is None:
            continue

        bone.head = Vector(target["head"])
        bone.tail = Vector(target["tail"])

        adapted.append(bone_name)

    # Suppression automatique des huit os palm.
    removed_palms = remove_palm_bones(edit_bones)

    bpy.ops.object.mode_set(mode="OBJECT")

    bpy.context.view_layer.update()

    main_adapted = [
        name for name in adapted
        if name in MIXAMO_TO_METARIG.values()
    ]

    fingers_adapted = [
        name for name in adapted
        if name not in MIXAMO_TO_METARIG.values()
    ]

    result["adaptation"] = {
        "adapted": adapted,
        "skipped": skipped,
        "count": len(adapted),
        "main_count": len(main_adapted),
        "finger_count": len(fingers_adapted),
        "removed_palms": removed_palms,
        "original_positions": original_positions,
    }

    return result


def format_adaptation_report(result):
    """Génère le rapport d'adaptation."""

    lines = [
        "MOVIESTUDIO - ADAPTATION METARIG",
        "=" * 42,
        f"Personnage : {result['armature'].name}",
        f"Meta-Rig : {result['metarig'].name}",
        f"Os Mixamo : {result['skeleton']['bone_count']}",
        f"Correspondances principales : {result['validation']['mapping_count']}",
        f"Correspondances doigts : {result.get('finger_count', 0)}",
    ]

    adaptation = result.get("adaptation")

    if adaptation:
        lines.extend([
            "",
            f"Os adaptés : {adaptation['count']}",
            f"  Os principaux : {adaptation['main_count']}",
            f"  Os des doigts : {adaptation['finger_count']}",
            f"Os palm supprimés : {len(adaptation['removed_palms'])}",
            f"Os ignorés : {len(adaptation['skipped'])}",
            "",
            "Os palm supprimés :",
        ])

        for name in adaptation["removed_palms"]:
            lines.append(f"  - {name}")

        lines.extend([
            "",
            "Liste des os adaptés :",
        ])

        for name in adaptation["adapted"]:
            lines.append(f"  - {name}")

        if adaptation["skipped"]:
            lines.extend(["", "Os ignorés :"])

            for name in adaptation["skipped"]:
                lines.append(f"  - {name}")

    else:
        lines.append("")
        lines.append("Adaptation non encore effectuée.")

    return "\n".join(lines)


def test_metarig_adapter(context):
    """Prépare et adapte la copie du Meta-Rig."""

    result = prepare_metarig_adaptation(context)

    result = adapt_metarig_geometry(result)

    print(format_adaptation_report(result))

    return result
