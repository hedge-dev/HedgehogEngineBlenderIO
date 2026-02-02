import bpy
from bpy.props import (
    PointerProperty,
    CollectionProperty,
    IntProperty,
    FloatProperty
)

from .base_list import BaseList


class HEIO_LODInfoLevel(bpy.types.PropertyGroup):
    cascade: IntProperty(
        name="LoD Cascade",
        description="The cascade until which to start displaying the target LoD model",
        min=0,
        max=31
    )

    unknown: FloatProperty(
        name="Unknown",
        description="Yet to determine what this does. Seemingly always set to -1",
        default=-1
    )

    target: PointerProperty(
        name="Target",
        description="Target object tree to use for this LoD item",
        type=bpy.types.Object
    )


class HEIO_LODInfoLevelList(BaseList):
    elements: CollectionProperty(
        type=HEIO_LODInfoLevel
    )


class HEIO_LODInfo(bpy.types.PropertyGroup):

    levels: PointerProperty(
        type=HEIO_LODInfoLevelList
    )

    def initialize(self):
        if len(self.levels) == 0:
            self.levels.new()

    def delete(self):
        self.levels.clear()
