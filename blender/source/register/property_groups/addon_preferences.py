import bpy
from bpy.props import StringProperty, EnumProperty, IntProperty
from .. import definitions
from ..definitions.target_definition import TargetDefinition


class HEIO_AddonPreferences(bpy.types.AddonPreferences):
    bl_idname = '.'.join(__package__.split('.')[:3])

    multi_threading_mode: EnumProperty(
        name="Multi-threading mode",
        description="Whether and how to apply multi threading when e.g. exporting models",
        items=(
            ("AUTO", "Enabled - Automatic", "Use multi-threading. Automatically determine the number of thread to create"),
            ("LIMITED", "Enabled - Limited", "Use multi-threading. Limit the number threads to use (this can also be used to exceed the number of thread used by automatic)"),
            ("DISABLED", "Disabled", "Don't use multi-threading")
        ),
        default="AUTO"
    )

    multi_threading_limit: IntProperty(
        name="Multi-threading limit",
        description="The number of threads to limit processes to. This can also be used to exceed the number of thread used by automatic",
        min=2,
        soft_max=32,
        default=2
    )

    @property
    def dotnet_max_parallelism(self):
        if self.multi_threading_mode == 'AUTO':
            return -1
        elif self.multi_threading_mode == 'LIMITED':
            return self.multi_threading_limit
        else:
            return 0

    @classmethod
    def class_setup(cls):
        for definition in definitions.TARGET_DEFINITIONS.values():
            if not definition.has_preferences:
                continue

            keyword = definition.identifier.lower()

            def add_property(name, property):
                cls.__annotations__[name + "_" + keyword] = property

            if definition.uses_ntsp:
                add_property("ntsp_dir", StringProperty(
                    name="NTSP directory",
                    description="Game Directory with .NTSP files for texture streaming. Needed for importing streamed textures.",
                    subtype='DIR_PATH',
                ))

    def draw_menu(self, definition: TargetDefinition):
        if not definition.has_preferences:
            return

        keyword = definition.identifier.lower()

        header, body = self.layout.panel(
            "heio_pref_" + keyword, default_closed=True)
        header.label(text=definition.name)

        if not body:
            return

        body.prop(self, "ntsp_dir_" + keyword)

    def draw(self, context):
        self.layout.prop(self, "multi_threading_mode")
        if self.multi_threading_mode == 'LIMITED':
            self.layout.prop(self, "multi_threading_limit")

        for definition in definitions.TARGET_DEFINITIONS.values():
            self.draw_menu(definition)
