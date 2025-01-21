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

from ...importing import (
    i_image,
    i_material,
    i_mesh,
    i_node,
    i_model,
    i_collision_mesh,
    i_pointcloud
)

from ...dotnet import load_dotnet, SharpNeedle, HEIO_NET
from ...utility.general import get_addon_preferences, print_resolve_info
from ...utility import progress_console
from ...exceptions import HEIOUserException


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
            raise HEIOUserException("Invalid target game!")

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

    @classmethod
    def poll(cls, context):
        return context.mode == 'OBJECT'

    def draw(self, context):
        self.layout.use_property_decorate = False
        self.layout.use_property_split = True
        self.layout.separator()
        self.layout.prop(context.scene.heio_scene, "target_game")
        self.layout.prop(context.scene.heio_scene, "target_console")
        self.layout.separator()

    def print_resolve_info(self, context):
        print_resolve_info(context, self.resolve_infos)

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
            "HEIO_import_material", default_closed=True)
        header.label(text="Material")

        if not body:
            return

        body.use_property_split = False

        body.prop(self, "create_undefined_parameters")
        body.prop(self, "import_images")

        if self.import_images:
            body.use_property_split = True
            body.prop(self, "nrm_invert_y_channel")
            body.use_property_split = False

        body.prop(self, "use_existing_images")

        if "blender_dds_addon" not in bpy.context.preferences.addons.keys():
            body.separator()
            box = body.box()
            box.label(text="Please install and enable the blender")
            box.label(text="DDS addon for better texture import support")

            from .info_operators import HEIO_OT_Info_DDS_Addon
            body.operator(HEIO_OT_Info_DDS_Addon.bl_idname)
            body.separator()

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
        default=0.0001,
        precision=4,
        min=0,
        soft_min=0.0001,
        soft_max=0.1,
    )

    merge_split_edges: BoolProperty(
        name="Merge split edges",
        description="Merge overlapping edges as sharps",
        default=False
    )

    create_render_layer_attributes: BoolProperty(
        name="Create render layer attributes",
        description="Render layers will be imported as an integer attribute on polygons",
        default=False
    )

    import_tangents: BoolProperty(
        name="Import tangents",
        description="Import tangents instead of generating them based on the UVs",
        default=False
    )

    import_lod_models: BoolProperty(
        name="Import LoD models",
        description="Import LoD models (will be stored in a separate collection)",
        default=False
    )

    bone_orientation: EnumProperty(
        name="Bone Orientation",
        description="Bone orientation on import",
        items=(
            ('AUTO', "Auto", "Import based on target game configuration"),
            ('XY', "X, Y", "X forward, Y up"),
            ('XZ', "X, Z", "X forward, Z up"),
            ('ZNX', "Z, -X", "Z forward, -X up"),
        ),
        default='AUTO'
    )

    bone_length_mode: EnumProperty(
        name="Bone length mode",
        description="How to determine a bones length",
        items=(
            ('CLOSEST', "Closest", "Use distance to closest bone for length"),
            ('FURTHEST', "Furthest", "Use distance to farthest bone for length"),
            ('MOSTCHILDREN', "Most Children", "Use distance to the child with most children itself for length"),
            ('FIRST', "First", "Use distance to the first child for length"),
        ),
        default='MOSTCHILDREN'
    )

    min_bone_length: FloatProperty(
        name="Minimum bone length",
        description="The minimum length a bone should have",
        min=0.01,
        default=0.01
    )

    max_leaf_bone_length: FloatProperty(
        name="Maximum leaf bone length",
        description="The maximum length a bone with no children should have",
        min=0.01,
        default=1
    )

    def _draw_panel_model_vertex_merge(self, layout):
        header, body = layout.panel(
            "HEIO_import_model_merge", default_closed=True)

        header.use_property_split = True
        split = header.split(factor=0.4)
        split.label(text="Vertex merge mode")
        split.prop(self, "vertex_merge_mode", text="")

        if not body:
            return

        body.use_property_split = False
        body.active = self.vertex_merge_mode != 'NONE'
        body.prop(self, "vertex_merge_distance")
        body.prop(self, "merge_split_edges")

    def _draw_panel_model_attributes(self, layout):
        header, body = layout.panel(
            "HEIO_import_model_attributes", default_closed=True)
        header.label(text="Additional properties")

        if not body:
            return

        body.use_property_split = False
        body.prop(self, "create_render_layer_attributes")
        body.prop(self, "import_tangents")
        body.prop(self, "import_lod_models")

    def _draw_panel_armature(self, layout):
        header, body = layout.panel(
            "HEIO_import_model_armature", default_closed=True)
        header.label(text="Armature")

        if not body:
            return

        body.use_property_split = True
        body.prop(self, "bone_orientation")
        body.prop(self, "bone_length_mode")
        body.prop(self, "min_bone_length")
        body.prop(self, "max_leaf_bone_length")

    def draw_panel_model(self):
        header, body = self.layout.panel(
            "HEIO_import_model", default_closed=False)
        header.label(text="Model")

        if not body:
            return

        self._draw_panel_model_vertex_merge(body)
        self._draw_panel_model_attributes(body)
        self._draw_panel_armature(body)

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
            self.create_render_layer_attributes,
            self.import_tangents
        )

        self.node_converter = i_node.NodeConverter(
            context,
            self.target_definition,
            self.mesh_converter,
            self.bone_orientation,
            self.bone_length_mode,
            self.min_bone_length,
            self.max_leaf_bone_length
        )

    def _setup_lod_models(self, context: bpy.types.Context, model_infos: list[i_model.ModelInfo]):
        if not self.import_lod_models:
            return

        col_name = "HEIO LOD Imports"
        if col_name in bpy.data.collections:
            lod_collection = bpy.data.collections[col_name]
        else:
            lod_collection = bpy.data.collections.new(col_name)
            lod_collection.hide_render = True
            lod_collection.hide_viewport = True

        if col_name not in context.scene.collection.children:
            context.scene.collection.children.link(lod_collection)

        for model_info in model_infos:
            model_info.setup_lod_info(lod_collection, context)

    def _import_model_files(self, context: bpy.types.Context, type):
        progress_console.update("Resolving & reading files")

        directory = os.path.dirname(self.filepath)
        filepaths = [os.path.join(directory, file.name) for file in self.files]

        models, resolve_info = HEIO_NET.MODEL_HELPER.LoadModelFiles[type](
            filepaths, self.import_lod_models, HEIO_NET.RESOLVE_INFO())

        self.resolve_infos.append(resolve_info)

        progress_console.update("Importing data")

        model_infos = self.node_converter.convert_model_sets(models)

        for model_info in model_infos:
            model_info.create_object(
                model_info.name, context.scene.collection, context)

        self._setup_lod_models(context, model_infos)


class ImportModelOperator(ImportModelBaseOperator):

    filter_glob: StringProperty(
        default="*.model",
        options={'HIDDEN'},
    )


class ImportTerrainModelOperator(ImportModelBaseOperator):

    filter_glob: StringProperty(
        default="*.terrain-model",
        options={'HIDDEN'},
    )


class ImportCollisionMeshOperator(ImportOperator):

    filter_glob: StringProperty(
        default="*.btmesh",
        options={'HIDDEN'},
    )

    merge_collision_verts: BoolProperty(
        name="Merge vertices",
        description="Merge vertices by distance",
        default=True
    )

    merge_collision_vert_distance: FloatProperty(
        name="Merge distance",
        description="The distance two vertices have to be apart from each other to be merged",
        default=0.0001,
        precision=4,
        min=0,
        soft_min=0.0001,
        soft_max=0.1
    )

    remove_unused_vertices: BoolProperty(
        name="Remove unused vertices",
        description="Removes vertices that do not affect convex shapes or are not referenced by polygons",
        default=True
    )

    def _setup(self, context):
        super()._setup(context)

        self.collision_mesh_converter = i_collision_mesh.CollisionMeshConverter(
            self.target_definition,
            self.merge_collision_verts,
            self.merge_collision_vert_distance,
            self.remove_unused_vertices
        )

    def draw_panel_collision_mesh(self):
        header, body = self.layout.panel(
            "HEIO_import_collision_mesh", default_closed=True)
        header.label(text="Collision mesh")

        if not body:
            return

        body.use_property_split = True

        merge_header, merge_body = body.panel(
            "HEIO_import_collision_mesh_merge", default_closed=True)
        merge_header.row(heading="Merge vertices").prop(
            self, "merge_collision_verts", text="")

        if merge_body:
            merge_body.active = self.merge_collision_verts
            merge_body.prop(self, "merge_collision_vert_distance")
            body.separator()

        body.use_property_split = False
        body.prop(self, "remove_unused_vertices")

    def draw(self, context: Context):
        super().draw(context)
        self.draw_panel_collision_mesh()


class ImportPointCloudOperator(ImportCollisionMeshOperator, ImportModelBaseOperator):

    filter_glob: StringProperty(
        default="*.pcmodel;*.pccol",
        options={'HIDDEN'},
    )

    def import_point_cloud_models(self, context: bpy.types.Context, point_cloud_collection):
        progress_console.update("Importing Models")

        model_infos = self.node_converter.convert_model_sets(
            point_cloud_collection.Models)

        collections = i_pointcloud.convert_point_clouds(
            context, point_cloud_collection.ModelCollections, model_infos)

        self._setup_lod_models(context, model_infos)

        return collections

    def import_point_cloud_collision_meshes(self, context: bpy.types.Context, point_cloud_collection):
        progress_console.update("Importing Collision Meshes")

        collision_meshes = self.collision_mesh_converter.convert_collision_meshes(
            point_cloud_collection.CollisionMeshes)

        return i_pointcloud.convert_point_clouds(
            context, point_cloud_collection.CollisionMeshCollections, collision_meshes)
