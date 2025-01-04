import bpy
import gpu
from gpu_extras.batch import batch_for_shader
from mathutils import Matrix
import colorsys
from random import Random

from .cpt_shaders import CollisionMeshShaders
from ....utility import mesh_generators

SHAPE_COLORS = {
    "SPHERE": (1, 0.5, 0.5),
    "BOX": (1, 1, 0.5),
    "CAPSULE": (0.5, 1, 0.5),
    "CYLINDER": (0.5, 1, 1),
}


class HEIO_3D_CollisionPrimitiveRenderer:

    DONT_REGISTER_CLASS = True

    @classmethod
    def register(cls):

        cls.draw_handle = bpy.types.SpaceView3D.draw_handler_add(
            cls.draw_callback, (), "WINDOW", "POST_VIEW"
        )

        sphere_verts = mesh_generators.generate_icosphere(3)
        sphere_lines = mesh_generators.generate_sphere_lines(32)
        cube_verts = mesh_generators.generate_cube()
        cube_lines = mesh_generators.generate_cube_lines()
        cylinder_verts = mesh_generators.generate_cylinder(20)
        cylinder_lines = mesh_generators.generate_cylinder_lines(32)
        capsule_verts = mesh_generators.generate_capsule(3)
        capsule_lines = mesh_generators.generate_capsule_lines(32)

        cls.shader = gpu.shader.from_builtin('UNIFORM_COLOR')
        cls.capsule_shader = CollisionMeshShaders.capsule_shader

        def get_batch(type, pos, shader=None):
            if shader is None:
                shader = cls.shader
            return batch_for_shader(shader, type, {"pos": pos})

        cls.batch_shapes = {
            "SPHERE": (
                cls.shader,
                get_batch('TRIS', sphere_verts),
                get_batch('LINE_STRIP', sphere_lines)),
            "BOX": (
                cls.shader,
                get_batch('TRI_STRIP', cube_verts),
                get_batch('LINES', cube_lines)),
            "CAPSULE": (
                cls.capsule_shader,
                get_batch('TRIS', capsule_verts, cls.capsule_shader),
                get_batch('LINE_STRIP', capsule_lines, cls.capsule_shader)),
            "CYLINDER": (
                cls.shader,
                get_batch('TRIS', cylinder_verts),
                get_batch('LINES', cylinder_lines)),
        }

    @classmethod
    def unregister(cls):
        bpy.types.SpaceView3D.draw_handler_remove(cls.draw_handle, "WINDOW")

    @classmethod
    def draw_callback(cls):

        if not bpy.context.space_data.overlay.show_overlays:
            return

        overlay_props = bpy.context.screen.heio_collision_primitives
        if not overlay_props.show_primitives:
            return

        batches = []
        rand = Random(overlay_props.random_seed)
        view = bpy.context.space_data
        depsgraph = bpy.context.evaluated_depsgraph_get()

        for obj, obj_eval in zip(depsgraph.view_layer.objects, depsgraph.view_layer_eval.objects):

            if obj.type != 'MESH' or not obj_eval.visible_in_viewport_get(view):
                continue

            for primitive in obj.data.heio_collision_mesh.primitives:

                # transformation matrix
                matrix = obj.matrix_world.normalized() @ Matrix.LocRotScale(primitive.position,
                                                                            primitive.rotation, None).normalized()

                r = primitive.dimensions[0]
                h = primitive.dimensions[2]

                if primitive.shape_type == 'SPHERE':
                    matrix = matrix @ Matrix.Scale(r, 4)
                elif primitive.shape_type == 'BOX':
                    matrix = matrix @ Matrix.LocRotScale(
                        None, None, primitive.dimensions)
                elif primitive.shape_type == 'CYLINDER':
                    matrix = matrix @ Matrix.LocRotScale(None, None, (r, r, h))

                mvp_matrix = bpy.context.region_data.perspective_matrix @ matrix

                # distance for basic transparency sorting
                mv_matrix = bpy.context.region_data.view_matrix @ matrix
                x = mv_matrix[0][3]
                y = mv_matrix[1][3]
                z = mv_matrix[2][3]
                distance = x * x + y * y + z * z

                # colors
                if overlay_props.random_colors:
                    color = colorsys.hsv_to_rgb(rand.random(), 0.5, 1)
                else:
                    color = SHAPE_COLORS[primitive.shape_type]

                batches.append(
                    (primitive.shape_type, mvp_matrix, distance, color, primitive.dimensions))

        if len(batches) == 0:
            return

        batches.sort(key=lambda x: x[2], reverse=True)

        gpu.state.depth_test_set('LESS_EQUAL')
        gpu.state.face_culling_set('BACK')
        gpu.state.line_width_set(overlay_props.line_width)

        if overlay_props.surface_visibility == 1:
            cls.draw_opaque(batches)
        else:
            cls.draw_transparent(batches)

    @classmethod
    def draw_transparent(cls, batches):
        gpu.state.depth_mask_set(False)
        gpu.state.blend_set('ALPHA')

        overlay_props = bpy.context.screen.heio_collision_primitives
        line_fac = 1 - max(((overlay_props.surface_visibility - 0.75) * 4), 0)

        for batch in batches:
            batch_shape = cls.batch_shapes[batch[0]]
            shader = batch_shape[0]

            shader.uniform_float("ModelViewProjectionMatrix", batch[1])
            if batch[0] == 'CAPSULE':
                shader.uniform_float("radius", batch[4][0])
                shader.uniform_float("height", batch[4][2])

            col = batch[3]

            if overlay_props.surface_visibility > 0:
                shader.uniform_float(
                    "color", (col[0], col[1], col[2], overlay_props.surface_visibility))
                batch_shape[1].draw(shader)

            if overlay_props.line_visibility > 0:
                shader.uniform_float(
                    "color", (col[0] * line_fac, col[1] * line_fac, col[2] * line_fac, overlay_props.line_visibility))
                batch_shape[2].draw(shader)

    @classmethod
    def draw_opaque(cls, batches):
        gpu.state.depth_mask_set(True)
        gpu.state.blend_set('NONE')

        overlay_props = bpy.context.screen.heio_collision_primitives
        line_fac = 1 - overlay_props.line_visibility

        for batch in batches:
            batch_shape = cls.batch_shapes[batch[0]]
            shader = batch_shape[0]

            shader.uniform_float("ModelViewProjectionMatrix", batch[1])
            if batch[0] == 'CAPSULE':
                shader.uniform_float("radius", batch[4][0])
                shader.uniform_float("height", batch[4][2])

            col = batch[3]

            shader.uniform_float("color", (col[0], col[1], col[2], 1))
            batch_shape[1].draw(shader)

            if line_fac < 1:
                lines_matrix = batch[1].copy()
                lines_matrix[3][3] = lines_matrix[3][3] + 0.001
                shader.uniform_float("ModelViewProjectionMatrix", lines_matrix)

                shader.uniform_float(
                    "color", (col[0] * line_fac, col[1] * line_fac, col[2] * line_fac, 1))
                batch_shape[2].draw(shader)
