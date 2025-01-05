import bpy

from ..operators.mesh_info_operators import (
    NO_ATTRIB,
    HEIO_OT_MeshInfo_Initialize,
    HEIO_OT_MeshInfo_Delete,
    HEIO_OT_MeshInfo_Add,
    HEIO_OT_MeshInfo_Remove,
    HEIO_OT_MeshInfo_Move,
    HEIO_OT_MeshInfo_Assign,
    HEIO_OT_CollisionFlag_Remove,
    HEIO_OT_MeshInfo_DeSelect
)

from ...utility.draw import draw_list, TOOL_PROPERTY

MESH_INFO_TOOLS: list[TOOL_PROPERTY] = [
    (
        HEIO_OT_MeshInfo_Add.bl_idname,
        "ADD",
        {}
    ),
    (
        HEIO_OT_MeshInfo_Remove.bl_idname,
        "REMOVE",
        {}
    ),
    None,
    (
        HEIO_OT_MeshInfo_Move.bl_idname,
        "TRIA_UP",
        {"direction": "UP"}
    ),
    (
        HEIO_OT_MeshInfo_Move.bl_idname,
        "TRIA_DOWN",
        {"direction": "DOWN"}
    )
]


class BaseMeshInfoContextMenu(bpy.types.Menu):

    def draw(self, context):
        op = self.layout.operator(HEIO_OT_MeshInfo_Delete.bl_idname)
        op.type = self.type


def draw_mesh_info_layout(
        layout: bpy.types.UILayout,
        context: bpy.types.Context,
        mesh_info_list,
        ui_list: bpy.types.UIList,
        menu: bpy.types.Menu,
        type: str):

    no_attrib = type in NO_ATTRIB

    if not no_attrib:

        if not mesh_info_list.initialized:
            op = layout.operator(HEIO_OT_MeshInfo_Initialize.bl_idname)
            op.type = type
            return None

        if mesh_info_list.attribute_invalid:
            box = layout.box()
            box.label(
                text=f"Invalid \"{mesh_info_list.attribute_name}\" attribute!")
            box.label(text="Must use domain \"Face\" and type \"Integer\"!")
            box.label(text="Please remove or convert")
            return None

    def set_op_type(operator, i):
        operator.type = type

    draw_list(
        layout,
        ui_list,
        menu,
        mesh_info_list,
        MESH_INFO_TOOLS,
        set_op_type
    )

    if context.mode == 'EDIT_MESH' and not no_attrib:
        row = layout.row(align=True)

        def setup_op(operator, text):
            op = row.operator(operator.bl_idname, text=text)
            op.type = type
            return op

        if type == 'COLLISION_FLAGS':
            setup_op(HEIO_OT_MeshInfo_Assign, "Assign")
            setup_op(HEIO_OT_CollisionFlag_Remove, "Remove")

            row = layout.row(align=True)
            setup_op(HEIO_OT_MeshInfo_DeSelect, "Select").select = True
            setup_op(HEIO_OT_MeshInfo_DeSelect, "Deselect").select = False

        else:
            setup_op(HEIO_OT_MeshInfo_Assign, "Assign")
            setup_op(HEIO_OT_MeshInfo_DeSelect, "Select").select = True
            setup_op(HEIO_OT_MeshInfo_DeSelect, "Deselect").select = False

    elif no_attrib and mesh_info_list.active_element is None:
        return None

    return layout


def draw_mesh_info_panel(
        layout: bpy.types.UILayout,
        context: bpy.types.Context,
        mesh_info_list,
        ui_list: bpy.types.UIList,
        menu: bpy.types.Menu,
        type: str,
        label: str):

    header, body = layout.panel(
        "heio_mesh_info_" + type.lower(),
        default_closed=True)

    header.label(text=label)
    if not body:
        return None

    return draw_mesh_info_layout(
        body,
        context,
        mesh_info_list,
        ui_list,
        menu,
        type
    )


class HEIO_UL_CollisionInfoList(bpy.types.UIList):

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

        split = layout.split(factor=0.15)
        split.label(text=str(index))

        row = split.row(align=True)
        if item.custom:
            row.prop(item, "value", text="", emboss=False)
        else:
            row.prop(item, "value_enum", text="", emboss=False)
        row.prop(item, "custom", text="", icon='RESTRICT_INSTANCED_ON' if item.custom else 'RESTRICT_INSTANCED_OFF')

def draw_collision_info_editor(
        layout: bpy.types.UILayout,
        collision_info,
        label: str):

    if layout is None:
        return

    layout.use_property_decorate = False

    split = layout.split(factor=0.4)
    split.alignment = 'RIGHT'
    split.label(text=label)

    row = split.row(align=True)
    row.prop(collision_info, "custom", text="", icon='RESTRICT_INSTANCED_ON' if collision_info.custom else 'RESTRICT_INSTANCED_OFF')
    if collision_info.custom:
        row.prop(collision_info, "value", text="")
    else:
        row.prop(collision_info, "value_enum", text="")

