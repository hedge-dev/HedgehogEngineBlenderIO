import bpy
import os

from ..property_groups.mesh_properties import MESH_DATA_TYPES

from ...utility import progress_console
from ...dotnet import SharpNeedle, HEIO_NET

from .base_import_operators import (
    ImportMaterialOperator,
    ImportModelOperator,
    ImportTerrainModelOperator,
    ImportCollisionMeshOperator,
    ImportPointCloudOperator
)


class HEIO_OT_Import_Material(ImportMaterialOperator):
    """Load a hedgehog engine material file"""
    bl_idname = "heio.import_material"
    bl_label = "Import HE Material (*.material)"

    def import_(self, context):
        self.import_material_files()
        return {'FINISHED'}


class HEIO_OT_Import_Material_Active(ImportMaterialOperator):
    """Load a hedgehog engine material file"""
    bl_idname = "heio.import_material_active"
    bl_label = "Import HE Material (*.material)"

    @classmethod
    def poll(cls, context):
        return (
            context.mode in {'OBJECT', 'MESH'}
            and context.active_object is not None
            and context.active_object.type in MESH_DATA_TYPES
        )

    def import_(self, context):
        self.import_material_files()

        object = context.active_object
        for material in self.material_converter.get_converted_materials():
            object.data.materials.append(material)

        return {'FINISHED'}


class HEIO_OT_Import_Material_Active_if(ImportMaterialOperator):
    """Load a hedgehog engine material file"""
    bl_idname = "heio.import_material_active_if"
    bl_label = "Import HE Material (*.material)"

    def import_(self, context):
        self.import_material_files()

        object = context.active_object
        if object is not None and object.select_get():
            for material in self.material_converter.get_converted_materials():
                object.data.materials.append(material)

        return {'FINISHED'}


class HEIO_OT_Import_Model(ImportModelOperator):
    """Load a hedgehog engine model file"""
    bl_idname = "heio.import_model"
    bl_label = "Import HE Model (*.model)"

    def import_(self, context):
        self._import_model_files(context, SharpNeedle.MODEL)
        return {'FINISHED'}


class HEIO_OT_Import_TerrainModel(ImportTerrainModelOperator):
    """Load a hedgehog engine terrain model file"""
    bl_idname = "heio.import_terrainmodel"
    bl_label = "Import HE Terrain-Model (*.terrain-model)"

    def import_(self, context):
        self._import_model_files(context, SharpNeedle.TERRAIN_MODEL)
        return {'FINISHED'}


class HEIO_OT_Import_CollisionMesh(ImportCollisionMeshOperator):
    """Load a hedgehog engine collision mesh file"""
    bl_idname = "heio.import_collisionmesh"
    bl_label = "Import HE Collision Mesh (*.btmesh)"

    def import_(self, context):
        progress_console.update("Resolving & reading files")

        directory = os.path.dirname(self.filepath)
        filepaths = [os.path.join(directory, file.name) for file in self.files]

        collision_meshes = HEIO_NET.MODEL_HELPER.LoadBulletMeshFiles(filepaths)

        progress_console.update("Importing data")

        meshes = self.collision_mesh_converter.convert_collision_meshes(
            collision_meshes)

        for mesh in meshes:
            obj = bpy.data.objects.new(mesh.name, mesh)
            context.scene.collection.objects.link(obj)
        return {'FINISHED'}


class HEIO_OT_Import_PointCloud(ImportPointCloudOperator):
    """Load a hedgehog engine pointcloud file"""
    bl_idname = "heio.import_pointcloud"
    bl_label = "Import HE Point Cloud (*.pcmodel;*.pccol)"

    def import_(self, context):
        progress_console.update("Resolving & reading files")

        directory = os.path.dirname(self.filepath)
        filepaths = [os.path.join(directory, file.name) for file in self.files]

        point_cloud_collection, resolve_info = HEIO_NET.POINT_CLOUD_COLLECTION.LoadPointClouds(
            filepaths, self.import_lod_models, HEIO_NET.RESOLVE_INFO())

        self.resolve_infos.append(resolve_info)

        collections = []

        collections += self.import_point_cloud_models(
            context, point_cloud_collection)
        collections += self.import_point_cloud_collision_meshes(
            context, point_cloud_collection)

        for collection in collections:
            context.collection.children.link(collection)

        self.point_cloud_converter.cleanup()

        return {'FINISHED'}
