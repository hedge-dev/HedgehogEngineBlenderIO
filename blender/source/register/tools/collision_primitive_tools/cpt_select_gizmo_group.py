import bpy

from . import cpt_gizmo_state
from .cpt_select_gizmo import (
    HEIO_GT_CollisionPrimitive_Select,
    HEIO_OT_CollisionPrimitive_GizmoClicked
)


class BaseCollisionPrimitiveSelectGizmoGroup(bpy.types.GizmoGroup):
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'WINDOW'
    bl_options = {'3D', 'SCALE'}

    primitive_gizmos: list[bpy.types.Gizmo]
    current_object: bpy.types.Object | None

    @classmethod
    def poll(cls, context):
        obj = context.object
        return (
            obj is not None
            and obj.type == 'MESH'
            and len(obj.data.heio_collision_mesh.primitives) > 0
        )

    def setup(self, context):
        if hasattr(self, "current_object"):
            return

        self.primitive_gizmos = []
        self.current_object = None

    def _create_select_gizmos(self, primitives):
        primitive_count = len(primitives)

        while len(self.primitive_gizmos) < primitive_count:
            gizmo = self.gizmos.new(
                HEIO_GT_CollisionPrimitive_Select.bl_idname)

            op = gizmo.target_set_operator(
                HEIO_OT_CollisionPrimitive_GizmoClicked.bl_idname)
            op.select_index = len(self.primitive_gizmos)

            gizmo.alpha = 0
            gizmo.color_highlight = 1, 1, 1
            gizmo.alpha_highlight = 0.15
            gizmo.use_draw_modal = True

            self.primitive_gizmos.append(gizmo)

    def _object_update(self, obj):
        if obj == self.current_object:
            return

        self.current_object = obj

    def refresh(self, context):
        obj = context.object
        primitives = obj.data.heio_collision_mesh.primitives

        self._create_select_gizmos(primitives)
        self._object_update(obj)

        for i, gizmo in enumerate(self.primitive_gizmos):
            if i >= len(primitives) or (cpt_gizmo_state.MANUAL_SELECT_MODE and i == primitives.active_index):
                gizmo.hide = True
                continue

            gizmo.hide = False
            primitive = primitives[i]

            gizmo.shape_type = primitive.shape_type
            gizmo.position = primitive.position
            gizmo.rotation = primitive.rotation
            gizmo.dimensions = primitive.dimensions
            gizmo.matrix_basis = obj.matrix_world.normalized()


class HEIO_GGT_CollisionPrimitive_Select(BaseCollisionPrimitiveSelectGizmoGroup):
    bl_idname = "heio.ggt.collision_primitive_select"
    bl_label = "HEIO Collision Primitive select"
