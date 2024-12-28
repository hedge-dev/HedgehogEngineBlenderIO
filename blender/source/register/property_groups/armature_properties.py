import bpy
from bpy.props import (
    PointerProperty
)

from .lod_info_properties import HEIO_LODInfo


class HEIO_Armature(bpy.types.PropertyGroup):

    lod_info: PointerProperty(
        type=HEIO_LODInfo
    )

    @classmethod
    def register(cls):
        bpy.types.Armature.heio_armature = PointerProperty(type=cls)
