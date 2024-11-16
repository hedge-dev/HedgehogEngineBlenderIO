import bpy
from bpy.props import StringProperty

class HEIO_AddonPreferences(bpy.types.AddonPreferences):
    bl_idname = '.'.join(__package__.split('.')[:3])

    ntsp_dir_unleashed: StringProperty(
        name="NTSP directory: Unleashed",
        description="Game Directory with .NTSP files for texture streaming. Needed for importing streamed textures.",
        subtype='DIR_PATH',
    )

    ntsp_dir_colors: StringProperty(
        name="NTSP directory: Colors",
        description="Game Directory with .NTSP files for texture streaming. Needed for importing streamed textures.",
        subtype='DIR_PATH',
    )

    ntsp_dir_generations: StringProperty(
        name="NTSP directory: Generations",
        description="Game Directory with .NTSP files for texture streaming. Needed for importing streamed textures.",
        subtype='DIR_PATH',
    )

    ntsp_dir_lost_world: StringProperty(
        name="NTSP directory: Lost World",
        description="Game Directory with .NTSP files for texture streaming. Needed for importing streamed textures.",
        subtype='DIR_PATH',
    )

    ntsp_dir_forces: StringProperty(
        name="NTSP directory: Forces",
        description="Game Directory with .NTSP files for texture streaming. Needed for importing streamed textures.",
        subtype='DIR_PATH',
    )

    ntsp_dir_origins: StringProperty(
        name="NTSP directory: Origins",
        description="Game Directory with .NTSP files for texture streaming. Needed for importing streamed textures.",
        subtype='DIR_PATH',
    )

    ntsp_dir_frontiers: StringProperty(
        name="NTSP directory: Frontiers",
        description="Game Directory with .NTSP files for texture streaming. Needed for importing streamed textures.",
        subtype='DIR_PATH',
    )

    ntsp_dir_shadow_generations: StringProperty(
        name="NTSP directory: Shadow Generations",
        description="Game Directory with .NTSP files for texture streaming. Needed for importing streamed textures.",
        subtype='DIR_PATH',
    )

    def draw(self, context):
        self.layout.prop(self, "ntsp_dir_unleashed")
        self.layout.prop(self, "ntsp_dir_colors")
        self.layout.prop(self, "ntsp_dir_generations")
        self.layout.prop(self, "ntsp_dir_lost_world")
        self.layout.prop(self, "ntsp_dir_forces")
        self.layout.prop(self, "ntsp_dir_origins")
        self.layout.prop(self, "ntsp_dir_frontiers")
        self.layout.prop(self, "ntsp_dir_shadow_generations")
