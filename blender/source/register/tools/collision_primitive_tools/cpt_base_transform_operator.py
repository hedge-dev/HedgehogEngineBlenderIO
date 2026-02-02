from bpy.types import Context, Event
from bpy.props import FloatProperty
from mathutils import Vector, Quaternion, Matrix
import math

from ...operators.base import HEIOBaseModalOperator
from ....utility import math_utils

class BaseTransformOperator(HEIOBaseModalOperator):
    bl_options = {'REGISTER', 'UNDO', 'INTERNAL'}

    _snap: bool
    _precision: bool
    _alt: bool

    _initial_position: Vector
    _initial_rotation: Quaternion
    _initial_dimensions: Vector

    def _get_primitive(self, context: Context):
        return context.object.data.heio_mesh.collision_primitives.active_element

    def _get_header_text(self) -> str:
        raise NotImplementedError()

    def _update_transform(self, context: Context, primitive):
        raise NotImplementedError()

    def _execute(self, context: Context):
        primitive = self._get_primitive(context)
        self._update_transform(context, primitive)
        return {'FINISHED'}

    def _on_mouse_moved(self, context: Context, event: Event):
        raise NotImplementedError()

    def _on_modal_update(self, context: Context, event: Event):
        return

    def _modal(self, context: Context, event: Event):
        update = True

        if event.type == 'MOUSEMOVE':
            self._snap = event.ctrl
            self._precision = event.shift
            self._alt = event.alt

            self._on_mouse_moved(context, event)

        elif event.type in {'LEFT_CTRL', 'RIGHT_CTRL', 'CTRL'}:
            self._snap = event.ctrl

        elif event.type in {'LEFT_SHIFT', 'RIGHT_SHIFT', 'SHIFT'}:
            self._precision = event.shift

        elif event.type in {'LEFT_ALT', 'RIGHT_ALT', 'ALT'}:
            self._alt = event.alt

        elif event.type == 'LEFTMOUSE':
            context.area.header_text_set(None)
            context.workspace.status_text_set(None)
            return {'FINISHED'}

        elif event.type in {'RIGHTMOUSE', 'ESC'}:
            primitive = self._get_primitive(context)
            primitive.position = self._initial_position
            primitive.rotation = self._initial_rotation
            primitive.dimensions = self._initial_dimensions

            context.area.header_text_set(None)
            context.workspace.status_text_set(None)
            return {'CANCELLED'}
        else:
            update = False

        if update:
            self._on_modal_update(context, event)
            self._execute(context)
            context.area.header_text_set(self._get_header_text())

            # so that the ui list updates too
            for area in context.screen.areas:
                area.tag_redraw()

        return {'RUNNING_MODAL'}

    def _get_status_text(self):
        return "[ESC] or [RMB]: Cancel   |   [Shift]: Precision Mode   |   [Ctrl]: Snap"

    def _setup(self, context: Context, primitive):
        return

    def _invoke(self, context: Context, event: Event):
        self._snap = False
        self._precision = False
        self._alt = False

        primitive = self._get_primitive(context)
        self._initial_position = Vector(primitive.position)
        self._initial_rotation = Quaternion(primitive.rotation)
        self._initial_dimensions = Vector(primitive.dimensions)

        self._setup(context, primitive)

        context.window_manager.modal_handler_add(self)
        context.workspace.status_text_set(self._get_status_text())

        return {'RUNNING_MODAL'}


class BaseRotateOperator(BaseTransformOperator):

    rotation: FloatProperty(
        name="Rotation",
        subtype='ANGLE'
    )

    _internal_rotation: bool
    _flip_angle: bool

    _origin_matrix: Matrix

    def _get_header_text(self):
        return f"Rotation {math.degrees(self.rotation):.4f}°"

    def _get_mouse_dir(self, context: Context, event: Event, prev):
        return math_utils.get_mouse_dir(context, event, self._origin_matrix, prev)

    def _on_mouse_moved(self, context: Context, event: Event):

        prev_mouse_dir = self._get_mouse_dir(context, event, True)
        mouse_dir = self._get_mouse_dir(context, event, False)
        angle = prev_mouse_dir.angle_signed(mouse_dir)

        if self._flip_angle:
            angle = -angle

        if self._precision:
            angle /= 30

        self._internal_rotation += angle

    def _on_modal_update(self, context: Context, event: Event):
        if self._snap:
            if self._precision:
                fac = math.radians(1)
            else:
                fac = math.radians(5)

            self.rotation = round(self._internal_rotation / fac) * fac
        else:
            self.rotation = self._internal_rotation

    def _setup(self, context: Context, primitive):
        self._internal_rotation = 0
        self._flip_angle = False

        self._origin_matrix = context.object.matrix_world @ Matrix.Translation(self._initial_position)