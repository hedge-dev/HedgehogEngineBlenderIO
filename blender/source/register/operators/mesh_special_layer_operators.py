from .base import (
    HEIOBaseOperator,
    ListAdd,
    ListRemove,
    ListMove
)


class MeshSpecialLayerOperator(HEIOBaseOperator):
    bl_options = {'UNDO'}

    def _execute(self, context):
        self.list_execute(
            context, context.active_object.data.heio_mesh.special_layers)
        return {'FINISHED'}

    @classmethod
    def poll(cls, context):
        return (
            context.active_object is not None
            and context.active_object.type == 'MESH'
        )


class HEIO_OT_MeshSpecialLayer_Add(MeshSpecialLayerOperator, ListAdd):
    bl_idname = "heio.mesh_special_layer_add"
    bl_label = "Add mesh special layer"
    bl_description = "Adds a special layer to the active mesh"


class HEIO_OT_MeshSpecialLayer_Remove(MeshSpecialLayerOperator, ListRemove):
    bl_idname = "heio.mesh_special_layer_remove"
    bl_label = "Remove mesh special layer"
    bl_description = "Removes the selected special layer from the its mesh"


class HEIO_OT_MeshSpecialLayer_Move(MeshSpecialLayerOperator, ListMove):
    bl_idname = "heio.mesh_special_layer_move"
    bl_label = "Move mesh special layer"
    bl_description = "Moves the selected special layer slot in the mesh"
