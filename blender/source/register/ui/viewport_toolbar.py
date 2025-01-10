import bpy

from .. operators import (
    mesh_geometry_operators,
    material_operators,
    image_operators,
    info_operators,
    scap_mass_edit_operators
)

from . import (
    scene_panel,
    mesh_panel,
    material_panel,
    armature_panel,
    node_panel
)

from ...utility.draw import draw_error_box


class ViewportToolPanel(bpy.types.Panel):
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "HEIO Tools"
    bl_options = {'DEFAULT_CLOSED'}


class HEIO_PT_VTP_GeneralTools(ViewportToolPanel):
    bl_label = "General Tools"

    def draw(self, context):
        layout = self.layout

        layout.operator(
            mesh_geometry_operators.HEIO_OT_SplitMeshGroups.bl_idname)
        layout.operator(
            mesh_geometry_operators.HEIO_OT_MergeMeshGroups.bl_idname)
        layout.operator(
            mesh_geometry_operators.HEIO_OT_CollisionPrimitivesToGeometry.bl_idname)

        layout.separator(type='LINE', factor=1.5)

        layout.operator(
            material_operators.HEIO_OT_Material_SetupNodes.bl_idname)

        layout.separator(type='LINE', factor=1.5)

        layout.operator(
            image_operators.HEIO_OT_ReimportImages.bl_idname)


class HEIO_PT_VTP_SCAP_MassEdit(ViewportToolPanel):
    bl_label = "SCA Parameter Mass-edit"

    @staticmethod
    def _draw_values(layout: bpy.types.UILayout, mass_edit_info):

        col = layout.column(align=True)

        row = col.row(align=True)

        if mass_edit_info.use_preset:
            row.prop(mass_edit_info, "value_name_enum", text="")
        else:
            if len(mass_edit_info.value_name) == 0:
                icon = "ERROR"
            else:
                icon = "NONE"
            row.prop(mass_edit_info, "value_name", text="", icon=icon)

        row.prop(mass_edit_info, "use_preset", text="", icon='PRESET')

        split = col.split(factor=0.5, align=True)

        enum_row = split.row(align=True)
        enum_row.active = not mass_edit_info.use_preset
        enum_row.prop(mass_edit_info, "value_type", text="")

        property = "value"
        if mass_edit_info.value_type != 'INTEGER':
            property = mass_edit_info.value_type.lower() + "_value"

        split.prop(mass_edit_info, property, text="")

    def draw(self, context):
        layout = self.layout
        mass_edit_info = context.scene.heio_scap_massedit

        layout.use_property_split = True
        layout.use_property_decorate = False

        layout.prop(mass_edit_info, "mode")

        layout.use_property_split = False
        self._draw_values(layout, mass_edit_info)

        layout.separator()

        row = layout.row(align=True)
        row.operator(
            scap_mass_edit_operators.HEIO_OT_SCAP_MassEdit_Select.bl_idname).exact = False
        row.operator(scap_mass_edit_operators.HEIO_OT_SCAP_MassEdit_Select.bl_idname,
                     text="Select Exact").exact = True

        row = layout.row(align=True)
        row.operator(
            scap_mass_edit_operators.HEIO_OT_SCAP_MassEdit_Set.bl_idname)
        row.operator(
            scap_mass_edit_operators.HEIO_OT_SCAP_MassEdit_Remove.bl_idname)


class HEIO_PT_VTP_Info(ViewportToolPanel):
    bl_label = "Info"

    def draw(self, context):
        layout = self.layout

        box = layout.box()
        box.label(text="You can right click any button")
        box.label(text="or property field added by the")
        box.label(text="addon and click \"Online Manual\"")
        box.label(text="to read about it.")

        layout.operator(info_operators.HEIO_OT_Info_Manual.bl_idname)
        layout.operator(info_operators.HEIO_OT_Info_Discord.bl_idname)
        layout.operator(info_operators.HEIO_OT_Info_Report.bl_idname)


class ViewportToolDataPanel(ViewportToolPanel):

    base: bpy.types.Panel

    def draw_target_header(self, context: bpy.types.Context):
        return

    def get_target_name(self, context: bpy.types.Context):
        return f"Active Object: {context.active_object.name}"

    def draw(self, context):
        self.draw_target_header(context)
        return self.base.draw(self, context)

    def draw_panel(self, context):
        self.layout.label(text=self.get_target_name(context))
        return self.base.draw_panel(self, context)  # pylint: disable=no-member


class HEIO_PT_VTP_SceneData(ViewportToolDataPanel):
    bl_label = "Scene data"

    def draw(self, context):
        scene_panel.HEIO_PT_Scene.draw_panel(
            self.layout,
            context
        )


class HEIO_PT_VTP_ObjectData(ViewportToolPanel):
    bl_label = "Object data"

    @staticmethod
    def _draw_panel(
            layout: bpy.types.UILayout,
            context: bpy.types.Context,
            typename: str,
            label: str,
            base_panel,
            get_target_name,
            start_info=None):

        header, body = layout.panel(
            "heio_vtp_obj_" + typename, default_closed=True)
        header.label(text=label)

        if not body:
            return

        if start_info is not None:
            start_info(body, context)

        if draw_error_box(body, base_panel.verify(context)):
            return

        target_name = get_target_name(context)
        if target_name is not None:
            body.label(text=target_name)

        base_panel.draw_panel(body, context)

    @staticmethod
    def draw_materials_list(layout: bpy.types.UILayout, context: bpy.types.Context):
        obj = context.active_object
        if obj is None or obj.type != 'MESH':
            return

        layout.label(text=f"Active object: {obj.name}")

        is_sortable = len(obj.material_slots) > 1
        rows = 3
        if is_sortable:
            rows = 5

        row = layout.row()

        row.template_list(
            "MATERIAL_UL_matslots",
            "",
            obj,
            "material_slots",
            obj,
            "active_material_index",
            rows=rows)

        col = row.column(align=True)
        col.operator("object.material_slot_add", icon='ADD', text="")
        col.operator("object.material_slot_remove", icon='REMOVE', text="")

        col.separator()

        col.menu("MATERIAL_MT_context_menu", icon='DOWNARROW_HLT', text="")

        if is_sortable:
            col.separator()

            col.operator(
                "object.material_slot_move",
                icon='TRIA_UP',
                text="").direction = 'UP'

            col.operator(
                "object.material_slot_move",
                icon='TRIA_DOWN',
                text="").direction = 'DOWN'

        row = layout.row()
        row.template_ID(obj, "active_material", new="material.new")

        slot = None
        if obj.active_material_index < len(obj.material_slots):
            slot = obj.material_slots[obj.active_material_index]

        if slot:
            icon_link = 'MESH_DATA' if slot.link == 'DATA' else 'OBJECT_DATA'
            row.prop(slot, "link", icon=icon_link, icon_only=True)

        if obj.mode == 'EDIT':
            row = layout.row(align=True)
            row.operator("object.material_slot_assign", text="Assign")
            row.operator("object.material_slot_select", text="Select")
            row.operator("object.material_slot_deselect", text="Deselect")

    def draw(self, context):
        layout = self.layout

        self._draw_panel(
            layout,
            context,
            "mesh",
            "Mesh",
            mesh_panel.HEIO_PT_Mesh,
            lambda c: f"Active mesh: {c.active_object.data.name}"
        )

        self._draw_panel(
            layout,
            context,
            "material",
            "Material",
            material_panel.HEIO_PT_Material,
            lambda c: None,
            self.draw_materials_list
        )

        self._draw_panel(
            layout,
            context,
            "armature",
            "Armature",
            armature_panel.HEIO_PT_Armature,
            lambda c: f"Active armature: {c.active_object.data.name}"
        )

        self._draw_panel(
            layout,
            context,
            "bone",
            "Bone",
            node_panel.HEIO_PT_Node_Bone,
            lambda c: f"Active bone: {c.active_bone.name}"
        )
