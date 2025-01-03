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

from .cpt_select_gizmo_group import BaseCollisionPrimitiveSelectGizmoGroup


class HEIO_GGT_CollisionPrimitive_Transform(BaseCollisionPrimitiveSelectGizmoGroup):
    bl_idname = "heio.ggt.collision_primitive_edit"
    bl_label = "HEIO Collision Primitive edit"

    move_gizmo: HEIO_GT_CollisionPrimitive_Move

    def setup(self, context):
        super().setup(context)

        if hasattr(self, "move_gizmo"):
            return

        self.move_gizmo = self.gizmos.new(HEIO_GT_CollisionPrimitive_Move.bl_idname)
        self.move_gizmo.target_set_operator(HEIO_OT_CollisionPrimitive_Move.bl_idname)
        self.move_gizmo.use_draw_modal = True

        self.rotate_gizmo_x = self.gizmos.new(HEIO_GT_CollisionPrimitive_Rotate.bl_idname)
        op = self.rotate_gizmo_x.target_set_operator(HEIO_OT_CollisionPrimitive_Rotate.bl_idname)
        op.mode = 'X'
        self.rotate_gizmo_x.set_mode('X')
        self.rotate_gizmo_x.use_draw_modal = True

        self.rotate_gizmo_y = self.gizmos.new(HEIO_GT_CollisionPrimitive_Rotate.bl_idname)
        op = self.rotate_gizmo_y.target_set_operator(HEIO_OT_CollisionPrimitive_Rotate.bl_idname)
        op.mode = 'Y'
        self.rotate_gizmo_y.set_mode('Y')
        self.rotate_gizmo_y.use_draw_modal = True

        self.rotate_gizmo_z = self.gizmos.new(HEIO_GT_CollisionPrimitive_Rotate.bl_idname)
        op = self.rotate_gizmo_z.target_set_operator(HEIO_OT_CollisionPrimitive_Rotate.bl_idname)
        op.mode = 'Z'
        self.rotate_gizmo_z.set_mode('Z')
        self.rotate_gizmo_z.use_draw_modal = True

        self.rotate_gizmo_view = self.gizmos.new(HEIO_GT_CollisionPrimitive_Rotate.bl_idname)
        op = self.rotate_gizmo_view.target_set_operator(HEIO_OT_CollisionPrimitive_Rotate.bl_idname)
        op.mode = 'VIEW'
        self.rotate_gizmo_view.set_mode('VIEW')
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

        hide = not cpt_gizmo_state.MANUAL_SELECT_MODE
        for gizmo in self.transform_gizmos:
            gizmo.hide = hide

        if not cpt_gizmo_state.MANUAL_SELECT_MODE:
            return

        obj = context.object
        matrix = obj.matrix_world.normalized()

        pos = matrix.to_translation()
        self.move_gizmo.matrix_basis = Matrix.Translation(pos)
        self.rotate_gizmo_view.matrix_basis = matrix


    def draw_prepare(self, context):
        if not cpt_gizmo_state.MANUAL_SELECT_MODE:
            return

        obj = context.object
        primitive = obj.data.heio_collision_mesh.primitives.active_element

        self.move_gizmo.position = Vector(primitive.position)

        matrix = obj.matrix_world.normalized() @ Matrix.LocRotScale(primitive.position, primitive.rotation, None).normalized()
        self.rotate_gizmo_x.matrix_basis = matrix
        self.rotate_gizmo_y.matrix_basis = matrix
        self.rotate_gizmo_z.matrix_basis = matrix

        any_modal = any([x.is_modal for x in self.transform_gizmos])

        for gizmo in self.transform_gizmos:
            gizmo.hide = any_modal and not gizmo.is_modal


