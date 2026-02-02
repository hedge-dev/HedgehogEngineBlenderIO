
from ..property_groups.mesh_properties import MESH_DATA_TYPES

from .base_export_operators import (
    ExportMaterialOperator,
    ExportModelBaseOperator,
    ExportCollisionModelOperator,
    ExportPointCloudOperator,
    ExportPointCloudsOperator
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

    def _hide_morph_export_option(self):
        return False

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
        self.export_basemesh_files(context, self.collision_mesh_processor)
        return {'FINISHED'}


class HEIO_OT_Export_ModelPointCloud(ExportPointCloudOperator, ExportModelBaseOperator):
    """Export a hedgehog engine model pointcloud file"""
    bl_idname = "heio.export_modelpointcloud"
    bl_label = "Export as HE Model Pointcloud (*.pcmodel)"

    filename_ext = '.pcmodel'

    def _get_mesh_processor(self):
        return self.model_processor

    def export(self, context):
        self.export_collection(context)
        return {'FINISHED'}

class HEIO_OT_Export_CollisionPointCloud(ExportPointCloudOperator, ExportCollisionModelOperator):
    """Export a hedgehog engine collision pointcloud file"""
    bl_idname = "heio.export_colpointcloud"
    bl_label = "Export as HE Collision Pointcloud (*.pccol)"

    filename_ext = '.pccol'

    def _get_mesh_processor(self):
        return self.collision_mesh_processor

    def export(self, context):
        self.export_collection(context)
        return {'FINISHED'}

class HEIO_OT_Export_ModelPointClouds(ExportPointCloudsOperator, ExportModelBaseOperator):
    """Export multiple hedgehog engine pointcloud files"""
    bl_idname = "heio.export_modelpointclouds"
    bl_label = "Collections as HE Model Pointclouds (*.pcmodel)"
    bl_options = {'PRESET', 'UNDO', 'INTERNAL'}

    filename_ext = '.pcmodel'

    def _get_mesh_processor(self):
        return self.model_processor

    def export(self, context):
        self.export_collections(context)
        return {'FINISHED'}

class HEIO_OT_Export_CollisionPointClouds(ExportPointCloudsOperator, ExportCollisionModelOperator):
    """Export multiple hedgehog engine pointcloud files"""
    bl_idname = "heio.export_colpointclouds"
    bl_label = "Collections as HE Collision Pointclouds (*.pccol)"
    bl_options = {'PRESET', 'UNDO', 'INTERNAL'}

    filename_ext = '.pccol'

    def _get_mesh_processor(self):
        return self.collision_mesh_processor

    def export(self, context):
        self.export_collections(context)
        return {'FINISHED'}