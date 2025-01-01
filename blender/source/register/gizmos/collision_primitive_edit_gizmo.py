import bpy
from bpy.props import FloatVectorProperty
from mathutils import Matrix, Vector

from . import collision_primitive_select_gizmo
from ..operators.base import HEIOBaseModalOperator


MANUAL_SELECT_MODE = False


class HEIO_GGT_CollisionPrimitive_Edit(bpy.types.GizmoGroup):
    bl_idname = "heio.collision_primitive_edit_gizmogroup"
    bl_label = "HEIO Collision Primitive edit"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'WINDOW'
    bl_options = {'3D', 'PERSISTENT', 'SHOW_MODAL_ALL'}

    current_object: bpy.types.Object | None
    move_gizmo: bpy.types.Gizmo

    @classmethod
    def poll(cls, context):
        obj = context.object
        return (
            obj is not None
            and obj.type == 'MESH'
            and len(obj.data.heio_collision_mesh.primitives) > 0
            and collision_primitive_select_gizmo.MANUAL_SELECT_MODE
        )

    def setup(self, context):

        if hasattr(self, "current_primitive_index"):
            return

        self.current_object = None

        self.move_gizmo = self.gizmos.new("GIZMO_GT_move_3d")

        self.move_gizmo.target_set_operator(
            HEIO_OT_CollisionPrimitive_GizmoMove.bl_idname)
        self.move_gizmo.draw_options = {"FILL", "ALIGN_VIEW"}

        self.move_gizmo.use_draw_value = True

        self.move_gizmo.color = 0.8, 0.8, 0.8
        self.move_gizmo.alpha = 0.8

        self.move_gizmo.color_highlight = 1.0, 1.0, 1.0
        self.move_gizmo.alpha_highlight = 1.0

        self.move_gizmo.scale_basis = 0.2

    def draw_prepare(self, context):
        obj = context.object
        primitive = obj.data.heio_collision_mesh.primitives.active_element

        self.current_object = obj
        matrix = obj.matrix_world.normalized() @ Matrix.LocRotScale(primitive.position,
                                                                    primitive.rotation, None).normalized()
        self.move_gizmo.matrix_basis = matrix


class HEIO_OT_CollisionPrimitive_GizmoMove(HEIOBaseModalOperator):
    bl_idname = "heio.collision_primitive_gizmo_move"
    bl_label = "Move collision primitive"
    bl_description = "Move the collision primitive"
    bl_options = {'UNDO', 'INTERNAL'}

    offset: FloatVectorProperty(
        name="Offset",
        size=3,
    )

    def _execute(self, context):
        context.object.data.heio_collision_mesh.primitives.active_element.position = self._initial_location + \
            Vector(self.offset)

    def _modal(self, context: bpy.types.Context, event: bpy.types.Event):
        if event.type == 'MOUSEMOVE':
            delta_x = (event.mouse_x - self._initial_mouse.x) / \
                context.region.width * 2
            delta_y = (event.mouse_y - self._initial_mouse.y) / \
                context.region.height * 2
            delta = Vector((delta_x, delta_y, 0, 0))

            matrix = context.region_data.perspective_matrix @ context.object.matrix_world.normalized()

            persp_pos = matrix @ self._initial_location.to_4d()
            persp_pos += delta * persp_pos.w

            new_pos = matrix.inverted() @ persp_pos
            new_pos = new_pos / new_pos.w

            self.offset = new_pos.to_3d() - self._initial_location

            self._execute(context)
            context.area.header_text_set(
                "Offset {:.4f} {:.4f} {:.4f}".format(*self.offset))

        elif event.type == 'LEFTMOUSE':
            context.area.header_text_set(None)
            return {'FINISHED'}

        elif event.type in {'RIGHTMOUSE', 'ESC'}:
            context.object.data.heio_collision_mesh.primitives.active_element.position = self._initial_location
            context.area.header_text_set(None)
            return {'CANCELLED'}

        return {'RUNNING_MODAL'}

    def _invoke(self, context, event):
        self._initial_mouse = Vector((event.mouse_x, event.mouse_y))
        self._initial_location = Vector(
            context.object.data.heio_collision_mesh.primitives.active_element.position)
        context.window_manager.modal_handler_add(self)
        return {'RUNNING_MODAL'}
