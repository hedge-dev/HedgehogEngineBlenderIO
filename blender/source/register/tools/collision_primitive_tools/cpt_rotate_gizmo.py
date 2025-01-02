import bpy
from bpy.props import FloatProperty, EnumProperty
from mathutils import Matrix, Vector, Quaternion

from ...operators.base import HEIOBaseModalOperator

class HEIO_OT_CollisionPrimitive_GizmoRotate(HEIOBaseModalOperator):
    bl_idname = "heio.gt.collision_primitive_gizmo_rotate"
    bl_label = "Rotate collision primitive"
    bl_description = "Rotate the collision primitive"
    bl_options = {'REGISTER', 'UNDO', 'INTERNAL'}

    offset: FloatProperty()

    mode: EnumProperty(
        name="Rotation mode",
        items=(
            ('X', "X Axis", ""),
            ('Y', "Y Axis", ""),
            ('Z', "Z Axis", ""),
            ('VIEW', "View Axis", "")
        )
    )

    def _execute(self, context):
        primitive = self._get_primitive(context)

        axis = self.mode
        if axis == 'VIEW':
            axis = context.region_data.view_matrix.to_3x3(
            ).inverted().normalized() @ Vector((0, 0, -1))

        primitive.rotation = self._initial_rotation @ Matrix.Rotation(
            self.offset, 4, axis).to_quaternion()

        return {'FINISHED'}

    def _get_primitive(self, context):
        return context.object.data.heio_collision_mesh.primitives.active_element

    def _modal(self, context: bpy.types.Context, event: bpy.types.Event):
        if event.type == 'MOUSEMOVE':
            self.offset += event.mouse_x - event.mouse_prev_x

            self._execute(context)
            context.area.header_text_set(f"Offset {self.offset:.4f}")
            context.region.tag_redraw()

        elif event.type == 'LEFTMOUSE':
            context.area.header_text_set(None)
            context.workspace.status_text_set(None)
            return {'FINISHED'}

        elif event.type in {'RIGHTMOUSE', 'ESC'}:
            self._get_primitive(context).rotation = self._initial_rotation
            context.area.header_text_set(None)
            context.workspace.status_text_set(None)
            return {'CANCELLED'}

        return {'RUNNING_MODAL'}

    def _invoke(self, context, event):
        self.offset = 0
        self.snap = False
        self.precision = False
        self.display_dial = True

        self._previous_mouse = Vector((event.mouse_x, event.mouse_y))
        self._initial_rotation = Quaternion(
            self._get_primitive(context).rotation)

        context.window_manager.modal_handler_add(self)
        context.workspace.status_text_set(
            "[ESC] or [RMB]: Cancel   |   [Shift]: Precision Mode   |   [Ctrl]: Snap")

        return {'RUNNING_MODAL'}
