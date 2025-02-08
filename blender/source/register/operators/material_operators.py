import bpy
from bpy.props import EnumProperty
from bpy.types import Context

from .base import HEIOBaseOperator, HEIOBasePopupOperator
from .. import definitions
from ..property_groups.mesh_properties import MESH_DATA_TYPES

from ...utility.material_setup import (
    setup_and_update_materials,
    setup_principled_bsdf_materials
)


class MaterialOperator(HEIOBasePopupOperator):
    bl_options = {'UNDO'}

    targetmode: EnumProperty(
        name="Target Mode",
        description="Determining which materials should be updated",
        items=(
            ("ACTIVE", "Active Material", "Only the active material"),
            ("SELECTED", "Selected objects", "Materials of selected objects"),
            ("SCENE", "Scene objects", "Materials used in the active scene"),
            ("ALL", "All", "All materials in the blend file"),
        ),
        default="SCENE"
    )

    @staticmethod
    def get_materials(context: bpy.types.Context, targetmode: str):

        results = set()

        def add(obj: bpy.types.Object):
            if obj.type in MESH_DATA_TYPES:
                results.update(
                    [slot.material for slot in obj.material_slots if slot.material is not None])

        if targetmode == 'ACTIVE':
            if (context.active_object.type in MESH_DATA_TYPES
                    and context.active_object.active_material is not None):
                results.add(context.active_object.active_material)
        elif targetmode == 'SELECTED':
            for obj in context.selected_objects:
                add(obj)
        elif targetmode == 'SCENE':
            for obj in context.scene.objects:
                add(obj)
        else:  # ALL
            results.update(bpy.data.materials)

        return results

    def mat_execute(self, context, materials):
        pass

    @classmethod
    def poll(cls, context: Context):
        return context.mode == 'OBJECT'

    def _execute(self, context):
        materials = MaterialOperator.get_materials(context, self.targetmode)
        self.mat_execute(context, materials)
        return {'FINISHED'}


class HEIO_OT_Material_SetupNodes(MaterialOperator):
    bl_idname = "heio.material_setup_nodes"
    bl_label = "Setup/Update Material Nodes"
    bl_description = "Set up material nodes based on the selected shader"

    def mat_execute(self, context, materials):
        target_definition = definitions.get_target_definition(context)
        setup_and_update_materials(target_definition, materials)


class HEIO_OT_Material_SetupNodes_Active(HEIOBaseOperator):
    bl_idname = "heio.material_setup_nodes_active"
    bl_label = "Setup/Update Nodes"
    bl_options = {'UNDO'}

    def _execute(self, context: bpy.types.Context):
        materials = MaterialOperator.get_materials(context, 'ACTIVE')
        target_definition = definitions.get_target_definition(context)
        setup_and_update_materials(target_definition, materials)

        return {'FINISHED'}


class HEIO_OT_Material_ToPrincipled(MaterialOperator):
    bl_idname = "heio.material_to_principled"
    bl_label = "Materials to Principled BSDF"
    bl_description = "Set up node trees with a principled BSDF node tree for general purpose exporting"

    def mat_execute(self, context, materials: set[bpy.types.Material]):
        target_definition = definitions.get_target_definition(context)
        setup_principled_bsdf_materials(target_definition, materials)


class HEIO_OT_Material_FromPrincipled(MaterialOperator):
    bl_idname = "heio.material_from_principled"
    bl_label = "Material Textures from Principled BSDF"
    bl_description = "Attempt to gather diffuse and normal textures from materials with principled BSDF node trees"

    def draw(self, context):
        self.layout.prop(self, "targetmode")

        self.layout.separator(type='LINE')
        self.layout.label(text="Note: Set up material shaders beforehand!")

    def mat_execute(self, context, materials: set[bpy.types.Material]):
        for material in materials:
            if material.node_tree is None or len(material.node_tree.nodes) == 0:
                continue

            diffuse_texture = material.heio_material.textures.elements.get("diffuse", None)
            normal_texture = material.heio_material.textures.elements.get("normal", None)

            if diffuse_texture is None and normal_texture is None and not material.heio_material.custom_shader:
                continue

            output_node = None

            for node in material.node_tree.nodes:
                if isinstance(node, bpy.types.ShaderNodeOutputMaterial):
                    output_node = node
                    break

            if output_node is None:
                continue

            def trace_to_first_node(input_socket: bpy.types.NodeSocket, node_type):
                if not input_socket.is_linked:
                    return None

                traversed = {input_socket.node}
                queue = [input_socket.links[0].from_node]

                while len(queue) > 0:
                    node = queue.pop()

                    if isinstance(node, node_type):
                        return node

                    traversed.add(node)

                    for input in reversed(node.inputs):
                        if not input.is_linked:
                            continue

                        linked_node = input.links[0].from_node
                        if linked_node in traversed:
                            continue

                        traversed.add(linked_node)
                        queue.append(linked_node)

                return None

            principled_node = trace_to_first_node(
                output_node.inputs[0], bpy.types.ShaderNodeBsdfPrincipled)

            if principled_node is None:
                continue

            def find_and_setup_texture(texture, name, input_index):
                if texture is None and not material.heio_material.custom_shader:
                    return

                texture_node = trace_to_first_node(principled_node.inputs[input_index], bpy.types.ShaderNodeTexImage)

                if texture_node is None or texture_node.image is None:
                    return

                if texture is None:
                    texture = material.heio_material.textures.new(name=name)

                texture.image = texture_node.image

            find_and_setup_texture(diffuse_texture, "diffuse", 0)
            find_and_setup_texture(normal_texture, "normal", 4)

