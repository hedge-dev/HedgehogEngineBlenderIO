import bpy
from bpy.props import (
    BoolProperty,
    FloatProperty,
    IntProperty,
    FloatVectorProperty,

    StringProperty,
    EnumProperty,

    PointerProperty,
    CollectionProperty
)

from .base_list import BaseList

from ..definitions import shader_definitions


def _update_is_color(parameter, context):
    if parameter.is_color:
        parameter.color_value = parameter.value
    else:
        parameter.value = parameter.color_value


class HEIO_MaterialParameterFloat(bpy.types.PropertyGroup):

    name: StringProperty(
        name="Name"
    )

    value: FloatVectorProperty(
        name="Value",
        size=4,
        precision=3
    )

    color_value: FloatVectorProperty(
        name="Value",
        subtype="COLOR",
        size=4,
        soft_min=0,
        soft_max=1,
        default=(1, 1, 1, 1)
    )

    is_color: BoolProperty(
        name="Is Color",
        description="Whether the parameter is a color",
        default=False,
        update=_update_is_color
    )

    @property
    def display_value(self) -> str:
        return f"{{{self.value[0]:.3f}, {self.value[1]:.3f}, {self.value[2]:.3f}, {self.value[3]:.3f}}}"


class HEIO_MaterialParameterFloatList(BaseList):

    elements: CollectionProperty(
        type=HEIO_MaterialParameterFloat
    )


class HEIO_MaterialParameterBoolean(bpy.types.PropertyGroup):

    name: StringProperty(
        name="Name"
    )

    value: BoolProperty(
        name="Value"
    )

    @property
    def display_value(self) -> str:
        t = "X"
        f = "-"
        return f"{{{t if self.value[0] else f}, {t if self.value[1] else f}, {t if self.value[2] else f}, {t if self.value[3] else f}}}"


class HEIO_MaterialParameterBooleanList(BaseList):

    elements: CollectionProperty(
        type=HEIO_MaterialParameterBoolean
    )


class HEIO_MaterialTexture(bpy.types.PropertyGroup):

    name: StringProperty(
        name="Type Name",
        description=(
            "Texture slot of the shader to place this texture into."
            " Common types are \"diffuse\", \"specular\", \"normal\", \"emission\" and \"transparency\""
        )
    )

    texcoord_index: IntProperty(
        name="Texture coordinate index",
        min=0,
        max=255
    )

    wrapmode_u: EnumProperty(
        name="Wrapmode U",
        items=(
            ("REPEAT", "Repeat", ""),
            ("MIRROR", "Mirror", ""),
            ("CLAMP", "Clamp", ""),
            ("MIRRORONCE", "Mirror Once", ""),
            ("BORDER", "Border", ""),
        ),
        description="Wrapmode along the horizontal axis of the texture coordinates",
        default="REPEAT"
    )

    wrapmode_v: EnumProperty(
        name="Wrapmode V",
        items=(
            ("REPEAT", "Repeat", ""),
            ("MIRROR", "Mirror", ""),
            ("CLAMP", "Clamp", ""),
            ("MIRRORONCE", "Mirror Once", ""),
            ("BORDER", "Border", ""),
        ),
        description="Wrapmode along the vertical axis of the texture coordinates",
        default="REPEAT"
    )


class HEIO_MaterialTextureList(BaseList):

    elements: CollectionProperty(
        type=HEIO_MaterialTexture
    )


def _get_shader_enum_params(context: bpy.types.Context) -> tuple[bool, shader_definitions.ShaderDefinitionCollection]:
    target_game: str = context.scene.heio_scene.target_game
    show_all: bool = context.scene.heio_scene.show_all_shaders
    shader_definition_collection = shader_definitions.SHADER_DEFINITIONS[target_game]

    return show_all, shader_definition_collection


def _get_shader_definition_items(material_properties, context: bpy.types.Context):
    show_all, sdc = _get_shader_enum_params(context)

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
    show_all, sdc = _get_shader_enum_params(bpy.context)

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

    show_all, sdc = _get_shader_enum_params(bpy.context)
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
        default="AUTO"
    )

    alpha_threshold: FloatProperty(
        name="Alpha threshold",
        description="Alpha threshold below which to discard a rendered pixel (only applies to punch-through layer)",
        min=0, max=1,
        default=0.5
    )

    no_backface_culling: BoolProperty(
        name="No backface culling",
        description="Render the backside of polygons",
        default=False
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
            if name in list:
                item = list[name]
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

        def after_setup_float(item: HEIO_MaterialParameterFloat, created):
            if item.is_color:
                item.is_color = False

        def after_setup_color(item: HEIO_MaterialParameterFloat, created):
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

        while len(self.boolean_parameters) > current_boolean_index:
            self.boolean_parameters.remove(current_boolean_index)

        while len(self.float_parameters) > current_float_index:
            self.float_parameters.remove(current_float_index)

        while len(self.textures) > current_texture_index:
            self.textures.remove(current_texture_index)

    @classmethod
    def register(cls):
        bpy.types.Material.heio_material = PointerProperty(type=cls)
