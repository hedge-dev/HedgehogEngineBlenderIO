import bpy
from mathutils import Matrix, Vector, Quaternion
import gpu

from .cpt_base_rotation import get_mouse_dir, BaseCollisionPrimitiveRotateOperator
from ....utility import mesh_generators


class HEIO_GT_CollisionPrimitive_ViewRotate(bpy.types.Gizmo):
    bl_idname = "heio.gt.collision_primitive_viewrotate"

    shape_circle: tuple[gpu.types.GPUBatch, gpu.types.GPUShader]
    shape_line: tuple[gpu.types.GPUBatch, gpu.types.GPUShader]

    view_rotation: Quaternion
    base_hide: bool

    def _draw(self, context: bpy.types.Context, select_id):
        self.matrix_offset = context.region_data.view_rotation.to_matrix().to_4x4()

        if select_id is not None:
            gpu.select.load_id(select_id)
        gpu.state.line_width_set(3)
        gpu.state.blend_set('ALPHA')

        color = (1, 1, 1, 1 if self.is_highlight or self.is_modal else 0.5)

        with gpu.matrix.push_pop():
            batch, shader = self.shape_circle
            shader.uniform_float("color", color)
            gpu.matrix.multiply_matrix(self.matrix_world)
            batch.draw()

        if self._line_matrix is None:
            gpu.state.blend_set('NONE')
            return

        line_batch, line_shader = self.shape_line
        line_shader.uniform_float("color", color)
        gpu.state.line_width_set(1)

        with gpu.matrix.push_pop():
            gpu.matrix.multiply_matrix(self.matrix_world @ self._line_matrix)
            line_batch.draw()

            gpu.state.line_width_set(3)
            difference = self._initial_view_rotation.rotation_difference(
                self.view_rotation)

            angle = difference.angle
            if self._view_vector.dot(difference.axis) > 0:
                angle = -angle

            gpu.matrix.multiply_matrix(Matrix.Rotation(angle, 4, 'Z'))
            line_batch.draw()

    def draw(self, context):
        self._draw(context, None)

    def draw_select(self, context, select_id):
        self._draw(context, select_id)

    def setup(self):
        if hasattr(self, '_line_matrix'):
            return

        self._line_matrix = None
        self._initial_view_rotation = None
        self._view_vector = None
        self.base_hide = False

    def invoke(self, context, event):

        mouse_dir = get_mouse_dir(context, event, self.matrix_world)
        angle = mouse_dir.angle_signed((0, -1))
        self._line_matrix = Matrix.Rotation(angle, 4, 'Z')
        self._initial_view_rotation = self.view_rotation

        obj_rot = context.object.matrix_world.to_quaternion().inverted().normalized()
        self._view_vector = obj_rot @ context.region_data.view_rotation @ Vector(
            (0, 0, -1))

        context.region.tag_redraw()
        return {'RUNNING_MODAL'}

    def modal(self, context, event, tweak):
        context.region.tag_redraw()
        return {'RUNNING_MODAL'}

    def exit(self, context, cancel):
        self._line_matrix = None
        self._initial_view_rotation = None
        self._view_vector = None

    @classmethod
    def register(cls):
        circle_lines = mesh_generators.generate_circle_lines(32)
        cls.shape_circle = cls.new_custom_shape('LINE_STRIP', circle_lines)
        cls.shape_line = cls.new_custom_shape('LINES', [(0, 0, 0), (0, -1, 0)])


class HEIO_OT_CollisionPrimitive_ViewRotate(BaseCollisionPrimitiveRotateOperator):
    bl_idname = "heio.collision_primitive_viewrotate"
    bl_label = "View-Rotate collision primitive"
    bl_description = "Rotate the collision primitive based on the viewing angle"

    def _execute(self, context):
        primitive = self._get_primitive(context)

        obj_rot = context.object.matrix_world.to_quaternion().inverted().normalized()
        axis = obj_rot @ context.region_data.view_rotation @ Vector((0, 0, -1))
        primitive.rotation = self._initial_rotation @ Matrix.Rotation(self.rotation, 4, axis).to_quaternion()

        return {'FINISHED'}
