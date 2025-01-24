import bpy

from . import cpt_gizmo_state
from .cpt_select_gizmo import (
    HEIO_GT_CollisionPrimitive_Select,
    HEIO_OT_CollisionPrimitive_GizmoClicked
)

from ...property_groups.mesh_properties import MESH_DATA_TYPES


class BaseCollisionPrimitiveSelectGizmoGroup(bpy.types.GizmoGroup):
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'WINDOW'
    bl_options = {'3D'}

    primitive_gizmos: list[bpy.types.Gizmo]

    @classmethod
    def poll(cls, context):
        obj = context.object
        return (
            context.space_data.overlay.show_overlays
            and context.screen.heio_collision_primitives.show_primitives
            and context.mode == 'OBJECT'
            and obj is not None
            and obj.visible_get(view_layer=context.view_layer)
            and obj.type not in MESH_DATA_TYPES
            and len(obj.data.heio_mesh.collision_primitives) > 0
        )

    def setup(self, context):
        if hasattr(self, "primitive_gizmos"):
            return

        self.primitive_gizmos = []

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
            gizmo.use_draw_scale = False

            self.primitive_gizmos.append(gizmo)

    def _object_update(self, obj):
        if obj == cpt_gizmo_state.CURRENT_OBJECT:
            return

        cpt_gizmo_state.CURRENT_OBJECT = obj
        cpt_gizmo_state.MANUAL_SELECT_MODE = False

    def refresh(self, context):
        obj = context.object
        primitives = obj.data.heio_mesh.collision_primitives

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
