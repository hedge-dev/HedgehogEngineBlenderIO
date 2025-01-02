import bpy
from bpy.types import WorkSpaceTool
import os

from .cpt_select_gizmo_group import HEIO_GGT_CollisionPrimitive_Select
from .cpt_transform_gizmo_group import HEIO_GGT_CollisionPrimitive_Transform

from ....utility import general

class HEIO_WST_CollisionPrimitive_Select(WorkSpaceTool):
    bl_idname = "heio.wst.collision_primitive_select"
    bl_space_type = 'VIEW_3D'
    bl_context_mode = 'OBJECT'
    bl_label = "Select collision primitive"
    bl_description = "Select a meshes collision primitive by clicking it"
    bl_icon = os.path.join(general.ICON_DIR, "heio.collision_primitive.select")
    bl_widget = HEIO_GGT_CollisionPrimitive_Select.bl_idname
    bl_keymap = None


class HEIO_WST_CollisionPrimitive_Transform(WorkSpaceTool):
    bl_idname = "heio.wst.collision_primitive_transform"
    bl_space_type = 'VIEW_3D'
    bl_context_mode = 'OBJECT'
    bl_label = "Transform collision primitive"
    bl_description = "Selecn and transform a meshes collision primitives"
    bl_icon = os.path.join(general.ICON_DIR, "heio.collision_primitive.transform")
    bl_widget = HEIO_GGT_CollisionPrimitive_Transform.bl_idname
    bl_keymap = None


class CollisionPrimitiveWSTRegister:

    DONT_REGISTER_CLASS = True

    @classmethod
    def register(cls):
        bpy.utils.register_tool(HEIO_WST_CollisionPrimitive_Select, after={"builtin.scale_cage"}, separator=True, group=True)
        bpy.utils.register_tool(HEIO_WST_CollisionPrimitive_Transform, after={HEIO_WST_CollisionPrimitive_Select.bl_idname})

    @classmethod
    def unregister(cls):
        bpy.utils.unregister_tool(HEIO_WST_CollisionPrimitive_Select)
        bpy.utils.unregister_tool(HEIO_WST_CollisionPrimitive_Transform)