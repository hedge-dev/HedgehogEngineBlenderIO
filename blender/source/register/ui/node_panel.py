import bpy

from .base_panel import PropertiesPanel
from .sca_parameter_panel import draw_sca_editor_menu


class HEIO_PT_Node_Bone(PropertiesPanel):
    bl_label = "HEIO Node Properties"
    bl_context = "bone"

    @staticmethod
    def draw_node_properties(
            layout: bpy.types.UILayout,
            context: bpy.types.Context,
            bone: bpy.types.Bone | bpy.types.EditBone):

        draw_sca_editor_menu(layout, bone.heio_node.sca_parameters, 'BONE')

    @classmethod
    def poll(cls, context: bpy.types.Context):
        return cls.verify(context) is None

    @classmethod
    def verify(cls, context: bpy.types.Context):
        obj = context.active_object
        if obj is None:
            return "No active object"

        if obj.type != 'ARMATURE':
            return "Active object not an armature"

        if context.active_bone is None:
            return "No active bone!"

        return None

    def draw(self, context: bpy.types.Context):

        HEIO_PT_Node_Bone.draw_node_properties(
            self.layout,
            context,
            context.active_bone,
        )
