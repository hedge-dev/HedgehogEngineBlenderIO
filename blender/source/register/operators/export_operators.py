import os
import bpy

from ...exporting import o_transform
from ...exceptions import HEIOUserException, HEIODevException
from ...dotnet import SharpNeedle

from .base_export_operators import (
    ExportMaterialOperator,
    ExportModelBaseOperator,
    ExportCollisionModelOperator,
    ExportPointCloudOperator
)


class HEIO_OT_Export_Material(ExportMaterialOperator):
    bl_idname = "heio.export_material"
    bl_label = "Export as HE Material (*.material)"

    def export(self, context):
        materials = set([
            slot.material
            for obj in self.objects if obj.type == 'MESH'
            for slot in obj.material_slots if slot.material is not None
        ])

        self.material_manager.convert_materials(materials)
        self.material_manager.write_output_to_files(self.directory)
        return {'FINISHED'}


class HEIO_OT_Export_Material_Active(ExportMaterialOperator):
    bl_idname = "heio.export_material_active"
    bl_label = "Export as HE Material (*.material)"

    @classmethod
    def poll(cls, context):
        return (
            context.active_object is not None
            and context.active_object.type == 'MESH'
            and context.active_object.active_material is not None
        )

    def export(self, context):
        self.material_manager.convert_materials([context.active_object.active_material])
        self.material_manager.write_output_to_files(self.directory)
        return {'FINISHED'}

class HEIO_OT_Export_Model(ExportModelBaseOperator):
    bl_idname = "heio.export_model"
    bl_label = "Export as HE Model (*.model)"

    filename_ext = ".model"

    def export(self, context):
        self.export_model_files(context, 'MODEL')
        return {'FINISHED'}

class HEIO_OT_Export_TerrainModel(ExportModelBaseOperator):
    bl_idname = "heio.export_terrainmodel"
    bl_label = "Export as HE Terrain-Model (*.terrain-model)"

    filename_ext = ".terrain-model"
    show_bone_orientation = False

    def export(self, context):
        self.export_model_files(context, 'TERRAIN')
        return {'FINISHED'}


class HEIO_OT_Export_CollisionMesh(ExportCollisionModelOperator):
    bl_idname = "heio.export_collisionmesh"
    bl_label = "Export as HE Collision Mesh (*.btmesh)"

    def export(self, context):
        self.modelmesh_manager.evaluate_begin(context, False)
        self.collision_mesh_processor.prepare_all_meshdata()
        self.modelmesh_manager.evaluate_end()

        name = None
        if self.mesh_mode == 'MERGE':
            name = os.path.splitext(os.path.basename(self.filepath))[0]

        if self.mesh_mode == 'SEPARATE' or len(self.object_manager.base_objects) == 1:
            for root, children in self.object_manager.object_trees.items():
                self.collision_mesh_processor.compile_bulletmesh(
                    root, children, name)

        else:
            self.collision_mesh_processor.compile_bulletmesh(
                None, self.object_manager.base_objects, name)

        self.collision_mesh_processor.write_output_to_files(self.directory)
        return {'FINISHED'}


class HEIO_OT_Export_PointCloud(ExportPointCloudOperator):
    bl_idname = "heio.export_pointcloud"
    bl_label = "Export as HE Pointcloud (*.pcmodel;*.pccol)"

    def export(self, context):
        self.modelmesh_manager.evaluate_begin(context, self.cloud_type == 'MODEL')

        if self.cloud_type == 'COL':
            self.collision_mesh_processor.prepare_all_meshdata()
            compile = None
            write = self.collision_mesh_processor.write_output_to_files
        elif self.cloud_type == 'MODEL':
            self.model_processor.prepare_all_meshdata()
            compile = self.model_processor.compile_output
            write = self.model_processor.write_output_to_files

        self.modelmesh_manager.evaluate_end()

        pointcloud = self.pointcloud_processor.object_trees_to_pointscloud(
            self.object_manager.object_trees,
            self.cloud_type
        )

        if self.write_resources:
            if compile is not None:
                compile()
            write(self.directory)

        SharpNeedle.RESOURCE_EXTENSIONS.Write(pointcloud, self.filepath)
        return {'FINISHED'}

class HEIO_OT_Export_PointClouds(ExportPointCloudOperator):
    bl_idname = "heio.export_pointclouds"
    bl_label = "Collections as HE Pointclouds (*.pcmodel;*.pccol)"
    bl_options = {'PRESET', 'UNDO', 'INTERNAL'}

    def export(self, context):
        if len(self.collection) == 0:
            raise HEIODevException("Invalid export call!")

        self.modelmesh_manager.evaluate_begin(context, self.cloud_type == 'MODEL')

        if self.cloud_type == 'COL':
            self.collision_mesh_processor.prepare_all_meshdata()
            compile = None
            write = self.collision_mesh_processor.write_output_to_files
        elif self.cloud_type == 'MODEL':
            self.model_processor.prepare_all_meshdata()
            compile = self.model_processor.compile_output
            write = self.model_processor.write_output_to_files

        self.modelmesh_manager.evaluate_end()

        collection = bpy.data.collections[self.collection]
        pointclouds = []

        for col in collection.children:
            if len(col.all_objects) == 0:
                continue

            object_trees = self.object_manager.assemble_object_trees(col.all_objects)

            pointcloud = self.pointcloud_processor.object_trees_to_pointscloud(
                object_trees,
                self.cloud_type
            )

            pointclouds.append((col.name, pointcloud))

        directory = os.path.dirname(self.filepath)

        if self.write_resources:
            if compile is not None:
                compile()
            write(directory)

        for name, pc in pointclouds:
            filepath = os.path.join(directory, name + ".pc" + self.cloud_type.lower())
            SharpNeedle.RESOURCE_EXTENSIONS.Write(pc, filepath)

        return {'FINISHED'}