import bpy
from bpy.props import FloatProperty
from mathutils import Matrix, Vector, Quaternion
import math

from ...operators.base import HEIOBaseModalOperator


def get_mouse_dir(context: bpy.types.Context, event, world_matrix):
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

    _snap: bool
    _precision: bool
    _flip_angle: bool

    def _get_primitive(self, context):
        return context.object.data.heio_collision_mesh.primitives.active_element

    def _get_mouse_dir(self, context: bpy.types.Context, event):

        prim_pos = self._get_primitive(context).position
        world_matrix = context.object.matrix_world @ Matrix.Translation(
            prim_pos)
        return get_mouse_dir(context, event, world_matrix)

    def _modal(self, context: bpy.types.Context, event: bpy.types.Event):
        if event.type == 'MOUSEMOVE':
            mouse_dir = self._get_mouse_dir(context, event)
            angle = self._initial_mouse_dir.angle_signed(mouse_dir)

            if self._flip_angle:
                angle = -angle

            self.rotation = angle

            self._execute(context)
            context.area.header_text_set(
                f"Rotation {math.degrees(self.rotation):.4f}°")
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
        self._snap = False
        self._precision = False
        self._flip_angle = False

        primitive = self._get_primitive(context)

        self._initial_mouse_dir = self._get_mouse_dir(context, event)
        self._initial_rotation = Quaternion(primitive.rotation).normalized()

        context.window_manager.modal_handler_add(self)
        context.workspace.status_text_set(
            "[ESC] or [RMB]: Cancel   |   [Shift]: Precision Mode   |   [Ctrl]: Snap")

        return {'RUNNING_MODAL'}
