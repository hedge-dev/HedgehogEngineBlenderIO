from typing import Iterable
import bpy

from . import i_enum, i_image, i_sca_parameters

from ..register import definitions
from ..register.property_groups.material_properties import (
    HEIO_Material,
    HEIO_MaterialTextureList,
    HEIO_MaterialParameterList
)

from ..utility.material_setup import (
    setup_and_update_materials
)

from ..utility.general import get_addon_preferences


def _convert_textures(
        sn_texture_set: any,
        output: HEIO_MaterialTextureList,
        create_missing: bool,
        image_loader: i_image.ImageLoader):

    name_indices = {}
    created_missing = False

    for sn_texture in sn_texture_set.Textures:

        from_index = 0
        if sn_texture.Type in name_indices:
            from_index = name_indices[sn_texture.Type] + 1

        index = output.find_next_index(sn_texture.Type, from_index)

        if index >= 0:
            name_indices[sn_texture.Type] = index
            texture = output[index]
        elif create_missing:
            name_indices[sn_texture.Type] = len(output)
            texture = output.new()
            texture.name = sn_texture.Type
            created_missing = True
        else:
            continue

        texture.texcoord_index = sn_texture.TexCoordIndex
        texture.wrapmode_u = i_enum.from_wrap_mode(sn_texture.WrapModeU)
        texture.wrapmode_v = i_enum.from_wrap_mode(sn_texture.WrapModeV)
        texture.image = image_loader.get_image(texture, sn_texture.PictureName)

    return created_missing


def _convert_parameters(sn_parameters: any, output: HEIO_MaterialParameterList, types: list[str], create_missing: bool, conv):
    created_missing = False

    for sn_key_parameter in sn_parameters:
        parameter = output.find_next(sn_key_parameter.Key, 0, types)

        if parameter is None:
            if create_missing:
                parameter = output.new()
                parameter.name = sn_key_parameter.Key
                parameter.value_type = types[0]
                created_missing = True
            else:
                continue

        value = sn_key_parameter.Value.Value
        if conv is not None:
            value = conv(value)

        setattr(parameter, parameter.value_type.lower() + "_value", value)

    return created_missing


def convert_sharpneedle_materials(
        context: bpy.types.Context,
        sn_materials: Iterable[any],
        create_undefined_parameters: bool,
        use_existing_images: bool,
        invert_normal_map_y_channel: bool,
        textures_path: str | None):

    converted: dict[any, bpy.types.Material] = {}
    target_definition = definitions.get_target_definition(context)

    for sn_material in sn_materials:
        if sn_material in converted:
            continue

        material = bpy.data.materials.new(sn_material.Name)
        converted[sn_material] = material

        material_properties: HEIO_Material = material.heio_material

        if sn_material.ShaderName[-1] == ']':
            index = sn_material.ShaderName.index('[')
            material_properties.shader_name = sn_material.ShaderName[:index]
            material_properties.variant_name = sn_material.ShaderName[(index+1):-1]
        else:
            material_properties.shader_name = sn_material.ShaderName

        material_properties.use_additive_blending = sn_material.UseAdditiveBlending
        material.alpha_threshold = sn_material.AlphaThreshold / 255.0
        material.use_backface_culling = not sn_material.NoBackFaceCulling

        if target_definition is not None and material_properties.shader_name in target_definition.shaders.definitions:
            material_properties.custom_shader = False
            material_properties.setup_definition(
                target_definition.shaders.definitions[material_properties.shader_name]
            )
        else:
            material_properties.custom_shader = True

    setup_and_update_materials(context, converted.values())

    ntsp_dir = ""

    if target_definition.uses_ntsp:
        pref = get_addon_preferences(context)
        ntsp_dir = getattr(pref, "ntsp_dir_" + target_definition.identifier.lower())

    image_loader = i_image.ImageLoader(use_existing_images, invert_normal_map_y_channel)
    image_loader.load_images_from_sn_materials(sn_materials, textures_path, ntsp_dir)

    for sn_material, material in converted.items():
        material_properties: HEIO_Material = material.heio_material
        create_missing = create_undefined_parameters or material_properties.custom_shader

        created_missing = _convert_parameters(
            sn_material.FloatParameters,
            material_properties.parameters,
            ['FLOAT', 'COLOR'],
            create_missing,
            lambda x: (x.X, x.Y, x.Z, x.W)
        )

        created_missing |= _convert_parameters(
            sn_material.BoolParameters,
            material_properties.parameters,
            ['BOOLEAN'],
            create_missing,
            None
        )

        created_missing |= _convert_textures(
            sn_material.Texset,
            material_properties.textures,
            create_missing,
            image_loader
        )

        i_sca_parameters.convert_from_data(
            sn_material,
            material_properties.sca_parameters,
            context,
            "material")

        if created_missing:
            material_properties.custom_shader = True

    return converted
