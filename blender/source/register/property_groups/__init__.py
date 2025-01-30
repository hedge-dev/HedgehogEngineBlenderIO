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
    material_properties,
    image_properties
)

to_register = [
    addon_preferences.HEIO_AddonPreferences,

    sca_parameter_properties.HEIO_SCA_Parameter,
    sca_parameter_properties.HEIO_SCA_Parameters,
	sca_parameter_properties.HEIO_SCAP_MassEdit,

    lod_info_properties.HEIO_LODInfoLevel,
    lod_info_properties.HEIO_LODInfoLevelList,
    lod_info_properties.HEIO_LODInfo,

    scene_properties.HEIO_Scene,

    armature_properties.HEIO_Armature,

    node_properties.HEIO_Node,

    mesh_properties.HEIO_RenderLayer,
    mesh_properties.HEIO_RenderLayerList,
    mesh_properties.HEIO_CollisionLayer,
    mesh_properties.HEIO_CollisionType,
    mesh_properties.HEIO_CollisionTypeList,
    mesh_properties.HEIO_CollisionFlag,
    mesh_properties.HEIO_CollisionFlagList,
    mesh_properties.HEIO_MeshGroup,
    mesh_properties.HEIO_MeshGroupList,
    mesh_properties.HEIO_CollisionPrimitive,
    mesh_properties.HEIO_CollisionPrimitiveList,
    mesh_properties.HEIO_Mesh,

    material_parameter_properties.HEIO_MaterialParameter,
    material_parameter_properties.HEIO_MaterialParameterList,

    material_texture_properties.HEIO_MaterialTexture,
    material_texture_properties.HEIO_MaterialTextureList,

    material_properties.HEIO_Material,

    image_properties.HEIO_Image
]
