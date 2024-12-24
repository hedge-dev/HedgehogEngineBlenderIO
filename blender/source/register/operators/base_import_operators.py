import os
import bpy
from bpy.types import Context
from bpy.props import (
    BoolProperty,
    EnumProperty,
    StringProperty,
    CollectionProperty,
    FloatProperty
)

from .base import HEIOBaseFileLoadOperator

from .. import definitions

from ...importing import i_image, i_material, i_mesh
from ...dotnet import load_dotnet, SharpNeedle, HEIO_NET
from ...utility.general import get_addon_preferences
from ...utility import progress_console
from ...exceptions import UserException


class ImportOperator(HEIOBaseFileLoadOperator):
    bl_options = {'PRESET', 'UNDO'}

    files: CollectionProperty(
        name='File paths',
        type=bpy.types.OperatorFileListElement
    )

    def _execute(self, context: Context):
        load_dotnet()

        self.target_definition = definitions.get_target_definition(context)
        if self.target_definition is None:
            raise UserException("Invalid target game!")

        self.addon_preference = get_addon_preferences(context)
        self._setup(context)

        progress_console.cleanup()
        progress_console.start("Importing")
        result = self.import_(context)
        progress_console.end()

        self.print_resolve_info(context)

        return result

    def _setup(self, context):
        self.resolve_infos = []

    def print_resolve_info(self, context: bpy.types.Context):
        resolve_info = HEIO_NET.RESOLVE_INFO.Combine(self.resolve_infos)

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

    def _setup(self, context):
        super()._setup(context)

        ntsp_dir = ""

        if self.target_definition.uses_ntsp:
            ntsp_dir = getattr(self.addon_preference, "ntsp_dir_" +
                               self.target_definition.identifier.lower())

        self.image_loader = i_image.ImageLoader(
            self.target_definition,
            self.use_existing_images,
            self.nrm_invert_y_channel,
            ntsp_dir
        )

        self.material_converter = i_material.MaterialConverter(
            self.target_definition,
            self.image_loader,
            self.create_undefined_parameters,
            self.import_images
        )

    def import_material_files(self):
        progress_console.update("Resolving & reading files")

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

        progress_console.update("Importing data")
        return self.material_converter.convert_materials(sn_materials)

    def print_resolve_info(self, context):
        self.resolve_infos.extend(self.image_loader.resolve_infos)
        return super().print_resolve_info(context)


class ImportModelBaseOperator(ImportMaterialOperator):

    vertex_merge_mode: EnumProperty(
        name="Vertex merge mode",
        description="\"Merge by distance\" mode",
        items=(
            ('NONE', "None", "No merging at all"),
            ('SUBMESH', "Per Submesh",
             "Merge vertices that are part of the same submesh"),
            ('SUBMESHGROUP', "Per Submesh group",
             "Merge vertices that are part of the same submesh group"),
            ('ALL', "All", "Merge all"),
        ),
        default='SUBMESHGROUP'
    )

    vertex_merge_distance: FloatProperty(
        name="Merge distance",
        description="The distance two vertices have to be apart from each other to be merged",
        default=0.001,
        precision=3,
        min=0,
        soft_min=0.001,
        soft_max=0.1,
    )

    merge_split_edges: BoolProperty(
        name="Merge split edges",
        description="Merge overlapping edges as sharps",
        default=True
    )

    create_mesh_layer_attributes: BoolProperty(
        name="Create layer attributes",
        description="Mesh layers will be imported as an integer attribute on polygons",
        default=False
    )

    create_meshgroup_attributes: BoolProperty(
        name="Create meshgroup attributes",
        description="Meshgrops will be imported as an integer attribute on polygons",
        default=True
    )

    import_tangents: BoolProperty(
        name="Import tangents",
        description="Import tangents instead of generating them based on the UVs",
        default=False
    )

    def draw_panel_model(self):
        header, body = self.layout.panel(
            "HEIO_import_model", default_closed=False)
        header.label(text="Model")

        if not body:
            return

        body.use_property_split = True
        body.use_property_decorate = False

        merge_header, merge_body = body.panel(
            "HEIO_import_model_merge", default_closed=True)
        merge_header.prop(self, "vertex_merge_mode")

        if merge_body:
            merge_body.active = self.vertex_merge_mode != 'NONE'
            merge_body.prop(self, "vertex_merge_distance")
            merge_body.prop(self, "merge_split_edges")
            body.separator()

        body.prop(self, "create_mesh_layer_attributes")
        body.prop(self, "create_meshgroup_attributes")
        body.prop(self, "import_tangents")

    def draw(self, context: Context):
        super().draw(context)
        self.draw_panel_model()

    def _setup(self, context):
        super()._setup(context)

        self.mesh_converter = i_mesh.MeshConverter(
            self.target_definition,
            self.material_converter,
            self.vertex_merge_mode,
            self.vertex_merge_distance,
            self.merge_split_edges,
            self.create_mesh_layer_attributes,
            self.create_meshgroup_attributes,
            self.import_tangents
        )

    def import_models(self, model_sets):

        sn_materials = HEIO_NET.MODEL_HELPER.GetMaterials(model_sets)
        self.material_converter.convert_materials(sn_materials)
        return self.mesh_converter.convert_model_sets(model_sets)


class ImportModelOperator(ImportModelBaseOperator):

    filter_glob: StringProperty(
        default="*.model",
        options={'HIDDEN'},
    )

    def import_model_files(self, context: bpy.types.Context):
        progress_console.update("Resolving & reading files")

        directory = os.path.dirname(self.filepath)
        filepaths = [os.path.join(directory, file.name) for file in self.files]

        models, resolve_info = HEIO_NET.MODEL_HELPER.LoadModelFiles[SharpNeedle.MODEL](
            filepaths, HEIO_NET.RESOLVE_INFO())

        self.resolve_infos.append(resolve_info)

        progress_console.update("Importing data")

        meshes = self.import_models(models)


class ImportTerrainModelOperator(ImportModelBaseOperator):

    filter_glob: StringProperty(
        default="*.terrain-model",
        options={'HIDDEN'},
    )

    def import_terrain_model_files(self, context: bpy.types.Context):
        progress_console.update("Resolving & reading files")

        directory = os.path.dirname(self.filepath)
        filepaths = [os.path.join(directory, file.name) for file in self.files]

        terrain_models, resolve_info = HEIO_NET.MODEL_HELPER.LoadModelFiles[SharpNeedle.TERRAIN_MODEL](
            filepaths, HEIO_NET.RESOLVE_INFO())

        self.resolve_infos.append(resolve_info)

        progress_console.update("Importing data")

        meshes = self.import_models(terrain_models)
        for mesh in meshes:
            obj = bpy.data.objects.new(mesh.name, mesh)
            context.scene.collection.objects.link(obj)


class ImportPointCloudOperator(ImportModelBaseOperator):

    filter_glob: StringProperty(
        default="*.pcmodel",
        options={'HIDDEN'},
    )

    def import_point_cloud_files(self, context: bpy.types.Context):
        progress_console.update("Resolving & reading files")

        directory = os.path.dirname(self.filepath)
        filepaths = [os.path.join(directory, file.name) for file in self.files]

        point_cloud_collection, resolve_info = HEIO_NET.POINT_CLOUD_COLLECTION.LoadPointClouds(
            filepaths, HEIO_NET.RESOLVE_INFO())

        self.resolve_infos.append(resolve_info)

        progress_console.update("Importing data")

        meshes = self.import_models(point_cloud_collection.TerrainModels)

        from ...importing import i_pointcloud
        collections = i_pointcloud.convert_point_cloud_collection(
            point_cloud_collection, meshes)

        for collection in collections:
            context.collection.children.link(collection)
