import bpy
from bpy.types import WorkSpaceTool
import os

from .cpt_select_gizmo_group import HEIO_GGT_CollisionPrimitive_Select
from .cpt_transform_gizmo_group import HEIO_GGT_CollisionPrimitive_Transform

from ...property_groups.mesh_properties import MESH_DATA_TYPES
from ...ui.mesh_panel import HEIO_PT_Mesh, HEIO_UL_CollisionPrimitiveList
from ....utility import general


class BaseCollisionPrimitiveWorkSpaceTool(WorkSpaceTool):
    bl_space_type = 'VIEW_3D'
    bl_context_mode = 'OBJECT'
    bl_keymap = None

    @staticmethod
    def draw_settings(context: bpy.types.Context, layout, tool):
        if (context.mode != 'OBJECT'
                or context.region.type == 'TOOL_HEADER'
                or context.active_object is None
                or context.active_object.type not in MESH_DATA_TYPES):
            return

        primitives = context.active_object.data.heio_mesh.collision_primitives

        body = HEIO_PT_Mesh.draw_mesh_info_layout(
            layout,
            context,
            primitives,
            HEIO_UL_CollisionPrimitiveList,
            None,
            'COLLISION_PRIMITIVES'
        )

        HEIO_PT_Mesh.draw_primitive_editor(
            body,
            context,
            primitives.active_element
        )


class HEIO_WST_CollisionPrimitive_Select(BaseCollisionPrimitiveWorkSpaceTool):
    bl_idname = "heio.wst.collision_primitive_select"
    bl_label = "Select collision primitive"
    bl_description = "Select a meshes collision primitive by clicking it"
    bl_icon = os.path.join(general.ICON_DIR, "heio.collision_primitive.select")
    bl_widget = HEIO_GGT_CollisionPrimitive_Select.bl_idname


class HEIO_WST_CollisionPrimitive_Transform(BaseCollisionPrimitiveWorkSpaceTool):
    bl_idname = "heio.wst.collision_primitive_transform"
    bl_label = "Transform collision primitive"
    bl_description = "Selecn and transform a meshes collision primitives"
    bl_icon = os.path.join(
        general.ICON_DIR, "heio.collision_primitive.transform")
    bl_widget = HEIO_GGT_CollisionPrimitive_Transform.bl_idname


class CollisionPrimitiveWSTRegister:

    DONT_REGISTER_CLASS = True

    @classmethod
    def register(cls):
        bpy.utils.register_tool(HEIO_WST_CollisionPrimitive_Select, after={
                                "builtin.scale_cage"}, separator=True, group=True)
        bpy.utils.register_tool(HEIO_WST_CollisionPrimitive_Transform, after={
                                HEIO_WST_CollisionPrimitive_Select.bl_idname})

    @classmethod
    def unregister(cls):
        bpy.utils.unregister_tool(HEIO_WST_CollisionPrimitive_Select)
        bpy.utils.unregister_tool(HEIO_WST_CollisionPrimitive_Transform)
