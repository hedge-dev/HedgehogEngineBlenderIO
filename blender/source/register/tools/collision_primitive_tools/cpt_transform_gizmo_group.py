import bpy
from mathutils import Matrix, Vector

from . import cpt_gizmo_state
from .cpt_move_gizmo import (
    HEIO_GT_CollisionPrimitive_Move,
    HEIO_OT_CollisionPrimitive_Move
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

    def refresh(self, context: bpy.types.Context):
        super().refresh(context)

        hide = not cpt_gizmo_state.MANUAL_SELECT_MODE
        self.move_gizmo.hide = hide

        if not cpt_gizmo_state.MANUAL_SELECT_MODE:
            return

        obj = context.object
        pos = obj.matrix_world.normalized().to_translation()
        self.move_gizmo.matrix_basis = Matrix.Translation(pos)


    def draw_prepare(self, context):
        if not cpt_gizmo_state.MANUAL_SELECT_MODE:
            return

        obj = context.object
        primitive = obj.data.heio_collision_mesh.primitives.active_element

        self.move_gizmo.position = Vector(primitive.position)



