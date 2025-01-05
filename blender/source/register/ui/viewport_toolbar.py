import bpy

from .. operators import (
    mesh_geometry_operators,
    material_operators,
    info_operators
)

class ViewportToolPanel(bpy.types.Panel):
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "HEIO Tools"
    bl_options = {'DEFAULT_CLOSED'}

class HEIO_PT_VTP_Mesh(bpy.types.Panel):
    bl_label = "Mesh"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "HEIO Tools"

    def draw(self, context):
        layout = self.layout

        layout.operator(mesh_geometry_operators.HEIO_OT_SplitMeshGroups.bl_idname)
        layout.operator(mesh_geometry_operators.HEIO_OT_MergeMeshGroups.bl_idname)
        layout.operator(mesh_geometry_operators.HEIO_OT_CollisionPrimitivesToGeometry.bl_idname)


class HEIO_PT_VTP_Material(bpy.types.Panel):
    bl_label = "Material"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "HEIO Tools"

    def draw(self, context):
        layout = self.layout

        layout.operator(material_operators.HEIO_OT_Material_SetupNodes.bl_idname)


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

        layout.operator(info_operators.HEIO_OT_Info_Manual.bl_idname)
        layout.operator(info_operators.HEIO_OT_Info_Discord.bl_idname)
        layout.operator(info_operators.HEIO_OT_Info_Report.bl_idname)