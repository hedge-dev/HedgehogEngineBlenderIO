import bpy
from typing import Iterable

from . import i_enum, i_image, i_sca_parameters

from ..register.definitions import TargetDefinition
from ..register.property_groups.material_properties import (
    HEIO_Material,
    HEIO_MaterialTextureList,
    HEIO_MaterialParameterList
)

from ..exceptions import HEIODevException
from ..utility.material_setup import (
    setup_and_update_materials,
    setup_principled_bsdf_materials
)
from ..utility import progress_console


class MaterialConverter:

    _target_definition: TargetDefinition
    _image_loader: i_image.ImageLoader

    _node_setup_mode: str
    _create_undefined_parameters: bool
    _import_images: bool

    converted_materials: dict[any, bpy.types.Material]
    _material_name_lookup: dict[str, bpy.types.Material]

    def __init__(
            self,
            target_definition: TargetDefinition,
            image_loader: i_image.ImageLoader,
            node_setup_mode: str,
            create_undefined_parameters: bool,
            import_images: bool):

        self._target_definition = target_definition
        self._image_loader = image_loader

        self._node_setup_mode = node_setup_mode
        self._create_undefined_parameters = create_undefined_parameters
        self._import_images = import_images

        self.converted_materials = dict()
        self._material_name_lookup = dict()

    def _convert_textures(
            self,
            sn_texture_set: any,
            output: HEIO_MaterialTextureList,
            create_missing: bool):

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
            texture.image = self._image_loader.get_setup_image(
                texture, sn_texture.PictureName)

        return created_missing

    def _convert_parameters(self, sn_parameters: any, output: HEIO_MaterialParameterList, types: list[str], create_missing: bool, conv):
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

    def convert_materials(self, sn_materials: Iterable[any]):

        if self._import_images:
            self._image_loader.load_images_from_materials(sn_materials)

        progress_console.start("Setting up Materials", len(sn_materials))

        new_converted_materials = dict()

        for i, sn_material in enumerate(sn_materials):
            if sn_material in self.converted_materials:
                continue

            progress_console.update(f"Creating material \"{sn_material.Name}\"", i)

            material = bpy.data.materials.new(sn_material.Name)
            self.converted_materials[sn_material] = material
            new_converted_materials[sn_material] = material
            self._material_name_lookup[sn_material.Name] = material

            material_properties: HEIO_Material = material.heio_material

            if len(sn_material.ShaderName) > 0 and sn_material.ShaderName[-1] == ']':
                index = sn_material.ShaderName.index('[')
                material_properties.shader_name = sn_material.ShaderName[:index]
                material_properties.variant_name = sn_material.ShaderName[(
                    index+1):-1]
            else:
                material_properties.shader_name = sn_material.ShaderName

            material_properties.blend_mode = i_enum.from_material_blend_mode(sn_material.BlendMode)
            material.alpha_threshold = sn_material.AlphaThreshold / 255.0
            material.use_backface_culling = not sn_material.NoBackFaceCulling

            if self._target_definition is not None and material_properties.shader_name in self._target_definition.shaders.definitions:
                material_properties.custom_shader = False
                material_properties.setup_definition(
                    self._target_definition.shaders.definitions[material_properties.shader_name]
                )
            else:
                material_properties.custom_shader = True

        if self._node_setup_mode == 'SHADER':
            progress_console.update(f"Setting up material node trees", len(sn_materials))
            setup_and_update_materials(self._target_definition, new_converted_materials.values())

            setup_principled_bsdf_materials(self._target_definition, new_converted_materials.values())

            progress_console.end()

        progress_console.start("Converting Materials", len(new_converted_materials))

        for i, item in enumerate(new_converted_materials.items()):
            progress_console.update(f"Converting material \"{sn_material.Name}\"", i, True)

            sn_material = item[0]
            material: bpy.types.Material = item[1]

            material_properties: HEIO_Material = material.heio_material
            create_missing = self._create_undefined_parameters or material_properties.custom_shader

            created_missing = self._convert_parameters(
                sn_material.FloatParameters,
                material_properties.parameters,
                ['FLOAT', 'COLOR'],
                create_missing,
                lambda x: (x.X, x.Y, x.Z, x.W)
            )

            created_missing |= self._convert_parameters(
                sn_material.BoolParameters,
                material_properties.parameters,
                ['BOOLEAN'],
                create_missing,
                None
            )

            created_missing |= self._convert_textures(
                sn_material.Texset,
                material_properties.textures,
                create_missing
            )

            i_sca_parameters.convert_from_data(
                sn_material,
                material_properties.sca_parameters,
                self._target_definition,
                "material")

            if created_missing:
                material_properties.custom_shader = True

            if "diffuse" in material_properties.textures:
                diffuse_tex_node = material_properties.textures["diffuse"].image_node
                if diffuse_tex_node is not None:
                    material.node_tree.nodes.active = diffuse_tex_node

        if self._node_setup_mode == 'PBSDF':
            progress_console.update(f"Setting up material node trees", len(sn_materials))
            setup_principled_bsdf_materials(self._target_definition, new_converted_materials.values())
            progress_console.end()

        progress_console.end()

    def get_material(self, key: any):

        if callable(getattr(key, "IsValid", None)):
            if not key.IsValid():
                key = key.Name
            else:
                key = key.Resource

        if isinstance(key, str):

            if key in self._material_name_lookup:
                return self._material_name_lookup[key]

            material = bpy.data.materials.new(key)
            self._material_name_lookup[key] = material
            return material

        if key in self.converted_materials:
            return self.converted_materials[key]

        if key.Name in self._material_name_lookup:
            return self._material_name_lookup[key.Name]

        raise HEIODevException("Material lookup failed")