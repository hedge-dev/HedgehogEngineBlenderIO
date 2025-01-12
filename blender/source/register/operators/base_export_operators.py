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
from ...dotnet import HEIO_NET, SharpNeedle
from ...exceptions import HEIOUserException
from ...exporting import (
	o_object_manager,
	o_modelmesh,
	o_collisionmesh,
	o_material,
	o_image,
	o_pointcloud
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

    def draw_panel_material(self):
        header, body = self.layout.panel(
            "HEIO_export_material", default_closed=False)
        header.label(text="Material")

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

    def export_material_files(self, context: bpy.types.Context, materials):
        sn_materials = o_material.convert_to_sharpneedle_materials(
            self.target_definition, materials)

        for sn_material in sn_materials.values():
            filepath = os.path.join(
                self.directory, sn_material.Name + ".material")
            SharpNeedle.RESOURCE_EXTENSIONS.Write(sn_material, filepath)

        if self.image_mode != 'NONE':

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


# class ExportModelBaseOperator(ExportMaterialOperator, ExportBaseMeshDataOperator):

#     def draw_panel_model(self):
#         header, body = self.layout.panel(
#             "HEIO_export_model", default_closed=False)
#         header.label(text="Model")

#         if not body:
#             return

#         body.use_property_split = True
#         body.use_property_decorate = False

#         body.prop(self, "mesh_mode")

#     def draw(self, context: Context):
#         super().draw(context)
#         self.draw_panel_model()


# class ExportModelOperator(ExportModelBaseOperator):
#     pass


# class ExportTerrainModelOperator(ExportModelBaseOperator):
#     pass


class ExportCollisionModelOperator(ExportBaseMeshDataOperator):

    filename_ext = '.btmesh'

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
        body.use_property_decorate = False

        if self.force_directory_mode is None:
            body.prop(self, "mesh_mode")

        body.prop(self, "apply_modifiers")
        body.prop(self, "apply_poses")

    def draw(self, context: Context):
        super().draw(context)
        self.draw_panel_collision_model()

    def setup(self, context):
        if self.target_definition.data_versions.bullet_mesh is None:
            raise HEIOUserException(f"Target game \"{self.target_definition.name}\" does not support exporting bullet meshes!")

        super().setup(context)

        self.collision_mesh_processor = o_collisionmesh.CollisionMeshProcessor(
            self.target_definition,
            self.object_manager,
            self.modelmesh_manager
        )


class ExportPointCloudOperator(ExportCollisionModelOperator):

    cloud_type: EnumProperty(
        name="Collection Type",
        description="Type of pointcloud to export",
        items=(
            ('MODEL', "Terrain (*.pcmodel) (WIP)", ''),
            ('COL', "Collision (*.pccol)", '')
        ),
        default='COL'
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

    def draw(self, context: Context):
        super().draw(context)
        self.draw_panel_pointcloud()

    def check(self, context):
        self.filename_ext = '.pc' + self.cloud_type.lower()
        self.show_collision_mesh_panel = self.cloud_type == 'COL'
        return super().check(context)

    def setup(self, context):
        if self.target_definition.data_versions.point_cloud is None:
            raise HEIOUserException(f"Target game \"{self.target_definition.name}\" does not support exporting point cloud!")

        super().setup(context)

        self.pointcloud_processor = o_pointcloud.PointCloudProcessor(
            self.target_definition,
            self.collision_mesh_processor
        )