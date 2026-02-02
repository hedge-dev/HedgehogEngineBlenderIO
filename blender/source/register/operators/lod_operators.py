import bpy

from ..property_groups.mesh_properties import MESH_DATA_TYPES

from .base import (
    HEIOBaseOperator,
    ListAdd,
    ListRemove,
    ListMove
)

class BaseLODInfoOperator(HEIOBaseOperator):
    bl_options = {'UNDO', 'INTERNAL'}

    @staticmethod
    def get_lod_info(context: bpy.types.Context):
        obj = context.active_object
        if obj is None:
            return None

        if obj.type in MESH_DATA_TYPES:
            return obj.data.heio_mesh.lod_info
        elif obj.type == 'ARMATURE':
            return obj.data.heio_armature.lod_info

        return None

class HEIO_OT_LODInfo_Initialize(BaseLODInfoOperator):
    bl_idname = "heio.lod_info_initialize"
    bl_label = "Initalize LoD info"
    bl_description = "Set up the mesh/armature to use LoD meshes"

    @classmethod
    def poll(cls, context):
        lod_info = cls.get_lod_info(context)
        return lod_info is not None and len(lod_info.levels) == 0

    def _execute(self, context):
        self.get_lod_info(context).initialize()
        return {'FINISHED'}


class HEIO_OT_LODInfo_Delete(BaseLODInfoOperator):
    bl_idname = "heio.lod_info_delete"
    bl_label = "Delete LoD info"
    bl_description = "Deletes the meshes/armatures LoD info"
    bl_options = {'UNDO', 'INTERNAL'}

    @classmethod
    def poll(cls, context):
        lod_info = cls.get_lod_info(context)
        return lod_info is not None and len(lod_info.levels) > 0

    def _execute(self, context):
        self.get_lod_info(context).delete()
        return {'FINISHED'}


class LODInfoListOperator(BaseLODInfoOperator):
    bl_options = {'UNDO', 'INTERNAL'}

    @classmethod
    def poll(cls, context):
        lod_info = cls.get_lod_info(context)
        return lod_info is not None and len(lod_info.levels) > 0

    def _execute(self, context):
        lod_info = self.get_lod_info(context)
        self.list_execute(context, lod_info.levels)
        return {'FINISHED'}


class HEIO_OT_LODInfo_Add(LODInfoListOperator, ListAdd):
    bl_idname = "heio.lod_info_add"
    bl_label = "Add LoD info level"
    bl_description = "Adds an LoD info level to the mesh/armature"


class HEIO_OT_LODInfo_Remove(LODInfoListOperator, ListRemove):
    bl_idname = "heio.lod_info_remove"
    bl_label = "Remove LoD info level"
    bl_description = "Removes the selected LoD info level from the mesh/armature"

    def list_execute(self, context: bpy.types.Context, target_list):

        if target_list.active_index < 1:
            self.report(
                {'ERROR'}, f"The first LoD level is required!")
            return {'CANCELLED'}

        return super().list_execute(context, target_list)


class HEIO_OT_LODInfo_Move(LODInfoListOperator, ListMove):
    bl_idname = "heio.lod_info_move"
    bl_label = "Move LoD info level"
    bl_description = "Moves the selected LoD info level in the mesh/armature"

    def list_execute(self, context, target_list):
        if target_list.active_index < 1:
            self.report(
                {'ERROR'}, f"The first LoD level cannot be moved!")
            return {'CANCELLED'}

        if target_list.active_index == 1 and self.direction == 'UP':
            self.report(
                {'ERROR'}, f"The second LoD level cannot be moved up!")
            return {'CANCELLED'}

        return super().list_execute(context, target_list)
