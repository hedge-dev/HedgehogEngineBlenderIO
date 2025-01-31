import bpy
from bpy.props import (
    StringProperty,
    IntProperty,
    PointerProperty,
    BoolProperty,
    FloatProperty
)

from .material_properties import HEIO_Material
from .material_parameter_properties import HEIO_MaterialParameter
from .material_texture_properties import HEIO_MaterialTexture


class HEIO_Material_MassEdit(bpy.types.PropertyGroup):

    material_properties: PointerProperty(
        type=HEIO_Material
    )

    alpha_threshold: FloatProperty(
        name="Clip threshold",
        subtype='FACTOR',
        min=0,
        max=1,
        precision=3,
        default=0.5
    )

    update_alpha_threshold: BoolProperty(
        name="Update alpha threshold"
    )

    use_backface_culling: BoolProperty(
        name="Backface culling",
        default=True
    )

    update_backface_culling: BoolProperty(
        name="Update backface culling"
    )

    update_render_layer: BoolProperty(
        name="Update render layer"
    )

    update_blend_mode: BoolProperty(
        name="Update blend mode"
    )

    parameter_name: StringProperty(
        name="Parameter name",
        description="Name of the parameter to update"
    )

    parameter_properties: PointerProperty(
        type=HEIO_MaterialParameter
    )

    texture_name: StringProperty(
        name="Texture name",
        description="Name of the texture slot to update"
    )

    texture_index: IntProperty(
        name="Texture index",
        description="Which occurence of the texture name to update (0-based)",
        soft_max=5,
        min=0
    )

    texture_properties: PointerProperty(
        type=HEIO_MaterialTexture
    )

    @classmethod
    def register(cls):
        bpy.types.Scene.heio_material_massedit = PointerProperty(type=cls)