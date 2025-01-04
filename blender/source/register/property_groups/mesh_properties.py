import bpy
from bpy.props import (
    StringProperty,
    PointerProperty,
    CollectionProperty
)

from .base_list import BaseList
from .sca_parameter_properties import HEIO_SCA_Parameters
from .lod_info_properties import HEIO_LODInfo


class HEIO_MeshInfo(bpy.types.PropertyGroup):
    name: StringProperty(name="name")


class BaseMeshInfoList(BaseList):

    elements: CollectionProperty(
        type=HEIO_MeshInfo
    )

    def _on_created(self, element, **args):
        if "name" in args:
            element.name = args["name"]

    def initialize(self):
        if len(self) == 0:
            self._on_init()

        if self.attribute_name not in self.id_data.attributes:
            self.id_data.attributes.new(self.attribute_name, "INT", "FACE")

    def delete(self):
        self.clear()
        attribute = self.attribute
        if attribute is not None and not self._check_attribute_invalid(attribute):
            self.id_data.attributes.remove(attribute)

    @staticmethod
    def _check_attribute_invalid(attribute: bpy.types.Attribute | None):
        return attribute is not None and (attribute.domain != 'FACE' or attribute.data_type != 'INT')

    @property
    def initialized(self):
        return len(self) > 0 and self.attribute_name in self.id_data.attributes

    @property
    def attribute_name(self):
        return None

    @property
    def attribute(self):
        return self.id_data.attributes.get(self.attribute_name, None)

    @property
    def attribute_invalid(self):
        return self._check_attribute_invalid(self.attribute)


class HEIO_MeshLayerList(BaseMeshInfoList):

    def _on_init(self):
        self.new(name="Opaque")
        self.new(name="Transparent")
        self.new(name="Punch through")

    @property
    def attribute_name(self):
        return "HEIOMeshLayer"


class HEIO_MeshGroupList(BaseMeshInfoList):

    def _on_init(self):
        self.new()

    @property
    def attribute_name(self):
        return "HEIOMeshGroup"


class HEIO_Mesh(bpy.types.PropertyGroup):

    groups: PointerProperty(
        type=HEIO_MeshGroupList
    )

    layers: PointerProperty(
        type=HEIO_MeshLayerList
    )

    sca_parameters: PointerProperty(
        type=HEIO_SCA_Parameters
    )

    lod_info: PointerProperty(
        type=HEIO_LODInfo
    )

    @classmethod
    def register(cls):
        bpy.types.Mesh.heio_mesh = PointerProperty(type=cls)
