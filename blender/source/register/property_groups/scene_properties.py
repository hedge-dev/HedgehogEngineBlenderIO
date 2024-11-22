
import bpy
from bpy.props import (
    BoolProperty,
    StringProperty,
    EnumProperty,
)

from .. import definitions

def _get_target_game_items(scene_properties, context):
    tg = scene_properties.target_game_name

    if tg in definitions.TARGET_DEFINITIONS:
        return definitions.TARGET_ENUM_ITEMS
    else:

        result = definitions.TARGET_ENUM_ITEMS_INVALID
        result[0] = ("ERROR_FALLBACK", tg, "")
        return result


def _get_target_game(scene_properties):
    tg = scene_properties.target_game_name

    if tg in definitions.TARGET_DEFINITIONS:
        for i, item in enumerate(definitions.TARGET_ENUM_ITEMS):
            if item[0] == tg:
                return i

    return 0


def _set_target_game(scene_properties, value):
    items = _get_target_game_items(scene_properties, bpy.context)
    scene_properties.target_game_name = items[value][0]

class HEIO_Scene(bpy.types.PropertyGroup):

    target_game_name: StringProperty(
        name="Test",
        default="SHADOW_GENERATIONS"
    )

    target_game: EnumProperty(
        name="Target Game",
        description="Which game to target when exporting and setting up models/materials",
        items=_get_target_game_items,
        get=_get_target_game,
        set=_set_target_game
    )

    show_all_shaders: BoolProperty(
        name="Show all shaders",
        description="Show all shaders defined, instead of only the commonly used ones."
    )

    @classmethod
    def register(cls):
        bpy.types.Scene.heio_scene = bpy.props.PointerProperty(type=cls)