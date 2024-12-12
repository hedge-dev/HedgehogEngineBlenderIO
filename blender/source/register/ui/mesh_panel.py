import bpy
from bpy.types import Context

from .base_panel import PropertiesPanel

from ..property_groups.mesh_properties import HEIO_Mesh
from ..operators import mesh_special_layer_operators as mslo

from ...utility.draw import draw_list, TOOL_PROPERTY

SPECIAL_LAYER_TOOLS: list[TOOL_PROPERTY] = [
    (
        mslo.HEIO_OT_MeshSpecialLayer_Add.bl_idname,
        "ADD",
        {}
    ),
    (
        mslo.HEIO_OT_MeshSpecialLayer_Remove.bl_idname,
        "REMOVE",
        {}
    ),
    None,
    (
        mslo.HEIO_OT_MeshSpecialLayer_Move.bl_idname,
        "TRIA_UP",
        {"direction": "UP"}
    ),
    (
        mslo.HEIO_OT_MeshSpecialLayer_Move.bl_idname,
        "TRIA_DOWN",
        {"direction": "DOWN"}
    )
]


class HEIO_UL_SpecialLayerList(bpy.types.UIList):

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

        layout.prop(item, "name", text="", emboss=False, icon=icon)


class HEIO_PT_Mesh(PropertiesPanel):
    bl_label = "HEIO Mesh Properties"
    bl_context = "data"

    # === overriden methods === #

    @staticmethod
    def draw_special_layer_names(layout, mesh):
        header, menu = layout.panel("heio_mesh_special_layer_names", default_closed=False)
        header.label(text="Special layer names")
        if not menu:
            return

        draw_list(
            menu,
            HEIO_UL_SpecialLayerList,
            None,
            mesh.heio_mesh.special_layers,
            SPECIAL_LAYER_TOOLS,
            None
        )


    @staticmethod
    def draw_material_properties(
            layout: bpy.types.UILayout,
            context: bpy.types.Context,
            mesh: bpy.types.Mesh):

        HEIO_PT_Mesh.draw_special_layer_names(layout, mesh)

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
