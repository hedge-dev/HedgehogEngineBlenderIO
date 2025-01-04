import bpy
from bpy.props import FloatVectorProperty
from mathutils import Vector, Matrix
import gpu
import math

from . import cpt_gizmo_state
from ...operators.base import HEIOBaseModalOperator
from ....utility import mesh_generators


class HEIO_GT_CollisionPrimitive_Move(bpy.types.Gizmo):
    bl_idname = "heio.gt.collision_primitive_move"

    shape_circle: any

    position: Vector
    base_hide: bool

    _invoke_position: Vector

    def _draw(self, context: bpy.types.Context, select_id):

        rot = context.region_data.view_rotation.normalized()
        matrix = Matrix.LocRotScale(self.position, rot, None)

        if select_id is not None:
            gpu.select.load_id(select_id)

        if self._invoke_position is not None:
            matrix_transparent = Matrix.LocRotScale(
                self._invoke_position, rot, None)
            matrix_opaque = matrix

        elif self.is_highlight:
            matrix_transparent = None
            matrix_opaque = matrix

        else:
            matrix_transparent = matrix
            matrix_opaque = None

        batch, shader = self.shape_circle
        if matrix_opaque is not None:

            shader.uniform_float("color", (1, 1, 1, 1))
            with gpu.matrix.push_pop():
                # taking advantage of the internal scaling system
                self.matrix_offset = matrix_opaque
                gpu.matrix.multiply_matrix(self.matrix_world)
                batch.draw()

        if matrix_transparent is not None:
            gpu.state.blend_set('ALPHA')
            shader.uniform_float("color", (1, 1, 1, 0.5))
            with gpu.matrix.push_pop():
                # taking advantage of the internal scaling system
                self.matrix_offset = matrix_transparent
                gpu.matrix.multiply_matrix(self.matrix_world)
                batch.draw()
            gpu.state.blend_set('NONE')

    def draw(self, context):
        self._draw(context, None)

    def draw_select(self, context, select_id):
        self._draw(context, select_id)

    def setup(self):
        if hasattr(self, 'position'):
            return

        self.position = Vector()
        self.base_hide = False
        self._invoke_position = Vector()

    def invoke(self, context, event):
        self._invoke_position = self.position.copy()
        context.region.tag_redraw()
        return {'RUNNING_MODAL'}

    def modal(self, context, event, tweak):
        context.region.tag_redraw()
        return {'RUNNING_MODAL'}

    def exit(self, context, cancel):
        self._invoke_position = None

    @classmethod
    def register(cls):
        circle_verts = mesh_generators.generate_circle(16, 0.15)
        cls.shape_circle = cls.new_custom_shape('TRI_STRIP', circle_verts)


class HEIO_OT_CollisionPrimitive_Move(HEIOBaseModalOperator):
    bl_idname = "heio.collision_primitive_move"
    bl_label = "Move collision primitive"
    bl_description = "Move the collision primitive"
    bl_options = {'REGISTER', 'UNDO', 'INTERNAL'}

    offset: FloatVectorProperty(
        name="Offset",
        size=3
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
                snap_level = - \
                    int(math.floor(math.log10(context.region_data.view_distance / 18.8)))

            if self.precision:
                snap_level += 1

            world_pos.x = round(world_pos.x, snap_level)
            world_pos.y = round(world_pos.y, snap_level)
            world_pos.z = round(world_pos.z, snap_level)

            position = matrix.inverted() @ world_pos

        primitive.position = position
        self.applied_offset = position - self._initial_location
        return {'FINISHED'}

    @staticmethod
    def _get_view_delta(context: bpy.types.Context, event, pos):
        # Logic taken from blender source:
        # source/blender/editors/gizmo_library/gizmo_types/move3d_gizmo.cc -> move3d_get_translate(...)

        mat = context.region_data.perspective_matrix.copy()

        zfac = (
            (mat[3][0] * pos[0])
            + (mat[3][1] * pos[1])
            + (mat[3][2] * pos[2])
            + mat[3][3]
        )

        if zfac < 1.e-6 and zfac > -1.e-6:
            zfac = 1
        elif zfac < 0:
            zfac = -zfac

        delta_x = (event.mouse_x - event.mouse_prev_x) * \
            2 * zfac / context.region.width
        delta_y = (event.mouse_y - event.mouse_prev_y) * \
            2 * zfac / context.region.height

        mat.invert()
        return Vector((
            mat[0][0] * delta_x + mat[0][1] * delta_y,
            mat[1][0] * delta_x + mat[1][1] * delta_y,
            mat[2][0] * delta_x + mat[2][1] * delta_y,
        ))

    def _update_header_text(self, context):
        context.area.header_text_set(
            "Offset {:.4f} {:.4f} {:.4f}".format(*self.applied_offset))

    def _modal(self, context: bpy.types.Context, event: bpy.types.Event):

        if event.type == 'MOUSEMOVE':
            self.snap = event.ctrl
            self.precision = event.shift

            delta = + self._get_view_delta(
                context,
                event,
                self.offset)

            if self.precision:
                delta *= 0.1

            self.offset = Vector(self.offset) + delta

            self._execute(context)
            self._update_header_text(context)

        elif event.type in {'LEFT_CTRL', 'RIGHT_CTRL', 'CTRL'}:
            self.snap = event.ctrl
            self._execute(context)
            self._update_header_text(context)

        elif event.type in {'LEFT_SHIFT', 'RIGHT_SHIFT', 'SHIFT'}:
            self.precision = event.shift
            self._execute(context)
            self._update_header_text(context)

        elif event.type == 'LEFTMOUSE':
            context.area.header_text_set(None)
            context.workspace.status_text_set(None)
            cpt_gizmo_state.CURRENT_MODAL = None
            return {'FINISHED'}

        elif event.type in {'RIGHTMOUSE', 'ESC'}:
            self._get_primitive(context).position = self._initial_location
            context.area.header_text_set(None)
            context.workspace.status_text_set(None)
            cpt_gizmo_state.CURRENT_MODAL = None
            return {'CANCELLED'}

        return {'RUNNING_MODAL'}

    def _invoke(self, context: bpy.types.Context, event):
        self.offset = (0, 0, 0)
        self.applied_offset = (0, 0, 0)
        self.snap = False
        self.precision = False

        self._initial_location = Vector(self._get_primitive(context).position)

        global CURRENT_MODAL
        CURRENT_MODAL = self

        context.window_manager.modal_handler_add(self)
        context.workspace.status_text_set(
            "[ESC] or [RMB]: Cancel   |   [Shift]: Precision Mode   |   [Ctrl]: Snap")

        return {'RUNNING_MODAL'}
