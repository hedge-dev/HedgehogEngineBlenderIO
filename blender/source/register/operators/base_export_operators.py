import os
import bpy
from bpy.types import Context
from bpy.props import (
    BoolProperty,
    EnumProperty,
    StringProperty
)

from .base import HEIOBaseDirectorySaveOperator


class ExportOperator(HEIOBaseDirectorySaveOperator):
    bl_options = {'PRESET', 'UNDO'}

    def export(self, context: Context):
        return {'FINISHED'}

    def _execute(self, context: Context):
        from ...dotnet import load_dotnet
        load_dotnet()

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

        self.draw_panel_include(self.layout, is_file_browser)


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

    def export_materials(self, context, materials):
        from ...exporting import o_material
        sn_materials = o_material.convert_to_sharpneedle_materials(
            context, materials)

        from ...dotnet import SharpNeedle

        for sn_material in sn_materials.values():
            filepath = os.path.join(self.directory, sn_material.Name + ".material")
            SharpNeedle.RESOURCE_EXTENSIONS.Write(sn_material, filepath)

        if self.image_mode != 'NONE' and "blender_dds_addon" in context.preferences.addons.keys():
            from blender_dds_addon.ui.export_dds import export_as_dds
            context.scene.dds_options.allow_slow_codec = True

            images = set()
            for material in materials:
                for texture in material.heio_material.textures:
                    if texture.image is not None:
                        images.add(texture.image)

            for image in images:
                filepath = os.path.join(self.directory, image.name + ".dds")

                if self.image_mode == 'OVERWRITE' or not os.path.isfile(filepath):
                    export_as_dds(context, image, filepath)


        return {'FINISHED'}
