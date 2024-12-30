from . import (
	addon_preferences,
	sca_parameter_properties,
	lod_info_properties,
	scene_properties,
	armature_properties,
	node_properties,
	mesh_properties,
	collision_mesh_properties,
	material_parameter_properties,
	material_texture_properties,
    material_properties
)

to_register = [
	addon_preferences.HEIO_AddonPreferences,

    sca_parameter_properties.HEIO_SCA_Parameter,
	sca_parameter_properties.HEIO_SCA_Parameters,

	lod_info_properties.HEIO_LODInfoLevel,
	lod_info_properties.HEIO_LODInfoLevelList,
	lod_info_properties.HEIO_LODInfo,

    scene_properties.HEIO_Scene,

	armature_properties.HEIO_Armature,

	node_properties.HEIO_Node,

    mesh_properties.HEIO_MeshInfo,
	mesh_properties.HEIO_MeshLayerList,
	mesh_properties.HEIO_MeshGroupList,
    mesh_properties.HEIO_Mesh,

	collision_mesh_properties.HEIO_CollisionType,
	collision_mesh_properties.HEIO_CollisionTypeList,
	collision_mesh_properties.HEIO_CollisionFlag,
	collision_mesh_properties.HEIO_CollisionFlagList,
	collision_mesh_properties.HEIO_CollisionLayer,
	collision_mesh_properties.HEIO_CollisionLayerList,
	collision_mesh_properties.HEIO_CollisionMesh,

    material_parameter_properties.HEIO_MaterialParameter,
    material_parameter_properties.HEIO_MaterialParameterList,

    material_texture_properties.HEIO_MaterialTexture,
    material_texture_properties.HEIO_MaterialTextureList,

    material_properties.HEIO_Material,
]
