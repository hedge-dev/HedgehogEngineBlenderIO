import os
from typing import Iterable
import bpy
from ctypes import pointer

from . import o_sca_parameters, o_image, o_util

from ..external import HEIONET, util, enums, TPointer, CMaterial, CBoolMaterialParameter, CFloatMaterialParameter, CVector4, CTexture
from ..register.property_groups.material_properties import HEIO_Material
from ..register.definitions import TargetDefinition
from ..utility import progress_console


class MaterialProcessor:

    _target_definition: TargetDefinition

    _context: bpy.types.Context
    _auto_sca_parameters: bool
    _material_mode: str
    _image_mode: str
    _invert_normal_map_y_channel: bool

    _output: dict[bpy.types.Material, TPointer[CMaterial]]

    def __init__(
            self,
            target_definition: TargetDefinition,
            auto_sca_parameters: bool,
            context: bpy.types.Context,
            material_mode: str,
            image_mode: str,
            nrm_invert_y_channel: str):

        self._target_definition = target_definition
        self._auto_sca_parameters = auto_sca_parameters
        self._context = context
        self._material_mode = material_mode
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

            c_material = CMaterial()
            c_material_pointer = pointer(c_material)
            self._output[material] = c_material_pointer
            converted.append(c_material_pointer)

            material_properties: HEIO_Material = material.heio_material

            c_material.data_version = self._target_definition.data_versions.material
            c_material.name = o_util.correct_filename(material.name)

            if self._target_definition.data_versions.sample_chunk != 1:
                c_material.root_node = o_sca_parameters.setup("Material", c_material.data_version)
                o_sca_parameters.convert_to_node(
                    c_material.root_node[0].child, 
                    material_properties.sca_parameters, 
                    sca_defaults
                )

            c_material.shader_name = material_properties.shader_name
            if len(material_properties.variant_name) > 0:
                c_material.shader_name += f"[{material_properties.variant_name}]"

            c_material.alpha_threshold = int(material.alpha_threshold * 255)
            c_material.no_back_face_culling = not material.use_backface_culling
            c_material.blend_mode = enums.MATERIAL_BLEND_MODE.index(material_properties.blend_mode)

            boolean_parameters = []
            float_parameters = []

            for parameter in material_properties.parameters:

                if parameter.is_overridable(self._target_definition) and not parameter.override:
                    continue

                if parameter.value_type == 'BOOLEAN':
                    boolean_parameters.append(
                        CBoolMaterialParameter(
                            name = parameter.name,
                            value = parameter.boolean_value
                        )
                    )

                else:
                    float_parameters.append(
                        CFloatMaterialParameter(
                            name = parameter.name,
                            value = CVector4(
                                parameter.float_value[0],
                                parameter.float_value[1],
                                parameter.float_value[2],
                                parameter.float_value[3]
                            )
                        )
                    )

            c_material.bool_parameters = util.as_array(boolean_parameters, CBoolMaterialParameter)
            c_material.bool_parameters_size = len(boolean_parameters)

            c_material.float_parameters = util.as_array(float_parameters, CFloatMaterialParameter)
            c_material.float_parameters_size = len(float_parameters)

            c_material.textures_name = c_material.name

            textures = []

            for j, texture in enumerate(material_properties.textures):
                if texture.image is None:
                    continue

                textures.append(
                    CTexture(
                        name = f"{c_material.name}-{j:04}",
                        picture_name = o_util.correct_image_filename(texture.image.name),
                        tex_coord_index = texture.texcoord_index,
                        wrap_mode_u = enums.WRAP_MODE.index(texture.wrapmode_u),
                        wrap_mode_v = enums.WRAP_MODE.index(texture.wrapmode_v),
                        type = texture.name,
                    )
                )

            c_material.textures = util.as_array(textures, CTexture)
            c_material.textures_size = len(textures)

        progress_console.end()

        return converted

    def get_converted_material(self, material):
        return self._output[material]

    def write_output_to_files(self, directory: str):
        if self._material_mode == 'NONE':
            return

        progress_console.start("Writing Materials to files", len(self._output))

        for i, c_material in enumerate(self._output.values()):
            material_name = c_material.contents.name 
            filepath = os.path.join(directory, material_name + ".material")

            if self._material_mode != 'OVERWRITE' and os.path.isfile(filepath):
                continue

            progress_console.update(f"Writing material \"{material_name}\"", i)

            HEIONET.material_write_file(c_material, filepath)

        progress_console.end()

        self.write_output_images_to_files(directory)

    def write_output_images_to_files(self, directory):
        if self._image_mode == 'NONE' or self._material_mode == 'NONE':
            return

        o_image.export_material_images(
            self._output.keys(),
            self._context,
            self._image_mode,
            self._invert_normal_map_y_channel,
            directory
        )
