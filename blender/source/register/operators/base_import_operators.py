import os
import bpy
from bpy.types import Context
from bpy.props import (
    BoolProperty,
    EnumProperty,
    StringProperty,
    CollectionProperty
)

from .base import HEIOBaseFileLoadOperator
from .. import definitions
from ...exceptions import UserException

from ...dotnet import load_dotnet, SharpNeedle, HEIO_NET


class ImportOperator(HEIOBaseFileLoadOperator):
    bl_options = {'PRESET', 'UNDO'}

    files: CollectionProperty(
        name='File paths',
        type=bpy.types.OperatorFileListElement
    )

    def print_resolve_info(self, context: bpy.types.Context, resolve_info):
        if resolve_info.UnresolvedFiles.Length == 0:
            return

        resolve_info_text = bpy.data.texts.new("Import resolve report")
        resolve_info_text.write(
            f"{resolve_info.UnresolvedFiles.Length} files could not be found.\n\n")

        if resolve_info.PackedDependencies.Length > 0:
            resolve_info_text.write(
                "Some files may be located in the following archives and need to be unpacked:\n")
            for packed in resolve_info.PackedDependencies:
                resolve_info_text.write(f"\t{packed}\n")

            resolve_info_text.write("\n")

        if resolve_info.MissingDependencies.Length > 0:
            resolve_info_text.write(
                "Following dependencies were not found altogether:\n")
            for missing in resolve_info.MissingDependencies:
                resolve_info_text.write(f"\t{missing}\n")

            resolve_info_text.write("\n")

        resolve_info_text.write("List of unresolved files:\n")
        for unresolved_file in resolve_info.UnresolvedFiles:
            resolve_info_text.write(f"\t{unresolved_file}\n")

        bpy.ops.wm.window_new()
        context.area.type = 'TEXT_EDITOR'
        context.space_data.text = resolve_info_text
        context.space_data.top = 0

    def _execute(self, context: Context):
        from ...dotnet import load_dotnet
        load_dotnet()

        self.target_definition = definitions.get_target_definition(context)
        if self.target_definition is None:
            raise UserException("Invalid target game!")

        return self.import_(context)


class ImportMaterialOperator(ImportOperator):

    filter_glob: StringProperty(
        default="*.material",
        options={'HIDDEN'},
    )

    create_undefined_parameters: BoolProperty(
        name="Create undefined parameters/textures",
        description="If the shader of a material is defined, create parameters inside the material that are not part of the definition, otherwise ignore them.",
        default=False
    )

    import_images: BoolProperty(
        name="Import Images",
        description="Import images if found, otherwise use placeholders",
        default=True
    )

    nrm_invert_y_channel: EnumProperty(
        name="Invert Y channel of normal maps",
        description="Whether to invert the Y channel on normal maps when importing",
        items=(
            ("AUTO", "Automatic",
             "Automatically determine whether to invert the Y channel based on the target game"),
            ("INVERT", "Invert", "Always invert the Y channel"),
            ("DONT", "Don't invert", "Don't invert the Y channel")
        ),
        default="AUTO"
    )

    use_existing_images: BoolProperty(
        name="Use existing images",
        description="When the active file contains a image with a matching image file name, use that instead of importing an image file",
        default=False
    )

    def import_materials(self, context, materials):
        from ...importing import i_material
        return i_material.convert_sharpneedle_materials(
            context,
            materials,
            self.create_undefined_parameters,
            self.use_existing_images,
            self.nrm_invert_y_channel,
            self.import_images)

    def import_material_files(self, context):
        load_dotnet()

        directory = os.path.dirname(self.filepath)
        sn_materials = []
        resource_manager = SharpNeedle.RESOURCE_MANAGER()

        for file in self.files:
            filepath = os.path.join(directory, file.name)

            try:
                material = SharpNeedle.RESOURCE_EXTENSIONS.Open[SharpNeedle.MATERIAL](
                    resource_manager, filepath, True)
            except Exception as error:
                print(f"An error occured while importing {file.name}")
                raise error

            sn_materials.append(material)

        return self.import_materials(context, sn_materials)

    def draw_panel_material(self):
        header, body = self.layout.panel(
            "HEIO_import_material", default_closed=False)
        header.label(text=(
            "General"
            if "material" in self.bl_idname.lower()
            else "Material"
        ))

        if not body:
            return

        body.use_property_split = False
        body.use_property_decorate = False

        body.prop(self, "create_undefined_parameters")
        body.prop(self, "import_images")

        if self.import_images:
            body.use_property_split = True
            body.prop(self, "nrm_invert_y_channel")
            body.use_property_split = False

        body.prop(self, "use_existing_images")

        if "blender_dds_addon" not in bpy.context.preferences.addons.keys():
            box = body.box()
            box.label(text="Please install and enable the blender")
            box.label(text="DDS addon for better texture import support")

            from .info_operators import HEIO_OT_Info_DDS_Addon
            body.operator(HEIO_OT_Info_DDS_Addon.bl_idname)

    def draw(self, context: Context):
        super().draw(context)
        self.draw_panel_material()


class ImportModelBaseOperator(ImportMaterialOperator):

    vertex_merge_mode: EnumProperty(
        name="Vertex merge mode",
        description="\"Merge by distance\" mode",
        items=(
            ('NONE', "None", "No merging at all"),
            ('SUBMESH', "Per Submesh",
             "Merge vertices that are part of the same submesh"),
            ('ALL', "All", "Merge all"),
        ),
        default='ALL'
    )

    def import_models(self, context: bpy.types.Context, models):

        sn_materials = HEIO_NET.MODEL_HELPER.GetMaterials(models)
        materials = self.import_materials(context, sn_materials)

        from ...importing import i_mesh
        return i_mesh.convert_models(models, materials, self.vertex_merge_mode)

    def draw_panel_model(self):
        header, body = self.layout.panel(
            "HEIO_import_model", default_closed=False)
        header.label(text="Model")

        if not body:
            return

        body.use_property_split = True
        body.use_property_decorate = False

        body.prop(self, "vertex_merge_mode")

    def draw(self, context: Context):
        super().draw(context)
        self.draw_panel_model()


class ImportTerrainModelOperator(ImportModelBaseOperator):

    filter_glob: StringProperty(
        default="*.terrain-model",
        options={'HIDDEN'},
    )

    def import_terrain_model_files(self, context: bpy.types.Context):
        load_dotnet()

        directory = os.path.dirname(self.filepath)
        filepaths = [os.path.join(directory, file.name) for file in self.files]

        terrain_models, resolve_info = HEIO_NET.MODEL_HELPER.LoadTerrainFiles(
            filepaths, HEIO_NET.RESOLVE_INFO())

        meshes = self.import_models(context, terrain_models)
        for mesh in meshes:
            obj = bpy.data.objects.new(meshes.Name, mesh)
            context.scene.collection.objects.link(obj)

        self.print_resolve_info(context, resolve_info)


class ImportPointCloudOperator(ImportModelBaseOperator):

    filter_glob: StringProperty(
        default="*.pcmodel",
        options={'HIDDEN'},
    )

    def import_point_cloud_files(self, context: bpy.types.Context):
        directory = os.path.dirname(self.filepath)
        filepaths = [os.path.join(directory, file.name) for file in self.files]

        point_cloud_collection, resolve_info = HEIO_NET.POINT_CLOUD_COLLECTION.LoadPointClouds(
            filepaths, HEIO_NET.RESOLVE_INFO())

        meshes = self.import_models(context, point_cloud_collection.TerrainModels)

        from ...importing import i_pointcloud
        collections = i_pointcloud.convert_point_cloud_collection(point_cloud_collection, meshes)

        for collection in collections:
            context.collection.children.link(collection)

        self.print_resolve_info(context, resolve_info)
