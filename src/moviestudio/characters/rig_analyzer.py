
"""Read-only character rig analyzer for MovieStudio."""

import bpy

from ..utils import IMPORT_GROUP_PROPERTY


MIXAMO_REQUIRED_BONES = (
    "mixamorig:Hips",
    "mixamorig:Spine",
    "mixamorig:Spine1",
    "mixamorig:Spine2",
    "mixamorig:Neck",
    "mixamorig:Head",
    "mixamorig:LeftArm",
    "mixamorig:RightArm",
    "mixamorig:LeftForeArm",
    "mixamorig:RightForeArm",
    "mixamorig:LeftUpLeg",
    "mixamorig:RightUpLeg",
    "mixamorig:LeftLeg",
    "mixamorig:RightLeg",
    "mixamorig:LeftFoot",
    "mixamorig:RightFoot",
)

RIGIFY_REQUIRED_BONES = (
    "DEF-spine",
    "DEF-upper_arm.L",
    "DEF-upper_arm.R",
    "DEF-forearm.L",
    "DEF-forearm.R",
    "DEF-thigh.L",
    "DEF-thigh.R",
    "DEF-shin.L",
    "DEF-shin.R",
    "DEF-hand.L",
    "DEF-hand.R",
)


def get_character_objects(context):
    """Return objects belonging to the active import group."""

    active = context.active_object

    if active is not None:
        group_id = active.get(IMPORT_GROUP_PROPERTY)

        if group_id is not None:
            return [
                obj for obj in context.scene.objects
                if obj.get(IMPORT_GROUP_PROPERTY) == group_id
            ]

    return list(context.selected_objects)


def get_associated_meshes(objects, armature):
    """Find meshes associated with an armature."""

    meshes = []

    for obj in objects:
        if obj.type != "MESH":
            continue

        is_associated = obj.parent == armature

        if not is_associated:
            is_associated = any(
                modifier.type == "ARMATURE"
                and modifier.object == armature
                for modifier in obj.modifiers
            )

        if is_associated:
            meshes.append(obj)

    return meshes


def classify_armature(armature):
    """Identify a Mixamo or generated Rigify armature."""

    bone_names = {
        bone.name for bone in armature.data.bones
    }

    has_mixamo_names = any(
        name.startswith("mixamorig:")
        for name in bone_names
    )

    has_rigify_deform_bones = any(
        name.startswith("DEF-")
        for name in bone_names
    )

    has_rigify_structure = (
        any(name.startswith("ORG-") for name in bone_names)
        and any(name.startswith("MCH-") for name in bone_names)
    )

    if has_rigify_deform_bones and has_rigify_structure:
        return "RIGIFY"

    if has_mixamo_names:
        return "MIXAMO"

    return "UNKNOWN"


def check_mixamo_t_pose(armature):
    """Estimate whether Mixamo arms are in a T-pose."""

    bone_data = armature.data.bones

    required = (
        "mixamorig:LeftArm",
        "mixamorig:RightArm",
    )

    if not all(name in bone_data for name in required):
        return False, "Os des bras Mixamo introuvables."

    results = []

    for name, expected_direction in (
        ("mixamorig:LeftArm", 1),
        ("mixamorig:RightArm", -1),
    ):
        bone = bone_data[name]

        head = armature.matrix_world @ bone.head_local
        tail = armature.matrix_world @ bone.tail_local

        direction = tail - head
        length = direction.length

        if length == 0:
            return False, f"Os {name} de longueur nulle."

        horizontal_ratio = abs(direction.x) / length
        vertical_ratio = abs(direction.z) / length

        points_outward = direction.x * expected_direction > 0

        is_horizontal = (
            horizontal_ratio >= 0.90
            and vertical_ratio <= 0.20
        )

        results.append(points_outward and is_horizontal)

    if all(results):
        return True, "Pose en T détectée."

    return False, "Pose en T non confirmée."


def analyze_mesh_weights(mesh, armature):
    """Inspect vertex groups and their correspondence to bones."""

    bone_names = {
        bone.name for bone in armature.data.bones
    }

    group_names = {
        group.name for group in mesh.vertex_groups
    }

    matching = group_names & bone_names
    unmatched = group_names - bone_names

    weighted_vertices = set()
    unmatched_weighted_vertices = set()

    group_indices = {
        group.index: group.name
        for group in mesh.vertex_groups
    }

    for vertex in mesh.data.vertices:
        for assignment in vertex.groups:
            if assignment.weight <= 0:
                continue

            group_name = group_indices.get(assignment.group)

            if group_name in matching:
                weighted_vertices.add(vertex.index)

            elif group_name in unmatched:
                unmatched_weighted_vertices.add(vertex.index)

    return {
        "groups": len(group_names),
        "matching": len(matching),
        "unmatched": sorted(unmatched),
        "weighted_vertices": len(weighted_vertices),
        "unmatched_weighted_vertices": len(
            unmatched_weighted_vertices
        ),
    }


def analyze_armature(armature, objects):
    """Build a read-only diagnostic for one armature."""

    rig_type = classify_armature(armature)

    bone_names = {
        bone.name for bone in armature.data.bones
    }

    report = {
        "name": armature.name,
        "type": rig_type,
        "bones": len(bone_names),
        "meshes": [],
        "missing_bones": [],
        "t_pose": None,
        "t_pose_message": None,
        "deform_bones": sum(
            1 for bone in armature.data.bones
            if bone.use_deform
        ),
    }

    if rig_type == "MIXAMO":
        report["missing_bones"] = [
            name for name in MIXAMO_REQUIRED_BONES
            if name not in bone_names
        ]

        is_t_pose, message = check_mixamo_t_pose(armature)

        report["t_pose"] = is_t_pose
        report["t_pose_message"] = message

    elif rig_type == "RIGIFY":
        report["missing_bones"] = [
            name for name in RIGIFY_REQUIRED_BONES
            if name not in bone_names
        ]

    meshes = get_associated_meshes(objects, armature)

    for mesh in meshes:
        report["meshes"].append({
            "name": mesh.name,
            "vertices": len(mesh.data.vertices),
            "weights": analyze_mesh_weights(mesh, armature),
        })

    return report


def format_report(reports):
    """Format diagnostic results as readable text."""

    lines = [
        "",
        "=" * 60,
        "MOVIESTUDIO - DIAGNOSTIC DU PERSONNAGE",
        "=" * 60,
    ]

    for report in reports:
        lines.extend([
            "",
            f"ARMATURE : {report['name']}",
            f"Type détecté : {report['type']}",
            f"Nombre d'os : {report['bones']}",
            f"Os déformants : {report['deform_bones']}",
        ])

        if report["type"] == "MIXAMO":
            lines.append(
                f"Pose : {report['t_pose_message']}"
            )

        if report["missing_bones"]:
            lines.append("Os indispensables manquants :")

            for name in report["missing_bones"]:
                lines.append(f"  - {name}")
        else:
            lines.append("Structure osseuse : complète selon les contrôles.")

        if not report["meshes"]:
            lines.append("Aucun mesh associé détecté.")

        for mesh in report["meshes"]:
            weights = mesh["weights"]

            lines.extend([
                "",
                f"Mesh : {mesh['name']}",
                f"  Sommets : {mesh['vertices']}",
                f"  Groupes de sommets : {weights['groups']}",
                f"  Groupes correspondants : {weights['matching']}",
                f"  Sommets pondérés correspondants : "
                f"{weights['weighted_vertices']}",
                f"  Sommets avec groupes sans os correspondant : "
                f"{weights['unmatched_weighted_vertices']}",
            ])

            if weights["unmatched"]:
                lines.append("  Groupes sans os correspondant :")

                for name in weights["unmatched"]:
                    lines.append(f"    - {name}")

    lines.extend([
        "",
        "=" * 60,
        "FIN DU DIAGNOSTIC - AUCUNE MODIFICATION EFFECTUÉE",
        "=" * 60,
    ])

    return "\n".join(lines)


class MOVIESTUDIO_OT_analyze_character(bpy.types.Operator):
    """Analyze the selected character without modifying the scene."""

    bl_idname = "moviestudio.analyze_character"
    bl_label = "Analyser le personnage"
    bl_description = (
        "Analyser les armatures, les meshes et les pondérations"
    )
    bl_options = {"REGISTER"}

    @classmethod
    def poll(cls, context):
        return (
            context.active_object is not None
            or bool(context.selected_objects)
        )

    def execute(self, context):
        objects = get_character_objects(context)

        armatures = [
            obj for obj in objects
            if obj.type == "ARMATURE"
        ]

        if not armatures:
            self.report(
                {"WARNING"},
                "Aucune armature trouvée dans la sélection.",
            )
            return {"CANCELLED"}

        reports = [
            analyze_armature(armature, objects)
            for armature in armatures
        ]

        diagnostic = format_report(reports)

        print(diagnostic)

        types = {
            report["type"] for report in reports
        }

        if "UNKNOWN" in types:
            summary = "Analyse terminée : armature non reconnue."
        elif "MIXAMO" in types:
            summary = "Analyse Mixamo terminée. Voir la console."
        else:
            summary = "Analyse Rigify terminée. Voir la console."

        self.report({"INFO"}, summary)

        return {"FINISHED"}
