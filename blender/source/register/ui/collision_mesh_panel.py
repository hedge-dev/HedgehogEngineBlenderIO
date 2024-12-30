import bpy

from .base_panel import PropertiesPanel
from .mesh_info_ui import (
    BaseMeshInfoContextMenu,
    draw_mesh_info_panel,
    MESH_INFO_TOOLS
)

from ...utility.draw import draw_list


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

        split = layout.split(factor=0.1)
        split.label(text=str(index))

        if item.custom or item.value_enum == 'ERROR_FALLBACK':
            split.label(text=f"Custom: {item.value}")
        else:
            split.label(text=item.value_enum)


class HEIO_MT_CollisionLayersContextMenu(BaseMeshInfoContextMenu):
    bl_label = "Collision mesh layers operations"
    type = 'COLLISION_LAYERS'


class HEIO_MT_CollisionTypesContextMenu(BaseMeshInfoContextMenu):
    bl_label = "Collision mesh types operations"
    type = 'COLLISION_TYPES'


class HEIO_MT_CollisionFlagsContextMenu(BaseMeshInfoContextMenu):
    bl_label = "Collision mesh flags operations"
    type = 'COLLISION_FLAGS'


class HEIO_PT_CollisionMesh(PropertiesPanel):
    bl_label = "HEIO Collision Mesh Properties"
    bl_context = "data"

    @staticmethod
    def _draw_collision_info_editor(
            layout: bpy.types.UILayout,
            context: bpy.types.Context,
            collision_info):

        if layout is None:
            return

        layout.use_property_split = True
        layout.use_property_decorate = False

        if collision_info.custom or not context.scene.heio_scene.hide_custom_mesh_collision_info_toggle:
            layout.prop(collision_info, "custom")

        if collision_info.custom:
            layout.prop(collision_info, "value")
        else:
            layout.prop(collision_info, "value_enum")

    @staticmethod
    def _draw_layer_type_panel(layout, context, layer):
        header, body = layout.panel(
            "heio_mesh_info_collision_layer_type", default_closed=False)
        header.label(text="Convex layer type")

        if not body:
            return

        HEIO_PT_CollisionMesh._draw_collision_info_editor(
            body, context, layer.convex_type)

    @staticmethod
    def _draw_layer_flags_panel(layout, context, layer):
        header, body = layout.panel(
            "heio_mesh_info_collision_layer_flags", default_closed=False)
        header.label(text="Convex layer flags")

        if not body:
            return

        def set_op_type(operator, i):
            operator.type = 'COLLISION_CONVEXFLAGS'

        draw_list(
            body,
            HEIO_UL_CollisionInfoList,
            None,
            layer.convex_flags,
            MESH_INFO_TOOLS,
            set_op_type
        )

        flag_info = layer.convex_flags.active_element
        if flag_info is not None:
            HEIO_PT_CollisionMesh._draw_collision_info_editor(
                body, context, flag_info)

    @staticmethod
    def _draw_layer_editor(
            layout: bpy.types.UILayout | None,
            context: bpy.types.Context,
            layer):

        if layout is None:
            return

        HEIO_PT_CollisionMesh._draw_collision_info_editor(
            layout,
            context,
            layer
        )

        layout.prop(layer, "is_convex")

        if not layer.is_convex:
            return

        HEIO_PT_CollisionMesh._draw_layer_type_panel(layout, context, layer)
        HEIO_PT_CollisionMesh._draw_layer_flags_panel(layout, context, layer)

    @staticmethod
    def draw_collision_mesh_properties(
            layout: bpy.types.UILayout,
            context: bpy.types.Context,
            mesh: bpy.types.Mesh):

        layout.prop(context.scene.heio_scene,
                    "hide_custom_mesh_collision_info_toggle")

        layer_body = draw_mesh_info_panel(
            layout,
            context,
            mesh.heio_collision_mesh.layers,
            HEIO_UL_CollisionInfoList,
            HEIO_MT_CollisionLayersContextMenu,
            'COLLISION_LAYERS',
            'Layers'
        )

        HEIO_PT_CollisionMesh._draw_layer_editor(
            layer_body,
            context,
            mesh.heio_collision_mesh.layers.active_element
        )

        types_body = draw_mesh_info_panel(
            layout,
            context,
            mesh.heio_collision_mesh.types,
            HEIO_UL_CollisionInfoList,
            HEIO_MT_CollisionTypesContextMenu,
            'COLLISION_TYPES',
            'Types'
        )

        HEIO_PT_CollisionMesh._draw_collision_info_editor(
            types_body,
            context,
            mesh.heio_collision_mesh.types.active_element
        )

        flags_body = draw_mesh_info_panel(
            layout,
            context,
            mesh.heio_collision_mesh.flags,
            HEIO_UL_CollisionInfoList,
            HEIO_MT_CollisionFlagsContextMenu,
            'COLLISION_FLAGS',
            'Flags'
        )

        HEIO_PT_CollisionMesh._draw_collision_info_editor(
            flags_body,
            context,
            mesh.heio_collision_mesh.flags.active_element
        )

    # === overriden methods === #

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

        HEIO_PT_CollisionMesh.draw_collision_mesh_properties(
            self.layout,
            context,
            context.active_object.data)
