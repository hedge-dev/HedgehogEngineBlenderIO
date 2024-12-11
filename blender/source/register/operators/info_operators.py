import bpy
from .base import HEIOBaseOperator
import webbrowser

class HEIO_OT_Info_Manual(HEIOBaseOperator):
    bl_idname = "heio.info_manual"
    bl_label = "Open Manual"
    bl_description = "Opens the online manual for the addon"

    def _execute(self, context: bpy.types.Context):
        webbrowser.open("https://hedge-dev.github.io/HedgehogEngineBlenderIO/")
        return {'FINISHED'}


class HEIO_OT_Info_Discord(HEIOBaseOperator):
    bl_idname = "heio.info_discord"
    bl_label = "Open Discord Server"
    bl_description = "Opens the discord server invite link"

    def _execute(self, context: bpy.types.Context):
        webbrowser.open("https://dc.railgun.works/hems")
        return {'FINISHED'}


class HEIO_OT_Info_Report(HEIOBaseOperator):
    bl_idname = "heio.info_report"
    bl_label = "Report a bug / an issue"
    bl_description = "Opens the github repository issues page"

    def _execute(self, context: bpy.types.Context):
        webbrowser.open("https://github.com/hedge-dev/HedgehogEngineBlenderIO/issues")
        return {'FINISHED'}


class HEIO_OT_Info_DDS_Addon(HEIOBaseOperator):
    bl_idname = "heio.info_dds_addon"
    bl_label = "Open DDS Addon repository website"
    bl_description = "Opens the DDS addon github repository"

    def _execute(self, context: bpy.types.Context):
        webbrowser.open("https://github.com/matyalatte/Blender-DDS-Addon")
        return {'FINISHED'}