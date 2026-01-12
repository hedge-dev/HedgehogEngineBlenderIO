import bpy
from typing import Iterable
from ctypes import cast, POINTER

from . import i_image, i_sca_parameters

from ..external import pointer_to_address, TPointer, CMaterial, CTexture, CStringPointerPair
from ..external.enums import WRAP_MODE, MATERIAL_BLEND_MODE
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

    _converted_materials: dict[any, bpy.types.Material]
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

        self._converted_materials = dict()
        self._material_name_lookup = dict()

    def _convert_textures(
            self,
            c_textures: TPointer[CTexture],
            c_textures_size: int,
            output: HEIO_MaterialTextureList,
            create_missing: bool):

        name_indices = {}
        created_missing = False

        for i in range(c_textures_size):
            c_texture: CTexture = c_textures[i]

            from_index = 0
            if c_texture.type in name_indices:
                from_index = name_indices[c_texture.type] + 1

            index = output.find_next_index(c_texture.type, from_index)

            if index >= 0:
                name_indices[c_texture.type] = index
                texture = output[index]
            elif create_missing:
                name_indices[c_texture.type] = len(output)
                texture = output.new()
                texture.name = c_texture.type
                created_missing = True
            else:
                continue

            texture.texcoord_index = c_texture.texcoord_index
            texture.wrapmode_u = WRAP_MODE[c_texture.wrap_mode_u]
            texture.wrapmode_v = WRAP_MODE[c_texture.wrap_mode_v]
            texture.image = self._image_loader.get_setup_image(
                texture, c_texture.picture_name)

        return created_missing

    def _convert_parameters(self, c_parameters: TPointer, c_parameters_size: int, output: HEIO_MaterialParameterList, types: list[str], create_missing: bool, conv):
        created_missing = False

        for i in range(c_parameters_size):
            c_parameter = c_parameters[i]
            parameter = output.find_next(c_parameter.name, 0, types)
            
            if parameter is None:
                if create_missing:
                    parameter = output.new()
                    parameter.name = c_parameter.name
                    parameter.value_type = types[0]
                    created_missing = True
                else:
                    continue

            value = c_parameter.value
            if conv is not None:
                value = conv(value)

            setattr(parameter, parameter.value_type.lower() + "_value", value)
            parameter.override = True

        return created_missing

    def convert_materials(self, c_materials: Iterable[TPointer[CMaterial]]):

        if self._import_images:
            self._image_loader.load_images_from_materials(c_materials)

        progress_console.start("Setting up Materials", len(c_materials))

        new_converted_materials: list[tuple[CMaterial, bpy.types.Material]] = []

        for i, c_material in enumerate(c_materials):
            c_material_address = pointer_to_address(c_material)
            if c_material_address in self._converted_materials:
                continue

            c_material: CMaterial = c_material.contents
            progress_console.update(f"Creating material \"{c_material.name}\"", i)

            material = bpy.data.materials.new(c_material.name)
            self._converted_materials[c_material_address] = material
            new_converted_materials.append((c_material, material))
            self._material_name_lookup[c_material.name] = material

            material_properties: HEIO_Material = material.heio_material

            if len(c_material.shader_name) > 0 and c_material.shader_name[-1] == ']':
                index = c_material.shader_name.index('[')
                material_properties.shader_name = c_material.shader_name[:index]
                material_properties.variant_name = c_material.shader_name[(
                    index+1):-1]
            else:
                material_properties.shader_name = c_material.shader_name

            material_properties.blend_mode = MATERIAL_BLEND_MODE[c_material.blend_mode]
            material.alpha_threshold = c_material.alpha_threshold / 255.0
            material.use_backface_culling = not c_material.no_back_face_culling

            if self._target_definition is not None and material_properties.shader_name in self._target_definition.shaders.definitions:
                material_properties.custom_shader = False
                material_properties.setup_definition(
                    self._target_definition.shaders.definitions[material_properties.shader_name]
                )
            else:
                material_properties.custom_shader = True

        if self._node_setup_mode == 'SHADER':
            progress_console.update(f"Setting up material node trees", len(c_materials))
            setup_and_update_materials(self._target_definition, [ncm[1] for ncm in new_converted_materials])
            progress_console.end()

        progress_console.start("Converting Materials", len(new_converted_materials))

        for i, item in enumerate(new_converted_materials):
            c_material = item[0]
            material = item[1]

            progress_console.update(f"Converting material \"{c_material.name}\"", i, True)

            material_properties: HEIO_Material = material.heio_material
            create_missing = self._create_undefined_parameters or material_properties.custom_shader

            created_missing = self._convert_parameters(
                c_material.float_parameters,
                c_material.float_parameters_size,
                material_properties.parameters,
                ['FLOAT', 'COLOR'],
                create_missing,
                lambda x: (x.x, x.y, x.z, x.w)
            )

            created_missing |= self._convert_parameters(
                c_material.bool_parameters,
                c_material.bool_parameters_size,
                material_properties.parameters,
                ['BOOLEAN'],
                create_missing,
                None
            )

            created_missing |= self._convert_textures(
                c_material.textures,
                c_material.textures_size,
                material_properties.textures,
                create_missing
            )

            i_sca_parameters.convert_from_root(
                c_material.root_node,
                material_properties.sca_parameters,
                self._target_definition,
                "material"
            )

            if created_missing:
                material_properties.custom_shader = True

            if "diffuse" in material_properties.textures:
                diffuse_tex_node = material_properties.textures["diffuse"].image_node
                if diffuse_tex_node is not None:
                    material.node_tree.nodes.active = diffuse_tex_node

        if self._node_setup_mode == 'PBSDF':
            progress_console.update(f"Setting up material node trees", len(c_materials))
            setup_principled_bsdf_materials(self._target_definition, [ncm[1] for ncm in new_converted_materials])
            progress_console.end()

        progress_console.end()

    def get_converted_materials(self):
        return list(self._converted_materials.values())

    def get_material(self, key: any):

        if isinstance(key, POINTER(CStringPointerPair)):
            key = key.contents

        if isinstance(key, CStringPointerPair) and key.pointer:
            key = cast(key.pointer, POINTER(CMaterial))

        if isinstance(key, POINTER(CMaterial)):
            c_address = pointer_to_address(key)
            if c_address in self._converted_materials:
                return self._converted_materials[c_address]
            
        if hasattr(key, "name"):
            key = key.name

        if isinstance(key, str):

            if key in self._material_name_lookup:
                return self._material_name_lookup[key]

            material = bpy.data.materials.new(key)
            self._material_name_lookup[key] = material
            return material            

        raise HEIODevException("Material lookup failed")