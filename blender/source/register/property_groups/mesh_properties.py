import bpy
from bpy.props import (
    StringProperty,
    PointerProperty,
    CollectionProperty
)

from .base_list import BaseList

class HEIO_SpecialLayer(bpy.types.PropertyGroup):
    name: StringProperty(
        name="Special layer",
        description="Name of the special layer"
    )

class HEIO_SpecialLayerList(BaseList):

    elements: CollectionProperty(
        type=HEIO_SpecialLayer
    )

class HEIO_Mesh(bpy.types.PropertyGroup):

    special_layers: PointerProperty(
        type=HEIO_SpecialLayerList
    )

    @classmethod
    def register(cls):
        bpy.types.Mesh.heio_mesh = PointerProperty(type=cls)