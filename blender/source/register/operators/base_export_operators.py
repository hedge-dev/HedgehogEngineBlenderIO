import os
import bpy
from bpy.types import Context
from bpy.props import (
    BoolProperty,
    EnumProperty,
    StringProperty
)

from .base import HEIOBaseFileSaveOperator
from .. import definitions
from ...exceptions import HEIOUserException, HEIODevException
from ...exporting import (
    o_mesh,
    o_modelset,
    o_object_manager,
    o_collisionmesh,
    o_material,
    o_pointcloud,
    o_model,
    o_util
)

from ...external import HEIONET
from ...utility import progress_console


class ExportOperator(HEIOBaseFileSaveOperator):
    bl_options = {'PRESET', 'UNDO'}

    def export(self, context: Context):
        raise NotImplementedError()

    def _execute(self, context: Context):
        with HEIONET.load():

            self.target_definition = definitions.get_target_definition(context)
            if self.target_definition is None:
                raise HEIOUserException("Invalid target game!")

            self.setup(context)

            progress_console.cleanup()
            progress_console.start("Exporting")
            result = self.export(context)
            progress_console.end()

            return result

    def _invoke(self, context, event):
        self.directory_mode = True
        return super()._invoke(context, event)

    def setup(self, contex: bpy.types.Context):
        pass

    def draw(self, context):
        self.layout.use_property_decorate = False


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

    def _include_lod_models(self):
        return self.target_definition.hedgehog_engine_version > 1

    def _include_base_collection(self):
        return True

    def setup(self, context):
        super().setup(context)
        self.object_manager = o_object_manager.ObjectManager(
            self._include_lod_models())

        if len(self.collection) > 0:
            collection = bpy.data.collections[self.collection]
            
            if self._include_base_collection():
                collections = [ collection ]
            else:
                collections = list(collection.children)

            self.object_manager.collect_objects_from_collections(collections)

        else:
            self.object_manager.collect_objects(
                context,
                self.use_selection,
                self.use_visible,
                self.use_active_collection,
                self.use_active_scene
            )

        if len(self.object_manager.base_objects) == 0:
            raise HEIOUserException("No objects marked for export!")


class ExportMaterialOperator(ExportObjectSelectionOperator):

    image_mode: EnumProperty(
        name="Image Export Mode",
        description="Which images to export",
        items=(
             ('OVERWRITE', "Overwrite",
              "Export all images and overwrite existing ones."),
             ('MISSING', "Missing",
              "Export only images that dont already exist in the output folder."),
             ('NONE', "None", "Export no images at all"),
        ),
        default='MISSING'
    )

    material_mode: EnumProperty(
        name="Material Export Mode",
        description="Which materials (including their images) to export",
        items=(
             ('OVERWRITE', "Overwrite",
              "Export all materials and overwrite existing ones."),
             ('MISSING', "Missing",
              "Export only materials that dont already exist in the output folder."),
             ('NONE', "None", "Export no materials at all"),
        ),
        default='OVERWRITE'
    )

    nrm_invert_y_channel: EnumProperty(
        name="Invert Y channel of normal maps",
        description="Whether to invert the Y channel on normal maps when exporting",
        items=(
            ("AUTO", "Automatic",
             "Automatically determine whether to invert the Y channel based on the target game"),
            ("INVERT", "Invert", "Always invert the Y channel"),
            ("DONT", "Don't invert", "Don't invert the Y channel")
        ),
        default="AUTO"
    )

    auto_sca_parameters_material: BoolProperty(
        name="Automatic SCA parameters",
        description="Add default SCA parameters to the material if missing (defined per target game)",
        default=True
    )

    def _ignore_material_mode(self):
        return False

    def _hide_material_panel(self):
        return False

    def draw_panel_material(self, context):
        if self._hide_material_panel() or (not self._ignore_material_mode() and self.material_mode == 'NONE'):
            return

        header, body = self.layout.panel(
            "HEIO_export_material", default_closed=True)
        header.label(text="Material")

        if not body:
            return

        target_def = definitions.get_target_definition(context)
        if target_def is None or target_def.data_versions.sample_chunk >= 2:
            body.use_property_split = False
            body.prop(self, "auto_sca_parameters_material")

        if "blender_dds_addon" in bpy.context.preferences.addons.keys():
            body.use_property_split = True
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
        self.draw_panel_material(context)

    def setup(self, context):
        super().setup(context)

        material_mode = self.material_mode
        if self._ignore_material_mode():
            material_mode = 'OVERWRITE'

        self.material_processor = o_material.MaterialProcessor(
            self.target_definition,
            self.auto_sca_parameters_material,
            context,
            material_mode,
            self.image_mode,
            self.nrm_invert_y_channel)


class ExportBaseMeshDataOperator(ExportObjectSelectionOperator):

    mesh_mode: EnumProperty(
        name="Mesh mode",
        description="How mesh data should be exported",
        items=(
            ('SEPARATE', "Seperate", "Objects are seperated into their individual object trees that will be exported as seperate files named after the root objects"),
            ('MERGE', "Merge", "Merge all objects to be exported into one specific file")
        ),
        default='SEPARATE'
    )

    apply_modifiers: BoolProperty(
        name="Apply modifiers",
        description="Apply modifiers before exporting",
        default=True
    )

    apply_poses: BoolProperty(
        name="Apply poses",
        description="Apply armature poses before exporting",
        default=False
    )

    export_morphs: BoolProperty(
        name="Export morphs",
        description="Add shape keys on models as morphs to the exported model",
        default=True
    )

    use_multicore_processing: BoolProperty(
        name="Use multicore processing",
        description="Uses all CPU cores (threads) to speed up exporting model data",
        default=True
    )

    def check(self, context):
        force = self._get_force_directory_mode()
        if force is not None:
            self.directory_mode = force
        else:
            self.directory_mode = self.mesh_mode == 'SEPARATE'

        return super().check(context)

    def _get_force_directory_mode(self):
        return None

    def _hide_mesh_panel(self):
        return False

    def _hide_morph_export_option(self):
        return True

    def draw_mesh_mode(self, layout):
        if self._get_force_directory_mode() is None:
            layout.use_property_split = True
            layout.prop(self, "mesh_mode")

    def draw_panel_geometry(self, layout):
        header, body = layout.panel(
            "HEIO_export_geometry", default_closed=True)
        header.label(text="Geometry")

        if not body:
            return

        body.use_property_split = False
        body.prop(self, "apply_modifiers")
        body.prop(self, "apply_poses")

        if not self._hide_morph_export_option():
            body.prop(self, "export_morphs")

    def setup(self, context):
        super().setup(context)

        self.model_set_manager = o_modelset.ModelSetManager(
            self.target_definition,
            self.apply_modifiers,
            self.apply_poses,
            self.export_morphs and not self._hide_morph_export_option()
        )

        self.model_set_manager.register_objects(
            self.object_manager.all_objects)

    def export_basemesh_files(self, context, processor: o_mesh.BaseMeshProcessor):
        self.model_set_manager.evaluate_begin(context)
        processor.prepare_all_meshdata()
        self.model_set_manager.evaluate_end()

        name = None
        if self.mesh_mode == 'MERGE':
            name = os.path.splitext(os.path.basename(self.filepath))[0]

        if self.mesh_mode == 'SEPARATE' or len(self.object_manager.base_objects) == 1:
            for root, children in self.object_manager.object_trees.items():
                processor.enqueue_compile(root, children, name)

        else:
            processor.enqueue_compile(
                None, self.object_manager.base_objects, name)

        directory = os.path.dirname(self.filepath)
        processor.compile_output_to_files(self.use_multicore_processing, directory)


class ExportModelBaseOperator(ExportMaterialOperator, ExportBaseMeshDataOperator):

    auto_sca_parameters_model: BoolProperty(
        name="Automatic SCA parameters",
        description="Add default SCA parameters to the model if missing (defined per target game)",
        default=True
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

    use_model_version_4: BoolProperty(
        name="Export Version 4",
        description="HE1 models are usually version 5 (supports mesh groups), but some models like Werehog fur require the exported model to be version 4"
    )

    use_triangle_strips: BoolProperty(
        name="Use triangle strips",
        description="Use triangle strips instead of triangle lists (smaller files and gpu load, but might decrease rendering performance)",
        default=False
    )

    compressed_vertex_data: BoolProperty(
        name="Compressed vertex data",
        description="Use compressed vertex data (less precise but smaller files)",
        default=True
    )

    def _hide_material_panel(self):
        return self._hide_mesh_panel()

    def _draw_panel_model_general(self, layout, target_def: definitions.TargetDefinition):
        header, body = layout.panel(
            "HEIO_export_model_general", default_closed=True)
        header.label(text="General")

        if not body:
            return

        body.use_property_split = False
        if target_def is None or target_def.data_versions.sample_chunk >= 2:
            body.prop(self, "auto_sca_parameters_model")

        body.use_property_split = True
        body.prop(self, "material_mode")
        body.prop(self, "bone_orientation")

    def _draw_panel_model_advanced(self, layout, context, target_def: definitions.TargetDefinition):
        header, body = layout.panel(
            "HEIO_export_model_advanced", default_closed=True)
        header.label(text="Advanced")

        if not body:
            return

        body.use_property_split = False
        body.prop(self, "use_multicore_processing")

        if target_def is None or target_def.hedgehog_engine_version == 1:
            body.prop(self, "use_model_version_4")

        if target_def is None or target_def.supports_topology:
            body.prop(self, "use_triangle_strips")

        if target_def is None or target_def.hedgehog_engine_version == 2 or context.scene.heio_scene.target_console:
            body.prop(self, "compressed_vertex_data")

    def draw_panel_model(self, context):
        if self._hide_mesh_panel():
            return

        header, body = self.layout.panel(
            "HEIO_export_model", default_closed=False)
        header.label(text="Model")

        if not body:
            return

        target_def = definitions.get_target_definition(context)

        self.draw_mesh_mode(body)
        self.draw_panel_geometry(body)
        self._draw_panel_model_general(body, target_def)
        self._draw_panel_model_advanced(body, context, target_def)

    def draw(self, context: Context):
        super().draw(context)
        self.draw_panel_model(context)

    def setup(self, context):
        super().setup(context)

        if self.target_definition.hedgehog_engine_version == 2:
            model_version_mode = "HE2"
        elif self.use_model_version_4:
            model_version_mode = "HE1_V4"
        else:
            model_version_mode = "HE1"

        if not self.target_definition.supports_topology or self.use_triangle_strips:
            topology = 'TRIANGLE_STRIPS'
        else:
            topology = 'TRIANGLE_LIST'

        compressed_vertex_data = self.compressed_vertex_data
        if self.target_definition.hedgehog_engine_version == 1 and not context.scene.heio_scene.target_console:
            # he1 doesnt support compressed vertex data on pc
            compressed_vertex_data = False

        self.model_processor = o_model.ModelProcessor(
            self.target_definition,
            self.object_manager,
            self.model_set_manager,

            self.material_processor,
            self.auto_sca_parameters_model,
            self.apply_poses,
            self.bone_orientation,
            model_version_mode,
            topology,
            compressed_vertex_data
        )

    def export_model_files(self, context, mode):
        self.model_processor.mode = mode
        self.export_basemesh_files(context, self.model_processor)


class ExportCollisionModelOperator(ExportBaseMeshDataOperator):

    filename_ext = ".btmesh"

    def draw_panel_collision_model(self):
        if self._hide_mesh_panel():
            return

        header, body = self.layout.panel(
            "HEIO_export_collision_model", default_closed=False)
        header.label(text="Collision Model")

        if not body:
            return

        self.draw_mesh_mode(body)
        self.draw_panel_geometry(body)

    def draw(self, context: Context):
        super().draw(context)
        self.draw_panel_collision_model()

    def _include_lod_models(self):
        return False

    def setup(self, context):
        if self.target_definition.data_versions.bullet_mesh is None:
            raise HEIOUserException(
                f"Target game \"{self.target_definition.name}\" does not support exporting bullet meshes!")

        super().setup(context)

        self.collision_mesh_processor = o_collisionmesh.CollisionMeshProcessor(
            self.target_definition,
            self.object_manager,
            self.model_set_manager
        )


class ExportPointCloudOperator(ExportObjectSelectionOperator):

    write_resources: BoolProperty(
        name="Write Resources",
        description="Write only the .pcmodel/.pccol files, but not the .btmesh, .terrain-model or related files",
        default=True
    )

    def _get_force_directory_mode(self):
        return False

    def _hide_mesh_panel(self):
        return not self.write_resources

    def draw_panel_pointcloud(self):
        header, body = self.layout.panel(
            "HEIO_export_collision_pointcloud", default_closed=False)
        header.label(text="Point Cloud")

        if not body:
            return

        body.use_property_split = False
        body.prop(self, "write_resources")

    def draw(self, context: Context):
        super().draw(context)
        self.draw_panel_pointcloud()

    def _get_mesh_processor(self) -> o_mesh.BaseMeshProcessor:
        raise NotImplementedError()

    def setup(self, context):
        if self.target_definition.data_versions.point_cloud is None:
            raise HEIOUserException(
                f"Target game \"{self.target_definition.name}\" does not support exporting point clouds!")

        super().setup(context)

        self.pointcloud_processor = o_pointcloud.PointCloudProcessor(
            self.filename_ext[3:].upper(),
            self.write_resources,
            self.model_set_manager,
            self._get_mesh_processor(),
            self.target_definition,
        )

    def export_collection(self, context):
        self.pointcloud_processor.prepare(context)

        self.pointcloud_processor.object_trees_to_pointcloud_file(
            self.filepath,
            self.object_manager.object_trees
        )

        self.pointcloud_processor.compile_resources_to_files(
            self.use_multicore_processing,
            os.path.dirname(self.filepath)
        )

class ExportPointCloudsOperator(ExportPointCloudOperator):

    def _include_base_collection(self):
        return False

    def export_collections(self, context):
        if len(self.collection) == 0:
            raise HEIODevException("Invalid export call!")

        self.pointcloud_processor.prepare(context)

        collection: bpy.types.Collection = bpy.data.collections[self.collection]

        directory = os.path.dirname(self.filepath)

        for col in collection.children:
            if len(col.all_objects) == 0:
                continue

            object_trees = self.object_manager.assemble_object_trees(
                set(col.all_objects))
            
            name = col.name
            if name.lower().endswith(self.filename_ext):
                name = name[:-len(self.filename_ext)]

            filename = o_util.correct_filename(name)
            filepath = os.path.join(directory, filename + self.filename_ext)

            self.pointcloud_processor.object_trees_to_pointcloud_file(
                filepath,
                object_trees
            )

        self.pointcloud_processor.compile_resources_to_files(self.use_multicore_processing, directory)