import bpy
from bpy.props import (
    StringProperty,
    PointerProperty,
    CollectionProperty
)

from .base_list import BaseList


class HEIO_Layer(bpy.types.PropertyGroup):
    name: StringProperty(
        name="Layer",
        description="Name of the layer"
    )


class HEIO_LayerList(BaseList):

    elements: CollectionProperty(
        type=HEIO_Layer
    )

    def _on_created(self, value, **args):
        if "name" in args:
            value.name = args["name"]


class HEIO_Mesh(bpy.types.PropertyGroup):

    layers: PointerProperty(
        type=HEIO_LayerList
    )

    def initialize_layers(self):
        if len(self.layers) == 0:
            self.layers.new(name="Opaque")
            self.layers.new(name="Transparent")
            self.layers.new(name="Punch through")

        if "Layer" not in self.id_data.attributes:
            self.id_data.attributes.new("Layer", "INT", "FACE")

    @classmethod
    def register(cls):
        bpy.types.Mesh.heio_mesh = PointerProperty(type=cls)
