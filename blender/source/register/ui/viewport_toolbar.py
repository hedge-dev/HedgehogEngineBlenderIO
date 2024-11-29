import bpy

from ..operators.material_operators import (
    HEIO_OT_Material_SetupNodes
)

from ..operators.info_operators import (
    HEIO_OT_Info_Manual,
    HEIO_OT_Info_Discord,
    HEIO_OT_Info_Report
)

class ViewportToolPanel(bpy.types.Panel):
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "HEIO Tools"
    bl_options = {'DEFAULT_CLOSED'}


class HEIO_PT_VTP_Material(bpy.types.Panel):
    bl_label = "Material"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "HEIO Tools"

    def draw(self, context):
        layout = self.layout

        layout.operator(HEIO_OT_Material_SetupNodes.bl_idname)


class HEIO_PT_VTP_Info(bpy.types.Panel):
    bl_label = "Info"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "HEIO Tools"

    def draw(self, context):
        layout = self.layout

        box = layout.box()
        box.label(text="You can right click any button")
        box.label(text="or property field added by the")
        box.label(text="addon and click \"Online Manual\"")
        box.label(text="to read about it.")

        layout.operator(HEIO_OT_Info_Manual.bl_idname)
        layout.operator(HEIO_OT_Info_Discord.bl_idname)
        layout.operator(HEIO_OT_Info_Report.bl_idname)