import bpy
from bpy.types import Material
from bpy.props import (
    StringProperty,
    EnumProperty,
    BoolProperty,
    FloatVectorProperty,
    CollectionProperty
)

from .base_list import BaseList
from ..definitions import TargetDefinition

from ...utility.material_setup import (
    get_node_of_type,
    get_first_connected_socket,
    reset_output_socket
)


def _get_color_value(parameter):
    return parameter.float_value


def _set_color_value(parameter, value):
    parameter.float_value = value


def _update_parameter(parameter, context):
    parameter.update_nodes()


class HEIO_MaterialParameter(bpy.types.PropertyGroup):

    name: StringProperty(
        name="Name",
        update=_update_parameter
    )

    value_type: EnumProperty(
        name="Type",
        items=(
            ("FLOAT", "Float", ""),
            ("COLOR", "Color", ""),
            ("BOOLEAN", "Boolean", ""),
        )
    )

    float_value: FloatVectorProperty(
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

    boolean_value: BoolProperty(
        name="Value",
        update=_update_parameter
    )

    override: BoolProperty(
        name="Override",
        description="This parameter is usually handled by the game itself, but can be overriden in the material"
    )

    def _get_parameter_definition(self, target_definition: TargetDefinition):
        if target_definition is None or not isinstance(self.id_data, bpy.types.Material) or self.id_data.heio_material.custom_shader:
            return None

        shader_definition = target_definition.shaders.definitions.get(self.id_data.heio_material.shader_name, None)
        if shader_definition is None:
            return None

        shader_parameter = shader_definition.parameters.get(self.name, None)
        return shader_parameter

    def is_hidden(self, target_definition: TargetDefinition):
        parameter_def = self._get_parameter_definition(target_definition)

        if parameter_def is None:
            return False

        return not parameter_def.is_used

    def is_overridable(self, target_definition: TargetDefinition):
        parameter_def = self._get_parameter_definition(target_definition)

        if parameter_def is None:
            return False

        return parameter_def.overridable


    def _get_float_nodes(self):
        if not isinstance(self.id_data, Material):
            return (None, None, None)

        from bpy.types import (
            ShaderNodeCombineXYZ as CombineXYZ,
            ShaderNodeCombineColor as CombineRGB,
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

    def _update_float_nodes(self):
        nodes = self._get_float_nodes()

        if nodes[0] is not None:
            node = nodes[0]

            if isinstance(node, bpy.types.ShaderNodeRGB):
                node.outputs[0].default_value = self.color_value

            elif isinstance(node, bpy.types.ShaderNodeValue):
                node.outputs[0].default_value = self.float_value[0]

            elif isinstance(node, bpy.types.ShaderNodeCombineColor):
                node.inputs[0].default_value = self.color_value[0]
                node.inputs[1].default_value = self.color_value[1]
                node.inputs[2].default_value = self.color_value[2]

            else:  # bpy.types.ShaderNodeCombineXYZ
                node.inputs[0].default_value = self.float_value[0]
                node.inputs[1].default_value = self.float_value[1]
                node.inputs[2].default_value = self.float_value[2]

        if nodes[1] is not None:
            nodes[1].outputs[0].default_value = self.float_value[3]

        if nodes[2] is not None:
            nodes[2].outputs[0].default_value = self.float_value[3]

    def _reset_float_nodes(self):
        nodes = self._get_float_nodes()

        if nodes[0] is not None:
            node = nodes[0]

            if isinstance(node, (bpy.types.ShaderNodeRGB, bpy.types.ShaderNodeValue)):
                reset_output_socket(node.outputs[0])

            else:  # bpy.types.ShaderNodeCombineColor | bpy.types.ShaderNodeCombineXYZ
                connected = get_first_connected_socket(node.outputs[0])
                if connected is not None:
                    node.inputs[0].default_value = connected.default_value[0]
                    node.inputs[1].default_value = connected.default_value[1]
                    node.inputs[2].default_value = connected.default_value[2]

        if nodes[1] is not None:
            reset_output_socket(nodes[1].outputs[0])

        if nodes[2] is not None:
            reset_output_socket(nodes[2].outputs[0])

    def _get_boolean_node(self):
        if not isinstance(self.id_data, Material):
            return None

        from bpy.types import ShaderNodeValue

        node: ShaderNodeValue | None = get_node_of_type(
            self.id_data, self.name, ShaderNodeValue)

        return node

    def _update_boolean_node(self):
        node = self._get_boolean_node()

        if node is None:
            return

        node.outputs[0].default_value = 1 if self.boolean_value else 0

    def _reset_boolean_node(self):
        node = self._get_boolean_node()

        if node is None:
            return

        reset_output_socket(node.outputs[0])

    def get_nodes(self):
        if self.value_type == 'BOOLEAN':
            return self._get_boolean_node()
        else:
            return self._get_float_nodes()

    def update_nodes(self):
        if self.value_type == 'BOOLEAN':
            self._update_boolean_node()
        else:
            self._update_float_nodes()

    def reset_nodes(self):
        if self.value_type == 'BOOLEAN':
            self._reset_boolean_node()
        else:
            self._reset_float_nodes()


class HEIO_MaterialParameterList(BaseList):

    elements: CollectionProperty(
        type=HEIO_MaterialParameter
    )

    def find_next_index(self, name: str, index: int, types: list[str] | None):
        for i, parameter in enumerate(self.elements[index:]):
            if parameter.name == name and (types is None or parameter.value_type in types):
                return index + i

        return -1

    def find_next(self, name: str, index: int, types: list[str] | None):
        index = self.find_next_index(name, index, types)
        if index == -1:
            return None
        return self[index]
