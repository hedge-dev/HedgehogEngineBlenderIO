import bpy

from .base_panel import PropertiesPanel
from .sca_parameter_panel import draw_sca_editor_menu
from .lod_info_panel import draw_lod_info_panel

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


##################################################
# UI Lists


class HEIO_UL_MeshGroups(bpy.types.UIList):

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

        layout.prop(item, "name", text="",
                    placeholder="empty name", emboss=False)


class HEIO_UL_MeshLayers(bpy.types.UIList):

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
            icon = "NONE"

        layout.active = index > 2
        layout.prop(item, "name", text="", emboss=False, icon=icon)


class HEIO_UL_CollisionPrimitiveList(bpy.types.UIList):

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

        split = layout.split(factor=0.1)
        split.label(text=str(index))
        split.label(text=item.shape_type)


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
        row.prop(item, "custom", text="",
                 icon='RESTRICT_INSTANCED_ON' if item.custom else 'RESTRICT_INSTANCED_OFF')

##################################################
# Context Menus


class BaseMeshInfoContextMenu(bpy.types.Menu):

    def draw(self, context):
        op = self.layout.operator(HEIO_OT_MeshInfo_Delete.bl_idname)
        op.type = self.type


class HEIO_MT_MeshLayersContextMenu(BaseMeshInfoContextMenu):
    bl_label = "Mesh layer operations"
    type = 'RENDER_LAYERS'


class HEIO_MT_CollisionLayersContextMenu(BaseMeshInfoContextMenu):
    bl_label = "Collision mesh layers operations"
    type = 'COLLISION_LAYERS'


class HEIO_MT_CollisionTypesContextMenu(BaseMeshInfoContextMenu):
    bl_label = "Collision mesh types operations"
    type = 'COLLISION_TYPES'


class HEIO_MT_CollisionFlagsContextMenu(BaseMeshInfoContextMenu):
    bl_label = "Collision mesh flags operations"
    type = 'COLLISION_FLAGS'


class HEIO_MT_MeshGroupsContextMenu(BaseMeshInfoContextMenu):
    bl_label = "Mesh group operations"
    type = 'MESH_GROUPS'


##################################################
# Panel Class

class HEIO_PT_Mesh(PropertiesPanel):
    bl_label = "HEIO Mesh Properties"
    bl_context = "data"

    @staticmethod
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

    @staticmethod
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

        return HEIO_PT_Mesh.draw_mesh_info_layout(
            body,
            context,
            mesh_info_list,
            ui_list,
            menu,
            type
        )

    @staticmethod
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
        row.prop(collision_info, "custom", text="",
                 icon='RESTRICT_INSTANCED_ON' if collision_info.custom else 'RESTRICT_INSTANCED_OFF')
        if collision_info.custom:
            row.prop(collision_info, "value", text="")
        else:
            row.prop(collision_info, "value_enum", text="")

    @staticmethod
    def draw_group_editor(
            layout,
            context,
            group):

        if layout is None:
            return

        layout.use_property_split = True
        layout.use_property_decorate = False

        HEIO_PT_Mesh.draw_collision_info_editor(
            layout,
            group.collision_layer,
            "Collision layer"
        )

        layout.prop(group, "is_convex_collision")

        if not group.is_convex_collision:
            return

        HEIO_PT_Mesh.draw_collision_info_editor(
            layout,
            group.convex_type,
            "Convex collision type"
        )

        HEIO_PT_Mesh.draw_mesh_info_panel(
            layout,
            context,
            group.convex_flags,
            HEIO_UL_CollisionInfoList,
            None,
            'COLLISION_CONVEXFLAGS',
            'Convex layer flags'
        )

    @staticmethod
    def draw_primitive_editor(
            layout: bpy.types.UILayout | None,
            context: bpy.types.Context,
            primitive):

        if layout is None:
            return

        layout.use_property_split = True
        layout.use_property_decorate = False

        layout.prop(primitive, "shape_type")
        layout.separator()
        layout.prop(primitive, "position")
        layout.prop(primitive, "rotation")

        if primitive.shape_type == 'SPHERE':
            layout.prop(primitive, "dimensions", text="Radius", index=0)
        elif primitive.shape_type == 'BOX':
            layout.prop(primitive, "dimensions")
        else:
            column = layout.column(align=True)
            column.prop(primitive, "dimensions", text="Radius", index=0)
            column.prop(primitive, "dimensions", text="Height", index=2)

        HEIO_PT_Mesh.draw_collision_info_editor(
            layout, primitive.collision_layer, "Collision layer")
        HEIO_PT_Mesh.draw_collision_info_editor(
            layout, primitive.collision_type, "Collision type")

        HEIO_PT_Mesh.draw_mesh_info_panel(
            layout,
            context,
            primitive.collision_flags,
            HEIO_UL_CollisionInfoList,
            None,
            'COLLISION_PRIMITIVEFLAGS',
            'Collision flags'
        )

    @staticmethod
    def draw_export_panel(
            layout: bpy.types.UILayout,
            props):

        header, body = layout.panel("heio_mesh_export", default_closed=True)

        header.label(text="Export settings")
        if not body:
            return None

        body.use_property_split = False
        body.use_property_decorate = False

        body.prop(props, "force_enable_8_weights")
        body.prop(props, "force_enable_multi_tangent")

    # === overriden methods === #

    @classmethod
    def verify(cls, context):
        obj = context.active_object
        if obj is None:
            return "No active object"

        if obj.type != 'MESH':
            return "Active object not a mesh"

        return None

    @classmethod
    def draw_panel(cls, layout, context):

        mesh = context.active_object.data

        HEIO_PT_Mesh.draw_export_panel(
            layout,
            mesh.heio_mesh
        )

        body = HEIO_PT_Mesh.draw_mesh_info_panel(
            layout,
            context,
            mesh.heio_mesh.groups,
            HEIO_UL_MeshGroups,
            HEIO_MT_MeshGroupsContextMenu,
            'MESH_GROUPS',
            'Groups'
        )

        HEIO_PT_Mesh.draw_group_editor(
            body,
            context,
            mesh.heio_mesh.groups.active_element
        )

        HEIO_PT_Mesh.draw_mesh_info_panel(
            layout,
            context,
            mesh.heio_mesh.render_layers,
            HEIO_UL_MeshLayers,
            HEIO_MT_MeshLayersContextMenu,
            'RENDER_LAYERS',
            'Render layers'
        )

        draw_lod_info_panel(layout, context, mesh.heio_mesh.lod_info)
        draw_sca_editor_menu(layout, mesh.heio_mesh.sca_parameters, 'MESH')

        layout.separator(type="LINE")

        HEIO_PT_Mesh.draw_mesh_info_panel(
            layout,
            context,
            mesh.heio_mesh.collision_types,
            HEIO_UL_CollisionInfoList,
            HEIO_MT_CollisionTypesContextMenu,
            'COLLISION_TYPES',
            'Collision types'
        )

        HEIO_PT_Mesh.draw_mesh_info_panel(
            layout,
            context,
            mesh.heio_mesh.collision_flags,
            HEIO_UL_CollisionInfoList,
            HEIO_MT_CollisionFlagsContextMenu,
            'COLLISION_FLAGS',
            'Collision flags'
        )

        primitive_body = HEIO_PT_Mesh.draw_mesh_info_panel(
            layout,
            context,
            mesh.heio_mesh.collision_primitives,
            HEIO_UL_CollisionPrimitiveList,
            None,
            'COLLISION_PRIMITIVES',
            'Collision primitives'
        )

        HEIO_PT_Mesh.draw_primitive_editor(
            primitive_body,
            context,
            mesh.heio_mesh.collision_primitives.active_element
        )