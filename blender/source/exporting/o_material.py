import os
from typing import Iterable
import bpy

from . import o_enum, o_sca_parameters, o_image, o_util

from ..dotnet import SharpNeedle, System, HEIO_NET
from ..register.property_groups.material_properties import HEIO_Material
from ..register.definitions import TargetDefinition
from ..utility import progress_console


class MaterialProcessor:

    _target_definition: TargetDefinition

    _context: bpy.types.Context
    _auto_sca_parameters: bool
    _image_mode: str
    _invert_normal_map_y_channel: bool

    _output: dict[bpy.types.Material, any]

    def __init__(
            self,
            target_definition: TargetDefinition,
            auto_sca_parameters: bool,
            context: bpy.types.Context,
            image_mode: str,
            nrm_invert_y_channel: str):

        self._target_definition = target_definition
        self._auto_sca_parameters = auto_sca_parameters
        self._context = context
        self._image_mode = image_mode

        self._invert_normal_map_y_channel = (
            nrm_invert_y_channel == "INVERT"
            or (
                nrm_invert_y_channel == "AUTO"
                and self._target_definition.hedgehog_engine_version == 1
            )
        )

        self._output = {}

    def convert_materials(
            self,
            materials: Iterable[bpy.types.Material]):

        progress_console.start("Converting Materials", len(materials))

        converted = []

        sca_defaults = {}
        if self._auto_sca_parameters and self._target_definition.data_versions.sample_chunk >= 2 and self._target_definition.sca_parameters is not None:
            sca_defaults = self._target_definition.sca_parameters.material_defaults

        for i, material in enumerate(materials):
            progress_console.update(f"Converting material \"{material.name}\"", i)

            if material in self._output:
                converted.append(self._output[material])
                continue

            sn_material = SharpNeedle.MATERIAL()
            self._output[material] = sn_material
            converted.append(sn_material)

            material_properties: HEIO_Material = material.heio_material

            sn_material.DataVersion = self._target_definition.data_versions.material
            sn_material.Name = o_util.correct_filename(material.name)

            if self._target_definition.data_versions.sample_chunk == 1:
                sn_material.Root = None
            else:
                sn_material.SetupNodes()
                o_sca_parameters.convert_for_data(
                    sn_material, material_properties.sca_parameters, sca_defaults)

            sn_material.ShaderName = material_properties.shader_name
            if len(material_properties.variant_name) > 0:
                sn_material.ShaderName += f"[{material_properties.variant_name}]"

            sn_material.AlphaThreshold = int(material.alpha_threshold * 255)
            sn_material.NoBackFaceCulling = not material.use_backface_culling
            sn_material.BlendMode = o_enum.to_material_blend_mode(material_properties.blend_mode)

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

            sn_material.Texset.Name = sn_material.Name

            for j, texture in enumerate(material_properties.textures):
                if texture.image is None:
                    continue

                sn_texture = SharpNeedle.TEXTURE()

                sn_texture.Name = f"{sn_material.Name}-{j:04}"
                sn_texture.PictureName = o_util.correct_filename(texture.image.name)
                sn_texture.Type = texture.name
                sn_texture.TexCoordIndex = texture.texcoord_index
                sn_texture.WrapModeU = o_enum.to_wrap_mode(texture.wrapmode_u)
                sn_texture.WrapModeV = o_enum.to_wrap_mode(texture.wrapmode_v)

                sn_material.Texset.Textures.Add(sn_texture)

        progress_console.end()

        return converted

    def get_converted_material(self, material):
        return self._output[material]

    def write_output_to_files(self, directory: str):
        progress_console.start("Writing Materials to files", len(self._output))

        for i, sn_material in enumerate(self._output.values()):
            progress_console.update(f"Writing material \"{sn_material.Name}\"", i)

            filepath = os.path.join(
                directory, sn_material.Name + ".material")

            SharpNeedle.RESOURCE_EXTENSIONS.Write(sn_material, filepath)

        progress_console.end()

        self.write_output_images_to_files(directory)

    def write_output_images_to_files(self, directory):
        if self._image_mode == 'NONE':
            return

        o_image.export_material_images(
            self._output.keys(),
            self._context,
            self._image_mode,
            self._invert_normal_map_y_channel,
            directory
        )
