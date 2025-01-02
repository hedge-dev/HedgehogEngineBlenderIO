import bpy
from bpy.props import (
    IntProperty,
    FloatProperty,
    BoolProperty
)


class HEIO_View3DOverlay_CollisionPrimitive(bpy.types.PropertyGroup):

    show_primitives: BoolProperty(
        name="Show collision primitives",
        default=True
    )

    random_colors: BoolProperty(
        name="Random colors",
        description="Use a random color for each collision primitive",
        default=False
    )

    random_seed: IntProperty(
        name="Random Seed"
    )

    line_width: IntProperty(
        name="Line width",
        description="Thickness of the lines drawn for collision primitives",
        min=0,
        soft_max=10,
        default=2
    )

    surface_visibility: FloatProperty(
        name="Surface visibility",
        description="How visible the surfaces of collision primitives should be",
        subtype='FACTOR',
        min=0,
        max=1,
        default=0.5
    )

    line_visibility: FloatProperty(
        name="Line visibility",
        description="How visible the lines of collision primitives should be",
        subtype='FACTOR',
        min=0,
        max=1,
        default=0.65
    )

    @classmethod
    def register(cls):
        bpy.types.Screen.heio_collision_primitives = bpy.props.PointerProperty(type=cls)

