import bpy
from bpy.props import EnumProperty, BoolProperty
import bmesh

from .base import (
    HEIOBaseOperator,
    ListAdd,
    ListRemove,
    ListMove
)

from ...exceptions import HEIOUserException, HEIODevException
from ...utility import attribute_utils


class BaseMeshInfoOperator(HEIOBaseOperator):
    bl_options = {'UNDO'}

    type: EnumProperty(
        name="Type",
        items=(
            ('MESH_LAYERS', "", ""),
            ('MESH_GROUPS', "", ""),
            ('COLLISION_LAYERS', "", ""),
            ('COLLISION_TYPES', "", ""),
            ('COLLISION_FLAGS', "", ""),
            ('COLLISION_CONVEXFLAGS', "", ""),
            ('ERROR', "", "")
        ),
        default='ERROR',
        options={"HIDDEN"}
    )

    @classmethod
    def poll(cls, context):
        return (
            context.active_object is not None
            and context.active_object.type == 'MESH'
        )

    def get_list(self, context: bpy.types.Context):
        collision_info = context.active_object.data.heio_collision_mesh
        mesh_info = context.active_object.data.heio_mesh

        if self.type == 'MESH_LAYERS':
            return mesh_info.layers

        elif self.type == 'MESH_GROUPS':
            return mesh_info.groups

        elif self.type == 'COLLISION_LAYERS':
            return collision_info.layers

        elif self.type == 'COLLISION_TYPES':
            return collision_info.types

        elif self.type == 'COLLISION_FLAGS':
            return collision_info.flags

        elif self.type == 'COLLISION_CONVEXFLAGS':
            layer = collision_info.layers.active_element
            if layer is None:
                raise HEIOUserException("No active mesh collision layer!")
            return layer.convex_flags

        else:  # ERROR
            raise HEIOUserException("Invalid call!")


class HEIO_OT_MeshInfo_Initialize(BaseMeshInfoOperator):
    bl_idname = "heio.mesh_info_initialize"
    bl_label = "Initalize mesh info"
    bl_description = "Set up the mesh to use certain mesh info"

    def _execute(self, context):
        self.get_list(context).initialize()
        return {'FINISHED'}


class HEIO_OT_MeshInfo_Delete(BaseMeshInfoOperator):
    bl_idname = "heio.mesh_info_delete"
    bl_label = "Delete mesh info"
    bl_description = "Delete mesh info from the mesh"

    def _execute(self, context):
        self.get_list(context).delete()
        return {'FINISHED'}


class MeshInfoEditOperator(BaseMeshInfoOperator):

    @classmethod
    def poll(cls, context):
        return super().poll(context) and context.mode == 'EDIT_MESH'

    def _execute(self, context):
        list = self.get_list(context)

        if self.type == 'COLLISION_CONVEXFLAGS':
            raise HEIODevException("Invalid type")

        if not list.initialized:
            raise HEIOUserException("Not initialized!")

        if list.attribute_invalid:
            raise HEIOUserException("Invalid attribute!")

        self._edit(context, list)
        return {'FINISHED'}


class HEIO_OT_MeshInfo_Assign(MeshInfoEditOperator):
    bl_idname = "heio.mesh_info_assign"
    bl_label = "Assign mesh info"
    bl_description = "Assign selected polygons to the active mesh info"

    def _edit(self, context, list):
        value = list.active_index
        mesh = context.edit_object.data

        bm = bmesh.from_edit_mesh(mesh)
        layer = bm.faces.layers.int[list.attribute_name]

        if self.type == 'COLLISION_FLAGS':
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


class HEIO_OT_CollisionFlag_Remove(MeshInfoEditOperator):
    bl_idname = "heio.collision_flag_remove"
    bl_label = "Remove collision flag"
    bl_description = "Remove the active collision flag from the selected polygons"

    def _edit(self, context, list):
        if self.type != 'COLLISION_FLAGS':
            raise HEIOUserException("Invalid type!")

        flag = ~(1 << list.active_index)
        mesh = context.edit_object.data

        bm = bmesh.from_edit_mesh(mesh)
        layer = bm.faces.layers.int[list.attribute_name]

        for face in bm.faces:
            if face.select:
                face[layer] &= flag

        bmesh.update_edit_mesh(mesh)
        return {'FINISHED'}


class HEIO_OT_MeshInfo_DeSelect(MeshInfoEditOperator):
    bl_idname = "heio.mesh_info_de_select"
    bl_label = "De/Select mesh info"
    bl_description = "Select polygons with the active mesh info"

    select: BoolProperty(options={'HIDDEN'})

    def _edit(self, context, list):
        value = list.active_index
        mesh = context.edit_object.data

        bm = bmesh.from_edit_mesh(mesh)
        layer = bm.faces.layers.int[list.attribute_name]

        if self.type == 'COLLISION_FLAGS':
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


class MeshListOperator(BaseMeshInfoOperator):

    def _execute(self, context):
        list = self.get_list(context)

        if self.type != 'COLLISION_CONVEXFLAGS' and not list.initialized:
            raise HEIOUserException("Not initialized!")

        self.attribute_utility = attribute_utils.AttributeUtility(
            context,
            context.active_object.data,
            list.attribute_name
        )

        self.list_execute(context, list)
        return {'FINISHED'}


class HEIO_OT_MeshInfo_Add(MeshListOperator, ListAdd):
    bl_idname = "heio.mesh_info_add"
    bl_label = "Add mesh info"
    bl_description = "Adds a mesh info item to the active mesh"


class HEIO_OT_MeshInfo_Remove(MeshListOperator, ListRemove):
    bl_idname = "heio.mesh_info_remove"
    bl_label = "Remove mesh info"
    bl_description = "Removes the selected mesh info item from the mesh"

    def list_execute(self, context: bpy.types.Context, target_list):
        if self.type != 'COLLISION_CONVEXFLAGS':
            if context.mode == "EDIT_MESH":
                raise HEIOUserException(
                    "Cannot remove mesh info while in edit mode!")

            if self.type == 'MESH_LAYER' and target_list.active_index < 3:
                raise HEIOUserException(
                    f"The {target_list.active_element.name} layer is required!")
            elif len(target_list) <= 1:
                raise HEIOUserException(
                    "At least one mesh info item is required!")

        removed_index = super().list_execute(context, target_list)

        if self.type == 'MESH_LAYERS':
            if removed_index == 3:
                self.attribute_utility.change_int_values(removed_index, 0)

            if len(target_list) > 3:
                self.attribute_utility.decrease_int_values(removed_index)

        elif self.type == 'COLLISION_FLAGS':
            self.attribute_utility.rightshift_int_flags(removed_index, 1)

        elif self.type != 'COLLISION_CONVEXFLAGS':
            self.attribute_utility.decrease_int_values(max(removed_index, 1))


class HEIO_OT_MeshInfo_Move(MeshListOperator, ListMove):
    bl_idname = "heio.mesh_info_move"
    bl_label = "Move mesh info"
    bl_description = "Moves the selected mesh info item in the mesh"

    def list_execute(self, context, target_list):
        if self.type != 'COLLISION_CONVEXFLAGS' and context.mode == "EDIT_MESH":
            raise HEIOUserException(
                "Cannot move mesh info while in edit mode!")

        if self.type == 'MESH_LAYERS':
            if target_list.active_index < 3:
                raise HEIOUserException(
                    f"The {target_list.active_element.name} layer cannot be moved!")

            if target_list.active_index == 3 and self.direction == 'UP':
                raise HEIOUserException(
                    f"The {target_list.active_element.name} layer cannot be moved up here!")

        old_index, new_index = super().list_execute(context, target_list)

        if old_index is None:
            return

        if self.type == 'COLLISION_FLAGS':
            self.attribute_utility.swap_int_flags(
                1 << old_index, 1 << new_index)

        elif self.type != 'COLLISION_CONVEXFLAGS':
            self.attribute_utility.swap_int_values(
                old_index, new_index)


