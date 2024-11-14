from typing import Iterable
import os
import bpy

from . import i_enum

from ..dotnet import HEIO_NET
from ..register.definitions.shader_definitions import SHADER_DEFINITIONS
from ..register.property_groups.material_properties import (
    HEIO_Material,
    HEIO_MaterialTextureList
)

from ..utility.material_setup import (
    setup_and_update_materials,
    get_first_connected_socket
)


def _get_placeholder_image_color(node: bpy.types.ShaderNodeTexImage):
    if node is None:
        return (1, 1, 1, 1)

    rgb_connection = get_first_connected_socket(node.outputs[0])
    alpha_connection = get_first_connected_socket(node.outputs[1])

    red = green = blue = alpha = 1

    if rgb_connection is not None:
        if rgb_connection.type == 'VALUE':
            red = green = blue = rgb_connection.default_value
        elif rgb_connection.type in ['RGBA', 'VECTOR']:
            red = rgb_connection.default_value[0]
            green = rgb_connection.default_value[1]
            blue = rgb_connection.default_value[2]

    if alpha_connection is not None:
        if alpha_connection.type == 'VALUE':
            alpha = alpha_connection.default_value
        elif alpha_connection.type in ['RGBA', 'VECTOR']:
            rgb = alpha_connection.default_value
            alpha = 0.2989 * rgb[0] + 0.5870 * rgb[1] + 0.1140 * rgb[2]

    return (red, green, blue, alpha)


def _load_image(texture, image_name: str, textures_path: str):
    image = None

    if textures_path is not None:
        image_file_path = os.path.join(
            textures_path, image_name + ".dds")

        image_data = HEIO_NET.IMAGE.LoadDDS(image_file_path)
        if image_data is not None:
            image = bpy.data.images.new(
                image_name,
                image_data.Item1,
                image_data.Item2,
                alpha=image_data.Item4,
                float_buffer=image_data.Item5
            )

            image.pixels = image_data.Item3

    if image is None:
        # placeholder texture
        image = bpy.data.images.new(
            image_name,
            16,
            16,
            alpha=True)

        image.source = 'GENERATED'
        image.generated_color = _get_placeholder_image_color(texture.image_node)

    image.update()
    image.pack()

    return image


def _convert_textures(
        sn_texture_set: any,
        output: HEIO_MaterialTextureList,
        create_missing: bool,
        use_existing_images: bool,
        textures_path: str | None,
        loaded_images: dict[str, bpy.types.Image]):

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

        if len(sn_texture.PictureName.strip()) > 0:
            if sn_texture.PictureName in loaded_images:
                texture.image = loaded_images[sn_texture.PictureName]
            elif use_existing_images and sn_texture.PictureName in bpy.data.images:
                texture.image = bpy.data.images[sn_texture.PictureName]
            else:
                image = _load_image(
                    texture, sn_texture.PictureName, textures_path)
                loaded_images[sn_texture.PictureName] = image
                texture.image = image

    return created_missing


def _convert_parameters(sn_parameters: any, output, create_missing: bool, conv):
    created_missing = False

    for sn_key_parameter in sn_parameters:
        if sn_key_parameter.Key in output:
            parameter = output[sn_key_parameter.Key]
        elif create_missing:
            parameter = output.new()
            parameter.name = sn_key_parameter.Key
            created_missing = True
        else:
            continue

        if conv is not None:
            parameter.value = conv(sn_key_parameter.Value.Value)
        else:
            parameter.value = sn_key_parameter.Value.Value

    return created_missing


def convert_sharpneedle_materials(
        sn_materials: Iterable[any],
        context: bpy.types.Context,
        create_undefined_parameters: bool,
        use_existing_images: bool,
        textures_path: str | None):

    materials: dict[any, bpy.types.Material] = {}

    for sn_material in sn_materials:
        if sn_material in materials:
            continue

        material = bpy.data.materials.new(sn_material.Name)
        materials[sn_material] = material

        material_properties: HEIO_Material = material.heio_material

        material_properties.shader_name = sn_material.ShaderName
        material_properties.use_additive_blending = sn_material.UseAdditiveBlending
        material.alpha_threshold = sn_material.AlphaThreshold
        material.use_backface_culling = not sn_material.NoBackFaceCulling

        shader_definitions = SHADER_DEFINITIONS[context.scene.heio_scene.target_game]
        if material_properties.shader_name in shader_definitions.definitions:
            material_properties.custom_shader = False
            material_properties.setup_definition_parameters_and_textures(
                shader_definitions.definitions[material_properties.shader_name]
            )
        else:
            material_properties.custom_shader = True

    setup_and_update_materials(context, materials.values())

    loaded_textures = {}

    for sn_material, material in materials.items():
        material_properties: HEIO_Material = material.heio_material
        create_missing = create_undefined_parameters or material_properties.custom_shader

        created_missing_floats = _convert_parameters(
            sn_material.FloatParameters,
            material_properties.float_parameters,
            create_missing,
            lambda x: (x.X, x.Y, x.Z, x.W)
        )

        created_missing_booleans = _convert_parameters(
            sn_material.BoolParameters,
            material_properties.boolean_parameters,
            create_missing,
            None
        )

        created_missing_textures = _convert_textures(
            sn_material.Texset,
            material_properties.textures,
            create_missing,
            use_existing_images,
            textures_path,
            loaded_textures
        )

        if created_missing_floats or created_missing_booleans or created_missing_textures:
            material_properties.custom_shader = True

    return materials
