import os
import bpy

from ...exporting import o_util
from ..property_groups.mesh_properties import MESH_DATA_TYPES

from ...exceptions import HEIODevException
from ...dotnet import SharpNeedle

from .base_export_operators import (
    ExportMaterialOperator,
    ExportModelBaseOperator,
    ExportCollisionModelOperator,
    ExportPointCloudOperator
)


class HEIO_OT_Export_Material(ExportMaterialOperator):
    """Export a hedgehog engine material file"""
    bl_idname = "heio.export_material"
    bl_label = "Export as HE Material (*.material)"

    def draw(self, context):
        super().draw(context)
        self.layout.use_property_split = True
        self.layout.prop(self, "material_mode")

    def export(self, context):
        materials = set([
            slot.material
            for obj in self.object_manager.all_objects if obj.type in MESH_DATA_TYPES
            for slot in obj.material_slots if slot.material is not None
        ])

        self.material_processor.convert_materials(materials)
        self.material_processor.write_output_to_files(self.directory)
        return {'FINISHED'}


class HEIO_OT_Export_Material_Active(ExportMaterialOperator):
    """Export a hedgehog engine material file"""
    bl_idname = "heio.export_material_active"
    bl_label = "Export as HE Material (*.material)"

    @classmethod
    def poll(cls, context):
        return (
            context.active_object is not None
            and context.active_object.type in MESH_DATA_TYPES
            and context.active_object.active_material is not None
        )

    def _ignore_material_mode(self):
        return True

    def export(self, context):
        self.material_processor.convert_materials(
            [context.active_object.active_material])
        self.material_processor.write_output_to_files(self.directory)
        return {'FINISHED'}


class HEIO_OT_Export_Model(ExportModelBaseOperator):
    """Export a hedgehog engine model file"""
    bl_idname = "heio.export_model"
    bl_label = "Export as HE Model (*.model)"

    filename_ext = ".model"

    def export(self, context):
        self.export_model_files(context, 'MODEL')
        return {'FINISHED'}


class HEIO_OT_Export_TerrainModel(ExportModelBaseOperator):
    """Export a hedgehog engine terrain model file"""
    bl_idname = "heio.export_terrainmodel"
    bl_label = "Export as HE Terrain-Model (*.terrain-model)"

    filename_ext = ".terrain-model"
    show_bone_orientation = False

    def export(self, context):
        self.export_model_files(context, 'TERRAIN')
        return {'FINISHED'}


class HEIO_OT_Export_CollisionMesh(ExportCollisionModelOperator):
    """Export a hedgehog engine collision mesh file"""
    bl_idname = "heio.export_collisionmesh"
    bl_label = "Export as HE Collision Mesh (*.btmesh)"

    def export(self, context):
        self.export_basemesh_files(
            context, self.collision_mesh_processor, False)
        return {'FINISHED'}


class HEIO_OT_Export_PointCloud(ExportPointCloudOperator):
    """Export a hedgehog engine pointcloud file"""
    bl_idname = "heio.export_pointcloud"
    bl_label = "Export as HE Pointcloud (*.pcmodel;*.pccol)"

    def export(self, context):
        if self.cloud_type == 'COL':
            processor = self.collision_mesh_processor
        elif self.cloud_type == 'MODEL':
            processor = self.model_processor

        if self.write_resources:
            self.model_set_manager.evaluate_begin(
                context, self.cloud_type == 'MODEL')
            processor.prepare_all_meshdata()
            self.model_set_manager.evaluate_end()

        pointcloud = self.pointcloud_processor.object_trees_to_pointscloud(
            os.path.splitext(os.path.basename(self.filepath))[0],
            self.object_manager.object_trees,
            self.cloud_type,
            self.write_resources
        )

        directory = os.path.dirname(self.filepath)

        if self.write_resources:
            processor.compile_output(self.use_multicore_processing)
            processor.write_output_to_files(directory)

        SharpNeedle.RESOURCE_EXTENSIONS.Write(pointcloud, self.filepath)
        return {'FINISHED'}


class HEIO_OT_Export_PointClouds(ExportPointCloudOperator):
    """Export multiple hedgehog engine pointcloud files"""
    bl_idname = "heio.export_pointclouds"
    bl_label = "Collections as HE Pointclouds (*.pcmodel;*.pccol)"
    bl_options = {'PRESET', 'UNDO', 'INTERNAL'}

    def export(self, context):
        if len(self.collection) == 0:
            raise HEIODevException("Invalid export call!")

        if self.cloud_type == 'COL':
            processor = self.collision_mesh_processor
        elif self.cloud_type == 'MODEL':
            processor = self.model_processor

        if self.write_resources:
            self.model_set_manager.evaluate_begin(
                context, self.cloud_type == 'MODEL')
            processor.prepare_all_meshdata()
            self.model_set_manager.evaluate_end()

        collection = bpy.data.collections[self.collection]
        pointclouds = []

        for col in collection.children:
            if len(col.all_objects) == 0:
                continue

            object_trees = self.object_manager.assemble_object_trees(
                set(col.all_objects))

            pointcloud = self.pointcloud_processor.object_trees_to_pointscloud(
                col.name,
                object_trees,
                self.cloud_type,
                self.write_resources
            )

            pointclouds.append(pointcloud)

        directory = os.path.dirname(self.filepath)

        if self.write_resources:
            processor.compile_output(self.use_multicore_processing)
            processor.write_output_to_files(directory)

        extension = ".pc" + self.cloud_type.lower()

        for pc in pointclouds:
            if pc.Name.lower().endswith(extension):
                pc.Name = pc.Name[:-len(extension)]

            filename = o_util.correct_filename(pc.Name)

            filepath = os.path.join(
                directory, filename + extension)

            SharpNeedle.RESOURCE_EXTENSIONS.Write(pc, filepath)

        return {'FINISHED'}
