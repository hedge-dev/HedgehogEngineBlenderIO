import bpy

from .base_panel import PropertiesPanel
from .mesh_info_ui import (
    BaseMeshInfoContextMenu,
    draw_mesh_info_panel
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

        split = layout.split(factor=0.1)
        split.label(text=str(index))

        if item.custom or item.value_enum == 'ERROR_FALLBACK':
            split.label(text=f"Custom: {item.value}")
        else:
            split.label(text=item.value_enum)


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
    def _draw_mesh_info_panel(
            layout: bpy.types.UILayout,
            context: bpy.types.Context,
            mesh_info_list,
            menu: bpy.types.Menu,
            type: str,
            label: str):

        body = draw_mesh_info_panel(
            layout,
            context,
            mesh_info_list,
            HEIO_UL_CollisionInfoList,
            menu,
            type,
            label
        )

        HEIO_PT_CollisionMesh._draw_collision_info_editor(
            body,
            context,
            mesh_info_list.active_element
        )

    @staticmethod
    def _draw_type_panel(layout, context, type, label, typename):
        header, body = layout.panel(
            "heio_mesh_info_collision_" + typename, default_closed=False)
        header.label(text=label)

        if not body:
            return

        HEIO_PT_CollisionMesh._draw_collision_info_editor(
            body, context, type)

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

        HEIO_PT_CollisionMesh._draw_type_panel(
            layout,
            context,
            layer.convex_type,
            "Convex layer type",
            "layer_type")

        HEIO_PT_CollisionMesh._draw_mesh_info_panel(
            layout,
            context,
            layer.convex_flags,
            None,
            'COLLISION_CONVEXFLAGS',
            'Convex layer flags'
        )

    @staticmethod
    def _draw_primitive_editor(
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

        HEIO_PT_CollisionMesh._draw_type_panel(
            layout,
            context,
            primitive.surface_layer,
            "Surface layer",
            "primitive_layer")

        HEIO_PT_CollisionMesh._draw_type_panel(
            layout,
            context,
            primitive.surface_type,
            "Surface type",
            "primitive_type")

        HEIO_PT_CollisionMesh._draw_mesh_info_panel(
            layout,
            context,
            primitive.surface_flags,
            None,
            'COLLISION_PRIMITIVEFLAGS',
            'Surface flags'
        )

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

        HEIO_PT_CollisionMesh._draw_mesh_info_panel(
            layout,
            context,
            mesh.heio_collision_mesh.types,
            HEIO_MT_CollisionTypesContextMenu,
            'COLLISION_TYPES',
            'Types'
        )

        HEIO_PT_CollisionMesh._draw_mesh_info_panel(
            layout,
            context,
            mesh.heio_collision_mesh.flags,
            HEIO_MT_CollisionFlagsContextMenu,
            'COLLISION_FLAGS',
            'Flags'
        )

        primitive_body = draw_mesh_info_panel(
            layout,
            context,
            mesh.heio_collision_mesh.primitives,
            HEIO_UL_CollisionPrimitiveList,
            None,
            'COLLISION_PRIMITIVES',
            'Primitives'
        )

        HEIO_PT_CollisionMesh._draw_primitive_editor(
            primitive_body,
            context,
            mesh.heio_collision_mesh.primitives.active_element
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
