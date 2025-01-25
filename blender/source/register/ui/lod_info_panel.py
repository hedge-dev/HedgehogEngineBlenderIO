import bpy

from ..operators import lod_operators as lodo
from ..property_groups.lod_info_properties import HEIO_LODInfo

from ...utility.draw import draw_list, TOOL_PROPERTY

LOD_TOOLS: list[TOOL_PROPERTY] = [
    (
        lodo.HEIO_OT_LODInfo_Add.bl_idname,
        "ADD",
        {}
    ),
    (
        lodo.HEIO_OT_LODInfo_Remove.bl_idname,
        "REMOVE",
        {}
    ),
    None,
    (
        lodo.HEIO_OT_LODInfo_Move.bl_idname,
        "TRIA_UP",
        {"direction": "UP"}
    ),
    (
        lodo.HEIO_OT_LODInfo_Move.bl_idname,
        "TRIA_DOWN",
        {"direction": "DOWN"}
    )
]


class HEIO_UL_LODInfoLevels(bpy.types.UIList):

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

        layout.active = index > 0

        if not layout.active:
            icon = 'BLANK1'
            name = "self"

        elif item.target is None:
            icon = "ERROR"
            name = ""

        else:
            icon = 'NONE'
            name = item.target.name

        split = layout.split(factor=0.7)
        split.label(text=name, icon=icon)
        split.prop(item, "cascade", text="")


class HEIO_MT_LODInfoLevelContextMenu(bpy.types.Menu):
    bl_label = "LOD info operations"

    def draw(self, context):
        self.layout.operator(lodo.HEIO_OT_LODInfo_Delete.bl_idname)


def draw_lod_info_panel(
        layout: bpy.types.UILayout,
        context: bpy.types.Context,
        lod_info: HEIO_LODInfo):

    header, body = layout.panel("heio_lod_info", default_closed=True)
    header.label(text="LOD Info")
    if not body:
        return

    if len(lod_info.levels) == 0:
        body.operator(lodo.HEIO_OT_LODInfo_Initialize.bl_idname)
        return

    body.use_property_split = True
    body.use_property_decorate = False

    draw_list(
        body,
        HEIO_UL_LODInfoLevels,
        HEIO_MT_LODInfoLevelContextMenu,
        lod_info.levels,
        LOD_TOOLS,
        None
    )

    lod_info_level = lod_info.levels.active_element
    if lod_info_level is None:
        return

    if lod_info.levels.active_index > 0:
        body.prop_search(lod_info_level, "target", bpy.data, "objects")

    body.prop(lod_info_level, "cascade")
    body.prop(lod_info_level, "unknown")
