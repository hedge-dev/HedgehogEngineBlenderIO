import bpy
from bpy.types import Context

from .base_panel import PropertiesPanel
from .sca_parameter_panel import draw_sca_editor_menu

from ..operators import material_parameter_operators as mpop
from ..operators.material_operators import HEIO_OT_Material_SetupNodes_Active

from ..property_groups.mesh_properties import MESH_DATA_TYPES
from ..property_groups.material_properties import HEIO_Material
from .. import definitions

from ...utility.draw import draw_list, TOOL_PROPERTY


TEXTURE_WRAPMODE_NAMES = {
    "REPEAT": "Repeat",
    "MIRROR": "Mirror",
    "CLAMP": "Clamp",
    "MIRRORONCE": "Mirror Once",
    "BORDER": "Border",
}

MATERIAL_PARAMETER_TOOLS: list[TOOL_PROPERTY] = [
    (
        mpop.HEIO_OT_MaterialParameters_Add.bl_idname,
        "ADD",
        {}
    ),
    (
        mpop.HEIO_OT_MaterialParameters_Remove.bl_idname,
        "REMOVE",
        {}
    ),
    None,
    (
        mpop.HEIO_OT_MaterialParameters_Move.bl_idname,
        "TRIA_UP",
        {"direction": "UP"}
    ),
    (
        mpop.HEIO_OT_MaterialParameters_Move.bl_idname,
        "TRIA_DOWN",
        {"direction": "DOWN"}
    )
]


class BaseParameterList:

    def draw_item(
            self,
            context: bpy.types.Context,
            layout: bpy.types.UILayout,
            data,
            item,
            icon: str,
            active_data,
            active_property,
            index,
            flt_flag):

        icon = "BLANK1"
        if len(item.name) == 0:
            icon = "ERROR"

        split = layout.split(factor=0.4, align=True)
        self.draw_item_name(split, item, icon)
        split.row(align=True).prop(
            item, item.value_type.lower() + "_value", text="")


class HEIO_UL_ParameterList(bpy.types.UIList, BaseParameterList):

    def draw_item_name(self, layout, item, icon):
        layout.label(text=item.name, icon=icon)


class HEIO_UL_CustomParameterList(bpy.types.UIList, BaseParameterList):

    def draw_item_name(self, layout, item, icon):
        layout.prop(item, "name", text="", emboss=False, icon=icon)


class BaseTextureList:

    def draw_item(
            self,
            context: bpy.types.Context,
            layout: bpy.types.UILayout,
            data,
            item,
            icon: str,
            active_data,
            active_property,
            index,
            flt_flag):

        if len(item.name) == 0:
            icon = "ERROR"
        elif item.image is None:
            icon = "MESH_PLANE"
        else:
            icon = "OUTLINER_OB_IMAGE"

        split = layout.split(factor=0.4)
        self.draw_item_name(split, item, icon)

        split = split.split(factor=0.2)
        split.label(text=str(item.texcoord_index))

        split = split.split(factor=0.5)
        split.label(text=TEXTURE_WRAPMODE_NAMES[item.wrapmode_u])
        split.label(text=TEXTURE_WRAPMODE_NAMES[item.wrapmode_v])


class HEIO_UL_TextureList(bpy.types.UIList, BaseTextureList):

    def draw_item_name(self, layout, item, icon):
        layout.label(text=item.name, icon=icon)


class HEIO_UL_CustomTextureList(bpy.types.UIList, BaseTextureList):

    def draw_item_name(self, layout, item, icon):
        layout.prop(item, "name", text="", emboss=False, icon=icon)


class HEIO_PT_Material(PropertiesPanel):
    bl_label = "HEIO Material Properties"
    bl_context = "material"

    @staticmethod
    def draw_parameter_editor(
            layout: bpy.types.UILayout,
            material_properties: HEIO_Material):

        header, body = layout.panel("heio_mat_param", default_closed=True)
        header.label(text="Parameters")
        if not body:
            return

        tools = MATERIAL_PARAMETER_TOOLS if material_properties.custom_shader else None

        def set_op_mode(operator, i):
            operator.mode = "PARAMETER"

        draw_list(
            body,
            HEIO_UL_CustomParameterList if material_properties.custom_shader else HEIO_UL_ParameterList,
            None,
            material_properties.parameters,
            tools,
            set_op_mode
        )

        parameter = material_properties.parameters.active_element
        if parameter is None:
            return

        body.use_property_split = True
        body.use_property_decorate = False

        name_icon = "ERROR" if len(parameter.name) == 0 else "NONE"
        if material_properties.custom_shader:
            body.prop(parameter, "name", icon=name_icon)
        else:
            split: bpy.types.UILayout = body.split(factor=0.4)
            split.alignment = "RIGHT"
            split.label(text="Name")
            split.alignment = "LEFT"
            split.label(text="  " + parameter.name, icon=name_icon)

        if material_properties.custom_shader:
            body.prop(parameter, "value_type")

        body.row(align=True).prop(
            parameter, parameter.value_type.lower() + "_value")

    @staticmethod
    def draw_texture_editor(
            layout: bpy.types.UILayout,
            material_properties: HEIO_Material):

        header, body = layout.panel("heio_mat_tex", default_closed=True)
        header.label(text="Textures")
        if not body:
            return

        tools = MATERIAL_PARAMETER_TOOLS if material_properties.custom_shader else None

        def set_op_mode(operator, i):
            operator.mode = "TEXTURE"

        draw_list(
            body,
            HEIO_UL_CustomTextureList if material_properties.custom_shader else HEIO_UL_TextureList,
            None,
            material_properties.textures,
            tools,
            set_op_mode
        )

        texture = material_properties.textures.active_element
        if texture is None:
            return

        body.use_property_split = True
        body.use_property_decorate = False

        name_icon = "ERROR" if len(texture.name) == 0 else "NONE"
        if material_properties.custom_shader:
            body.prop(texture, "name", icon=name_icon)
        else:
            split: bpy.types.UILayout = body.split(factor=0.4)
            split.alignment = "RIGHT"
            split.label(text="Name")
            split.alignment = "LEFT"
            split.label(text="  " + texture.name, icon=name_icon)

        body.prop_search(texture, "image", bpy.data, "images")

        body.prop(texture, "texcoord_index")
        body.prop(texture, "wrapmode_u")
        body.prop(texture, "wrapmode_v")

    @staticmethod
    def draw_general_properties(
            layout: bpy.types.UILayout,
            material: bpy.types.Material,
            material_properties: HEIO_Material):

        header, body = layout.panel("heio_mat_general", default_closed=True)
        header.label(text="General")
        if not body:
            return

        body.use_property_split = True
        body.use_property_decorate = False

        body.prop(material_properties, "render_layer")

        if material_properties.render_layer == 'SPECIAL':
            body.prop(
                material_properties,
                "special_render_layer_name",
                icon="ERROR"
                if len(material_properties.special_render_layer_name) == 0
                else "NONE"
            )

        body.prop(material, "alpha_threshold", slider=True)
        body.prop(material, "use_backface_culling")
        body.prop(material_properties, "use_additive_blending")

    @staticmethod
    def draw_header_properties(
            layout: bpy.types.UILayout,
            context: bpy.types.Context,
            material_properties: HEIO_Material):

        row = layout.row(align=True)

        row.prop(material_properties, "custom_shader")

        if material_properties.custom_shader:
            layout.prop(
                material_properties,
                "shader_name",
                icon="NONE" if len(
                    material_properties.shader_name) > 0 else "ERROR"
            )

            layout.prop(material_properties, "variant_name")

        else:
            row.prop(context.scene.heio_scene, "show_all_shaders")

            layout.prop(
                material_properties,
                "shader_definition",
                icon="ERROR" if material_properties.shader_definition == "ERROR_FALLBACK" else "NONE"
            )

            definition = definitions.get_target_definition(context)
            if material_properties.shader_name in definition.shaders.definitions:
                shader_definition = definition.shaders.definitions[material_properties.shader_name]
                if len(shader_definition.variants) > 0 or material_properties.variant_name != "":
                    layout.prop(
                        material_properties,
                        "variant_definition",
                        icon="ERROR" if material_properties.variant_definition == "ERROR_FALLBACK" else "NONE"
                    )

        layout.operator(HEIO_OT_Material_SetupNodes_Active.bl_idname)

    # === overriden methods === #

    @classmethod
    def verify(cls, context: bpy.types.Context):
        obj = context.active_object
        if obj is None:
            return "No active object"

        if obj.type not in MESH_DATA_TYPES:
            return "Active object not a mesh"

        if obj.active_material is None:
            return "No active material"

        return None

    @classmethod
    def draw_panel(cls, layout, context):

        material = context.active_object.active_material
        material_properties = material.heio_material

        HEIO_PT_Material.draw_header_properties(
            layout,
            context,
            material_properties
        )

        HEIO_PT_Material.draw_general_properties(
            layout,
            material,
            material_properties
        )

        HEIO_PT_Material.draw_parameter_editor(
            layout,
            material_properties
        )

        HEIO_PT_Material.draw_texture_editor(
            layout,
            material_properties
        )

        draw_sca_editor_menu(
            layout,
            material_properties.sca_parameters,
            "MATERIAL"
        )
