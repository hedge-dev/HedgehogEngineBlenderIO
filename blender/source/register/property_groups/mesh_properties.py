import bpy
from bpy.props import (
    StringProperty,
    PointerProperty,
    CollectionProperty
)

from .base_list import BaseList
from .sca_parameter_properties import HEIO_SCA_Parameters
from .lod_info_properties import HEIO_LODInfo


class HEIO_MeshLayer(bpy.types.PropertyGroup):
    name: StringProperty(
        name="Layer name",
        description="Name of the layer"
    )


class HEIO_MeshLayerList(BaseList):

    elements: CollectionProperty(
        type=HEIO_MeshLayer
    )

    def _on_created(self, element, **args):
        if "name" in args:
            element.name = args["name"]


class HEIO_Meshgroup(bpy.types.PropertyGroup):
    name: StringProperty(
        name="Meshgroup name",
        description="Name of the meshgroup"
    )


class HEIO_MeshgroupList(BaseList):

    elements: CollectionProperty(
        type=HEIO_Meshgroup
    )

    def _on_created(self, element, **args):
        if "name" in args:
            element.name = args["name"]


class HEIO_Mesh(bpy.types.PropertyGroup):

    layers: PointerProperty(
        type=HEIO_MeshLayerList
    )

    meshgroups: PointerProperty(
        type=HEIO_MeshgroupList
    )

    sca_parameters: PointerProperty(
        type=HEIO_SCA_Parameters
    )

    lod_info: PointerProperty(
        type=HEIO_LODInfo
    )

    def initialize_layers(self):
        if len(self.layers) == 0:
            self.layers.new(name="Opaque")
            self.layers.new(name="Transparent")
            self.layers.new(name="Punch through")

        if "Layer" not in self.id_data.attributes:
            self.id_data.attributes.new("Layer", "INT", "FACE")

    def initialize_meshgroups(self):
        if len(self.meshgroups) == 0:
            self.meshgroups.new(name="")

        if "Meshgroup" not in self.id_data.attributes:
            self.id_data.attributes.new("Meshgroup", "INT", "FACE")

    @classmethod
    def register(cls):
        bpy.types.Mesh.heio_mesh = PointerProperty(type=cls)
