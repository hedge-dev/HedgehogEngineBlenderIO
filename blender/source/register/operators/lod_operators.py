import bpy
import bmesh

from .base import (
    HEIOBaseOperator,
    ListAdd,
    ListRemove,
    ListMove
)


class HEIO_OT_LODInfo_Initialize(HEIOBaseOperator):
    bl_idname = "heio.lod_info_initialize"
    bl_label = "Initalize LOD info"
    bl_description = "Set up the mesh/armature to use LOD meshes"
    bl_options = {'UNDO', 'INTERNAL'}

    @classmethod
    def poll(cls, context):
        return (
            context.active_object is not None
            and ((
                context.active_object.type == 'MESH'
                and len(context.active_object.data.heio_mesh.lod_info.levels) == 0
            ) or (
                context.active_object.type == 'ARMATURE'
                and len(context.active_object.data.heio_armature.lod_info.levels) == 0
            ))
        )

    def _execute(self, context):
        obj = context.active_object

        if obj.type == 'MESH':
            lod_info = obj.data.heio_mesh.lod_info
        else:
            lod_info = obj.data.heio_armature.lod_info

        lod_info.initialize()

        return {'FINISHED'}


class HEIO_OT_LODInfo_Delete(HEIOBaseOperator):
    bl_idname = "heio.lod_info_delete"
    bl_label = "Delete LOD info"
    bl_description = "Deletes the meshes/armatures LOD info"
    bl_options = {'UNDO', 'INTERNAL'}

    @classmethod
    def poll(cls, context):
        return (
            context.active_object is not None
            and ((
                context.active_object.type == 'MESH'
                and len(context.active_object.data.heio_mesh.lod_info.levels) > 0
            ) or (
                context.active_object.type == 'ARMATURE'
                and len(context.active_object.data.heio_armature.lod_info.levels) > 0
            ))
        )

    def _execute(self, context):
        obj = context.active_object

        if obj.type == 'MESH':
            lod_info = obj.data.heio_mesh.lod_info
        else:
            lod_info = obj.data.heio_armature.lod_info

        lod_info.delete()

        return {'FINISHED'}


class LODInfoListOperator(HEIOBaseOperator):
    bl_options = {'UNDO', 'INTERNAL'}

    @classmethod
    def poll(cls, context):
        return (
            context.active_object is not None
            and ((
                context.active_object.type == 'MESH'
                and len(context.active_object.data.heio_mesh.lod_info.levels) > 0
            ) or (
                context.active_object.type == 'ARMATURE'
                and len(context.active_object.data.heio_armature.lod_info.levels) > 0
            ))
        )

    def _execute(self, context):
        obj = context.active_object

        if obj.type == 'MESH':
            lod_info = obj.data.heio_mesh.lod_info
        else:
            lod_info = obj.data.heio_armature.lod_info

        self.list_execute(context, lod_info.levels)
        return {'FINISHED'}


class HEIO_OT_LODInfo_Add(LODInfoListOperator, ListAdd):
    bl_idname = "heio.lod_info_add"
    bl_label = "Add LOD info level"
    bl_description = "Adds an LOD info level to the mesh/armature"


class HEIO_OT_LODInfo_Remove(LODInfoListOperator, ListRemove):
    bl_idname = "heio.lod_info_remove"
    bl_label = "Remove LOD info level"
    bl_description = "Removes the selected LOD info level from the mesh/armature"

    def list_execute(self, context: bpy.types.Context, target_list):

        if target_list.active_index < 1:
            self.report(
                {'ERROR'}, f"The first LOD level is required!")
            return {'CANCELLED'}

        return super().list_execute(context, target_list)


class HEIO_OT_LODInfo_Move(LODInfoListOperator, ListMove):
    bl_idname = "heio.lod_info_move"
    bl_label = "Move LOD info level"
    bl_description = "Moves the selected LOD info level in the mesh/armature"

    def list_execute(self, context, target_list):
        if target_list.active_index < 1:
            self.report(
                {'ERROR'}, f"The first LOD level cannot be moved!")
            return {'CANCELLED'}

        if target_list.active_index == 1 and self.direction == 'UP':
            self.report(
                {'ERROR'}, f"The second LOD level cannot be moved up!")
            return {'CANCELLED'}

        return super().list_execute(context, target_list)
