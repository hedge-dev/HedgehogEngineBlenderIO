import bpy
from bpy.types import Material
from bpy.props import (
    BoolProperty,
    StringProperty,
    EnumProperty,
    PointerProperty,
)

from .material_parameter_properties import HEIO_MaterialParameterList
from .material_texture_properties import HEIO_MaterialTextureList
from .sca_parameter_properties import HEIO_SCA_Parameters

from .. import definitions
from ..definitions.shader_definitions import ShaderDefinition, ShaderParameterType

SHADER_ERROR_FALLBACK = [("ERROR_FALLBACK", "", "")]
VARIANT_ERROR_FALLBACK = [("ERROR_FALLBACK", "", "")]
VARIANT_ERROR_FALLBACK_EMPTY = [("ERROR_FALLBACK", "", ""), ("/", "", "")]


def _update_blending(heio_material, context):
    heio_material.update_material_properties()


def _get_shader_enum_params(context: bpy.types.Context):
    show_all: bool = context.scene.heio_scene.show_all_shaders
    target_definition = definitions.get_target_definition(context)
    if target_definition is not None:
        shader_definition_collection = target_definition.shaders
    else:
        shader_definition_collection = None

    return show_all, shader_definition_collection


def _get_shader_definition_items(material_properties, context: bpy.types.Context):
    show_all, sdc = _get_shader_enum_params(
        context)

    if sdc is None:
        SHADER_ERROR_FALLBACK[0] = (
            "ERROR_FALLBACK", material_properties.shader_name, "")
        return SHADER_ERROR_FALLBACK

    if material_properties.shader_name in sdc.definitions:

        if show_all:
            return sdc.items_all

        if sdc.definitions[material_properties.shader_name].hide:
            sdc.items_visible_fallback[0] = (
                "HIDDEN_FALLBACK", material_properties.shader_name, "")
            return sdc.items_visible_fallback

        return sdc.items_visible
    else:

        result = sdc.items_all_fallback if show_all else sdc.items_visible_fallback
        result[0] = ("ERROR_FALLBACK", material_properties.shader_name, "")
        return result


def _get_shader_definition(material_properties):
    show_all, sdc = _get_shader_enum_params(
        bpy.context)

    if sdc is not None and material_properties.shader_name in sdc.definitions:
        definition = sdc.definitions[material_properties.shader_name]
        if show_all:
            return definition.all_items_index
        elif definition.visible_items_index == -1:
            return 0
        else:
            return definition.visible_items_index
    else:
        return 0


def _set_shader_definition(material_properties, value):
    if material_properties.custom_shader:
        return

    show_all, sdc = _get_shader_enum_params(
        bpy.context)

    if sdc is None:
        return

    fallback = False
    prev_name = material_properties.shader_name

    if prev_name in sdc.definitions:
        if show_all:
            items = sdc.items_all
        elif sdc.definitions[prev_name].hide:
            items = sdc.items_visible_fallback
            fallback = True
        else:
            items = sdc.items_visible
    else:
        fallback = True
        if show_all:
            items = sdc.items_all_fallback
        else:
            items = sdc.items_visible_fallback

    material_properties.shader_name = items[value][0]

    if material_properties.shader_name in sdc.definitions:
        definition = sdc.definitions[material_properties.shader_name]
        if len(definition.variants) == 0:
            material_properties.variant_name = ""
        elif material_properties.variant_name not in definition.variants:
            material_properties.variant_name = definition.variants[0]

    if prev_name == material_properties.shader_name or fallback and value == 0:
        return

    material_properties.setup_definition(
        sdc.definitions[material_properties.shader_name])


def _get_shader_variant_items(material_properties, context: bpy.types.Context):
    _, sdc = _get_shader_enum_params(context)

    if sdc is None or material_properties.shader_name not in sdc.definitions:

        VARIANT_ERROR_FALLBACK[0] = (
            "ERROR_FALLBACK", material_properties.variant_name, "")
        return VARIANT_ERROR_FALLBACK

    definition = sdc.definitions[material_properties.shader_name]
    if definition.variant_items is None:
        VARIANT_ERROR_FALLBACK_EMPTY[0] = (
            "ERROR_FALLBACK", material_properties.variant_name, "")
        return VARIANT_ERROR_FALLBACK_EMPTY

    if material_properties.variant_name in definition.variants:
        return definition.variant_items
    else:

        result = definition.variant_items_fallback
        result[0] = ("ERROR_FALLBACK", material_properties.variant_name, "")
        return result


def _get_shader_variant(material_properties):
    _, sdc = _get_shader_enum_params(bpy.context)

    if sdc is None or material_properties.shader_name not in sdc.definitions:
        return 0

    definition = sdc.definitions[material_properties.shader_name]
    if definition.variant_items is None:
        return 1 if material_properties.variant_name == "" else 0

    try:
        return definition.variants.index(material_properties.variant_name)
    except ValueError:
        return 0


def _set_shader_variant(material_properties, value):
    if material_properties.custom_shader:
        return

    _, sdc = _get_shader_enum_params(
        bpy.context)

    if sdc is None or material_properties.shader_name not in sdc.definitions:
        return

    definition = sdc.definitions[material_properties.shader_name]
    if definition.variant_items is None:
        items = VARIANT_ERROR_FALLBACK_EMPTY
    elif material_properties.variant_name in definition.variants:
        items = definition.variant_items
    else:
        items = definition.variant_items_fallback

    new_name = items[value][0]
    if new_name == "/":
        new_name = ""

    material_properties.variant_name = new_name


class HEIO_Material(bpy.types.PropertyGroup):

    custom_shader: BoolProperty(
        name="Custom Shader",
        description="Whether to create a custom shader setup, instead of using a preset.",
        default=True
    )

    shader_name: StringProperty(
        name="Shader name",
        description="Name of the shader to use."
    )

    shader_definition: EnumProperty(
        name="Shader",
        description="Shader preset to use. Depends on the target game defined in the scene settings",
        items=_get_shader_definition_items,
        get=_get_shader_definition,
        set=_set_shader_definition
    )

    variant_name: StringProperty(
        name="Variant name",
        description="Shader variant to use"
    )

    variant_definition: EnumProperty(
        name="Variant",
        description="Shader variant to use",
        items=_get_shader_variant_items,
        get=_get_shader_variant,
        set=_set_shader_variant
    )

    layer: EnumProperty(
        name="Layer",
        items=(
            ("AUTO", "Automatic", "Determines the layer based on the shader preset. Falls back to \"Opaque\" for custom shaders."),
            ("OPAQUE", "Opaque", "Fully opaque material, transparent elements get ignored."),
            ("TRANSPARENT", "Transparent",
             "Material has transparent elements and needs to be rendered as such."),
            ("PUNCHTHROUGH", "Punch-through",
             "Transparent pixels above the alpha threshold get discarded while rendering."),
            ("SPECIAL", "Special", "Variable layer, behavior depends on the game.")
        ),
        description="Determines which mesh group the mesh with the material gets assigned to.",
        default="AUTO",
        update=_update_blending
    )

    special_layer_name: StringProperty(
        name="\"Special\" layer name",
        description="Layer name for when the layer type \"special\" is used"
    )

    use_additive_blending: BoolProperty(
        name="Use Additive Blending",
        description="Transparency gets applied with additive mixing, instead of \"normal\" mixing.",
        default=False
    )

    parameters: PointerProperty(
        type=HEIO_MaterialParameterList
    )

    textures: PointerProperty(
        type=HEIO_MaterialTextureList
    )

    sca_parameters: PointerProperty(
        type=HEIO_SCA_Parameters
    )

    def setup_definition_parameters(self, definition: ShaderDefinition):
        current_index = 0
        parameters: HEIO_MaterialParameterList = self.parameters

        for parameter in definition.parameters.values():

            if parameter.type == ShaderParameterType.BOOLEAN:
                index = parameters.find_next_index(
                    parameter.name, current_index, ['BOOLEAN'])
            else:
                index = parameters.find_next_index(
                    parameter.name, current_index, ['FLOAT', 'COLOR'])

            if index >= 0:
                item = parameters[index]

                if item.value_type != parameter.type.name:
                    item.value_type = parameter.type.name

            else:
                index = len(parameters)
                item = parameters.new()
                item.name = parameter.name
                item.value_type = parameter.type.name

                setattr(item, item.value_type.lower() +
                        "_value", parameter.default)

            if index != current_index:
                parameters.move(index, current_index)

            current_index += 1

        remove_index = len(parameters) - 1
        while remove_index >= current_index:
            parameters[remove_index].reset_nodes()
            parameters.remove(remove_index)
            remove_index -= 1

    def setup_definition_textures(self, definition: ShaderDefinition):
        current_index = 0
        textures: HEIO_MaterialTextureList = self.textures

        for texture_name in definition.textures:
            index = textures.find_next_index(texture_name, current_index)

            if index >= 0:
                item = textures[index]
            else:
                index = len(textures)
                item = textures.new()
                item.name = texture_name

            if index != current_index:
                self.parameters.move(index, current_index)

            current_index += 1

        remove_index = len(textures) - 1
        while remove_index >= current_index:
            textures[remove_index].reset_nodes()
            textures.remove(remove_index)
            remove_index -= 1

    def setup_definition(self, definition: ShaderDefinition):
        self.setup_definition_parameters(definition)
        self.setup_definition_textures(definition)

    def update_material_properties(self):
        if self.layer == 'TRANSPARENT':
            self.id_data.surface_render_method = 'BLENDED'
        else:
            self.id_data.surface_render_method = 'DITHERED'

    def update_material_nodes(self):

        for parameter in self.parameters:
            parameter.update_nodes()

        for texture in self.textures:
            texture.update_nodes()

    def update_material_all(self):
        self.update_material_nodes()
        self.update_material_properties()

    @classmethod
    def register(cls):
        Material.heio_material = PointerProperty(type=cls)
