import bpy

from .base_panel import PropertiesPanel
from .sca_parameter_panel import draw_sca_editor_menu


class HEIO_PT_Node_Bone(PropertiesPanel):
    bl_label = "HEIO Node Properties"
    bl_context = "bone"

    @classmethod
    def verify(cls, context):
        obj = context.active_object
        if obj is None:
            return "No active object"

        if obj.type != 'ARMATURE':
            return "Active object not an armature"

        if context.active_bone is None:
            return "No active bone!"

        return None

    @classmethod
    def draw_panel(cls, layout, context):
        bone = context.active_bone
        draw_sca_editor_menu(layout, bone.heio_node.sca_parameters, 'BONE')

