import bpy
from bpy.props import FloatVectorProperty
import gpu
from mathutils import Vector, Matrix
import math

from . import cpt_gizmo_state
from ...operators.base import HEIOBaseModalOperator
from ....utility import mesh_generators


class HEIO_GT_CollisionPrimitive_Move(bpy.types.Gizmo):
    bl_idname = "heio.gt.collision_primitive_move"

    shape_circle: any

    def _get_scale(self, context: bpy.types.Context, matrix_world):
        matrix = self.matrix_space @ matrix_world
        persp_matrix = context.region_data.perspective_matrix

        return (
            (persp_matrix[3][0] * matrix[0][3])
            + (persp_matrix[3][1] * matrix[1][3])
            + (persp_matrix[3][2] * matrix[2][3])
            + persp_matrix[3][3]
        ) * context.preferences.system.pixel_size

    def _draw(self, context: bpy.types.Context, select_id):
        modal = cpt_gizmo_state.CURRENT_MODAL
        if modal is not None and not isinstance(modal, HEIO_OT_CollisionPrimitive_Move):
            return

        obj = context.object
        primitive = obj.data.heio_collision_mesh.primitives.active_element
        batch, shader = self.shape_circle

        scale = self._get_scale(context, obj.matrix_world)
        scale = (scale, scale, scale)

        obj_matrix = obj.matrix_world.normalized()
        rot = context.region_data.view_rotation.normalized()

        pos = obj_matrix @ Vector(primitive.position)
        matrix = Matrix.LocRotScale(pos, rot, scale)

        if select_id is not None:
            gpu.select.load_id(select_id)

        if modal is not None and isinstance(modal, HEIO_OT_CollisionPrimitive_Move):
            pos = obj_matrix @ modal._initial_location
            matrix_transparent = Matrix.LocRotScale(pos, rot, scale)
            matrix_opaque = matrix

        elif self.is_highlight:
            matrix_transparent = None
            matrix_opaque = matrix

        else:
            matrix_transparent = matrix
            matrix_opaque = None

        if matrix_opaque is not None:
            shader.uniform_float("color", (1, 1, 1, 1))
            with gpu.matrix.push_pop():
                gpu.matrix.multiply_matrix(matrix_opaque)
                batch.draw()

        if matrix_transparent is not None:
            gpu.state.blend_set('ALPHA')
            shader.uniform_float("color", (1, 1, 1, 0.5))
            with gpu.matrix.push_pop():
                gpu.matrix.multiply_matrix(matrix_transparent)
                batch.draw()
            gpu.state.blend_set('NONE')

    def draw(self, context):
        self._draw(context, None)

    def draw_select(self, context, select_id):
        self._draw(context, select_id)

    def modal(self, context, event, tweak):
        context.region.tag_redraw()
        return {'RUNNING_MODAL'}

    @classmethod
    def register(cls):
        circle_verts = mesh_generators.generate_circle(16, 0.02)
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
        return {'FINISHED'}

    def _modal(self, context: bpy.types.Context, event: bpy.types.Event):

        if event.type == 'MOUSEMOVE':
            self.snap = event.ctrl
            self.precision = event.shift

            delta_x = ((event.mouse_x - event.mouse_prev_x) /
                       context.region.width * 2)
            delta_y = ((event.mouse_y - event.mouse_prev_y) /
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

            context.area.header_text_set(
                "Offset {:.4f} {:.4f} {:.4f}".format(*self.offset))

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

        elif event.type in {'LEFT_CTRL', 'RIGHT_CTRL', 'CTRL'}:
            self.snap = event.ctrl
            self._execute(context)

        elif event.type in {'LEFT_SHIFT', 'RIGHT_SHIFT', 'SHIFT'}:
            self.precision = event.shift
            self._execute(context)

        return {'RUNNING_MODAL'}

    def _invoke(self, context: bpy.types.Context, event):
        self.offset = (0, 0, 0)
        self.snap = False
        self.precision = False

        self._initial_location = Vector(self._get_primitive(context).position)

        global CURRENT_MODAL
        CURRENT_MODAL = self

        context.window_manager.modal_handler_add(self)
        context.workspace.status_text_set(
            "[ESC] or [RMB]: Cancel   |   [Shift]: Precision Mode   |   [Ctrl]: Snap")

        return {'RUNNING_MODAL'}
