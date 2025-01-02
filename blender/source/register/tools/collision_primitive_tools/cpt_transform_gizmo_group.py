import bpy

from . import cpt_gizmo_state
from .cpt_move_gizmo import (
    HEIO_GT_CollisionPrimitive_Move,
    HEIO_OT_CollisionPrimitive_Move
)

from .cpt_select_gizmo_group import BaseCollisionPrimitiveSelectGizmoGroup


class HEIO_GGT_CollisionPrimitive_Transform(BaseCollisionPrimitiveSelectGizmoGroup):
    bl_idname = "heio.ggt.collision_primitive_edit"
    bl_label = "HEIO Collision Primitive edit"

    move_gizmo: bpy.types.Gizmo

    def setup(self, context):
        super().setup(context)

        if hasattr(self, "move_gizmo"):
            return

        self.move_gizmo = self.gizmos.new(HEIO_GT_CollisionPrimitive_Move.bl_idname)
        self.move_gizmo.target_set_operator(HEIO_OT_CollisionPrimitive_Move.bl_idname)
        self.move_gizmo.use_draw_modal = True

    def draw_prepare(self, context):
        hide = not cpt_gizmo_state.MANUAL_SELECT_MODE
        self.move_gizmo.hide = hide


