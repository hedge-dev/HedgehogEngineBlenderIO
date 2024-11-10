from . import (
	scene_properties,
    material_properties
)

to_register = [
    scene_properties.HEIO_Scene,

    material_properties.HEIO_MaterialParameterFloat,
    material_properties.HEIO_MaterialParameterFloatList,
    material_properties.HEIO_MaterialParameterBoolean,
    material_properties.HEIO_MaterialParameterBooleanList,
    material_properties.HEIO_MaterialTexture,
    material_properties.HEIO_MaterialTextureList,
    material_properties.HEIO_Material,
]
