import bpy

from .base_panel import PropertiesPanel
from .lod_info_panel import draw_lod_info_panel


class HEIO_PT_Armature(PropertiesPanel):
    bl_label = "HEIO Armatures Properties"
    bl_context = "data"

    @staticmethod
    def draw_armature_properties(
            layout: bpy.types.UILayout,
            context: bpy.types.Context,
            armature: bpy.types.Armature):

        draw_lod_info_panel(
            layout, context, armature.heio_armature.lod_info)

    # === overriden methods === #

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

        return None

    def draw_panel(self, context):

        HEIO_PT_Armature.draw_armature_properties(
            self.layout,
            context,
            context.active_object.data)
