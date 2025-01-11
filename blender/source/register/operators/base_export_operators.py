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
from ...exporting import o_modelmesh, o_collisionmesh, o_material, o_image


class ExportOperator(HEIOBaseFileSaveOperator):
    bl_options = {'PRESET', 'UNDO'}

    def export(self, context: Context):
        return {'FINISHED'}

    def _execute(self, context: Context):
        from ...dotnet import load_dotnet
        load_dotnet()

        self.target_definition = definitions.get_target_definition(context)
        if self.target_definition is None:
            raise HEIOUserException("Invalid target game!")

        self.setup()

        return self.export(context)

    def _invoke(self, context, event):
        self.directory_mode = True
        return super()._invoke(context, event)

    def setup(self):
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
                if (self.use_visible and not obj.visible_get(view_layer=context.view_layer)
                        or self.use_selection and not obj.select_get(view_layer=context.view_layer)):
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

    def assemble_object_trees(self, objects: list[bpy.types.Object]):
        trees: dict[bpy.types.Object, set[bpy.types.Object]] = {}

        for obj in objects:
            available_root_parent = None
            parent = obj.parent
            while parent is not None:
                if parent in objects:
                    available_root_parent = parent
                parent = parent.parent

            if available_root_parent is not None:
                tree = trees.get(available_root_parent, None)
                if tree is None:
                    tree = set()
                    trees[available_root_parent] = tree
                tree.add(obj)
            elif obj not in trees:
                trees[obj] = set()

        return trees

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

    def export(self, context):
        self.objects = self.collect_objects(context)

        if len(self.objects) == 0:
            raise HEIOUserException("No objects marked for export!")

        self.object_trees = self.assemble_object_trees(self.objects)
        return {'FINISHED'}


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

    def export_materials(self, context: bpy.types.Context, materials):
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


def _mesh_mode_updated(operator, context):
    operator.directory_mode = operator.mesh_mode == 'SEPARATE'

class ExportBaseMeshDataOperator(ExportObjectSelectionOperator):

    mesh_mode: EnumProperty(
        name="Mesh mode",
        description="How mesh data should be exported",
        items=(
            ('SEPARATE', "Seperate", "Objects are seperated into their individual object trees that will be exported as seperate files named after the root objects"),
            ('MERGE', "Merge", "Merge all objects to be exported into one specific file")
        ),
        default='SEPARATE',
        update=_mesh_mode_updated
    )

    apply_modifiers: BoolProperty(
        name="Apply modifiers",
        description="Apply modifiers before exporting",
        default=False
    )

    apply_poses: BoolProperty(
        name="Apply modifiers",
        description="Apply modifiers before exporting",
        default=False
    )

    def _invoke(self, context, event):
        result = super()._invoke(context, event)
        _mesh_mode_updated(self, context)
        return result

    def setup(self):
        super().setup()

        self.modelmesh_manager = o_modelmesh.ModelMeshManager(
            self.target_definition,
            self.apply_modifiers,
            self.apply_poses
        )

    def export(self, context):
        super().export(context)
        self.modelmesh_manager.register_objects(self.objects)
        return {'FINISHED'}


class ExportModelBaseOperator(ExportMaterialOperator, ExportBaseMeshDataOperator):

    def draw_panel_model(self):
        header, body = self.layout.panel(
            "HEIO_export_model", default_closed=False)
        header.label(text="Model")

        if not body:
            return

        body.use_property_split = True
        body.use_property_decorate = False

        body.prop(self, "mesh_mode")

    def draw(self, context: Context):
        super().draw(context)
        self.draw_panel_model()


class ExportModelOperator(ExportModelBaseOperator):
    pass


class ExportTerrainModelOperator(ExportModelBaseOperator):
    pass


class ExportCollisionModelOperator(ExportBaseMeshDataOperator):

    filename_ext = '.btmesh'

    def draw_panel_collision_model(self):
        header, body = self.layout.panel(
            "HEIO_export_collision_model", default_closed=False)
        header.label(text="Collision Model")

        if not body:
            return

        body.use_property_split = True
        body.use_property_decorate = False

        body.prop(self, "mesh_mode")

    def draw(self, context: Context):
        super().draw(context)
        self.draw_panel_collision_model()

    def setup(self):
        super().setup()

        self.collision_mesh_processor = o_collisionmesh.CollisionMeshProcessor(
            self.target_definition,
            self.modelmesh_manager
        )

    def export_collision_meshes(self, context: bpy.types.Context, objects: list[bpy.types.Object] | None):
        if objects is not None:
            raise NotImplementedError()

        self.modelmesh_manager.evaluate_begin(context)

        if objects is None:
            self.collision_mesh_processor.prepare_all_meshdata()
        else:
            raise NotImplementedError()

        self.modelmesh_manager.evaluate_end()

        exports = {}

        if self.mesh_mode == 'SEPARATE' or len(self.object_trees) == 1:
            for root, children in self.object_trees.items():
                sn_meshdata = []

                if root.type == 'MESH':
                    root_meshdata = self.collision_mesh_processor.get_meshdata(
                        root)
                    if root_meshdata is not None:
                        sn_meshdata.append(root_meshdata.convert_to_sn(None))

                parent_matrix = root.matrix_world.inverted()

                for child in children:
                    if child.type != 'MESH':
                        continue

                    child_meshdata = self.collision_mesh_processor.get_meshdata(
                        child)

                    if sn_meshdata is None:
                        continue

                    matrix = parent_matrix @ child.matrix_world
                    sn_meshdata.append((child_meshdata.convert_to_sn(matrix)))

                if len(sn_meshdata) > 0:
                    if self.mesh_mode != 'SEPARATE':
                        name = os.path.splitext(os.path.basename(self.filepath))[0]
                    elif root.type == 'MESH':
                        name = root.data.name
                    else:
                        name = root.name
                    exports[name] = sn_meshdata

        else:
            sn_meshdata = []

            for obj in self.objects:
                if obj.type != 'MESH':
                    continue

                meshdata = self.collision_mesh_processor.get_meshdata(obj)
                sn_meshdata.append(meshdata.convert_to_sn(obj.matrix_world))

            if len(sn_meshdata) > 0:
                filename = os.path.splitext(os.path.basename(self.filepath))[0]
                exports[filename] = sn_meshdata

        if len(exports) == 0:
            raise HEIOUserException("No data to export")

        for name, meshdata_list in exports.items():

            sn_meshdata = []
            sn_primitives = []

            for meshdata in meshdata_list:
                sn_meshdata.append(meshdata[0])
                sn_primitives.extend(meshdata[1])

            bullet_mesh = HEIO_NET.COLLISION_MESH_DATA.ToBulletMesh(sn_meshdata, sn_primitives)

            filepath = os.path.join(self.directory, name + ".btmesh")
            SharpNeedle.RESOURCE_EXTENSIONS.Write(bullet_mesh, filepath)


class ExportPointCloudOperator(ExportCollisionModelOperator, ExportTerrainModelOperator, ExportModelOperator):
    pass


class ExportPointCloudsOperator(ExportPointCloudOperator):
    pass
