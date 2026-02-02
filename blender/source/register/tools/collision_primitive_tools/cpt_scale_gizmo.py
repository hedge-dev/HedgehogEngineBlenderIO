import bpy
from bpy.props import FloatProperty, EnumProperty, BoolProperty
from mathutils import Vector, Matrix, Quaternion
import gpu
import math

from .cpt_base_transform_operator import BaseTransformOperator
from ....utility import mesh_generators, math_utils

_HALF = math.sqrt(0.5)
AXIS_SPACE: dict[str, tuple[Quaternion, Vector]] = {
    'X': (Quaternion((_HALF, 0, _HALF, 0)), Vector((1, 0, 0))),
    '-X': (Quaternion((_HALF, 0, -_HALF, 0)), Vector((-1, 0, 0))),
    'Y': (Quaternion((_HALF, -_HALF, 0, 0)), Vector((0, 1, 0))),
    '-Y': (Quaternion((_HALF, _HALF, 0, 0)), Vector((0, -1, 0))),
    'Z': (Quaternion(), Vector((0, 0, 1))),
    '-Z': (Quaternion((0, 1, 0, 0)), Vector((0, 0, -1))),
}


class HEIO_GT_CollisionPrimitive_Scale(bpy.types.Gizmo):
    bl_idname = "heio.gt.collision_primitive_scale"

    shape_cube: tuple[gpu.types.GPUBatch, gpu.types.GPUShader]
    shape_line: tuple[gpu.types.GPUBatch, gpu.types.GPUShader]

    axis: str

    offset: float
    base_hide: bool

    _axis_direction: Vector
    _axis_rotation: Quaternion
    _invoke_offset: float

    def _draw(self, context: bpy.types.Context, select_id):

        view_dir = context.region_data.view_rotation.to_matrix() @ Vector((0, 0, 1))
        axis_dir = self.matrix_basis.to_3x3() @ self._axis_direction
        lookat_fac = view_dir.dot(axis_dir)

        if lookat_fac > 0:
            alpha = 1 - ((lookat_fac - 0.9)) * 10
        else:
            alpha = 1 + lookat_fac * 3

        if alpha <= 0.01:
            return

        if select_id is not None:
            gpu.select.load_id(select_id)

        gpu.state.line_width_set(2)
        gpu.state.blend_set('ALPHA')

        color = (
            *self._axis_color,
            1 if self.is_highlight or self.is_modal else min(1, max(0, alpha))
        )

        self.matrix_offset = Matrix.LocRotScale(
            self._axis_direction * (self.offset + 0.1),
            self._axis_rotation, None)

        with gpu.matrix.push_pop():
            gpu.matrix.multiply_matrix(self.matrix_world)

            self.shape_cube[1].uniform_float("color", color)
            self.shape_cube[0].draw()

            self.shape_line[1].uniform_float("color", color)
            self.shape_line[0].draw()

        gpu.state.blend_set('NONE')

    def draw(self, context):
        self._draw(context, None)

    def draw_select(self, context, select_id):
        self._draw(context, select_id)

    def set_axis(self, axis: str):
        self.axis = axis

        if self.axis[-1] == 'X':
            self._axis_color = (1, 0.2, 0.322)
        elif self.axis[-1] == 'Y':
            self._axis_color = (0.545, 0.863, 0)
        elif self.axis[-1] == 'Z':
            self._axis_color = (0.157, 0.565, 1)

        self._axis_rotation, self._axis_direction = AXIS_SPACE[axis]

    def setup(self):
        if hasattr(self, 'offset'):
            return

        self.offset = 1
        self.base_hide = False
        self._invoke_offset = None

    def invoke(self, context, event):
        self._invoke_offset = self.offset
        context.region.tag_redraw()
        return {'RUNNING_MODAL'}

    def modal(self, context, event, tweak):
        # so that the ui list updates too
        for area in context.screen.areas:
            area.tag_redraw()
        return {'RUNNING_MODAL'}

    def exit(self, context, cancel):
        self._invoke_offset = None

    @classmethod
    def register(cls):
        size = 0.075
        cube_mesh = mesh_generators.cube(size)
        offset = Vector((0, 0, 1 - size))
        for i, vert in enumerate(cube_mesh.vertices):
            cube_mesh.vertices[i] = vert + offset

        cls.shape_cube = cube_mesh.to_custom_shape()
        cls.shape_line = cls.new_custom_shape(
            'LINES', [(0, 0, 0), (0, 0, 1 - size * 2)])


class HEIO_OT_CollisionPrimitive_Scale(BaseTransformOperator):
    bl_idname = "heio.collision_primitive_scale"
    bl_label = "Scale collision primitive"
    bl_description = "Scale the collision primitive"

    offset: FloatProperty(
        name="Offset"
    )

    one_directional: BoolProperty(
        name="One-directional",
        description="Shift the scaled site torwards a direction, instead of scaling both sides"
    )

    axis: EnumProperty(
        name="Rotation mode",
        items=(
            ('X', "X Axis", ""),
            ('-X', "-X Axis", ""),
            ('Y', "Y Axis", ""),
            ('-Y', "-Y Axis", ""),
            ('Z', "Z Axis", ""),
            ('-Z', "-Z Axis", ""),
        )
    )

    _internal_axis: str | None
    _internal_offset: float

    _axis_dir: Vector
    _origin: Vector
    _plane_normal: Vector

    def _update_axis(self, context: bpy.types.Context):
        if self._internal_axis == self.axis:
            return

        primitive = self._get_primitive(context)
        self._local_axis_dir = (Quaternion(primitive.rotation).normalized(
        ).to_matrix() @ AXIS_SPACE[self.axis][1]).normalized()

        self._internal_axis = self.axis

    def _update_transform(self, context, primitive):
        self._update_axis(context)

        if self.axis in {'X', '-X'}:
            dim_index = 0

        elif self.axis in {'Y', '-Y'}:
            dim_index = 1 if primitive.shape_type == 'BOX' else 0

        elif self.axis in {'Z', '-Z'}:
            dim_index = 2 if primitive.shape_type != 'SPHERE' else 0

        offset = self.offset

        if self.one_directional:
            offset *= 0.5

        dim = self._initial_dimensions[dim_index]
        if dim < -offset:
            offset = -dim
        primitive.dimensions[dim_index] = dim + offset

        loc = self._initial_position.copy()
        if self.one_directional:
            loc += self._local_axis_dir * offset
        primitive.position = loc

    def _get_header_text(self):
        text = f"Offset: {self.offset:.4f}"

        if self.one_directional:
            text += " (one-directional)"

        return text

    def _get_axis_offset(self, context: bpy.types.Context, event: bpy.types.Event, prev: bool):
        hit = math_utils.project_mouse_to_plane(
            context, event, prev, self._origin, self._plane_normal)

        return self._axis_dir.dot(hit - self._origin)

    def _on_mouse_moved(self, context, event):
        axis_distance = self._get_axis_offset(context, event, False)
        prev_axis_distance = self._get_axis_offset(context, event, True)

        delta = axis_distance - prev_axis_distance

        if self._precision:
            delta *= 0.1

        self._internal_offset += delta

    def _on_modal_update(self, context, event):
        self.one_directional = self._alt

        if self._snap:
            self.offset = round(
                self._internal_offset,
                2 if self._precision else 1)
        else:
            self.offset = self._internal_offset

    def _get_status_text(self):
        return super()._get_status_text() + "   |   [Alt]: one-directional scaling"

    def _setup(self, context, primitive):
        self.offset = 0
        self.one_directional = False

        self._internal_axis = None
        self._internal_offset = 0

        self._origin = context.object.matrix_world @ self._initial_position

        self._update_axis(context)

        self._axis_dir = (context.object.matrix_world.normalized(
        ).to_quaternion() @ self._local_axis_dir).normalized()

        view_dir = context.region_data.view_rotation @ Vector((0, 0, -1))
        up_dir = self._axis_dir.cross(view_dir).normalized()
        self._plane_normal = self._axis_dir.cross(up_dir).normalized()
