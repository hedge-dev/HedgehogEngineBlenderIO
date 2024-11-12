import bpy
from .base_panel import PropertiesPanel
from ..property_groups.scene_properties import HEIO_Scene

class HEIO_PT_Scene(PropertiesPanel):
    bl_label = "HEIO Settings"
    bl_context = "scene"

    @staticmethod
    def draw_scene_properties(
            layout: bpy.types.UILayout,
            scene: bpy.types.Scene):

        setting_properties: HEIO_Scene = scene.heio_scene

        layout.use_property_split = True
        layout.use_property_decorate = False

        layout.prop(setting_properties, "target_game")

    def draw_panel(self, context):
        HEIO_PT_Scene.draw_scene_properties(
            self.layout,
            context.scene)