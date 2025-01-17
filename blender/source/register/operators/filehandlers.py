import bpy
from . import import_operators, export_operators

from bpy_extras.io_utils import poll_file_object_drop


class HEIO_FH_Material(bpy.types.FileHandler):
    bl_idname = "HEIO_FH_material"
    bl_label = "HE Material (*.material)"
    bl_import_operator = import_operators.HEIO_OT_Import_Material_Active_if.bl_idname
    bl_export_operator = export_operators.HEIO_OT_Export_Material.bl_idname
    bl_file_extensions = ".material"

    @classmethod
    def poll_drop(cls, context):
        return poll_file_object_drop(context)


class HEIO_FH_Model(bpy.types.FileHandler):
    bl_idname = "HEIO_FH_model"
    bl_label = "HE Model (*.model)"
    bl_import_operator = import_operators.HEIO_OT_Import_Model.bl_idname
    bl_export_operator = export_operators.HEIO_OT_Export_Model.bl_idname
    bl_file_extensions = ".model"

    @classmethod
    def poll_drop(cls, context):
        return poll_file_object_drop(context)


class HEIO_FH_TerrainModel(bpy.types.FileHandler):
    bl_idname = "HEIO_FH_terrainmodel"
    bl_label = "HE Terrain-Model (*.terrain-model)"
    bl_import_operator = import_operators.HEIO_OT_Import_TerrainModel.bl_idname
    bl_export_operator = export_operators.HEIO_OT_Export_TerrainModel.bl_idname
    bl_file_extensions = ".terrain-model"

    @classmethod
    def poll_drop(cls, context):
        return poll_file_object_drop(context)


class HEIO_FH_CollisionMesh(bpy.types.FileHandler):
    bl_idname = "HEIO_FH_collisionmesh"
    bl_label = "HE Collision Mesh (*.btmesh)"
    bl_import_operator = import_operators.HEIO_OT_Import_CollisionMesh.bl_idname
    bl_export_operator = export_operators.HEIO_OT_Export_CollisionMesh.bl_idname
    bl_file_extensions = ".btmesh"

    @classmethod
    def poll_drop(cls, context):
        return poll_file_object_drop(context)


class HEIO_FH_PointCloud(bpy.types.FileHandler):
    bl_idname = "HEIO_FH_pointcloud"
    bl_label = "HE Point cloud (*.pcmodel;*.pccol)"
    bl_import_operator = import_operators.HEIO_OT_Import_PointCloud.bl_idname
    bl_export_operator = export_operators.HEIO_OT_Export_PointCloud.bl_idname
    bl_file_extensions = ".pcmodel;.pccol"

    @classmethod
    def poll_drop(cls, context):
        return poll_file_object_drop(context)


class HEIO_FH_PointClouds(bpy.types.FileHandler):
    bl_idname = "HEIO_FH_pointclouds"
    bl_label = "Collections as HE Point clouds (*.pcmodel;*.pccol)"
    bl_export_operator = export_operators.HEIO_OT_Export_PointClouds.bl_idname
    bl_file_extensions = ".pcmodel;.pccol"

    @classmethod
    def poll_drop(cls, context):
        return poll_file_object_drop(context)
