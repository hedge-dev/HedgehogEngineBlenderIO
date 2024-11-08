import bpy
from .base import HEIOBaseOperator


class HEIO_OT_Info_Manual(HEIOBaseOperator):
    bl_idname = "heio.info_manual"
    bl_label = "Open Manual"
    bl_description = "Opens the online manual for the addon"

    def _execute(self, context: bpy.types.Context):
        import webbrowser
        webbrowser.open("https://x-hax.github.io/HedgehogEngineBlenderIO/")
        return {'FINISHED'}


class HEIO_OT_Info_Discord(HEIOBaseOperator):
    bl_idname = "heio.info_discord"
    bl_label = "Open Discord Server"
    bl_description = "Opens the discord server invite link"

    def _execute(self, context: bpy.types.Context):
        import webbrowser
        webbrowser.open("https://dc.railgun.works/hems")
        return {'FINISHED'}
