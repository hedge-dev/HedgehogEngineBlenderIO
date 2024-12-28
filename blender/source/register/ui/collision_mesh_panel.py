import bpy

from .base_panel import PropertiesPanel

from ..property_groups.collision_mesh_properties import HEIO_CollisionMesh, BaseCollisionInfoList
from ..operators import collision_mesh_operators as cmo

from ...utility.draw import draw_list, TOOL_PROPERTY

COLLISION_MESH_INFO_TOOLS: list[TOOL_PROPERTY] = [
    (
        cmo.HEIO_OT_CollisionMeshInfo_Add.bl_idname,
        "ADD",
        {}
    ),
    (
        cmo.HEIO_OT_CollisionMeshInfo_Remove.bl_idname,
        "REMOVE",
        {}
    ),
    None,
    (
        cmo.HEIO_OT_CollisionMeshInfo_Move.bl_idname,
        "TRIA_UP",
        {"direction": "UP"}
    ),
    (
        cmo.HEIO_OT_CollisionMeshInfo_Move.bl_idname,
        "TRIA_DOWN",
        {"direction": "DOWN"}
    )
]

COLLISION_MESH_INFO_TOOLS_NO_MOVE: list[TOOL_PROPERTY] = [
    (
        cmo.HEIO_OT_CollisionMeshInfo_Add.bl_idname,
        "ADD",
        {}
    ),
    (
        cmo.HEIO_OT_CollisionMeshInfo_Remove.bl_idname,
        "REMOVE",
        {}
    )
]


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

        if item.custom:
            layout.label(text=f"Custom: {item.value}")
        else:
            layout.label(text=item.value_enum)


class HEIO_MT_CollisionLayersContextMenu(bpy.types.Menu):
    bl_label = "Collision mesh layers operations"

    def draw(self, context):
        op = self.layout.operator(
            cmo.HEIO_OT_CollisionMeshInfo_Delete.bl_idname)
        op.type = 'LAYERS'


class HEIO_MT_CollisionTypesContextMenu(bpy.types.Menu):
    bl_label = "Collision mesh types operations"

    def draw(self, context):
        op = self.layout.operator(
            cmo.HEIO_OT_CollisionMeshInfo_Delete.bl_idname)
        op.type = 'TYPES'


class HEIO_MT_CollisionFlagsContextMenu(bpy.types.Menu):
    bl_label = "Collision mesh flags operations"

    def draw(self, context):
        op = self.layout.operator(
            cmo.HEIO_OT_CollisionMeshInfo_Delete.bl_idname)
        op.type = 'FLAGS'


class HEIO_PT_CollisionMesh(PropertiesPanel):
    bl_label = "HEIO Collision Mesh Properties"
    bl_context = "data"

    @staticmethod
    def _draw_collision_info_editor(
            layout: bpy.types.UILayout,
            collision_info):

        layout.use_property_split = True
        layout.use_property_decorate = False

        layout.prop(collision_info, "custom")

        if collision_info.custom:
            layout.prop(collision_info, "value")
        else:
            layout.prop(collision_info, "value_enum")


    @staticmethod
    def _draw_collision_info_list(
            layout: bpy.types.UILayout,
            context: bpy.types.Context,
            collision_info_list: BaseCollisionInfoList,
            type: str,
            menu: bpy.types.Menu | None,
            tools : list[TOOL_PROPERTY]):

        lower = type.lower()
        upper = type.upper()

        header, body = layout.panel(
            "heio_collision_mesh_info_" + lower, default_closed=True)
        header.label(text=type)
        if not body:
            return None

        if not collision_info_list.initialized:
            op = body.operator(
                cmo.HEIO_OT_CollisionMeshInfo_Initialize.bl_idname)
            op.type = upper
            return None

        if collision_info_list.attribute_invalid:
            box = body.box()
            box.label(
                text=f"Invalid \"{collision_info_list.attribute_name}\" attribute!")
            box.label(text="Must use domain \"Face\" and type \"Integer\"!")
            box.label(text="Please remove or convert")
            return None

        def set_op_type(operator, i):
            operator.type = upper

        draw_list(
            body,
            HEIO_UL_CollisionInfoList,
            menu,
            collision_info_list,
            tools,
            set_op_type
        )

        collision_info = collision_info_list.active_element
        if collision_info is None:
            return None

        HEIO_PT_CollisionMesh._draw_collision_info_editor(body, collision_info)
        return body

    @staticmethod
    def _draw_layer_editor(
            layout: bpy.types.UILayout | None,
            context: bpy.types.Context,
            layers: BaseCollisionInfoList):

        if layout is None:
            return

        layer = layers.active_element

        layout.prop(layer, "is_convex")

        if not layer.is_convex:
            return

        header, body = layout.panel(
            "heio_collision_mesh_info_layer_type", default_closed=False)
        header.label(text="Convex layer type")
        if body:
            HEIO_PT_CollisionMesh._draw_collision_info_editor(body, layer.convex_type)

        header, body = layout.panel(
            "heio_collision_mesh_info_layer_flags", default_closed=False)
        header.label(text="Convex layer flags")

        if body:
            def set_op_type(operator, i):
                operator.type = 'CONVEXFLAGS'

            draw_list(
                body,
                HEIO_UL_CollisionInfoList,
                None,
                layer.convex_flags,
                COLLISION_MESH_INFO_TOOLS_NO_MOVE,
                set_op_type
            )

            flag_info = layer.convex_flags.active_element
            if flag_info is not None:
                 HEIO_PT_CollisionMesh._draw_collision_info_editor(body, flag_info)


    # === overriden methods === #

    @staticmethod
    def draw_material_properties(
            layout: bpy.types.UILayout,
            context: bpy.types.Context,
            mesh: bpy.types.Mesh):

        collision_mesh: HEIO_CollisionMesh = mesh.heio_collision_mesh

        layer_body = HEIO_PT_CollisionMesh._draw_collision_info_list(
            layout,
            context,
            collision_mesh.layers,
            'Layers',
            HEIO_MT_CollisionLayersContextMenu,
            COLLISION_MESH_INFO_TOOLS
        )

        HEIO_PT_CollisionMesh._draw_layer_editor(
            layer_body, context, collision_mesh.layers
        )

        HEIO_PT_CollisionMesh._draw_collision_info_list(
            layout,
            context,
            collision_mesh.types,
            'Types',
            HEIO_MT_CollisionTypesContextMenu,
            COLLISION_MESH_INFO_TOOLS_NO_MOVE
        )

        HEIO_PT_CollisionMesh._draw_collision_info_list(
            layout,
            context,
            collision_mesh.flags,
            'Flags',
            HEIO_MT_CollisionFlagsContextMenu,
            COLLISION_MESH_INFO_TOOLS_NO_MOVE
        )

    @classmethod
    def poll(cls, context: bpy.types.Context):
        return cls.verify(context) is None

    @classmethod
    def verify(cls, context: bpy.types.Context):
        obj = context.active_object
        if obj is None:
            return "No active object"

        if obj.type != 'MESH':
            return "Active object not a mesh"

        return None

    def draw_panel(self, context):

        HEIO_PT_CollisionMesh.draw_material_properties(
            self.layout,
            context,
            context.active_object.data)
