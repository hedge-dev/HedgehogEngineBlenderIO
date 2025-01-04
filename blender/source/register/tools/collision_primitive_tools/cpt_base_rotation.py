import bpy
from bpy.props import FloatProperty
from mathutils import Matrix, Vector, Quaternion
import math

from ...operators.base import HEIOBaseModalOperator


def get_mouse_dir(context: bpy.types.Context, event: bpy.types.Event, world_matrix, prev = False):
    if prev:
        mouse_x = event.mouse_prev_x - context.region.x
        mouse_y = event.mouse_prev_y - context.region.y
    else:
        mouse_x = event.mouse_x - context.region.x
        mouse_y = event.mouse_y - context.region.y

    pos = (context.region_data.perspective_matrix @
           world_matrix) @ Vector((0, 0, 0, 1))
    pos = pos / pos.w

    pos_x = (pos.x * 0.5 + 0.5) * context.region.width
    pos_y = (pos.y * 0.5 + 0.5) * context.region.height

    return Vector((mouse_x - pos_x, mouse_y - pos_y)).normalized()


class BaseCollisionPrimitiveRotateOperator(HEIOBaseModalOperator):
    bl_options = {'REGISTER', 'UNDO', 'INTERNAL'}

    rotation: FloatProperty(
        name="Rotation",
        subtype='ANGLE'
    )

    _applied_rotation: float
    _snap: bool
    _precision: bool
    _flip_angle: bool

    def _get_primitive(self, context):
        return context.object.data.heio_collision_mesh.primitives.active_element

    def _get_mouse_dir(self, context: bpy.types.Context, event: bpy.types.Event, prev):

        prim_pos = self._get_primitive(context).position
        world_matrix = context.object.matrix_world @ Matrix.Translation(
            prim_pos)
        return get_mouse_dir(context, event, world_matrix, prev)

    def _update_header_text(self, context):
        context.area.header_text_set(f"Rotation {math.degrees(self._applied_rotation):.4f}°")

    def _execute(self, context):
        rotation = self.rotation

        if self._snap:
            if self._precision:
                fac = math.radians(1)
            else:
                fac = math.radians(5)

            rotation = round(rotation / fac) * fac

        self._applied_rotation = rotation
        self._apply_rotation(context, rotation)
        return {'FINISHED'}

    def _modal(self, context: bpy.types.Context, event: bpy.types.Event):
        if event.type == 'MOUSEMOVE':
            self._snap = event.ctrl
            self._precision = event.shift

            prev_mouse_dir = self._get_mouse_dir(context, event, True)
            mouse_dir = self._get_mouse_dir(context, event, False)
            angle = prev_mouse_dir.angle_signed(mouse_dir)

            if self._flip_angle:
                angle = -angle

            if self._precision:
                angle /= 30

            self.rotation += angle

            self._execute(context)
            self._update_header_text(context)
            context.region.tag_redraw()

        elif event.type in {'LEFT_CTRL', 'RIGHT_CTRL', 'CTRL'}:
            self._snap = event.ctrl
            self._execute(context)
            self._update_header_text(context)
            context.region.tag_redraw()

        elif event.type in {'LEFT_SHIFT', 'RIGHT_SHIFT', 'SHIFT'}:
            self._precision = event.shift
            self._execute(context)
            self._update_header_text(context)
            context.region.tag_redraw()

        elif event.type == 'LEFTMOUSE':
            context.area.header_text_set(None)
            context.workspace.status_text_set(None)
            return {'FINISHED'}

        elif event.type in {'RIGHTMOUSE', 'ESC'}:
            self._get_primitive(context).rotation = self._initial_rotation
            context.area.header_text_set(None)
            context.workspace.status_text_set(None)
            return {'CANCELLED'}

        return {'RUNNING_MODAL'}

    def _invoke(self, context: bpy.types.Context, event):
        self.rotation = 0
        self._applied_rotation = 0
        self._snap = False
        self._precision = False
        self._flip_angle = False

        primitive = self._get_primitive(context)

        self._initial_rotation = Quaternion(primitive.rotation).normalized()

        context.window_manager.modal_handler_add(self)
        context.workspace.status_text_set(
            "[ESC] or [RMB]: Cancel   |   [Shift]: Precision Mode   |   [Ctrl]: Snap")

        return {'RUNNING_MODAL'}
