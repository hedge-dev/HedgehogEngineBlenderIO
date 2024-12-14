import bpy
from bpy.types import Material
from bpy.props import (
    StringProperty,
    PointerProperty,
    IntProperty,
    EnumProperty,
    CollectionProperty,
)

from .base_list import BaseList

from ...utility.material_setup import (
    get_node_of_type
)

TEXTURE_WRAP_MAPPING = {
    "REPEAT": (False, False),
    "MIRROR": (True, False),
    "CLAMP": (False, True),
    "MIRRORONCE": (True, True),
    "BORDER": (False, True),
}
"""[Mode] = (Mirror, Clamp)"""


def _update_texture(texture, context):
    texture.update_nodes()


class HEIO_MaterialTexture(bpy.types.PropertyGroup):

    name: StringProperty(
        name="Type Name",
        description=(
            "Texture slot of the shader to place this texture into."
            " Common types are \"diffuse\", \"specular\", \"normal\", \"emission\" and \"transparency\""
        ),
        update=_update_texture
    )

    image: PointerProperty(
        name="Image",
        description="Image behind the texture",
        type=bpy.types.Image,
        update=_update_texture
    )

    texcoord_index: IntProperty(
        name="Texture coordinate index",
        min=0,
        max=255,
        update=_update_texture
    )

    wrapmode_u: EnumProperty(
        name="Wrapmode U",
        items=(
            ("REPEAT", "Repeat", ""),
            ("MIRROR", "Mirror", ""),
            ("CLAMP", "Clamp", ""),
            ("MIRRORONCE", "Mirror Once", ""),
            ("BORDER", "Border", ""),
        ),
        description="Wrapmode along the horizontal axis of the texture coordinates",
        default="REPEAT",
        update=_update_texture
    )

    wrapmode_v: EnumProperty(
        name="Wrapmode V",
        items=(
            ("REPEAT", "Repeat", ""),
            ("MIRROR", "Mirror", ""),
            ("CLAMP", "Clamp", ""),
            ("MIRRORONCE", "Mirror Once", ""),
            ("BORDER", "Border", ""),
        ),
        description="Wrapmode along the vertical axis of the texture coordinates",
        default="REPEAT",
        update=_update_texture
    )

    @property
    def type_index(self):
        if not isinstance(self.id_data, Material):
            return 0

        result = 0

        for texture in self.id_data.heio_material.textures:
            if texture == self:
                return result
            elif texture.name == self.name:
                result += 1

        return None

    @property
    def image_node(self):
        return self.get_nodes()[0]

    def get_nodes(self):
        if not isinstance(self.id_data, Material):
            return (None, None, None, None)

        texture_name = self.name

        texture_index = self.type_index
        if texture_index > 0:
            texture_name += str(texture_index)

        from bpy.types import (
            ShaderNodeTexImage,
            ShaderNodeValue,
            ShaderNodeGroup
        )

        texture_node: ShaderNodeTexImage | None = get_node_of_type(
            self.id_data, "Texture " + texture_name, ShaderNodeTexImage)

        has_texture_node: ShaderNodeValue | None = get_node_of_type(
            self.id_data, "Has Texture " + texture_name, ShaderNodeValue)

        tiling_node: ShaderNodeGroup | None = get_node_of_type(
            self.id_data, "Tiling " + texture_name, ShaderNodeGroup)

        uv_node: ShaderNodeGroup | None = get_node_of_type(
            self.id_data, "UV " + texture_name, ShaderNodeGroup)

        return (texture_node, has_texture_node, tiling_node, uv_node)

    def update_nodes(self):
        nodes = self.get_nodes()

        if nodes[0] is not None:
            texture = nodes[0]
            texture.image = self.image
            texture.extension = 'EXTEND'
            texture.interpolation = 'Cubic'
            texture.projection = 'FLAT'

        if nodes[1] is not None:
            nodes[1].outputs[0].default_value = 0 if self.image is None else 1

        if nodes[2] is not None:
            tiling = nodes[2]
            tiling.inputs[1].default_value, tiling.inputs[3].default_value = TEXTURE_WRAP_MAPPING[self.wrapmode_u]
            tiling.inputs[2].default_value, tiling.inputs[4].default_value = TEXTURE_WRAP_MAPPING[self.wrapmode_v]

        if nodes[3] is not None:
            uv = nodes[3]
            for i in range(4):
                uv.inputs[i].default_value = self.texcoord_index == i


    def reset_nodes(self):
        nodes = self.get_nodes()

        if nodes[0] is not None:
            nodes[0].image = None

        if nodes[1] is not None:
            nodes[1].outputs[0].default_value = 0

        if nodes[2] is not None:
            tiling = nodes[2]
            for i in range(4):
                tiling.inputs[1 + i].default_value = False

        if nodes[3] is not None:
            uv = nodes[3]
            for i in range(4):
                uv.inputs[i].default_value = i == 1


class HEIO_MaterialTextureList(BaseList):

    elements: CollectionProperty(
        type=HEIO_MaterialTexture
    )

    def find_next_index(self, name: str, index: int):
        for i, texture in enumerate(self.elements[index:]):
            if texture.name == name:
                return index + i

        return -1

    def find_next(self, name: str, index: int):
        index = self.find_next_index(name, index)
        if index == -1:
            return None
        return self[index]
