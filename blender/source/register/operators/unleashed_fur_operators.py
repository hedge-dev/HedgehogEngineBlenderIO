import os
import bpy
from bpy.types import Context
from bpy.props import StringProperty, FloatVectorProperty

from .base import HEIOBaseOperator
from ...utility.general import ADDON_DIR
from ...exceptions import HEIOUserException


def _get_geometry_nodes(include_editor):

    templates_path = os.path.join(
        ADDON_DIR, "Definitions", "UnleashedFur.blend")

    with bpy.data.libraries.load(templates_path, link=True) as (data_from, data_to):

        if include_editor:
            data_to.node_groups = [
                "HEIO_UnleashedFurShells", "HEIO_UnleashedFurEditor"]
        else:
            data_to.node_groups = ["HEIO_UnleashedFurShells"]

    if include_editor:
        return data_to.node_groups[0], data_to.node_groups[1]
    else:
        return data_to.node_groups[0]


def _find_input_socket(node_tree: bpy.types.NodeTree, type, name: str):
    for socket in node_tree.interface.items_tree:
        if isinstance(socket, bpy.types.NodeTreeInterfaceSocket) and isinstance(socket, type) and socket.name == name and socket.in_out == 'INPUT':
            return socket.identifier
    return None


class BaseUnleashedFurOperator(HEIOBaseOperator):
    bl_options = {'UNDO'}

    @classmethod
    def poll(cls, context: Context):
        return (
            context.mode == 'OBJECT'
            and context.active_object is not None
            and context.active_object.type == 'MESH'
        )

    @staticmethod
    def _setup_shell_modifier(obj: bpy.types.Object, node_tree: bpy.types.NodeTree):

        modifiers = obj.modifiers

        for i, modifier in enumerate(modifiers):
            if not isinstance(modifier, bpy.types.NodesModifier):
                continue

            if modifier.node_group == node_tree:
                return i

        index = len(modifiers)
        modifier: bpy.types.NodesModifier = modifiers.new(
            "HEIO Unleashed Fur Shells", "NODES")
        modifier.node_group = node_tree
        modifiers.move(index, 0)

        mesh = obj.data

        attribute_name = "Color"
        if len(mesh.color_attributes) > 0:
            attribute_name = mesh.color_attributes[0].name
        modifier[_find_input_socket(
            node_tree, bpy.types.NodeTreeInterfaceSocketString, "Color attribute name")] = attribute_name

        uv_name = "UVMap"
        if len(mesh.uv_layers) > 0:
            uv_name = mesh.uv_layers[0].name
            modifier[_find_input_socket(
                node_tree, bpy.types.NodeTreeInterfaceSocketMenu, "Mode")] = 1

        modifier[_find_input_socket(
            node_tree, bpy.types.NodeTreeInterfaceSocketString, "UV Map")] = uv_name

        return 0


class HEIO_OT_UnleashedFur_AddShells(BaseUnleashedFurOperator):
    bl_idname = "heio.unleashedfur_addshells"
    bl_label = "Add Unleashed Fur Shells"
    bl_description = "Add a geometry modifier to the active model that generates fur shells"

    def _execute(self, context):
        node_group = _get_geometry_nodes(False)
        self._setup_shell_modifier(context.active_object, node_group)
        return {'FINISHED'}


class HEIO_OT_UnleashedFur_AddEditor(BaseUnleashedFurOperator):
    bl_idname = "heio.unleashedfur_addeditor"
    bl_label = "Add Unleashed Fur Editor"
    bl_description = "Add a geometry modifier to the active model that generates fur shells and an editor"

    @staticmethod
    def _setup_editor_modifier(obj: bpy.types.Object, node_tree: bpy.types.NodeTree, shell_modifier_index):
        has_modifier = False
        modifiers = obj.modifiers

        for index, modifier in enumerate(modifiers):
            if not isinstance(modifier, bpy.types.NodesModifier):
                continue

            if modifier.node_group == node_tree:
                has_modifier = True
                break

        mesh = obj.data

        if len(mesh.color_attributes) == 0:
            mesh.color_attributes.new("Color", "BYTE_COLOR", "CORNER")
            color_name = "Color"
            color_created = True
        else:
            color_name = mesh.color_attributes[mesh.color_attributes.render_color_index].name
            color_created = False

        if not has_modifier:
            index = len(modifiers)
            modifier = modifiers.new("HEIO Unleashed Fur Editor", "NODES")
            modifier.node_group = node_tree
            modifier[_find_input_socket(
                node_tree, bpy.types.NodeTreeInterfaceSocketString, "Color attribute name")] = color_name

        target_index = max(0, shell_modifier_index - 1)
        if index != target_index:
            modifiers.move(index, shell_modifier_index)

        if "FurLength" not in mesh.color_attributes:
            fur_length = mesh.color_attributes.new(
                "FurLength", "BYTE_COLOR", "CORNER")

            if color_created:
                for color in fur_length.data:
                    color.color = (1, 1, 1, 1)
            else:
                color_attribute = mesh.color_attributes[color_name]
                for i, color in enumerate(fur_length.data):
                    fac = color_attribute.data[i].color[3]
                    color.color = (fac, fac, fac, 1)

        if "FurDirection" not in mesh.color_attributes:
            fur_direction = mesh.color_attributes.new(
                "FurDirection", "BYTE_COLOR", "CORNER")

            if color_created:
                for color in fur_direction.data:
                    color.color = (0.5, 0.5, 0, 1)
            else:
                color_attribute = mesh.color_attributes[color_name]
                for i, color in enumerate(fur_direction.data):
                    color.color = color_attribute.data[i].color

        mesh.color_attributes.active_color_name = "FurDirection"
        mesh.color_attributes.render_color_index = mesh.color_attributes.find(
            color_name)

    def _execute(self, context):
        node_tree, editor_node_tree = _get_geometry_nodes(True)
        modifier_index = self._setup_shell_modifier(
            context.active_object, node_tree)
        self._setup_editor_modifier(
            context.active_object, editor_node_tree, modifier_index)
        return {'FINISHED'}


class HEIO_OT_UnleashedFur_SwitchVertexColors(HEIOBaseOperator):
    bl_idname = "heio.unleashedfur_switchpvertexcolors"
    bl_label = "Switch vertex colors"
    bl_description = "Change the actively painted vertex colors"
    bl_options = {'UNDO'}

    attribute_name: StringProperty()

    @classmethod
    def poll(cls, context: Context):
        return context.mode == 'PAINT_VERTEX'

    def _execute(self, context):
        color_attribs = context.active_object.data.color_attributes
        if self.attribute_name not in color_attribs:
            raise HEIOUserException(f"Mesh has no color attribute \"{self.attribute_name}\"! Please set up the fur editor!")
        color_attribs.active_color_name = self.attribute_name
        return {'FINISHED'}


class HEIO_OT_UnleashedFur_SetBrushDir(HEIOBaseOperator):
    bl_idname = "heio.unleashedfur_setbrushdir"
    bl_label = "Set paint brush fur direction"
    bl_description = "Change the vertex paint direction"
    bl_options = {'UNDO'}

    direction: FloatVectorProperty()

    @classmethod
    def poll(cls, context: Context):
        return context.mode == 'PAINT_VERTEX'

    def _execute(self, context):
        context.scene.heio_blender_utilities.vertex_paint_direction = (
            self.direction[0],
            self.direction[1],
            self.direction[2]
        )
        return {'FINISHED'}
