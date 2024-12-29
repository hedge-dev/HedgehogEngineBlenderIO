import bpy
from bpy.props import EnumProperty, BoolProperty
import bmesh

from .base import (
    HEIOBaseOperator,
    ListAdd,
    ListRemove,
    ListMove
)

from ..property_groups.collision_mesh_properties import HEIO_CollisionMesh, BaseCollisionInfoList
from ...exceptions import HEIOUserException, HEIODevException
from ...utility import attribute_utils


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

    def get_list(self, context: bpy.types.Context) -> BaseCollisionInfoList:
        collision_info: HEIO_CollisionMesh = context.active_object.data.heio_collision_mesh

        if self.type == 'ERROR':
            raise HEIOUserException("Invalid call!")
        elif self.type == 'LAYERS':
            return collision_info.layers
        elif self.type == 'TYPES':
            return collision_info.types
        elif self.type == 'FLAGS':
            return collision_info.flags
        else:  # CONVEXFLAGS
            layer = collision_info.layers.active_element
            if layer is None:
                raise HEIOUserException("No active mesh collision layer!")
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


class CollisionMeshEditOperator(CollisionMeshBaseOperator):

    def _execute(self, context):
        list = self.get_list(context)

        if self.type == 'CONVEXFLAGS':
            raise HEIODevException("Invalid type")

        if not list.initialized:
            raise HEIODevException("Not initialized!")

        if list.attribute_invalid:
            raise HEIODevException("Invalid attribute!")

        self.edit(context, list)
        return {'FINISHED'}


class HEIO_OT_CollisionMeshInfo_Assign(CollisionMeshEditOperator):
    bl_idname = "heio.collision_mesh_info_assign"
    bl_label = "Assign collision mesh info"
    bl_description = "Assign the active collision info to selected polygons"

    def edit(self, context, list):
        value = list.active_index
        mesh = bpy.context.edit_object.data

        bm = bmesh.from_edit_mesh(mesh)
        layer = bm.faces.layers.int[list.attribute_name]

        if self.type == 'FLAGS':
            flag = 1 << value

            for face in bm.faces:
                if face.select:
                    face[layer] |= flag

        else:
            for face in bm.faces:
                if face.select:
                    face[layer] = value

        bmesh.update_edit_mesh(mesh)
        return {'FINISHED'}


class HEIO_OT_CollisionFlag_Remove(CollisionMeshEditOperator):
    bl_idname = "heio.collision_flag_remove"
    bl_label = "Remove collision flag"
    bl_description = "Remove the active collision flag from the selected polygons"

    def edit(self, context, list):
        if self.type != 'FLAGS':
            raise HEIODevException("Invalid type!")

        flag = ~(1 << list.active_index)
        mesh = context.edit_object.data

        bm = bmesh.from_edit_mesh(mesh)
        layer = bm.faces.layers.int[list.attribute_name]

        for face in bm.faces:
            if face.select:
                face[layer] &= flag

        bmesh.update_edit_mesh(mesh)
        return {'FINISHED'}


class HEIO_OT_CollisionMeshInfo_DeSelect(CollisionMeshEditOperator):
    bl_idname = "heio.collision_mesh_info_de_select"
    bl_label = "De/Select collision mesh info"
    bl_description = "Select polygons with the active layer"

    select: BoolProperty(options={'HIDDEN'})

    def edit(self, context, list):
        value = list.active_index
        mesh = context.edit_object.data

        bm = bmesh.from_edit_mesh(mesh)
        layer = bm.faces.layers.int[list.attribute_name]

        if self.type == 'FLAGS':
            flag = 1 << value

            for face in bm.faces:
                if (face[layer] & flag) != 0:
                    face.select = self.select

        else:
            for face in bm.faces:
                if face[layer] == value:
                    face.select = self.select

        bmesh.update_edit_mesh(mesh)
        return {'FINISHED'}


class CollisionMeshListOperator(CollisionMeshBaseOperator):

    def _execute(self, context):
        list = self.get_list(context)

        if self.type != 'CONVEXFLAGS' and not list.initialized:
            raise HEIOUserException("Not initialized!")

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
        if self.type != 'CONVEXFLAGS':
            if context.mode == "EDIT_MESH":
                raise HEIOUserException("Cannot remove collision info during edit mode!")

            if self.type != 'CONVEXFLAGS' and len(target_list) <= 1:
                raise HEIOUserException("At least one collision info item is required!")

        removed_index = super().list_execute(context, target_list)

        if self.type == 'FLAGS':
            attribute_utils.rightshift_int_flags(
                context,
                context.active_object.data,
                target_list.attribute_name,
                removed_index,
                1
            )

        elif self.type != 'CONVEXFLAGS':
            attribute_utils.decrease_int_values(
                context,
                context.active_object.data,
                target_list.attribute_name,
                max(removed_index, 1)
            )

class HEIO_OT_CollisionMeshInfo_Move(CollisionMeshListOperator, ListMove):
    bl_idname = "heio.collision_mesh_info_move"
    bl_label = "Move collision mesh info"
    bl_description = "Moves the selected collision mesh info item in the mesh"

    def list_execute(self, context, target_list):
        if self.type != 'CONVEXFLAGS' and context.mode == "EDIT_MESH":
            raise HEIOUserException("Cannot move layers during edit mode!")

        old_index, new_index = super().list_execute(context, target_list)

        if old_index is None:
            return

        if self.type == 'FLAGS':
            attribute_utils.swap_int_flags(
                context,
                context.active_object.data,
                target_list.attribute_name,
                1 << old_index,
                1 << new_index
            )
        elif self.type != 'CONVEXFLAGS':
            attribute_utils.swap_int_values(
                context,
                context.active_object.data,
                target_list.attribute_name,
                old_index,
                new_index
            )
