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
from ...exceptions import HEIOUserException
from ...exporting import (
    o_enum,
    o_object_manager,
    o_modelmesh,
    o_collisionmesh,
    o_material,
    o_pointcloud,
    o_model
)


class ExportOperator(HEIOBaseFileSaveOperator):
    bl_options = {'PRESET', 'UNDO'}

    def export(self, context: Context):
        raise NotImplementedError()

    def _execute(self, context: Context):
        from ...dotnet import load_dotnet
        load_dotnet()

        self.target_definition = definitions.get_target_definition(context)
        if self.target_definition is None:
            raise HEIOUserException("Invalid target game!")

        self.setup(context)

        return self.export(context)

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

    def setup(self, context):
        super().setup(context)
        self.object_manager = o_object_manager.ObjectManager()

        if len(self.collection) > 0:
            collection = bpy.data.collections[self.collection]
            self.object_manager.collect_objects_from_collection(collection)

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

    def draw_panel_material(self):
        header, body = self.layout.panel(
            "HEIO_export_material", default_closed=False)
        header.label(text="Material")

        if not body:
            return

        body.use_property_split = True
        body.prop(self, "auto_sca_parameters_material")

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

    def setup(self, context):
        super().setup(context)

        self.material_manager = o_material.MaterialProcessor(
            self.target_definition,
            self.auto_sca_parameters_material,
            context,
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
        default=False
    )

    apply_poses: BoolProperty(
        name="Apply poses",
        description="Apply armature poses before exporting",
        default=False
    )

    force_directory_mode: bool | None = None

    def check(self, context):
        if self.force_directory_mode is not None:
            self.directory_mode = self.force_directory_mode
        else:
            self.directory_mode = self.mesh_mode == 'SEPARATE'

        return super().check(context)

    def setup(self, context):
        super().setup(context)

        self.modelmesh_manager = o_modelmesh.ModelMeshManager(
            self.target_definition,
            self.apply_modifiers,
            self.apply_poses
        )

        self.modelmesh_manager.register_objects(
            self.object_manager.all_objects)


class ExportModelBaseOperator(ExportMaterialOperator, ExportBaseMeshDataOperator):

    show_model_panel = True
    show_bone_orientation = True

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

    use_triangle_strips: BoolProperty(
        name="Use triangle strips",
        description="Use triangle strips instead of triangle lists (smaller files and gpu load, but might decrease rendering performance)",
        default=False
    )

    optimized_vertex_data: BoolProperty(
        name="Optimized vertex data",
        description="Use optimized vertex data (less precise but smaller files)",
        default=True
    )

    def draw_panel_model(self, context):
        if not self.show_model_panel:
            return

        header, body = self.layout.panel(
            "HEIO_export_model", default_closed=False)
        header.label(text="Model")

        if not body:
            return

        body.use_property_split = True
        body.prop(self, "mesh_mode")

        body.use_property_split = False
        body.prop(self, "apply_modifiers")
        body.prop(self, "apply_poses")
        body.prop(self, "auto_sca_parameters_model")

        body.use_property_split = True
        if self.show_bone_orientation:
            body.prop(self, "bone_orientation")

        body.separator()
        body.use_property_split = False

        target_def = definitions.get_target_definition(context)
        if target_def is None or target_def.supports_topology:
            body.prop(self, "use_triangle_strips")

        body.prop(self, "optimized_vertex_data")

    def draw(self, context: Context):
        super().draw(context)
        self.draw_panel_model(context)

    def setup(self, context):
        super().setup(context)

        if not self.target_definition.supports_topology or self.use_triangle_strips:
            topology = 'TRIANGLE_STRIPS'
        else:
            topology = 'TRIANGLE_LIST'

        optimize_vertex_data = self.optimized_vertex_data
        if self.target_definition.hedgehog_engine_version == 1 and not context.scene.heio_scene.target_console:
            # he1 doesnt support optimized vertex data on pc
            optimize_vertex_data = False

        self.model_processor = o_model.ModelProcessor(
            self.target_definition,
            self.material_manager,
            self.object_manager,
            self.modelmesh_manager,
            self.auto_sca_parameters_model,
            self.apply_poses,
            self.bone_orientation,
            o_enum.to_topology(topology),
            optimize_vertex_data
        )

    def export_model_files(self, context, directory, mode):
        self.modelmesh_manager.evaluate_begin(context, mode != 'TERRAIN')
        self.model_processor.prepare_all_meshdata()
        self.modelmesh_manager.evaluate_end()

        name = None
        if self.mesh_mode == 'MERGE':
            name = os.path.splitext(os.path.basename(self.filepath))[0]

        if self.mesh_mode == 'SEPARATE' or len(self.object_manager.base_objects) == 1:
            for root, children in self.object_manager.object_trees.items():
                self.model_processor.enqueue_compile_model(
                    root, children, mode, name)

        else:
            self.model_processor.enqueue_compile_model(
                None, self.object_manager.base_objects, mode, name)

        self.model_processor.compile_output()
        self.model_processor.write_output_to_files(directory)


class ExportCollisionModelOperator(ExportBaseMeshDataOperator):

    filename_ext = ".btmesh"

    show_collision_mesh_panel = True

    def draw_panel_collision_model(self):
        if not self.show_collision_mesh_panel:
            return

        header, body = self.layout.panel(
            "HEIO_export_collision_model", default_closed=False)
        header.label(text="Collision Model")

        if not body:
            return

        body.use_property_split = True
        if self.force_directory_mode is None:
            body.prop(self, "mesh_mode")

        body.use_property_split = False
        body.prop(self, "apply_modifiers")
        body.prop(self, "apply_poses")

    def draw(self, context: Context):
        super().draw(context)
        self.draw_panel_collision_model()

    def setup(self, context):
        if self.target_definition.data_versions.bullet_mesh is None:
            raise HEIOUserException(
                f"Target game \"{self.target_definition.name}\" does not support exporting bullet meshes!")

        super().setup(context)

        self.collision_mesh_processor = o_collisionmesh.CollisionMeshProcessor(
            self.target_definition,
            self.object_manager,
            self.modelmesh_manager
        )


class ExportPointCloudOperator(ExportCollisionModelOperator, ExportModelBaseOperator):

    cloud_type: EnumProperty(
        name="Collection Type",
        description="Type of pointcloud to export",
        items=(
            ('MODEL', "Terrain (*.pcmodel) (WIP)", ''),
            ('COL', "Collision (*.pccol)", '')
        ),
        default='MODEL'
    )

    write_resources: BoolProperty(
        name="Write Resources",
        description="Write only the .pcmodel/.pccol files, but not the .btmesh, .terrain-model or related files",
        default=True
    )

    force_directory_mode = False

    def draw_panel_pointcloud(self):
        header, body = self.layout.panel(
            "HEIO_export_collision_pointcloud", default_closed=False)
        header.label(text="Point Cloud")

        if not body:
            return

        body.use_property_split = True
        body.prop(self, "cloud_type")

        body.use_property_split = False
        body.prop(self, "write_resources")

    def draw(self, context: Context):
        super().draw(context)
        self.draw_panel_pointcloud()

    def check(self, context):
        self.filename_ext = '.pc' + self.cloud_type.lower()
        self.show_collision_mesh_panel = self.cloud_type == 'COL'
        self.show_model_panel = self.cloud_type == 'MODEL'
        return super().check(context)

    def setup(self, context):
        if self.target_definition.data_versions.point_cloud is None:
            raise HEIOUserException(
                f"Target game \"{self.target_definition.name}\" does not support exporting point cloud!")

        super().setup(context)

        self.pointcloud_processor = o_pointcloud.PointCloudProcessor(
            self.target_definition,
            self.model_processor,
            self.collision_mesh_processor
        )
