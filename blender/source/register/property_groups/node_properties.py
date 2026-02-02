import bpy
from bpy.props import (
    PointerProperty,
)

from .sca_parameter_properties import HEIO_SCA_Parameters

class HEIO_Node(bpy.types.PropertyGroup):

    sca_parameters: PointerProperty(
        type=HEIO_SCA_Parameters
    )

    @classmethod
    def register(cls):
        bpy.types.Bone.heio_node = PointerProperty(type=cls)
        bpy.types.EditBone.heio_node = PointerProperty(type=cls)