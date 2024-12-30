from . import (
    lod_info_panel,
    sca_parameter_panel,
    scene_panel,
    armature_panel,
    node_panel,
    mesh_panel,
    collision_mesh_panel,
    material_panel,
    menus,
    viewport_toolbar
)

to_register = [
    sca_parameter_panel.HEIO_UL_SCAParameterList,

    lod_info_panel.HEIO_UL_LODInfoLevels,
    lod_info_panel.HEIO_MT_LODInfoLevelContextMenu,

    scene_panel.HEIO_PT_Scene,

    armature_panel.HEIO_PT_Armature,

    node_panel.HEIO_PT_Node_Bone,

    mesh_panel.HEIO_UL_MeshLayers,
    mesh_panel.HEIO_MT_MeshLayersContextMenu,
    mesh_panel.HEIO_UL_MeshGroups,
    mesh_panel.HEIO_MT_MeshGroupsContextMenu,
    mesh_panel.HEIO_PT_Mesh,

    collision_mesh_panel.HEIO_UL_CollisionInfoList,
	collision_mesh_panel.HEIO_MT_CollisionLayersContextMenu,
    collision_mesh_panel.HEIO_MT_CollisionTypesContextMenu,
    collision_mesh_panel.HEIO_MT_CollisionFlagsContextMenu,
    collision_mesh_panel.HEIO_PT_CollisionMesh,

    material_panel.HEIO_UL_ParameterList,
    material_panel.HEIO_UL_CustomParameterList,
    material_panel.HEIO_UL_TextureList,
    material_panel.HEIO_UL_CustomTextureList,
    material_panel.HEIO_PT_Material,

    menus.TOPBAR_MT_HEIO_Export,
    menus.TOPBAR_MT_HEIO_Import,
    menus.NativeHooks,

    viewport_toolbar.HEIO_PT_VTP_Mesh,
    viewport_toolbar.HEIO_PT_VTP_Material,
    viewport_toolbar.HEIO_PT_VTP_Info
]