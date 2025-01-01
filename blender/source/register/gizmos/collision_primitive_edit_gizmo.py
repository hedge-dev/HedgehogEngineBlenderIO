import bpy
from bpy.props import FloatVectorProperty
from mathutils import Matrix, Vector
import math

from . import collision_primitive_select_gizmo
from ..operators.base import HEIOBaseModalOperator


MANUAL_SELECT_MODE = False


class HEIO_GGT_CollisionPrimitive_Edit(bpy.types.GizmoGroup):
    bl_idname = "heio.collision_primitive_edit_gizmogroup"
    bl_label = "HEIO Collision Primitive edit"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'WINDOW'
    bl_options = {'3D', 'PERSISTENT'}

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
    bl_options = {'REGISTER', 'UNDO', 'INTERNAL'}

    offset: FloatVectorProperty(
        name="Offset",
        size=3,
    )

    def _get_primitive(self, context):
        return context.object.data.heio_collision_mesh.primitives.active_element

    def _execute(self, context):
        primitive = self._get_primitive(context)
        position = self._initial_location + Vector(self.offset)

        if self.snap:
            matrix = context.object.matrix_world.normalized()
            world_pos = matrix @ position

            snap_level = 0
            if not context.region_data.is_perspective and context.region_data.is_orthographic_side_view:
                snap_level = -int(math.floor(math.log10(context.region_data.view_distance / 18.8)))

            world_pos.x = round(world_pos.x, snap_level)
            world_pos.y = round(world_pos.y, snap_level)
            world_pos.z = round(world_pos.z, snap_level)

            position = matrix.inverted() @ world_pos

        primitive.position = position

    def _modal(self, context: bpy.types.Context, event: bpy.types.Event):
        if event.type == 'MOUSEMOVE':
            self.snap = event.ctrl

            delta_x = ((event.mouse_x - self._previous_mouse.x) /
                       context.region.width * 2)
            delta_y = ((event.mouse_y - self._previous_mouse.y) /
                       context.region.height * 2)
            delta = Vector((delta_x, delta_y, 0, 0))

            if event.shift:
                delta *= 0.1

            matrix = context.region_data.perspective_matrix @ context.object.matrix_world.normalized()

            persp_pos = matrix @ (self._initial_location +
                                  Vector(self.offset)).to_4d()
            persp_pos += delta * persp_pos.w

            new_pos = matrix.inverted() @ persp_pos
            new_pos = new_pos / new_pos.w

            self.offset = new_pos.to_3d() - self._initial_location

            self._execute(context)

            self._previous_mouse = Vector((event.mouse_x, event.mouse_y))
            context.area.header_text_set(
                "Offset {:.4f} {:.4f} {:.4f}".format(*self.offset))

        elif event.type == 'LEFTMOUSE':
            context.area.header_text_set(None)
            context.workspace.status_text_set(None)
            return {'FINISHED'}

        elif event.type in {'RIGHTMOUSE', 'ESC'}:
            self._get_primitive(context).position = self._initial_location
            context.area.header_text_set(None)
            context.workspace.status_text_set(None)
            return {'CANCELLED'}

        return {'RUNNING_MODAL'}

    def _invoke(self, context, event):
        self.offset = (0, 0, 0)
        self.snap = False

        self._previous_mouse = Vector((event.mouse_x, event.mouse_y))
        self._initial_location = Vector(self._get_primitive(context).position)

        context.window_manager.modal_handler_add(self)
        context.workspace.status_text_set(
            "[ESC]: Cancel   |   [Shift]: Precision Mode   |   [Ctrl]: Snap")

        return {'RUNNING_MODAL'}
