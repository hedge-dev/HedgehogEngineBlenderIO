import bpy

from .base_panel import PropertiesPanel
from .mesh_info_ui import (
    BaseMeshInfoContextMenu,
    draw_mesh_info_panel,
    HEIO_UL_CollisionInfoList,
    draw_collision_info_editor
)


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


class HEIO_PT_CollisionAttributes(PropertiesPanel):
    bl_label = "HEIO Collision Attributes"
    bl_context = "data"

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

        draw_collision_info_editor(layout, primitive.collision_layer, "Collision layer")
        draw_collision_info_editor(layout, primitive.collision_type, "Collision type")

        draw_mesh_info_panel(
            layout,
            context,
            primitive.collision_flags,
            HEIO_UL_CollisionInfoList,
            None,
            'COLLISION_PRIMITIVEFLAGS',
            'Collision flags'
        )

    @staticmethod
    def draw_collision_mesh_properties(
            layout: bpy.types.UILayout,
            context: bpy.types.Context,
            mesh: bpy.types.Mesh):

        draw_mesh_info_panel(
            layout,
            context,
            mesh.heio_mesh.collision_types,
            HEIO_UL_CollisionInfoList,
            HEIO_MT_CollisionTypesContextMenu,
            'COLLISION_TYPES',
            'Types'
        )

        draw_mesh_info_panel(
            layout,
            context,
            mesh.heio_mesh.collision_flags,
            HEIO_UL_CollisionInfoList,
            HEIO_MT_CollisionFlagsContextMenu,
            'COLLISION_FLAGS',
            'Flags'
        )

        primitive_body = draw_mesh_info_panel(
            layout,
            context,
            mesh.heio_mesh.collision_primitives,
            HEIO_UL_CollisionPrimitiveList,
            None,
            'COLLISION_PRIMITIVES',
            'Primitives'
        )

        HEIO_PT_CollisionAttributes._draw_primitive_editor(
            primitive_body,
            context,
            mesh.heio_mesh.collision_primitives.active_element
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

        HEIO_PT_CollisionAttributes.draw_collision_mesh_properties(
            self.layout,
            context,
            context.active_object.data)
