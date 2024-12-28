import bpy
from bpy.props import EnumProperty
import bmesh

from .base import (
    HEIOBaseOperator,
    ListAdd,
    ListRemove,
    ListMove
)

from ..property_groups.collision_mesh_properties import HEIO_CollisionMesh, BaseCollisionInfoList
from ...exceptions import UserException, HEIOException


class CollisionMeshBaseOperator(HEIOBaseOperator):
    bl_options = {'UNDO'}

    type: EnumProperty(
        name="Type",
        items=(
            ("LAYERS", "", ""),
            ("TYPES", "", ""),
            ("FLAGS", "", ""),
            ("CONVEXFLAGS", "", ""),
            ("ERROR", "", "")
        ),
        options={"HIDDEN"}
    )

    @classmethod
    def poll(cls, context):
        return (
            context.active_object is not None
            and context.active_object.type == 'MESH'
        )

    def raise_error(self):
        if self.type == 'ERROR':
            raise UserException("Invalid call!")

    def get_list(self, context: bpy.types.Context) -> BaseCollisionInfoList:
        collision_info: HEIO_CollisionMesh = context.active_object.data.heio_collision_mesh

        if self.type == 'ERROR':
            raise UserException("Invalid call!")
        elif self.type == 'LAYERS':
            return collision_info.layers
        elif self.type == 'TYPES':
            return collision_info.types
        elif self.type == 'FLAGS':
            return collision_info.flags
        else:  # CONVEXFLAGS
            layer = collision_info.layers.active_element
            if layer is None:
                raise UserException("No active mesh collision layer!")
            return layer.convex_flags


class HEIO_OT_CollisionMeshInfo_Initialize(CollisionMeshBaseOperator):
    bl_idname = "heio.collision_mesh_info_initialize"
    bl_label = "Initalize collision mesh info"
    bl_description = "Set up the mesh to use certain collision mesh info"

    def _execute(self, context):
        self.get_list(context).initialize()
        return {'FINISHED'}


class HEIO_OT_CollisionMeshInfo_Delete(CollisionMeshBaseOperator):
    bl_idname = "heio.collision_mesh_info_delete"
    bl_label = "Delete collision mesh info"
    bl_description = "Delete certain collision info from the mesh"

    def _execute(self, context):
        self.get_list(context).delete()
        return {'FINISHED'}


class CollisionMeshListOperator(CollisionMeshBaseOperator):

    def _execute(self, context):
        list = self.get_list(context)

        if self.type != 'CONVEXFLAGS' and not list.initialized:
            raise HEIOException("Not initialized!")

        self.list_execute(context, list)
        return {'FINISHED'}


class HEIO_OT_CollisionMeshInfo_Add(CollisionMeshListOperator, ListAdd):
    bl_idname = "heio.collision_mesh_info_add"
    bl_label = "Add collision mesh info"
    bl_description = "Adds a collision mesh info item to the active mesh"


class HEIO_OT_CollisionMeshInfo_Remove(CollisionMeshListOperator, ListRemove):
    bl_idname = "heio.collision_mesh_info_remove"
    bl_label = "Remove collision mesh info"
    bl_description = "Removes the selected collision mesh info item from the mesh"

    def list_execute(self, context: bpy.types.Context, target_list):
        if context.mode == "EDIT_MESH":
            self.report(
                {'ERROR'}, f"Cannot remove collision info during edit mode!")
            return {'CANCELLED'}

        if self.type != 'CONVEXFLAGS' and len(target_list) <= 1:
            self.report(
                {'ERROR'}, f"At least one collision info item is required!")
            return {'CANCELLED'}

        return super().list_execute(context, target_list)


class HEIO_OT_CollisionMeshInfo_Move(CollisionMeshListOperator, ListMove):
    bl_idname = "heio.collision_mesh_info_move"
    bl_label = "Move collision mesh info"
    bl_description = "Moves the selected collision mesh info item in the mesh"

    def list_execute(self, context, target_list):
        if self.type != 'LAYERS':
            raise HEIOException("Cannot move this type of collision info!")

        if context.mode == "EDIT_MESH":
            raise HEIOException("Cannot move layers during edit mode!")

        return super().list_execute(context, target_list)
