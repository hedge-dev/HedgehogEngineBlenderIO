import bpy
from bpy.types import Context

from .base_panel import PropertiesPanel
from .sca_parameter_panel import draw_sca_editor_menu
from .lod_info_panel import draw_lod_info_panel
from .mesh_info_ui import (
    BaseMeshInfoContextMenu,
    draw_mesh_info_panel
)


class HEIO_UL_MeshLayers(bpy.types.UIList):

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


class HEIO_MT_MeshLayersContextMenu(BaseMeshInfoContextMenu):
    bl_label = "Mesh layer operations"
    type = 'MESH_LAYERS'


class HEIO_UL_MeshGroups(bpy.types.UIList):

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

        layout.prop(item, "name", text="",
                    placeholder="empty name", emboss=False)


class HEIO_MT_MeshGroupsContextMenu(BaseMeshInfoContextMenu):
    bl_label = "Mesh group operations"
    type = 'MESH_GROUPS'


class HEIO_PT_Mesh(PropertiesPanel):
    bl_label = "HEIO Mesh Properties"
    bl_context = "data"

    @staticmethod
    def draw_material_properties(
            layout: bpy.types.UILayout,
            context: bpy.types.Context,
            mesh: bpy.types.Mesh):

        draw_mesh_info_panel(
            layout,
            context,
            mesh.heio_mesh.groups,
            HEIO_UL_MeshGroups,
            HEIO_MT_MeshGroupsContextMenu,
            'MESH_GROUPS',
            'Groups'
        )

        draw_mesh_info_panel(
            layout,
            context,
            mesh.heio_mesh.layers,
            HEIO_UL_MeshLayers,
            HEIO_MT_MeshLayersContextMenu,
            'MESH_LAYERS',
            'Layers'
        )

        draw_lod_info_panel(layout, context, mesh.heio_mesh.lod_info)
        draw_sca_editor_menu(layout, mesh.heio_mesh.sca_parameters, 'MESH')

    # === overriden methods === #

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
