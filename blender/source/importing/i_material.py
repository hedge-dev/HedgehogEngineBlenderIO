from typing import Iterable
import bpy

from . import i_enum, i_sca_parameters

from ..dotnet import HEIO_NET
from ..register import definitions
from ..register.property_groups.material_properties import (
    HEIO_Material,
    HEIO_MaterialTextureList,
    HEIO_MaterialParameterList
)

from ..utility.material_setup import (
    setup_and_update_materials,
    get_first_connected_socket
)

from ..utility.general import get_addon_preferences


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


def _import_image_dds_addon(image_name: str, net_image):
    from blender_dds_addon.ui.import_dds import load_dds
    import os

    if net_image.StreamedData is not None:
        from tempfile import TemporaryDirectory

        byte_data = bytes(net_image.StreamedData)

        with TemporaryDirectory() as temp_dir:
            temp = os.path.join(temp_dir, image_name + ".dds")

            with open(temp, "wb") as temp_file:
                temp_file.write(byte_data)

            image = load_dds(temp)

    else:
        image = load_dds(net_image.Filepath)

    image.name = image_name
    image.filepath = os.path.splitext(net_image.Filepath)[0] + ".tga"

    return image


def _import_image_native(image_name: str, net_image):
    if net_image.StreamedData is not None:
        image = bpy.data.images.new(image_name, 1, 1)
        image.source = 'FILE'
        image.filepath = net_image.Filepath
        byte_data = bytes(net_image.StreamedData)
        image.pack(data=byte_data, data_len=len(byte_data))

    else:
        image = bpy.data.images.load(net_image.Filepath, check_existing=True)
        image.name = image_name

    return image


def _load_image(
        texture,
        image_name: str,
        net_images: dict[str, any],):

    image = None
    node: bpy.types.ShaderNodeTexImage = texture.image_node

    if image_name in net_images:
        net_image = net_images[image_name]

        if "blender_dds_addon" in bpy.context.preferences.addons.keys():
            image = _import_image_dds_addon(image_name, net_image)
        else:
            image = _import_image_native(image_name, net_image)

    if image is None:
        # placeholder texture
        image = bpy.data.images.new(
            image_name,
            16,
            16,
            alpha=True)

        image.source = 'GENERATED'
        image.generated_color = _get_placeholder_image_color(node)

    if node is not None:
        label_colorspace = node.label.split(";")[0]
        if label_colorspace in ["sRGB", "Non-Color"]:
            image.colorspace_settings.name = label_colorspace

    image.update()

    return image


def _convert_textures(
        sn_texture_set: any,
        output: HEIO_MaterialTextureList,
        create_missing: bool,
        use_existing_images: bool,
        images: dict[str, any],
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
                    texture,
                    sn_texture.PictureName,
                    images)

                loaded_images[sn_texture.PictureName] = image
                texture.image = image

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

    images = HEIO_NET.IMAGE.LoadMaterialImages(
        sn_materials, textures_path, ntsp_dir)

    loaded_textures = {}

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
            use_existing_images,
            images,
            loaded_textures
        )

        i_sca_parameters.convert_from_data(
            sn_material,
            material_properties.sca_parameters,
            context,
            "material")

        if created_missing:
            material_properties.custom_shader = True

    return converted
