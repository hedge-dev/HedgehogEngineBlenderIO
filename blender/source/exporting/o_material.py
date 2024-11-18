from typing import Iterable
import bpy

from . import o_enum, o_sca_parameters

from ..dotnet import SharpNeedle, System, HEIO_NET
from ..register.property_groups.material_properties import HEIO_Material

def convert_to_sharpneedle_materials(
		context: bpy.types.Context,
        materials: Iterable[bpy.types.Material]):

	converted = {}

	if context.scene.heio_scene.target_game == 'UNLEASHED':
		data_version = 1
	else:
		data_version = 3

	for material in materials:
		if material in converted:
			continue

		sn_material = SharpNeedle.MATERIAL()
		converted[material] = sn_material

		material_properties: HEIO_Material = material.heio_material

		sn_material.DataVersion = data_version
		sn_material.Name = material.name

		if data_version == 1 or len(material_properties.sca_parameters) == 0:
			sn_material.Root = None
		else:
			sn_material.SetupNodes()
			o_sca_parameters.convert_for_data(sn_material, material_properties.sca_parameters)

		sn_material.ShaderName = material_properties.shader_name
		sn_material.AlphaThreshold = int(material.alpha_threshold * 255)
		sn_material.NoBackFaceCulling = not material.use_backface_culling
		sn_material.UseAdditiveBlending = material_properties.use_additive_blending

		for parameter in material_properties.parameters:

			if parameter.value_type == 'BOOLEAN':
				sn_material.BoolParameters.Add(
					parameter.name,
					HEIO_NET.PYTHON_HELPERS.CreateBoolParameter(parameter.boolean_value)
				)

			else:
				value = System.VECTOR4(
					parameter.float_value[0],
					parameter.float_value[1],
					parameter.float_value[2],
					parameter.float_value[3]
				)

				sn_material.FloatParameters.Add(
					parameter.name,
					HEIO_NET.PYTHON_HELPERS.CreateFloatParameter(value)
				)

		sn_material.Texset.Name = material.name

		for i, texture in enumerate(material_properties.textures):
			if texture.image is None:
				continue

			sn_texture = SharpNeedle.TEXTURE()

			sn_texture.Name = f"{material.name}-{i:04}"
			sn_texture.PictureName = texture.image.name
			sn_texture.Type = texture.name
			sn_texture.TexCoordIndex = texture.texcoord_index
			sn_texture.WrapModeU = o_enum.to_wrap_mode(texture.wrapmode_u)
			sn_texture.WrapModeV = o_enum.to_wrap_mode(texture.wrapmode_v)

			sn_material.Texset.Textures.Add(sn_texture)

	return converted