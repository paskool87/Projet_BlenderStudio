
import bpy

# Dimensions du plateau
SIZE = 20
GRID_SPACING = 1

# Créer le sol
bpy.ops.mesh.primitive_plane_add(
    size=SIZE,
    location=(0, 0, 0)
)

floor = bpy.context.object
floor.name = "MovieStudio_Plateau"

# Créer la grille avec des traits
curve_data = bpy.data.curves.new(
    "MovieStudio_Grille",
    type="CURVE"
)
curve_data.dimensions = "3D"
curve_data.bevel_depth = 0.008

half = SIZE / 2

for i in range(SIZE + 1):
    position = -half + i * GRID_SPACING

    for start, end in [
        ((position, -half, 0.01), (position, half, 0.01)),
        ((-half, position, 0.01), (half, position, 0.01)),
    ]:
        spline = curve_data.splines.new("POLY")
        spline.points.add(1)
        spline.points[0].co = (*start, 1)
        spline.points[1].co = (*end, 1)

grid = bpy.data.objects.new(
    "MovieStudio_Quadrillage",
    curve_data
)
bpy.context.collection.objects.link(grid)

# Empêcher de sélectionner accidentellement le sol et la grille
floor.hide_select = True
grid.hide_select = True

print("MovieStudio : plateau créé.")
