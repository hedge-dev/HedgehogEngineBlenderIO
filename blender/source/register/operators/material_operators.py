import bpy
from bpy.props import EnumProperty
from bpy.types import Context

from .base import HEIOBaseOperator, HEIOBasePopupOperator
from .. import definitions
from ..property_groups.mesh_properties import MESH_DATA_TYPES

from ...utility.material_setup import (
    setup_and_update_materials
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
                results.update([slot.material for slot in obj.material_slots if slot.material is not None])

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