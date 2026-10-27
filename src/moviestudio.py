
import bpy

# MovieStudio - Configuration
PLATE_SIZE = 20
GRID_SPACING = 1
GRID_LINE_THICKNESS = 0.008
OBJECT_SIZE = 1


def clear_scene():
    """Remove all existing objects from the scene."""
    bpy.ops.object.select_all(action="SELECT")
    bpy.ops.object.delete(use_global=False)


def create_floor():
    """Create the square floor."""
    bpy.ops.mesh.primitive_plane_add(
        size=PLATE_SIZE,
        location=(0, 0, 0),
    )

    floor = bpy.context.object
    floor.name = "MovieStudio_Floor"
    floor.hide_select = True

    return floor


def create_grid():
    """Create a regular grid above the floor."""
    curve_data = bpy.data.curves.new(
        name="MovieStudio_Grid",
        type="CURVE",
    )
    curve_data.dimensions = "3D"
    curve_data.bevel_depth = GRID_LINE_THICKNESS
    curve_data.resolution_u = 1

    half_size = PLATE_SIZE / 2
    line_count = int(PLATE_SIZE / GRID_SPACING)

    for index in range(line_count + 1):
        position = -half_size + index * GRID_SPACING

        lines = [
            (
                (position, -half_size, 0.01),
                (position, half_size, 0.01),
            ),
            (
                (-half_size, position, 0.01),
                (half_size, position, 0.01),
            ),
        ]

        for start, end in lines:
            spline = curve_data.splines.new("POLY")
            spline.points.add(1)
            spline.points[0].co = (*start, 1)
            spline.points[1].co = (*end, 1)

    grid = bpy.data.objects.new(
        "MovieStudio_Grid",
        curve_data,
    )
    bpy.context.collection.objects.link(grid)
    grid.hide_select = True

    return grid


def create_test_object():
    """Create a cube resting on the floor."""
    bpy.ops.mesh.primitive_cube_add(
        size=OBJECT_SIZE,
        location=(0, 0, OBJECT_SIZE / 2),
    )

    obj = bpy.context.object
    obj.name = "MovieStudio_TestObject"

    return obj


def main():
    clear_scene()
    create_floor()
    create_grid()
    create_test_object()

    print("MovieStudio: floor, grid and test object created.")


if __name__ == "__main__":
    main()
