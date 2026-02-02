import bpy
from bpy.props import FloatVectorProperty
from mathutils import Vector, Matrix
import gpu
import math

from .cpt_base_transform_operator import BaseTransformOperator
from ....utility import mesh_generators, math_utils


class HEIO_GT_CollisionPrimitive_Move(bpy.types.Gizmo):
    bl_idname = "heio.gt.collision_primitive_move"

    shape_circle: tuple[gpu.types.GPUBatch, gpu.types.GPUShader]

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
            # taking advantage of the internal scaling system
            with gpu.matrix.push_pop():
                self.matrix_offset = matrix_opaque
                gpu.matrix.multiply_matrix(self.matrix_world)
                batch.draw()

        if matrix_transparent is not None:
            gpu.state.blend_set('ALPHA')
            shader.uniform_float("color", (1, 1, 1, 0.5))
            # taking advantage of the internal scaling system
            with gpu.matrix.push_pop():
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
        self._invoke_position = None

    def invoke(self, context, event):
        self._invoke_position = self.position.copy()
        context.region.tag_redraw()
        return {'RUNNING_MODAL'}

    def modal(self, context, event, tweak):
        # so that the ui list updates too
        for area in context.screen.areas:
            area.tag_redraw()
        return {'RUNNING_MODAL'}

    def exit(self, context, cancel):
        self._invoke_position = None

    @classmethod
    def register(cls):
        cls.shape_circle = mesh_generators.circle(16, 0.15).to_custom_shape()


class HEIO_OT_CollisionPrimitive_Move(BaseTransformOperator):
    bl_idname = "heio.collision_primitive_move"
    bl_label = "Move collision primitive"
    bl_description = "Move the collision primitive"

    offset: FloatVectorProperty(
        name="Offset",
        size=3
    )

    _internal_offset: Vector
    _object_rotation: Matrix

    def _update_transform(self, context, primitive):
        primitive.position = self._initial_position + Vector(self.offset)

    def _get_header_text(self):
        return "Offset {:.4f} {:.4f} {:.4f}".format(*self.offset)

    def _on_mouse_moved(self, context, event):
        delta = math_utils.get_mouse_view_delta(
            context,
            event,
            self._initial_position)

        if self._precision:
            delta *= 0.1

        self._internal_offset += self._object_rotation @ delta

    def _on_modal_update(self, context, event):
        if self._snap:
            snap_level = 0
            if not context.region_data.is_perspective and context.region_data.is_orthographic_side_view:
                snap_level = - int(math.floor(math.log10(context.region_data.view_distance / 18.8)))

            if self._precision:
                snap_level += 1

            self.offset = Vector((
                round(self._internal_offset.x, snap_level),
                round(self._internal_offset.y, snap_level),
                round(self._internal_offset.z, snap_level)
            ))
        else:
            self.offset = self._internal_offset

    def _setup(self, context, primitive):
        self.offset = Vector()
        self._internal_offset = Vector()
        self._object_rotation = context.object.matrix_world.inverted().to_3x3().normalized()
