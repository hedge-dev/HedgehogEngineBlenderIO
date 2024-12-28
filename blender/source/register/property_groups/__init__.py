from . import (
	addon_preferences,
	sca_parameter_properties,
	lod_info_properties,
	scene_properties,
	armature_properties,
	node_properties,
	mesh_properties,
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

    mesh_properties.HEIO_Layer,
	mesh_properties.HEIO_LayerList,
	mesh_properties.HEIO_Meshgroup,
	mesh_properties.HEIO_MeshgroupList,
    mesh_properties.HEIO_Mesh,

    material_parameter_properties.HEIO_MaterialParameter,
    material_parameter_properties.HEIO_MaterialParameterList,

    material_texture_properties.HEIO_MaterialTexture,
    material_texture_properties.HEIO_MaterialTextureList,

    material_properties.HEIO_Material,
]
