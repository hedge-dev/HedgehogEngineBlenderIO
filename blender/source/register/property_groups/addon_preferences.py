import bpy
from bpy.props import StringProperty
from .. import definitions

class HEIO_AddonPreferences(bpy.types.AddonPreferences):
    bl_idname = '.'.join(__package__.split('.')[:3])

    @classmethod
    def register(cls):
        for definition in definitions.TARGET_DEFINITIONS.keys():
            keyword = definition.lower()
            def add_property(name, property):
                cls.__annotations__[name + "_" + keyword] = property

            add_property("ntsp_dir", StringProperty(
                name="NTSP directory",
                description="Game Directory with .NTSP files for texture streaming. Needed for importing streamed textures.",
                subtype='DIR_PATH',
            ))

    def draw_menu(self, keyword: str, label: str):
        header, menu = self.layout.panel("heio_pref_" + keyword, default_closed=True)
        header.label(text=label)

        if not menu:
            return

        menu.prop(self, "ntsp_dir_" + keyword)

    def draw(self, context):
        for definition in definitions.TARGET_DEFINITIONS.values():
            self.draw_menu(definition.identifier.lower(), definition.name)
