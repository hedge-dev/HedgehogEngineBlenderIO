import bpy

from .base_panel import PropertiesPanel
from .lod_info_panel import draw_lod_info_panel


class HEIO_PT_Armature(PropertiesPanel):
    bl_label = "HEIO Armatures Properties"
    bl_context = "data"

    @classmethod
    def verify(cls, context: bpy.types.Context):
        obj = context.active_object
        if obj is None:
            return "No active object"

        if obj.type != 'ARMATURE':
            return "Active object not an armature"

        return None

    @classmethod
    def draw_panel(cls, layout, context):
        armature = context.active_object.data

        draw_lod_info_panel(
            layout, context, armature.heio_armature.lod_info)
