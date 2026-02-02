import bpy
from mathutils import Matrix
from ...operators.base import HEIOBaseOperator
from ...property_groups.mesh_properties import MESH_DATA_TYPES

class HEIO_OT_View3D_SnapCursorToActiveCollisionPrimitive(HEIOBaseOperator):
    bl_idname = "heio.snap_cursor_to_active_collision_primitive"
    bl_label = 'Cursor to active collision primitive'
    bl_options = set()

    def _execute(self, context):
        if context.object is None or context.object.type not in MESH_DATA_TYPES:
            return {'FINISHED'}

        primitive = context.object.data.heio_mesh.collision_primitives.active_element
        if primitive is None:
            return {'FINISHED'}

        context.scene.cursor.matrix = (
            context.object.matrix_world.normalized()
            @ Matrix.LocRotScale(primitive.position, primitive.rotation, None)
        )

        return {'FINISHED'}


class HEIO_OT_View3D_SnapActiveCollisionPrimitiveToCursor(HEIOBaseOperator):
    bl_idname = "heio.snap_active_collision_primitive_to_cursor"
    bl_label = 'Active collision primitive to cursor'
    bl_options = set()

    def _execute(self, context):
        if context.object is None or context.object.type not in MESH_DATA_TYPES:
            return {'FINISHED'}

        primitive = context.object.data.heio_mesh.collision_primitives.active_element
        if primitive is None:
            return {'FINISHED'}

        primitive.position = (
            context.object.matrix_world.normalized().inverted()
            @ context.scene.cursor.location
        )

        return {'FINISHED'}


class CPTMenuAppends:

    DONT_REGISTER_CLASS = True

    @staticmethod
    def snap_menu_func(self, context):
        self.layout.separator(type='LINE')
        self.layout.operator(
            HEIO_OT_View3D_SnapCursorToActiveCollisionPrimitive.bl_idname)
        self.layout.operator(
            HEIO_OT_View3D_SnapActiveCollisionPrimitiveToCursor.bl_idname)

    @classmethod
    def register(cls):
        bpy.types.VIEW3D_MT_snap.append(CPTMenuAppends.snap_menu_func)

    @classmethod
    def unregister(cls):
        bpy.types.VIEW3D_MT_snap.remove(CPTMenuAppends.snap_menu_func)
