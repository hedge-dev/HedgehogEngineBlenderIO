import os
import bpy
from bpy.types import Context

from .base import HEIOBaseOperator
from ...utility.general import ADDON_DIR


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

        uv_name = "UV0"
        if len(mesh.uv_layers) > 0:
            uv_name = mesh.uv_layers[0].name
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
        else:
            color_name = mesh.color_attributes[0].name

        if not has_modifier:
            index = len(modifiers)
            modifier = modifiers.new("HEIO Unleashed Fur Editor", "NODES")
            modifier.node_group = node_tree
            modifier[_find_input_socket(
                node_tree, bpy.types.NodeTreeInterfaceSocketString, "Color attribute name")] = color_name

        target_index = max(0, shell_modifier_index - 1)
        if index != target_index:
            modifiers.move(index, shell_modifier_index)

        if "FurParam" not in mesh.color_attributes:
            fur_param = mesh.color_attributes.new(
                "FurParam", "BYTE_COLOR", "CORNER")

            for color in fur_param.data:
                # gamma adjusted values for 0.5 and 0.25, to accomodate for the blender vertex paint mode
                color.color = (0.212, 0.051, 1, 1)

    def _execute(self, context):
        node_tree, editor_node_tree = _get_geometry_nodes(True)
        modifier_index = self._setup_shell_modifier(context.active_object, node_tree)
        self._setup_editor_modifier(context.active_object, editor_node_tree, modifier_index)
        return {'FINISHED'}
