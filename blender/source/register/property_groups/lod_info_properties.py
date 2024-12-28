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
        name="LOD Cascade",
        description="The cascade before which to start displaying this lod mesh",
        min=0,
        max=31
    )

    unknown: FloatProperty(
        name="Unknown",
        description="Yet to determine what this does. Seemingly always set to -1",
        default=-1
    )

    mesh: PointerProperty(
        name="Mesh",
        description="Mesh to use for this lod level",
        type=bpy.types.Mesh
    )

    armature: PointerProperty(
        name="Armature",
        description="Armature to use for this lod level",
        type=bpy.types.Armature
    )


class HEIO_LODInfoLevelList(BaseList):
    elements: CollectionProperty(
        type=HEIO_LODInfoLevel
    )


class HEIO_LODInfo(bpy.types.PropertyGroup):

    unknown: IntProperty(
        name="Unknown",
        description="Yet to determine what this does. Only seen to use either 4 or 132",
        default=4
    )

    levels: PointerProperty(
        type=HEIO_LODInfoLevelList
    )

    def initialize(self):
        if len(self.levels) == 0:
            self.levels.new()

    def delete(self):
        self.levels.clear()
