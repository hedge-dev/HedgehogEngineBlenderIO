import bpy
from bpy.props import IntProperty
from mathutils import Matrix, Quaternion, Vector

from . import cpt_gizmo_state
from ...operators.base import HEIOBaseOperator
from ....utility import mesh_generators


class HEIO_GT_CollisionPrimitive_Select(bpy.types.Gizmo):
    bl_idname = "heio.gt.collision_primitive_select"

    shape_sphere: any
    shape_box: any
    shape_capsule_top: any
    shape_capsule_middle: any
    shape_capsule_bottom: any
    shape_cylinder: any

    shape_type: any
    position: Vector
    rotation: Quaternion
    dimensions: Vector

    def _draw(self, select_id=None):
        pos = self.position
        rot = self.rotation

        base_matrix = (
            self.matrix_world.normalized()
            @ Matrix.LocRotScale(pos, rot, None).normalized()
        )

        r = self.dimensions[0]
        h = self.dimensions[1]

        if self.shape_type == 'SPHERE':
            matrix = base_matrix @ Matrix.Scale(r, 4)
            shape = self.shape_sphere

        elif self.shape_type == 'BOX':
            matrix = base_matrix @ Matrix.LocRotScale(
                None, None, self.dimensions)
            shape = self.shape_box

        elif self.shape_type == 'CYLINDER':
            matrix = base_matrix @ Matrix.LocRotScale(None, None, (r, r, h))
            shape = self.shape_cylinder

        else:

            matrix = base_matrix @ Matrix.LocRotScale(None, None, (r, r, h))
            self.draw_custom_shape(
                self.shape_capsule_middle, matrix=matrix, select_id=select_id)

            matrix = base_matrix @ Matrix.Translation(
                (0, 0, h)) @ Matrix.Scale(r, 4)
            self.draw_custom_shape(
                self.shape_capsule_top, matrix=matrix, select_id=select_id)

            matrix = base_matrix @ Matrix.Translation(
                (0, 0, -h)) @ Matrix.Scale(r, 4)
            self.draw_custom_shape(
                self.shape_capsule_bottom, matrix=matrix, select_id=select_id)

            return

        self.draw_custom_shape(shape, matrix=matrix, select_id=select_id)

    def draw(self, context):
        self._draw()

    def draw_select(self, context, select_id):
        self._draw(select_id=select_id)

    def setup(self):
        if hasattr(self, "index"):
            return

        self.shape_type = 'SPHERE'
        self.position = Vector()
        self.rotation = Quaternion()
        self.dimensions = Vector((1, 1, 1))

    @classmethod
    def register(cls):
        spere_verts = mesh_generators.generate_icosphere(3)
        cube_verts = mesh_generators.generate_cube()
        cube_cylinder = mesh_generators.generate_cylinder(32)
        capsule_verts_top, capsule_verts_middle, capsule_verts_bottom = mesh_generators.generate_capsule_parts(
            3, False)

        cls.shape_sphere = cls.new_custom_shape('TRIS', spere_verts)
        cls.shape_box = cls.new_custom_shape('TRI_STRIP', cube_verts)
        cls.shape_cylinder = cls.new_custom_shape('TRIS', cube_cylinder)
        cls.shape_capsule_top = cls.new_custom_shape('TRIS', capsule_verts_top)
        cls.shape_capsule_middle = cls.new_custom_shape(
            'TRIS', capsule_verts_middle)
        cls.shape_capsule_bottom = cls.new_custom_shape(
            'TRIS', capsule_verts_bottom)


class HEIO_OT_CollisionPrimitive_GizmoClicked(HEIOBaseOperator):
    bl_idname = "heio.collision_primitive_gizmo_clicked"
    bl_label = "Select collision primitive"
    bl_description = "Select the collision primitive"
    bl_options = {'UNDO', 'INTERNAL'}

    select_index: IntProperty()
    callback_id: IntProperty()

    def _execute(self, context):
        cpt_gizmo_state.MANUAL_SELECT_MODE = True
        context.active_object.data.heio_collision_mesh.primitives.active_index = self.select_index
        context.active_object.data.update()
        return {'FINISHED'}
