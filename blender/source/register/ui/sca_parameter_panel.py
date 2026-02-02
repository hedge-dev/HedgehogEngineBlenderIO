import bpy
from ..property_groups.sca_parameter_properties import HEIO_SCA_Parameters
from ..operators import sca_parameter_operators as scapop

from ...utility.draw import draw_list, TOOL_PROPERTY

SCA_PARAMETER_TOOLS: list[TOOL_PROPERTY] = [
    (
        scapop.HEIO_OT_SCAParameters_Add.bl_idname,
        "ADD",
        {}
    ),
    (
        scapop.HEIO_OT_SCAParameters_Remove.bl_idname,
        "REMOVE",
        {}
    ),
    None,
    (
        scapop.HEIO_OT_SCAParameters_Move.bl_idname,
        "TRIA_UP",
        {"direction": "UP"}
    ),
    (
        scapop.HEIO_OT_SCAParameters_Move.bl_idname,
        "TRIA_DOWN",
        {"direction": "DOWN"}
    ),
    None,
    (
        scapop.HEIO_OT_SCAParameters_NewFromPreset.bl_idname,
        "PRESET",
        {}
    )
]

SCA_PARAMETER_MENU_LABELS = {
    "MATERIAL": "Material"
}


class HEIO_UL_SCAParameterList(bpy.types.UIList):

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
        else:
            icon = "BLANK1"

        split = layout.split(factor=0.4)
        split.prop(item, "name", text="", emboss=False, icon=icon)

        split = split.split(factor=0.5)
        split.prop(item, "value_type", text="")

        property = "value"
        if item.value_type != 'INTEGER':
            property = item.value_type.lower() + "_value"

        split.prop(item, property, text="")


def draw_sca_editor(layout: bpy.types.UILayout, sca_parameters: HEIO_SCA_Parameters, mode: str):

    def set_op_mode(operator, i):
        operator.mode = mode

    draw_list(
        layout,
        HEIO_UL_SCAParameterList,
        None,
        sca_parameters,
        SCA_PARAMETER_TOOLS,
        set_op_mode
    )

    sca_parameter = sca_parameters.active_element
    if sca_parameter is None:
        return

    layout.use_property_split = True
    layout.use_property_decorate = False

    if len(sca_parameter.name) == 0:
        icon = "ERROR"
    else:
        icon = "NONE"

    layout.prop(sca_parameter, "name", icon=icon)
    layout.prop(sca_parameter, "value_type")

    property = "value"
    if sca_parameter.value_type == 'FLOAT':
        property = "float_value"
    elif sca_parameter.value_type == 'BOOLEAN':
        property = "boolean_value"

    layout.prop(sca_parameter, property)


def draw_sca_editor_menu(layout: bpy.types.UILayout, sca_parameters: HEIO_SCA_Parameters, mode: str):
    header, body = layout.panel(
        "heio_sca_param_" + mode.lower(), default_closed=True)
    header.label(text="SCA Parameters")

    if body:
        draw_sca_editor(body, sca_parameters, mode)
