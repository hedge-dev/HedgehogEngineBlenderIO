import os
import bpy
from bpy.types import Context
from bpy.props import (
    BoolProperty,
    EnumProperty,
    StringProperty
)

from .base import HEIOBaseDirectorySaveOperator
from .. import definitions
from ...exceptions import UserException


class ExportOperator(HEIOBaseDirectorySaveOperator):
    bl_options = {'PRESET', 'UNDO'}

    def export(self, context: Context):
        return {'FINISHED'}

    def _execute(self, context: Context):
        from ...dotnet import load_dotnet
        load_dotnet()

        self.target_definition = definitions.get_target_definition(context)
        if self.target_definition is None:
            raise UserException("Invalid target game!")

        return self.export(context)


class ExportObjectSelectionOperator(ExportOperator):

    use_selection: BoolProperty(
        name='Selected Objects',
        description='Export selected objects only',
        default=False
    )

    use_visible: BoolProperty(
        name='Visible Objects',
        description='Export visible objects only',
        default=False
    )

    use_active_collection: BoolProperty(
        name='Active Collection',
        description='Export objects in the active collection only',
        default=False
    )

    use_active_scene: BoolProperty(
        name='Active Scene',
        description='Export active scene only',
        default=True
    )

    collection: StringProperty(
        name="Source Collection",
        description="Export only objects from this collection (and its children)",
        default="",
    )

    def collect_objects(self, context: Context):
        if self.collection:
            collection: bpy.types.Collection = bpy.data.collections[self.collection]
            result = set(collection.all_objects)
        else:
            result = set()

            if self.use_active_collection:
                objects = context.collection.all_objects
            elif self.use_active_scene:
                objects = context.scene.objects
            else:
                objects = bpy.data.objects

            for obj in objects:
                if (self.use_visible and not obj.visible_get()
                        or self.use_selection and not obj.select_get()):
                    continue
                result.add(obj)

        roots = set()
        for obj in result:
            parent = obj
            while parent.parent is not None:
                parent = parent.parent
            roots.add(parent)

        if len(roots) == 1:
            for root in roots:
                if root.type == 'ARMATURE':
                    result.add(root)

        return result

    def draw_panel_include(self, is_file_browser: bool):
        if not is_file_browser:
            return

        header, body = self.layout.panel(
            "HEIO_export_include", default_closed=False)
        header.label(text="Include")

        if body:
            col = body.column(heading="Limit to", align=True)
            col.prop(self, "use_selection")
            col.prop(self, "use_visible")
            col.prop(self, "use_active_collection")
            col.prop(self, "use_active_scene")

        return body

    def draw(self, context: Context):
        super().draw(context)

        # Are we inside the File browser
        is_file_browser = context.space_data.type == 'FILE_BROWSER'

        self.draw_panel_include(is_file_browser)


class ExportMaterialOperator(ExportObjectSelectionOperator):

    image_mode: EnumProperty(
        name="Image Export Mode",
        items=(
             ('OVERWRITE', "Overwrite",
              "Export all images and overwrite existing ones."),
             ('MISSING', "Missing",
              "Export only images that dont already exist in the output folder."),
             ('NONE', "None", "Export no images at all"),
        ),
        default='MISSING'
    )

    nrm_invert_y_channel: EnumProperty(
        name="Invert Y channel of normal maps",
        description="Whether to invert the Y channel on normal maps when exporting",
        items=(
            ("AUTO", "Automatic", "Automatically determine whether to invert the Y channel based on the target game"),
            ("INVERT", "Invert", "Always invert the Y channel"),
            ("DONT", "Don't invert", "Don't invert the Y channel")
        ),
        default="AUTO"
    )

    def draw_panel_material(self):
        header, body = self.layout.panel(
            "HEIO_export_material", default_closed=False)
        header.label(text=(
            "General"
            if self.bl_idname.startswith("HEIO_OT_export_material")
            else "Material"
        ))

        if not body:
            return

        body.use_property_split = True
        body.use_property_decorate = False

        if "blender_dds_addon" in bpy.context.preferences.addons.keys():
            body.prop(self, "image_mode")

            if self.image_mode != 'NONE':
                body.prop(self, "nrm_invert_y_channel")

        else:
            box = body.box()
            box.label(text="Please install and enable the blender")
            box.label(text="DDS addon export textures")

            from .info_operators import HEIO_OT_Info_DDS_Addon
            body.operator(HEIO_OT_Info_DDS_Addon.bl_idname)


    def draw(self, context: Context):
        super().draw(context)
        self.draw_panel_material()

    def get_materials(self, context):
        objects = self.collect_objects(context)
        result = set()

        for object in objects:
            if object.type == 'MESH':
                result.update(object.data.materials)

        return result

    def export_materials(self, context: bpy.types.Context, materials):
        from ...exporting import o_material
        sn_materials = o_material.convert_to_sharpneedle_materials(
            self.target_definition, materials)

        from ...dotnet import SharpNeedle

        for sn_material in sn_materials.values():
            filepath = os.path.join(self.directory, sn_material.Name + ".material")
            SharpNeedle.RESOURCE_EXTENSIONS.Write(sn_material, filepath)

        if self.image_mode != 'NONE':
            from ...exporting import o_image

            invert_normal_map_y_channel = (
                self.nrm_invert_y_channel == "INVERT"
                or (
                    self.nrm_invert_y_channel == "AUTO"
                    and self.target_definition.hedgehog_engine_version == 1
                )
            )

            o_image.export_material_images(
                materials,
                context,
                self.image_mode,
                invert_normal_map_y_channel,
                self.filepath
            )

        return {'FINISHED'}
