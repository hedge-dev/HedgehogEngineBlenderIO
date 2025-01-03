import bpy
from bpy.props import FloatProperty, EnumProperty
from mathutils import Matrix, Vector, Quaternion
import gpu
import math

from ...operators.base import HEIOBaseModalOperator
from ....utility import mesh_generators


class HEIO_GT_CollisionPrimitive_Rotate(bpy.types.Gizmo):
    bl_idname = "heio.gt.collision_primitive_rotate"

    shape_circle: tuple[gpu.types.GPUBatch, gpu.types.GPUShader]
    shape_line: tuple[gpu.types.GPUBatch, gpu.types.GPUShader]

    mode: str

    _line_matrix: Matrix | None
    _line_offset_matrix: Matrix | None
    _flip_angle: bool | None

    def _get_color(self):
        if self.mode == 'X':
            color = (1, 0.2, 0.322)

        elif self.mode == 'Y':
            color = (0.545, 0.863, 0)

        elif self.mode == 'Z':
            color = (0.157, 0.565, 1)

        else:
            color = (1,1,1)

        if self.is_highlight or self.is_modal:
            color = (*color, 1)
        else:
            color = (*color, 0.5)

        return color

    def _get_clip_plane(self, context: bpy.types.Context):
        matrix = context.region_data.view_matrix.inverted()

        result = Vector((
            matrix[0][2],
            matrix[1][2],
            matrix[2][2],
            matrix[3][2]
        ))

        result.w = 0.02 - Vector.dot(result, Vector((
            self.matrix_basis[0][3],
            self.matrix_basis[1][3],
            self.matrix_basis[2][3],
            self.matrix_basis[3][3]
        )))

        return result

    def _draw(self, context: bpy.types.Context, select_id):

        if self.mode == 'VIEW':
            self.matrix_offset = context.region_data.view_rotation.to_matrix().to_4x4()

        if select_id is not None:
            gpu.select.load_id(select_id)
        gpu.state.line_width_set(3)
        gpu.state.blend_set('ALPHA')

        batch, shader, shader_clipped = self.shape_circle

        if not self.is_modal and self.mode != 'VIEW':
            gpu.state.clip_distances_set(1)
            used_shader = shader_clipped

            mw = self.matrix_world.transposed()
            clip_plane = self._get_clip_plane(context)

            values = [*mw[0], *mw[1], *mw[2], *mw[3], *clip_plane, *([0] * 20)]
            buffer = gpu.types.Buffer('FLOAT', len(values), values)
            ubo = gpu.types.GPUUniformBuf(buffer)

            used_shader.uniform_block("clipPlanes", ubo)
        else:
            gpu.state.clip_distances_set(0)
            used_shader = shader

        color = self._get_color()

        batch.program_set(used_shader)
        used_shader.uniform_float("color", color)

        with gpu.matrix.push_pop():
            gpu.matrix.multiply_matrix(self.matrix_world)
            batch.draw()

        gpu.state.clip_distances_set(0)

        if self._line_matrix is None:
            gpu.state.blend_set('NONE')
            return

        line_batch, line_shader = self.shape_line
        line_shader.uniform_float("color", color)

        if self.mode == 'VIEW':
            gpu.state.line_width_set(1)
            other_line_width = 3
            matrix = self.matrix_world @ self._line_matrix
        else:
            other_line_width = 1
            matrix = self._line_matrix @ self.matrix_world

        with gpu.matrix.push_pop():
            gpu.matrix.multiply_matrix(matrix)
            line_batch.draw()

            gpu.state.line_width_set(other_line_width)
            with gpu.matrix.push_pop():
                gpu.matrix.multiply_matrix(self._line_offset_matrix)
                line_batch.draw()

        gpu.state.blend_set('NONE')

    def draw(self, context):
        self._draw(context, None)

    def draw_select(self, context, select_id):
        self._draw(context, select_id)

    def set_mode(self, mode):
        self.mode = mode

        matrix = Matrix((
            (0, 0, 0, 0),
            (0, 0, 0, 0),
            (0, 0, 0, 0),
            (0, 0, 0, 1)
        ))

        if self.mode == 'X':
            matrix[1][0] = -1
            matrix[2][1] = -1
            matrix[0][2] = 1

        elif self.mode == 'Y':
            matrix[0][0] = 1
            matrix[2][1] = -1
            matrix[1][2] = 1

        elif self.mode == 'Z':
            matrix[0][0] = 1
            matrix[1][1] = 1
            matrix[2][2] = 1

        self.matrix_offset = matrix

    def setup(self):
        if hasattr(self, 'mode'):
            return

        self.set_mode('X')
        self._line_matrix = None
        self._line_offset_matrix = None

    @staticmethod
    def _get_mouse_ray(context, event) -> tuple[Vector, Vector]:
        near_fac = context.space_data.clip_start
        far_fac = context.space_data.clip_end

        mouse_x = ((event.mouse_x - context.region.x) /
                   context.region.width) * 2 - 1
        mouse_y = ((event.mouse_y - context.region.y) /
                   context.region.height) * 2 - 1

        mouse_x_near = mouse_x * near_fac
        mouse_y_near = mouse_y * near_fac
        mouse_x_far = mouse_x * far_fac
        mouse_y_far = mouse_y * far_fac

        mat = context.region_data.perspective_matrix.inverted()

        near = mat @ Vector((mouse_x_near, mouse_y_near, -1, near_fac))
        near = near / near.w
        far = mat @ Vector((mouse_x_far, mouse_y_far, 1, far_fac))
        far = far / far.w

        ray_pos = near
        ray_dir = (far - near).normalized()

        return ray_pos.to_3d(), ray_dir.to_3d()

    def _get_mouse_dir(self, context: bpy.types.Context, event):
        mouse_x = event.mouse_x - context.region.x
        mouse_y = event.mouse_y - context.region.y

        pos = (context.region_data.perspective_matrix @
               self.matrix_world).to_translation()

        pos_x = (pos.x * 0.5 + 0.5) * context.region.width
        pos_y = (pos.y * 0.5 + 0.5) * context.region.height

        return Vector((mouse_x - pos_x, mouse_y - pos_y)).normalized()

    def invoke(self, context, event):
        ray_pos, ray_dir = self._get_mouse_ray(context, event)

        normal_matrix = self.matrix_world.normalized().to_3x3()
        normal = normal_matrix @ Vector((0, 0, 1))
        pos = self.matrix_world.to_translation()

        div = normal.dot(ray_dir)
        if div != 0:
            hit = ray_pos + ray_dir * \
                ((normal.dot(pos) - normal.dot(ray_pos)) / div)

            direction = (hit - pos).normalized()
            line_default = normal_matrix @ Vector((0, -1, 0))

            angle = math.acos(Vector.dot(line_default, direction))
            if normal.dot(line_default.cross(direction)) < 0:
                angle = -angle

            self._line_offset_matrix = Matrix.Identity(4)

            self._initial_mouse_dir = self._get_mouse_dir(context, event)

            if self.mode == 'VIEW':
                self._flip_angle = True
                self._line_matrix = Matrix.Rotation(angle, 4, 'Z')
            else:
                self._line_matrix = Matrix.Rotation(angle, 4, normal)

                view_dir = (
                    context.region_data.view_matrix
                    .inverted().normalized().to_3x3()
                    @ Vector((0, 0, -1))
                )
                self._flip_angle = normal.dot(view_dir) > 0

        context.region.tag_redraw()
        return {'RUNNING_MODAL'}

    def modal(self, context, event, tweak):

        if self._line_offset_matrix is not None:
            mouse_dir = self._get_mouse_dir(context, event)
            angle = self._initial_mouse_dir.angle_signed(mouse_dir)

            if self._flip_angle:
                angle = -angle

            self._line_offset_matrix = Matrix.Rotation(
                angle, 4, Vector((0, 0, 1)))

        context.region.tag_redraw()
        return {'RUNNING_MODAL'}

    def exit(self, context, cancel):
        self._line_matrix = None
        self._line_offset_matrix = None
        self._flip_angle = None

    @classmethod
    def register(cls):
        circle_lines = mesh_generators.generate_circle_lines(32)
        batch, shader = cls.new_custom_shape('LINE_STRIP', circle_lines)
        shader_clipped = gpu.shader.from_builtin(
            'UNIFORM_COLOR', config='CLIPPED')
        cls.shape_circle = (batch, shader, shader_clipped)

        cls.shape_line = cls.new_custom_shape('LINES', [(0, 0, 0), (0, -1, 0)])


class HEIO_OT_CollisionPrimitive_Rotate(HEIOBaseModalOperator):
    bl_idname = "heio.collision_primitive_rotate"
    bl_label = "Rotate collision primitive"
    bl_description = "Rotate the collision primitive"
    bl_options = {'REGISTER', 'UNDO', 'INTERNAL'}

    rotation: FloatProperty(
        name="Rotation",
        subtype='ANGLE'
    )

    mode: EnumProperty(
        name="Rotation mode",
        items=(
            ('X', "X Axis", ""),
            ('Y', "Y Axis", ""),
            ('Z', "Z Axis", ""),
            ('VIEW', "View Axis", "")
        )
    )

    def _execute(self, context):
        primitive = self._get_primitive(context)

        if self.mode == 'VIEW':
            axis = context.region_data.view_matrix.inverted().normalized().to_3x3() @ Vector((0, 0, -1))
            primitive.rotation = Matrix.Rotation(
                self.rotation, 4, axis).to_quaternion() @ self._initial_rotation
        else:
            primitive.rotation = self._initial_rotation @ Matrix.Rotation(
                self.rotation, 4, self.mode).to_quaternion()

        return {'FINISHED'}

    def _get_primitive(self, context):
        return context.object.data.heio_collision_mesh.primitives.active_element

    def _modal(self, context: bpy.types.Context, event: bpy.types.Event):
        if event.type == 'MOUSEMOVE':
            mouse_dir = self._get_mouse_dir(context, event)
            angle = self._initial_mouse_dir.angle_signed(mouse_dir)

            if self._flip_angle:
                angle = -angle

            self.rotation = angle

            self._execute(context)
            context.area.header_text_set(f"Rotation {math.degrees(self.rotation):.4f}°")
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

    def _get_mouse_dir(self, context: bpy.types.Context, event):
        mouse_x = event.mouse_x - context.region.x
        mouse_y = event.mouse_y - context.region.y

        prim_pos = self._get_primitive(context).position
        pos = context.region_data.perspective_matrix @ Vector(prim_pos)

        pos_x = (pos.x * 0.5 + 0.5) * context.region.width
        pos_y = (pos.y * 0.5 + 0.5) * context.region.height

        return Vector((mouse_x - pos_x, mouse_y - pos_y)).normalized()

    def _invoke(self, context: bpy.types.Context, event):
        self.rotation = 0
        self.snap = False
        self.precision = False

        obj = context.object
        primitive = self._get_primitive(context)

        self._initial_mouse_dir = self._get_mouse_dir(context, event)
        self._initial_rotation = Quaternion(primitive.rotation)

        self._view_dir = (
            context.region_data.view_matrix
            .inverted().normalized().to_3x3()
            @ Vector((0, 0, -1))
        )

        if self.mode != 'VIEW':
            matrix = obj.matrix_world.normalized() @ Matrix.LocRotScale(primitive.position, primitive.rotation, None)
            normal_matrix = matrix.normalized().to_3x3()

            if self.mode == 'X':
                normal = Vector((1,0,0))
            elif self.mode == 'Y':
                normal = Vector((0,1,0))
            elif self.mode == 'Z':
                normal = Vector((0,0,1))

            normal = normal_matrix @ normal
            self._flip_angle = normal.dot(self._view_dir) < 0
        else:
            self._flip_angle = False

        context.window_manager.modal_handler_add(self)
        context.workspace.status_text_set(
            "[ESC] or [RMB]: Cancel   |   [Shift]: Precision Mode   |   [Ctrl]: Snap")

        return {'RUNNING_MODAL'}
