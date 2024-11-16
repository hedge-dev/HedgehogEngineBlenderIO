from . import (
	addon_preferences,
	sca_parameter_properties,
	scene_properties,
	material_parameter_properties,
	material_texture_properties,
    material_properties
)

to_register = [
	addon_preferences.HEIO_AddonPreferences,

    sca_parameter_properties.HEIO_SCA_Parameter,
	sca_parameter_properties.HEIO_SCA_Parameters,

    scene_properties.HEIO_Scene,

    material_parameter_properties.HEIO_MaterialParameterFloat,
    material_parameter_properties.HEIO_MaterialParameterFloatList,
    material_parameter_properties.HEIO_MaterialParameterBoolean,
    material_parameter_properties.HEIO_MaterialParameterBooleanList,

    material_texture_properties.HEIO_MaterialTexture,
    material_texture_properties.HEIO_MaterialTextureList,

    material_properties.HEIO_Material,
]
