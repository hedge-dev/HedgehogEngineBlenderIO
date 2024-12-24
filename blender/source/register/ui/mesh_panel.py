import bpy
from bpy.types import Context

from .base_panel import PropertiesPanel

from ..operators import mesh_layer_operators as mlo, meshgroup_operators as mgo

from ...utility.draw import draw_list, TOOL_PROPERTY

LAYER_TOOLS: list[TOOL_PROPERTY] = [
    (
        mlo.HEIO_OT_MeshLayer_Add.bl_idname,
        "ADD",
        {}
    ),
    (
        mlo.HEIO_OT_MeshLayer_Remove.bl_idname,
        "REMOVE",
        {}
    ),
    None,
    (
        mlo.HEIO_OT_MeshLayer_Move.bl_idname,
        "TRIA_UP",
        {"direction": "UP"}
    ),
    (
        mlo.HEIO_OT_MeshLayer_Move.bl_idname,
        "TRIA_DOWN",
        {"direction": "DOWN"}
    )
]

MESHGROUP_TOOLS: list[TOOL_PROPERTY] = [
    (
        mgo.HEIO_OT_Meshgroup_Add.bl_idname,
        "ADD",
        {}
    ),
    (
        mgo.HEIO_OT_Meshgroup_Remove.bl_idname,
        "REMOVE",
        {}
    ),
    None,
    (
        mgo.HEIO_OT_Meshgroup_Move.bl_idname,
        "TRIA_UP",
        {"direction": "UP"}
    ),
    (
        mgo.HEIO_OT_Meshgroup_Move.bl_idname,
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


class HEIO_MT_LayersContextMenu(bpy.types.Menu):
    bl_label = "Mesh layer operations"

    def draw(self, context):
        self.layout.operator(mlo.HEIO_OT_MeshLayer_Delete.bl_idname)


class HEIO_UL_Meshgroups(bpy.types.UIList):

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

        layout.prop(item, "name", text="", placeholder="empty name", emboss=False)


class HEIO_MT_MeshgroupsContextMenu(bpy.types.Menu):
    bl_label = "Mesh layer operations"

    def draw(self, context):
        self.layout.operator(mgo.HEIO_OT_Meshgroup_Delete.bl_idname)


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
            body.operator(mlo.HEIO_OT_MeshLayer_Initialize.bl_idname)
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
            HEIO_MT_LayersContextMenu,
            mesh.heio_mesh.layers,
            LAYER_TOOLS,
            None
        )

        if context.mode == 'EDIT_MESH':
            row = body.row(align=True)
            row.operator(mlo.HEIO_OT_MeshLayer_Assign.bl_idname)
            row.operator(mlo.HEIO_OT_MeshLayer_Select.bl_idname)
            row.operator(mlo.HEIO_OT_MeshLayer_Deselect.bl_idname)

    @staticmethod
    def draw_meshgroups_panel(
            layout: bpy.types.UILayout,
            context: bpy.types.Context,
            mesh: bpy.types.Mesh):

        header, body = layout.panel("heio_meshgroups", default_closed=False)
        header.label(text="Meshgroups")
        if not body:
            return

        if len(mesh.heio_mesh.meshgroups) == 0 or "Meshgroup" not in mesh.attributes:
            body.operator(mgo.HEIO_OT_Meshgroup_Initialize.bl_idname)
            return

        attribute = mesh.attributes["Meshgroup"]
        if attribute.domain != "FACE" or attribute.data_type != "INT":
            box = body.box()
            box.label(text="Invalid \"Meshgroup\" attribute!")
            box.label(text="Must use domain \"Face\" and type \"Integer\"!")
            box.label(text="Please remove or convert")
            return

        draw_list(
            body,
            HEIO_UL_Meshgroups,
            HEIO_MT_MeshgroupsContextMenu,
            mesh.heio_mesh.meshgroups,
            MESHGROUP_TOOLS,
            None
        )

        if context.mode == 'EDIT_MESH':
            row = body.row(align=True)
            row.operator(mgo.HEIO_OT_Meshgroup_Assign.bl_idname)
            row.operator(mgo.HEIO_OT_Meshgroup_Select.bl_idname)
            row.operator(mgo.HEIO_OT_Meshgroup_Deselect.bl_idname)


    @staticmethod
    def draw_material_properties(
            layout: bpy.types.UILayout,
            context: bpy.types.Context,
            mesh: bpy.types.Mesh):

        HEIO_PT_Mesh.draw_layers_panel(layout, context, mesh)
        HEIO_PT_Mesh.draw_meshgroups_panel(layout, context, mesh)

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
