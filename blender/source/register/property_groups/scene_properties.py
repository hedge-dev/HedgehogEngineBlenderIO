
import bpy
from bpy.props import (
    BoolProperty,
    EnumProperty,
)

class HEIO_Scene(bpy.types.PropertyGroup):

    target_game: EnumProperty(
        name="Target Game",
        description="Which game to target when exporting and setting up models/materials",
        items=(
            ("UNLEASHED", "Sonic Unleashed", ""),
            ("COLORS", "Sonic Colors", ""),
            ("GENERATIONS", "Sonic Generations", ""),
            ("LOST_WORLD", "Sonic Lost World", ""),
            ("FORCES", "Sonic Forces", ""),
            ("ORIGINS", "Sonic Origins", ""),
            ("FRONTIERS", "Sonic Frontiers", ""),
            ("SHADOW_GENERATIONS", "Shadow Generations", ""),
        ),
        default="SHADOW_GENERATIONS"
    )

    show_all_shaders: BoolProperty(
        name="Show all shaders",
        description="Show all shaders defined, instead of only the commonly used ones."
    )

    @classmethod
    def register(cls):
        bpy.types.Scene.heio_scene = bpy.props.PointerProperty(type=cls)