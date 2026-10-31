
"""Read-only comparison between Mixamo and Rigify Meta-Rig."""

import bpy
import math


# Mixamo bone -> Rigify Meta-Rig bone
BONE_MAPPING = (
    ("mixamorig:Hips", "spine"),
    ("mixamorig:Spine", "spine.001"),
    ("mixamorig:Spine1", "spine.002"),
    ("mixamorig:Spine2", "spine.003"),
    ("mixamorig:Neck", "spine.004"),
    ("mixamorig:Head", "spine.005"),

    ("mixamorig:LeftShoulder", "shoulder.L"),
    ("mixamorig:RightShoulder", "shoulder.R"),

    ("mixamorig:LeftArm", "upper_arm.L"),
    ("mixamorig:RightArm", "upper_arm.R"),
    ("mixamorig:LeftForeArm", "forearm.L"),
    ("mixamorig:RightForeArm", "forearm.R"),
    ("mixamorig:LeftHand", "hand.L"),
    ("mixamorig:RightHand", "hand.R"),

    ("mixamorig:LeftUpLeg", "thigh.L"),
    ("mixamorig:RightUpLeg", "thigh.R"),
    ("mixamorig:LeftLeg", "shin.L"),
    ("mixamorig:RightLeg", "shin.R"),
    ("mixamorig:LeftFoot", "foot.L"),
    ("mixamorig:RightFoot", "foot.R"),
)


def is_mixamo(armature):
    """Identify a Mixamo armature."""

    return any(
        bone.name.startswith("mixamorig:")
        for bone in armature.data.bones
    )


def is_metarig(armature):
    """Identify a Rigify Human Meta-Rig."""

    bone_names = {
        bone.name for bone in armature.data.bones
    }

    required = {
        "spine",
        "spine.001",
        "upper_arm.L",
        "upper_arm.R",
        "forearm.L",
        "forearm.R",
        "thigh.L",
        "thigh.R",
    }

    return required.issubset(bone_names)


def get_world_bone_data(armature, bone_name):
    """Return a bone's world-space head, tail and length."""

    bone = armature.data.bones.get(bone_name)

    if bone is None:
        return None

    head = armature.matrix_world @ bone.head_local
    tail = armature.matrix_world @ bone.tail_local

    direction = tail - head
    length = direction.length

    return {
        "head": head,
        "tail": tail,
        "direction": direction,
        "length": length,
    }


def format_vector(vector):
    """Format a vector for the diagnostic report."""

    return (
        f"({vector.x:+.3f}, "
        f"{vector.y:+.3f}, "
        f"{vector.z:+.3f})"
    )


def compare_bones(mixamo, metarig):
    """Compare mapped bones in world coordinates."""

    results = []

    for mixamo_name, rigify_name in BONE_MAPPING:
        mixamo_data = get_world_bone_data(
            mixamo,
            mixamo_name,
        )

        rigify_data = get_world_bone_data(
            metarig,
            rigify_name,
        )

        if mixamo_data is None or rigify_data is None:
            results.append({
                "mixamo": mixamo_name,
                "rigify": rigify_name,
                "missing": True,
            })
            continue

        head_offset = (
            mixamo_data["head"] - rigify_data["head"]
        )

        tail_offset = (
            mixamo_data["tail"] - rigify_data["tail"]
        )

        mixamo_length = mixamo_data["length"]
        rigify_length = rigify_data["length"]

        if (
            mixamo_length > 0
            and rigify_length > 0
        ):
            angle = math.degrees(
                mixamo_data["direction"].angle(
                    rigify_data["direction"]
                )
            )
        else:
            angle = None

        results.append({
            "mixamo": mixamo_name,
            "rigify": rigify_name,
            "missing": False,
            "head_offset": head_offset,
            "head_distance": head_offset.length,
            "tail_offset": tail_offset,
            "tail_distance": tail_offset.length,
            "mixamo_length": mixamo_length,
            "rigify_length": rigify_length,
            "length_difference": (
                mixamo_length - rigify_length
            ),
            "angle": angle,
        })

    return results


def format_comparison(mixamo, metarig, results):
    """Build the comparison report."""

    lines = [
        "",
        "=" * 72,
        "MOVIESTUDIO - COMPARAISON MIXAMO / RIGIFY",
        "=" * 72,
        "",
        f"Armature Mixamo : {mixamo.name}",
        f"Meta-Rig Rigify : {metarig.name}",
        "",
        "Les coordonnées sont exprimées dans l'espace mondial.",
        "Aucune modification des armatures n'a été effectuée.",
        "",
        "-" * 72,
    ]

    matched = 0

    for result in results:
        lines.extend([
            "",
            f"MIXAMO : {result['mixamo']}",
            f"RIGIFY : {result['rigify']}",
        ])

        if result["missing"]:
            lines.append("  Os absent : comparaison impossible.")
            continue

        matched += 1

        lines.extend([
            (
                "  Écart des têtes : "
                f"{format_vector(result['head_offset'])}"
            ),
            (
                "  Distance des têtes : "
                f"{result['head_distance']:.3f}"
            ),
            (
                "  Écart des extrémités : "
                f"{format_vector(result['tail_offset'])}"
            ),
            (
                "  Distance des extrémités : "
                f"{result['tail_distance']:.3f}"
            ),
            (
                "  Longueur Mixamo : "
                f"{result['mixamo_length']:.3f}"
            ),
            (
                "  Longueur Meta-Rig : "
                f"{result['rigify_length']:.3f}"
            ),
            (
                "  Différence de longueur : "
                f"{result['length_difference']:+.3f}"
            ),
        ])

        if result["angle"] is not None:
            lines.append(
                f"  Écart d'orientation : "
                f"{result['angle']:.1f}°"
            )

    lines.extend([
        "",
        "-" * 72,
        f"Correspondances analysées : {matched}/{len(results)}",
        "",
        "FIN DE LA COMPARAISON - AUCUNE MODIFICATION EFFECTUÉE",
        "=" * 72,
    ])

    return "\n".join(lines)


class MOVIESTUDIO_OT_compare_rigs(bpy.types.Operator):
    """Compare a selected Mixamo armature with a Rigify Meta-Rig."""

    bl_idname = "moviestudio.compare_rigs"
    bl_label = "Comparer Mixamo et Meta-Rig"
    bl_description = (
        "Comparer les positions, longueurs et orientations des os"
    )
    bl_options = {"REGISTER"}

    @classmethod
    def poll(cls, context):
        return sum(
            1 for obj in context.selected_objects
            if obj.type == "ARMATURE"
        ) >= 2

    def execute(self, context):
        armatures = [
            obj for obj in context.selected_objects
            if obj.type == "ARMATURE"
        ]

        mixamo_armatures = [
            obj for obj in armatures
            if is_mixamo(obj)
        ]

        metarigs = [
            obj for obj in armatures
            if is_metarig(obj)
        ]

        if len(mixamo_armatures) != 1:
            self.report(
                {"ERROR"},
                "Sélectionne une seule armature Mixamo.",
            )
            return {"CANCELLED"}

        if len(metarigs) != 1:
            self.report(
                {"ERROR"},
                "Sélectionne un seul Meta-Rig Rigify.",
            )
            return {"CANCELLED"}

        mixamo = mixamo_armatures[0]
        metarig = metarigs[0]

        results = compare_bones(mixamo, metarig)

        diagnostic = format_comparison(
            mixamo,
            metarig,
            results,
        )

        print(diagnostic)

        matched = sum(
            1 for result in results
            if not result["missing"]
        )

        self.report(
            {"INFO"},
            f"Comparaison terminée : {matched}/{len(results)} os.",
        )

        return {"FINISHED"}
