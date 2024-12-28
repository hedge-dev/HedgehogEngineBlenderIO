import bpy
import bmesh

from .base import (
    HEIOBaseOperator,
    ListAdd,
    ListRemove,
    ListMove
)


class HEIO_OT_MeshLayer_Initialize(HEIOBaseOperator):
    bl_idname = "heio.mesh_layers_initialize"
    bl_label = "Initalize mesh layers"
    bl_description = "Set up the mesh to use per-polygon mesh layers"
    bl_options = {'UNDO'}

    @classmethod
    def poll(cls, context):
        return (
            context.active_object is not None
            and context.active_object.type == 'MESH'
            and (
                len(context.active_object.data.heio_mesh.layers) == 0
                or "Layer" not in context.active_object.data.attributes
            )
        )

    def _execute(self, context):
        context.active_object.data.heio_mesh.initialize_layers()
        return {'FINISHED'}


class HEIO_OT_MeshLayer_Delete(HEIOBaseOperator):
    bl_idname = "heio.mesh_layers_delete"
    bl_label = "Delete mesh layers"
    bl_description = "Deletes the mesh layers and layer attribute"
    bl_options = {'UNDO'}

    @classmethod
    def poll(cls, context):
        if (
            context.mode == 'EDIT_MESH'
            or context.active_object is None
            or context.active_object.type != 'MESH'
            or (len(context.active_object.data.heio_mesh.layers) == 0
                and "Layer" not in context.active_object.data.attributes)
        ):
            return False

        attribute = context.active_object.data.attributes["Layer"]
        return len(context.active_object.data.heio_mesh.layers) > 0 or (attribute.domain == 'FACE' and attribute.data_type == 'INT')

    def _execute(self, context):
        mesh = context.active_object.data
        mesh.heio_mesh.layers.clear()

        if "Layer" in mesh.attributes:
            attribute = mesh.attributes["Layer"]

            if attribute.domain == 'FACE' and attribute.data_type == 'INT':
                mesh.attributes.remove(attribute)

        return {'FINISHED'}


class MeshLayerEditOperator(HEIOBaseOperator):
    bl_options = {'UNDO'}

    @classmethod
    def poll(cls, context):
        if (
            context.mode != "EDIT_MESH"
            or len(context.active_object.data.heio_mesh.layers) == 0
            or "Layer" not in context.active_object.data.attributes
        ):
            return False

        attribute = context.active_object.data.attributes["Layer"]
        return attribute.domain == 'FACE' and attribute.data_type == 'INT'


class HEIO_OT_MeshLayer_Assign(MeshLayerEditOperator):
    bl_idname = "heio.mesh_layer_assign"
    bl_label = "Assign"
    bl_description = "Assign the active layer to selected polygons"

    def _execute(self, context):
        active_index = bpy.context.edit_object.data.heio_mesh.layers.active_index
        mesh = bpy.context.edit_object.data

        bm = bmesh.from_edit_mesh(mesh)
        layer = bm.faces.layers.int["Layer"]

        for face in bm.faces:
            if face.select:
                face[layer] = active_index

        bmesh.update_edit_mesh(mesh)
        return {'FINISHED'}


class HEIO_OT_MeshLayer_Select(MeshLayerEditOperator):
    bl_idname = "heio.mesh_layer_select"
    bl_label = "Select"
    bl_description = "Select polygons with the active layer"

    def _execute(self, context):
        active_index = bpy.context.edit_object.data.heio_mesh.layers.active_index
        mesh = bpy.context.edit_object.data

        bm = bmesh.from_edit_mesh(mesh)
        layer = bm.faces.layers.int["Layer"]

        for face in bm.faces:
            if face[layer] == active_index:
                face.select = True

        bmesh.update_edit_mesh(mesh)
        return {'FINISHED'}


class HEIO_OT_MeshLayer_Deselect(MeshLayerEditOperator):
    bl_idname = "heio.mesh_layer_deselect"
    bl_label = "Deselect"
    bl_description = "Deselect polygons with the active layer"

    def _execute(self, context):
        active_index = bpy.context.edit_object.data.heio_mesh.layers.active_index
        mesh = bpy.context.edit_object.data

        bm = bmesh.from_edit_mesh(mesh)
        layer = bm.faces.layers.int["Layer"]

        for face in bm.faces:
            if face[layer] == active_index:
                face.select = False

        bmesh.update_edit_mesh(mesh)
        return {'FINISHED'}


class MeshLayerListOperator(HEIOBaseOperator):
    bl_options = {'UNDO'}

    @classmethod
    def poll(cls, context):
        return (
            context.active_object is not None
            and context.active_object.type == 'MESH'
            and len(context.active_object.data.heio_mesh.layers) > 0
        )

    def _execute(self, context):
        self.list_execute(
            context, context.active_object.data.heio_mesh.layers)
        return {'FINISHED'}


class HEIO_OT_MeshLayer_Add(MeshLayerListOperator, ListAdd):
    bl_idname = "heio.mesh_layer_add"
    bl_label = "Add mesh layer"
    bl_description = "Adds a layer to the active mesh"


class HEIO_OT_MeshLayer_Remove(MeshLayerListOperator, ListRemove):
    bl_idname = "heio.mesh_layer_remove"
    bl_label = "Remove mesh layer"
    bl_description = "Removes the selected layer from the mesh"

    def list_execute(self, context: bpy.types.Context, target_list):
        if context.mode == "EDIT_MESH":
            self.report({'ERROR'}, f"Cannot remove layers during edit mode!")
            return {'CANCELLED'}

        if target_list.active_index < 3:
            self.report(
                {'ERROR'}, f"The {target_list.active_element.name} layer is required!")
            return {'CANCELLED'}

        return super().list_execute(context, target_list)


class HEIO_OT_MeshLayer_Move(MeshLayerListOperator, ListMove):
    bl_idname = "heio.mesh_layer_move"
    bl_label = "Move mesh layer"
    bl_description = "Moves the selected layer slot in the mesh"

    def list_execute(self, context, target_list):
        if context.mode == "EDIT_MESH":
            self.report({'ERROR'}, f"Cannot move layers during edit mode!")
            return {'CANCELLED'}

        if target_list.active_index < 3:
            self.report(
                {'ERROR'}, f"The {target_list.active_element.name} layer cannot be moved!")
            return {'CANCELLED'}

        if target_list.active_index == 3 and self.direction == 'UP':
            self.report(
                {'ERROR'}, f"The {target_list.active_element.name} layer cannot be moved up here!")
            return {'CANCELLED'}

        return super().list_execute(context, target_list)
