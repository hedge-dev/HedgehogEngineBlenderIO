import bpy
from bpy.types import Context

from .base_panel import PropertiesPanel

from ..operators import material_parameter_operators as mpop
from ..operators.material_operators import HEIO_OT_Material_UpdateActiveProperties

from ..property_groups.material_properties import HEIO_Material
from ..property_groups.scene_properties import HEIO_Scene


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

        value_name = "value"
        if hasattr(item, "is_color") and item.is_color:
            value_name = "color_value"

        split = layout.split(factor=0.4, align=True)
        self.draw_item_name(split, item, icon)
        split.row(align=True).prop(item, value_name, text="")


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
        # elif item.image is None:
        #     icon = "MESH_PLANE"
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
            label: str,
            panel_identifier: str,
            mode: str,
            is_custom_shader: bool,
            parameter_collection: any):

        header, menu = layout.panel(panel_identifier, default_closed=True)
        header.label(text=label)
        if not menu:
            return

        tools = MATERIAL_PARAMETER_TOOLS if is_custom_shader else None

        def set_op_mode(operator, i):
            operator.mode = mode

        draw_list(
            menu,
            HEIO_UL_CustomParameterList if is_custom_shader else HEIO_UL_ParameterList,
            None,
            parameter_collection,
            tools,
            set_op_mode
        )

        parameter = parameter_collection.active_element
        if parameter is None:
            return

        menu.use_property_split = True
        menu.use_property_decorate = False

        name_icon = "ERROR" if len(parameter.name) == 0 else "NONE"
        if is_custom_shader:
            menu.prop(parameter, "name", icon=name_icon)
        else:
            split: bpy.types.UILayout = menu.split(factor=0.4)
            split.alignment = "RIGHT"
            split.label(text="Name")
            split.alignment = "LEFT"
            split.label(text="  " + parameter.name, icon=name_icon)

        value_name = "value"

        if hasattr(parameter, "is_color"):
            if is_custom_shader:
                menu.prop(parameter, "is_color")

            if parameter.is_color:
                value_name = "color_value"

        menu.row(align=True).prop(parameter, value_name)

    @staticmethod
    def draw_texture_editor(
            layout: bpy.types.UILayout,
            material: bpy.types.Material,
            material_properties: HEIO_Material):

        header, menu = layout.panel("heio_mat_tex", default_closed=True)
        header.label(text="Textures")
        if not menu:
            return

        tools = MATERIAL_PARAMETER_TOOLS if material_properties.custom_shader else None

        def set_op_mode(operator, i):
            operator.mode = "TEXTURE"

        draw_list(
            menu,
            HEIO_UL_CustomTextureList if material_properties.custom_shader else HEIO_UL_TextureList,
            None,
            material_properties.textures,
            tools,
            set_op_mode
        )

        texture = material_properties.textures.active_element
        if texture is None:
            return

        menu.use_property_split = True
        menu.use_property_decorate = False

        name_icon = "ERROR" if len(texture.name) == 0 else "NONE"
        if material_properties.custom_shader:
            menu.prop(texture, "name", icon=name_icon)
        else:
            split: bpy.types.UILayout = menu.split(factor=0.4)
            split.alignment = "RIGHT"
            split.label(text="Name")
            split.alignment = "LEFT"
            split.label(text="  " + texture.name, icon=name_icon)

        try:
            texture_name = texture.name

            texture_index = texture.type_index
            if texture_index > 0:
                texture_name += str(texture_index)

            texture_node = material.node_tree.nodes["Texture " + texture_name]
            menu.prop_search(texture_node, "image", bpy.data, "images")

        except:
            split: bpy.types.UILayout = menu.row().split(factor=0.4)
            split.alignment = "RIGHT"
            split.label(text="Image")
            split.alignment = "LEFT"
            split.label(text="  Material nodes not correctly set up", icon="ERROR")

        menu.prop(texture, "texcoord_index")
        menu.prop(texture, "wrapmode_u")
        menu.prop(texture, "wrapmode_v")

    @staticmethod
    def draw_general_properties(
            layout: bpy.types.UILayout,
            material: bpy.types.Material,
            material_properties: HEIO_Material):

        header, menu = layout.panel("heio_mat_general", default_closed=True)
        header.label(text="General")
        if not menu:
            return

        menu.use_property_split = True
        menu.use_property_decorate = False

        menu.prop(material_properties, "layer")
        menu.prop(material, "alpha_threshold", slider=True)
        menu.prop(material, "use_backface_culling")
        menu.prop(material_properties, "use_additive_blending")

    @staticmethod
    def draw_material_properties(
            layout: bpy.types.UILayout,
            scene_properties: HEIO_Scene,
            material: bpy.types.Material,
            material_properties: HEIO_Material):

        layout.operator(HEIO_OT_Material_UpdateActiveProperties.bl_idname)

        row = layout.row(align=True)

        row.prop(material_properties, "custom_shader")

        if material_properties.custom_shader:
            layout.prop(
                material_properties,
                "shader_name",
                icon="NONE" if len(
                    material_properties.shader_name) > 0 else "ERROR"
            )

        else:
            row.prop(
                scene_properties,
                "show_all_shaders"
            )

            layout.prop(
                material_properties,
                "shader_definition",
                icon="ERROR" if material_properties.shader_definition == "ERROR_FALLBACK" else "NONE"
            )

        HEIO_PT_Material.draw_general_properties(
            layout,
            material,
            material_properties
        )

        HEIO_PT_Material.draw_parameter_editor(
            layout,
            "Float Parameters",
            "heio_mat_param_float",
            "FLOAT",
            material_properties.custom_shader,
            material_properties.float_parameters
        )

        HEIO_PT_Material.draw_parameter_editor(
            layout,
            "Boolean Parameters",
            "heio_mat_param_boolean",
            "BOOLEAN",
            material_properties.custom_shader,
            material_properties.boolean_parameters
        )

        HEIO_PT_Material.draw_texture_editor(
            layout,
            material,
            material_properties
        )

    # === overriden methods === #

    @classmethod
    def poll(cls, context: Context):
        return cls.verify(context) is None

    @classmethod
    def verify(cls, context: bpy.types.Context):
        obj = context.active_object
        if obj is None:
            return "No active object"

        if obj.type != 'MESH':
            return "Active object not a mesh"

        if obj.active_material is None:
            return "No active material"

        return None

    def draw_panel(self, context):

        HEIO_PT_Material.draw_material_properties(
            self.layout,
            context.scene.heio_scene,
            context.active_object.active_material,
            context.active_object.active_material.heio_material)
