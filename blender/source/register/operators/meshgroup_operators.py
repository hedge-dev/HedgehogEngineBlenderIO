import bpy
import bmesh
from bpy.props import BoolProperty

from .base import (
    HEIOBaseOperator,
    ListAdd,
    ListRemove,
    ListMove
)

from ...utility import attribute_utils


class HEIO_OT_Meshgroup_Initialize(HEIOBaseOperator):
    bl_idname = "heio.meshgroups_initialize"
    bl_label = "Initalize meshgroups"
    bl_description = "Set up the mesh to use meshgroups"
    bl_options = {'UNDO'}

    @classmethod
    def poll(cls, context):
        return (
            context.active_object is not None
            and context.active_object.type == 'MESH'
            and (
                len(context.active_object.data.heio_mesh.meshgroups) == 0
                or "Meshgroup" not in context.active_object.data.attributes
            )
        )

    def _execute(self, context):
        context.active_object.data.heio_mesh.initialize_meshgroups()
        return {'FINISHED'}

class HEIO_OT_Meshgroup_Delete(HEIOBaseOperator):
    bl_idname = "heio.meshgroup_delete"
    bl_label = "Delete meshgroups"
    bl_description = "Deletes the meshgroups and meshgroup attribute"
    bl_options = {'UNDO'}

    @classmethod
    def poll(cls, context):
        if (
            context.mode == 'EDIT_MESH'
            or context.active_object is None
            or context.active_object.type != 'MESH'
            or (len(context.active_object.data.heio_mesh.meshgroups) == 0
            and "Meshgroup" not in context.active_object.data.attributes)
        ):
            return False

        attribute = context.active_object.data.attributes["Meshgroup"]
        return len(context.active_object.data.heio_mesh.meshgroups) > 0 or (attribute.domain == 'FACE' and attribute.data_type == 'INT')

    def _execute(self, context):
        mesh = context.active_object.data
        mesh.heio_mesh.meshgroups.clear()

        if "Meshgroup" in mesh.attributes:
            attribute = mesh.attributes["Meshgroup"]

            if attribute.domain == 'FACE' and attribute.data_type == 'INT':
                mesh.attributes.remove(attribute)

        return {'FINISHED'}

class MeshgroupEditOperator(HEIOBaseOperator):
    bl_options = {'UNDO'}

    @classmethod
    def poll(cls, context):
        if (
            context.mode != "EDIT_MESH"
            or len(context.active_object.data.heio_mesh.meshgroups) == 0
            or "Meshgroup" not in context.active_object.data.attributes
        ):
            return False

        attribute = context.active_object.data.attributes["Meshgroup"]
        return attribute.domain == 'FACE' and attribute.data_type == 'INT'


class HEIO_OT_Meshgroup_Assign(MeshgroupEditOperator):
    bl_idname = "heio.meshgroup_assign"
    bl_label = "Assign mesh group"
    bl_description = "Assign the activegroup to selected polygons"

    def _execute(self, context):
        active_index = bpy.context.edit_object.data.heio_mesh.meshgroups.active_index
        mesh = bpy.context.edit_object.data

        bm = bmesh.from_edit_mesh(mesh)
        meshgroup = bm.faces.layers.int["Meshgroup"]

        for face in bm.faces:
            if face.select:
                face[meshgroup] = active_index

        bmesh.update_edit_mesh(mesh)
        return {'FINISHED'}


class HEIO_OT_Meshgroup_DeSelect(MeshgroupEditOperator):
    bl_idname = "heio.meshgroup_de_select"
    bl_label = "De/Select mesh group"
    bl_description = "Select polygons with the active meshgroup"

    select: BoolProperty(options={'HIDDEN'})

    def _execute(self, context):
        active_index = bpy.context.edit_object.data.heio_mesh.meshgroups.active_index
        mesh = bpy.context.edit_object.data

        bm = bmesh.from_edit_mesh(mesh)
        meshgroup = bm.faces.layers.int["Meshgroup"]

        for face in bm.faces:
            if face[meshgroup] == active_index:
                face.select = self.select

        bmesh.update_edit_mesh(mesh)
        return {'FINISHED'}


class MeshgroupListOperator(HEIOBaseOperator):
    bl_options = {'UNDO'}

    @classmethod
    def poll(cls, context):
        return (
            context.active_object is not None
            and context.active_object.type == 'MESH'
            and len(context.active_object.data.heio_mesh.meshgroups) > 0
        )

    def _execute(self, context):
        self.list_execute(
            context, context.active_object.data.heio_mesh.meshgroups)
        return {'FINISHED'}


class HEIO_OT_Meshgroup_Add(MeshgroupListOperator, ListAdd):
    bl_idname = "heio.meshgroup_add"
    bl_label = "Add meshgroup"
    bl_description = "Adds a meshgroup to the active mesh"


class HEIO_OT_Meshgroup_Remove(MeshgroupListOperator, ListRemove):
    bl_idname = "heio.meshgroup_remove"
    bl_label = "Remove meshgroup"
    bl_description = "Removes the selected meshgroup from the its mesh"

    def list_execute(self, context: bpy.types.Context, target_list):
        if context.mode == "EDIT_MESH":
            self.report({'ERROR'}, f"Cannot remove meshgroups during edit mode!")
            return {'CANCELLED'}

        if len(target_list) <= 1:
            self.report(
                {'ERROR'}, f"At least one meshgroup has to exist!")
            return {'CANCELLED'}

        removed_index = super().list_execute(context, target_list)

        attribute_utils.decrease_int_values(
            context,
            context.active_object.data,
            "Meshgroup",
            max(removed_index, 1),
        )


class HEIO_OT_Meshgroup_Move(MeshgroupListOperator, ListMove):
    bl_idname = "heio.meshgroup_move"
    bl_label = "Move meshgroup"
    bl_description = "Moves the selected meshgroup slot in the mesh"

    def list_execute(self, context, target_list):
        if context.mode == "EDIT_MESH":
            self.report({'ERROR'}, f"Cannot move meshgroups during edit mode!")
            return {'CANCELLED'}

        old_index, new_index = super().list_execute(context, target_list)

        if old_index is not None:
            attribute_utils.swap_int_values(
                context,
                context.active_object.data,
                "Meshgroup",
                old_index,
                new_index
            )
