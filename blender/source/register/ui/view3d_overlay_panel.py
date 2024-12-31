import bpy

class HEIO_VIEW3D_PT_overlay_collision_primitives(bpy.types.Panel):
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'HEADER'
    bl_parent_id = "VIEW3D_PT_overlay"
    bl_label = "HEIO Collision primitives"

    def draw(self, context):
        props = context.screen.heio_collision_primitives
        self.layout.prop(props, "show_primitives")

        content = self.layout.column()
        content.active = props.show_primitives

        row = content.row()
        row.prop(props, "random_colors")
        row_col = row.column()
        row_col.active = props.random_colors
        row_col.prop(props, "random_seed")

        content.prop(props, "line_width")

        row = content.row()
        row.prop(props, "surface_visibility", text="Surface")
        row.prop(props, "line_visibility", text="Lines")