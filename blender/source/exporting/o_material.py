from typing import Iterable
import bpy

from . import o_enum, o_sca_parameters

from ..dotnet import SharpNeedle, System, HEIO_NET
from ..register.property_groups.material_properties import HEIO_Material
from ..register.definitions import TargetDefinition

def convert_to_sharpneedle_materials(
        target_definition: TargetDefinition,
        materials: Iterable[bpy.types.Material]):

    converted = {}

    for material in materials:
        if material in converted:
            continue

        sn_material = SharpNeedle.MATERIAL()
        converted[material] = sn_material

        material_properties: HEIO_Material = material.heio_material

        sn_material.DataVersion = target_definition.data_versions.material
        sn_material.Name = material.name

        if target_definition.data_versions.material_sample_chunk == 1:
            sn_material.Root = None
        else:
            sn_material.SetupNodes()
            o_sca_parameters.convert_for_data(
                sn_material, material_properties.sca_parameters)

        sn_material.ShaderName = material_properties.shader_name
        if len(material_properties.variant_name) > 0:
            sn_material.ShaderName += f"[{material_properties.variant_name}]"

        sn_material.AlphaThreshold = int(material.alpha_threshold * 255)
        sn_material.NoBackFaceCulling = not material.use_backface_culling
        sn_material.UseAdditiveBlending = material_properties.use_additive_blending

        for parameter in material_properties.parameters:

            if parameter.value_type == 'BOOLEAN':
                sn_material.BoolParameters.Add(
                    parameter.name,
                    HEIO_NET.PYTHON_HELPERS.CreateBoolParameter(
                        parameter.boolean_value)
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
