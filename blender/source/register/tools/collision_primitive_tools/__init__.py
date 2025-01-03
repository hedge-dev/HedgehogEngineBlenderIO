from . import (
	cpt_shaders,
	cpt_overlay_properties,
	cpt_renderer,
	cpt_select_gizmo,
	cpt_select_gizmo_group,
	cpt_move_gizmo,
	cpt_rotate_gizmo,
	cpt_transform_gizmo_group,
	cpt_workspace_tools,
)

to_register = [
	cpt_shaders.CollisionMeshShaders,

	cpt_overlay_properties.HEIO_View3DOverlay_CollisionPrimitive,

	cpt_renderer.HEIO_3D_CollisionPrimitiveRenderer,

	cpt_select_gizmo.HEIO_OT_CollisionPrimitive_GizmoClicked,
	cpt_select_gizmo.HEIO_GT_CollisionPrimitive_Select,

	cpt_select_gizmo_group.HEIO_GGT_CollisionPrimitive_Select,

	cpt_move_gizmo.HEIO_OT_CollisionPrimitive_Move,
	cpt_move_gizmo.HEIO_GT_CollisionPrimitive_Move,

	cpt_rotate_gizmo.HEIO_OT_CollisionPrimitive_Rotate,
	cpt_rotate_gizmo.HEIO_GT_CollisionPrimitive_Rotate,

	cpt_transform_gizmo_group.HEIO_GGT_CollisionPrimitive_Transform,

	cpt_workspace_tools.CollisionPrimitiveWSTRegister
]