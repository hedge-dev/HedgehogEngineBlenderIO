import bpy
from bpy.types import Material
from bpy.props import (
    BoolProperty,
    StringProperty,
    EnumProperty,
    PointerProperty,
)

from .base_list import BaseList
from .material_parameter_properties import (
    HEIO_MaterialParameterBooleanList,
    HEIO_MaterialParameterFloatList
)
from .material_texture_properties import (
    HEIO_MaterialTextureList
)

from ..definitions import shader_definitions


def _update_blending(heio_material, context):
    heio_material.update_material_properties()


def _get_shader_enum_params(context: bpy.types.Context) -> tuple[bool, shader_definitions.ShaderDefinitionCollection]:
    target_game: str = context.scene.heio_scene.target_game
    show_all: bool = context.scene.heio_scene.show_all_shaders
    shader_definition_collection = shader_definitions.SHADER_DEFINITIONS[target_game]

    return show_all, shader_definition_collection


def _get_shader_definition_items(material_properties, context: bpy.types.Context):
    show_all, sdc = _get_shader_enum_params(
        context)

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

    if material_properties.shader_name in sdc.definitions:
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
    fallback = False

    if material_properties.shader_name in sdc.definitions:
        if show_all:
            items = sdc.items_all
        elif sdc.definitions[material_properties.shader_name].hide:
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

    prev_name = material_properties.shader_name
    material_properties.shader_name = items[value][0]

    if prev_name == material_properties.shader_name or fallback and value == 0:
        return

    material_properties.setup_definition_parameters_and_textures(
        sdc.definitions[material_properties.shader_name])


class HEIO_Material(bpy.types.PropertyGroup):

    custom_shader: BoolProperty(
        name="Custom Shader",
        description="Whether to create a custom shader setup, instead of using a preset.",
        default=False
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

    use_additive_blending: BoolProperty(
        name="Use Additive Blending",
        description="Transparency gets applied with additive mixing, instead of \"normal\" mixing.",
        default=False
    )

    float_parameters: PointerProperty(
        type=HEIO_MaterialParameterFloatList
    )

    boolean_parameters: PointerProperty(
        type=HEIO_MaterialParameterBooleanList
    )

    textures: PointerProperty(
        type=HEIO_MaterialTextureList
    )

    def setup_definition_parameters_and_textures(self, definition: shader_definitions.ShaderDefinition):
        current_boolean_index = 0
        current_float_index = 0
        current_texture_index = 0

        def setup_item(list: BaseList, name: str, current_index: str, after_setup):
            if name in list.elements[current_index:]:
                item = list.elements[current_index:][name]
                old_index = list.get_index(item)
                created = False
            else:
                old_index = len(list)
                item = list.new()
                item.name = name
                created = True

            if after_setup is not None:
                after_setup(item, created)

            if old_index != current_index:
                list.move(old_index, current_index)

            return current_index + 1

        def after_setup_float(item, created):
            if item.is_color:
                item.is_color = False

        def after_setup_color(item, created):
            if item.is_color:
                return

            item.is_color = True
            if created:
                item.color_value = (1, 1, 1, 1)

        # setting up items

        for parameter_name, parameter_type in definition.parameters.items():

            if parameter_type == shader_definitions.ShaderParameterType.FLOAT:
                current_float_index = setup_item(
                    self.float_parameters, parameter_name, current_float_index, after_setup_float)

            elif parameter_type == shader_definitions.ShaderParameterType.COLOR:
                current_float_index = setup_item(
                    self.float_parameters, parameter_name, current_float_index, after_setup_color)

            else:  # BOOLEAN
                current_boolean_index = setup_item(
                    self.boolean_parameters, parameter_name, current_boolean_index, None)

        for texture_name in definition.textures:
            current_texture_index = setup_item(
                self.textures, texture_name, current_texture_index, None)

        # Removing irrelevant items

        def remove_above(list: BaseList, end_index: int):
            index = len(list) - 1
            while index >= end_index:
                list[index].reset_nodes()
                list.remove(index)
                index = len(list) - 1

        remove_above(self.float_parameters, current_float_index)
        remove_above(self.boolean_parameters, current_boolean_index)
        remove_above(self.textures, current_texture_index)

    def update_material_properties(self):
        if self.layer == 'TRANSPARENT':
            self.id_data.surface_render_method = 'BLENDED'
        else:
            self.id_data.surface_render_method = 'DITHERED'

    def update_material_nodes(self):

        for float_parameter in self.float_parameters:
            float_parameter.update_nodes()

        for boolean_parameter in self.boolean_parameters:
            boolean_parameter.update_nodes()

        for texture in self.textures:
            texture.update_nodes()

    def update_material_all(self):
        self.update_material_nodes()
        self.update_material_properties()

    @classmethod
    def register(cls):
        Material.heio_material = PointerProperty(type=cls)
