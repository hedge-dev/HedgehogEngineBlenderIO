import bpy
from mathutils import Matrix, Vector

from . import cpt_gizmo_state
from .cpt_move_gizmo import (
    HEIO_GT_CollisionPrimitive_Move,
    HEIO_OT_CollisionPrimitive_Move
)

from .cpt_rotate_gizmo import (
    HEIO_GT_CollisionPrimitive_Rotate,
    HEIO_OT_CollisionPrimitive_Rotate
)

from .cpt_viewrotate_gizmo import (
    HEIO_GT_CollisionPrimitive_ViewRotate,
    HEIO_OT_CollisionPrimitive_ViewRotate
)

from .cpt_select_gizmo_group import BaseCollisionPrimitiveSelectGizmoGroup


class HEIO_GGT_CollisionPrimitive_Transform(BaseCollisionPrimitiveSelectGizmoGroup):
    bl_idname = "heio.ggt.collision_primitive_edit"
    bl_label = "HEIO Collision Primitive edit"

    move_gizmo: HEIO_GT_CollisionPrimitive_Move

    def setup(self, context):
        super().setup(context)

        if hasattr(self, "move_gizmo"):
            return

        self.move_gizmo = self.gizmos.new(
            HEIO_GT_CollisionPrimitive_Move.bl_idname)
        self.move_gizmo.target_set_operator(
            HEIO_OT_CollisionPrimitive_Move.bl_idname)
        self.move_gizmo.use_draw_modal = True

        def create_rotate_gizmo(mode):
            gz = self.gizmos.new(HEIO_GT_CollisionPrimitive_Rotate.bl_idname)
            op = gz.target_set_operator(
                HEIO_OT_CollisionPrimitive_Rotate.bl_idname)
            op.mode = mode
            gz.set_mode(mode)
            gz.use_draw_modal = True

            return gz

        self.rotate_gizmo_x = create_rotate_gizmo('X')
        self.rotate_gizmo_y = create_rotate_gizmo('Y')
        self.rotate_gizmo_z = create_rotate_gizmo('Z')

        self.rotate_gizmo_view = self.gizmos.new(
            HEIO_GT_CollisionPrimitive_ViewRotate.bl_idname)
        self.rotate_gizmo_view.target_set_operator(
            HEIO_OT_CollisionPrimitive_ViewRotate.bl_idname)
        self.rotate_gizmo_view.use_draw_modal = True
        self.rotate_gizmo_view.scale_basis = 1.1

        self.transform_gizmos = [
            self.move_gizmo,
            self.rotate_gizmo_x,
            self.rotate_gizmo_y,
            self.rotate_gizmo_z,
            self.rotate_gizmo_view,
        ]

    def refresh(self, context: bpy.types.Context):
        super().refresh(context)

        obj = context.object
        primitive = obj.data.heio_mesh.collision_primitives.active_element

        self.move_gizmo.base_hide = False
        self.rotate_gizmo_x.base_hide = primitive.shape_type == 'SPHERE'
        self.rotate_gizmo_y.base_hide = primitive.shape_type == 'SPHERE'
        self.rotate_gizmo_z.base_hide = primitive.shape_type != 'BOX'
        self.rotate_gizmo_view.base_hide = primitive.shape_type == 'SPHERE'

        hide = not cpt_gizmo_state.MANUAL_SELECT_MODE
        for gizmo in self.transform_gizmos:
            gizmo.hide = hide or gizmo.base_hide

    def draw_prepare(self, context):
        if not cpt_gizmo_state.MANUAL_SELECT_MODE:
            return

        obj = context.object
        primitive = obj.data.heio_mesh.collision_primitives.active_element

        # Translation

        matrix = obj.matrix_world.normalized()

        self.move_gizmo.matrix_basis = Matrix.Translation(matrix.to_translation())
        self.move_gizmo.position = matrix.to_quaternion() @ Vector(primitive.position)

        # Rotation(s)

        matrix = matrix @ Matrix.LocRotScale(
            primitive.position, primitive.rotation, None).normalized()

        self.rotate_gizmo_x.matrix_basis = matrix
        self.rotate_gizmo_y.matrix_basis = matrix
        self.rotate_gizmo_z.matrix_basis = matrix

        self.rotate_gizmo_view.matrix_basis = Matrix.Translation(
            matrix.to_translation())
        self.rotate_gizmo_view.view_rotation = matrix.to_quaternion()

        # Visibility

        any_modal = any([x.is_modal for x in self.transform_gizmos])

        for gizmo in self.transform_gizmos:
            gizmo.hide = (any_modal and not gizmo.is_modal) or gizmo.base_hide
