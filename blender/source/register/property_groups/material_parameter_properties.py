import bpy
from bpy.types import Material
from bpy.props import (
    BoolProperty,
    FloatVectorProperty,
    StringProperty,
    CollectionProperty
)

from .base_list import BaseList

from ...utility.material_setup import (
    get_node_of_type,
    get_first_connected_socket,
    reset_output_socket
)


def _get_color_value(parameter):
    return parameter.value


def _set_color_value(parameter, value):
    parameter.value = value


def _update_parameter(parameter, context):
    parameter.update_nodes()


class HEIO_MaterialParameterFloat(bpy.types.PropertyGroup):

    name: StringProperty(
        name="Name",
        update=_update_parameter
    )

    value: FloatVectorProperty(
        name="Value",
        size=4,
        precision=3,
        update=_update_parameter
    )

    color_value: FloatVectorProperty(
        name="Value",
        subtype="COLOR",
        size=4,
        precision=3,
        soft_min=0,
        soft_max=1,
        get=_get_color_value,
        set=_set_color_value
    )

    is_color: BoolProperty(
        name="Is Color",
        description="Whether the parameter is a color",
        default=False
    )

    def get_nodes(self):
        if not isinstance(self.id_data, Material):
            return (None, None, None)

        from bpy.types import (
            ShaderNodeCombineXYZ as CombineXYZ,
            ShaderNodeCombineRGB as CombineRGB,
            ShaderNodeRGB as RGB,
            ShaderNodeValue as Value,
        )

        node: Value | CombineXYZ | CombineRGB | RGB | None = get_node_of_type(
            self.id_data, self.name, (Value, CombineXYZ, CombineRGB, RGB))

        node_w: Value | None = get_node_of_type(
            self.id_data, self.name + ".w", Value)

        node_a: Value | None = get_node_of_type(
            self.id_data, self.name + ".a", Value)

        return (node, node_w, node_a)

    def update_nodes(self):
        nodes = self.get_nodes()

        if nodes[0] is not None:
            node = nodes[0]

            if isinstance(node, bpy.types.ShaderNodeRGB):
                node.outputs[0].default_value = self.color_value

            elif isinstance(node, bpy.types.ShaderNodeValue):
                node.outputs[0].default_value = self.value[0]

            elif isinstance(node, bpy.types.ShaderNodeCombineRGB):
                node.inputs[0].default_value = self.color_value[0]
                node.inputs[1].default_value = self.color_value[1]
                node.inputs[2].default_value = self.color_value[2]

            else:  # bpy.types.ShaderNodeCombineXYZ
                node.inputs[0].default_value = self.value[0]
                node.inputs[1].default_value = self.value[1]
                node.inputs[2].default_value = self.value[2]

        if nodes[1] is not None:
            nodes[1].outputs[0].default_value = self.value[4]

        if nodes[2] is not None:
            nodes[2].outputs[0].default_value = self.value[4]

    def reset_nodes(self):
        nodes = self.get_nodes()

        if nodes[0] is not None:
            node = nodes[0]

            if isinstance(node, (bpy.types.ShaderNodeRGB, bpy.types.ShaderNodeValue)):
                reset_output_socket(node.outputs[0])

            else:  # bpy.types.ShaderNodeCombineRGB | bpy.types.ShaderNodeCombineXYZ
                connected = get_first_connected_socket(node.outputs[0])
                if connected is not None:
                    node.inputs[0].default_value = connected.default_value[0]
                    node.inputs[1].default_value = connected.default_value[1]
                    node.inputs[2].default_value = connected.default_value[2]

        if nodes[1] is not None:
            reset_output_socket(nodes[1].outputs[0])

        if nodes[2] is not None:
            reset_output_socket(nodes[2].outputs[0])


class HEIO_MaterialParameterFloatList(BaseList):

    elements: CollectionProperty(
        type=HEIO_MaterialParameterFloat
    )


class HEIO_MaterialParameterBoolean(bpy.types.PropertyGroup):

    name: StringProperty(
        name="Name",
        update=_update_parameter
    )

    value: BoolProperty(
        name="Value",
        update=_update_parameter
    )

    def get_node(self):
        if not isinstance(self.id_data, Material):
            return None

        from bpy.types import ShaderNodeValue

        node: ShaderNodeValue | None = get_node_of_type(
            self.id_data, self.name, ShaderNodeValue)

        return node

    def update_nodes(self):
        node = self.get_node()

        if node is None:
            return

        node.outputs[0].default_value = 1 if self.value else 0

    def reset_nodes(self):
        node = self.get_node()

        if node is None:
            return

        reset_output_socket(node.outputs[0])


class HEIO_MaterialParameterBooleanList(BaseList):

    elements: CollectionProperty(
        type=HEIO_MaterialParameterBoolean
    )
