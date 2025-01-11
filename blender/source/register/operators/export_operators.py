from .base_export_operators import (
    ExportMaterialOperator,
    ExportModelOperator,
    ExportTerrainModelOperator,
    ExportCollisionModelOperator,
    ExportPointCloudOperator
)


class HEIO_OT_Export_Material(ExportMaterialOperator):
    bl_idname = "heio.export_material"
    bl_label = "Export as HE Material (*.material)"

    def export(self, context):
        super().export(context)

        materials = set([
            slot.material
            for obj in self.objects if obj.type == 'MESH'
            for slot in obj.material_slots if slot.material is not None
        ])

        self.export_materials(context, materials)
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
        self.export_materials(context, [context.active_object.active_material])
        return {'FINISHED'}

# class HEIO_OT_Export_Model(ExportModelOperator):
#     bl_idname = "heio.export_model"
#     bl_label = "Export as HE Model (*.model)"

# class HEIO_OT_Export_TerrainModel(ExportTerrainModelOperator):
#     bl_idname = "heio.export_terrainmodel"
#     bl_label = "Export as HE Terrain-Model (*.terrain-model)"

class HEIO_OT_Export_CollisionModel(ExportCollisionModelOperator):
    bl_idname = "heio.export_collisionmodel"
    bl_label = "Export as HE Collisionmodel (*.btmesh)"

    def export(self, context):
        super().export(context)
        self.export_collision_meshes(context, None)
        return {'FINISHED'}

# class HEIO_OT_Export_PointCloud(ExportPointCloudOperator):
#     bl_idname = "heio.export_pointcloud"
#     bl_label = "Export as HE Pointcloud (*.pc*)"