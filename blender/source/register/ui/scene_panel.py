from .base_panel import PropertiesPanel
from ..property_groups.scene_properties import HEIO_Scene

class HEIO_PT_Scene(PropertiesPanel):
    bl_label = "HEIO Settings"
    bl_context = "scene"

    @classmethod
    def draw_panel(cls, layout, context):
        scene = context.scene

        setting_properties: HEIO_Scene = scene.heio_scene

        layout.use_property_split = True
        layout.use_property_decorate = False

        layout.prop(
            setting_properties,
            "target_game",
            icon="ERROR" if setting_properties.target_game == "ERROR_FALLBACK" else "NONE")
