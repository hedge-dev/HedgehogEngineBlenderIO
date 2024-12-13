import bpy
from bpy.types import Context

from .base_panel import PropertiesPanel

from ..property_groups.mesh_properties import HEIO_Mesh
from ..operators import mesh_layer_operators as mslo

from ...utility.draw import draw_list, TOOL_PROPERTY

LAYER_TOOLS: list[TOOL_PROPERTY] = [
    (
        mslo.HEIO_OT_MeshLayer_Add.bl_idname,
        "ADD",
        {}
    ),
    (
        mslo.HEIO_OT_MeshLayer_Remove.bl_idname,
        "REMOVE",
        {}
    ),
    None,
    (
        mslo.HEIO_OT_MeshLayer_Move.bl_idname,
        "TRIA_UP",
        {"direction": "UP"}
    ),
    (
        mslo.HEIO_OT_MeshLayer_Move.bl_idname,
        "TRIA_DOWN",
        {"direction": "DOWN"}
    )
]


class HEIO_UL_Layers(bpy.types.UIList):

    def draw_item(
            self,
            context: bpy.types.Context,
            layout: bpy.types.UILayout,
            data,
            item,
            icon: str,
            active_data,
            active_property,
            index,
            flt_flag):

        if len(item.name) == 0:
            icon = "ERROR"
        else:
            icon = "NONE"

        layout.active = index > 2
        layout.prop(item, "name", text="", emboss=False, icon=icon)


class HEOI_MT_LayersContextMenu(bpy.types.Menu):
    bl_label = "Mesh layer operations"

    def draw(self, context):
        self.layout.operator(mslo.HEIO_OT_MeshLayer_Delete.bl_idname)


class HEIO_PT_Mesh(PropertiesPanel):
    bl_label = "HEIO Mesh Properties"
    bl_context = "data"

    # === overriden methods === #

    @staticmethod
    def draw_layers_panel(
            layout: bpy.types.UILayout,
            context: bpy.types.Context,
            mesh: bpy.types.Mesh):

        header, body = layout.panel("heio_mesh_layers", default_closed=False)
        header.label(text="Layers")
        if not body:
            return

        if len(mesh.heio_mesh.layers) == 0 or "Layer" not in mesh.attributes:
            body.operator(mslo.HEIO_OT_MeshLayer_Initialize.bl_idname)
            return

        attribute = mesh.attributes["Layer"]
        if attribute.domain != "FACE" or attribute.data_type != "INT":
            box = body.box()
            box.label(text="Invalid \"Layer\" attribute!")
            box.label(text="Must use domain \"Face\" and type \"Integer\"!")
            box.label(text="Please remove or convert")
            return

        draw_list(
            body,
            HEIO_UL_Layers,
            HEOI_MT_LayersContextMenu,
            mesh.heio_mesh.layers,
            LAYER_TOOLS,
            None
        )

        if context.mode == 'EDIT_MESH':
            row = body.row(align=True)
            row.operator(mslo.HEIO_OT_MeshLayer_Assign.bl_idname)
            row.operator(mslo.HEIO_OT_MeshLayer_Select.bl_idname)
            row.operator(mslo.HEIO_OT_MeshLayer_Deselect.bl_idname)

    @staticmethod
    def draw_material_properties(
            layout: bpy.types.UILayout,
            context: bpy.types.Context,
            mesh: bpy.types.Mesh):

        HEIO_PT_Mesh.draw_layers_panel(layout, context, mesh)

    @classmethod
    def poll(cls, context: Context):
        return cls.verify(context) is None

    @classmethod
    def verify(cls, context: bpy.types.Context):
        obj = context.active_object
        if obj is None:
            return "No active object"

        if obj.type != 'MESH':
            return "Active object not a mesh"

        return None

    def draw_panel(self, context):

        HEIO_PT_Mesh.draw_material_properties(
            self.layout,
            context,
            context.active_object.data)
