from .base_import_operators import (
    ImportMaterialOperator,
    ImportModelOperator,
    ImportTerrainModelOperator,
    ImportBulletMeshOperator,
    ImportPointCloudModelOperator
)


class HEIO_OT_Import_Material(ImportMaterialOperator):
    bl_idname = "heio.import_material"
    bl_label = "HE Material (*.material)"

    def import_(self, context):
        self.import_material_files()
        return {'FINISHED'}


class HEIO_OT_Import_Material_Active(ImportMaterialOperator):
    bl_idname = "heio.import_material_active"
    bl_label = "Import HE Material (*.material)"

    @classmethod
    def poll(cls, context):
        return (
            context.mode in ['OBJECT', 'MESH']
            and context.active_object is not None
            and context.active_object.type == 'MESH'
        )

    def import_(self, context):
        self.import_material_files()

        object = context.active_object
        for material in self.material_converter.converted_materials.values():
            object.data.materials.append(material)

        return {'FINISHED'}


class HEIO_OT_Import_Material_Active_if(ImportMaterialOperator):
    bl_idname = "heio.import_material_active_if"
    bl_label = "Import HE Material (*.material)"

    def import_(self, context):
        self.import_material_files()

        object = context.active_object
        if object is not None and object.select_get():
            for material in self.material_converter.converted_materials.values():
                object.data.materials.append(material)

        return {'FINISHED'}


class HEIO_OT_Import_Model(ImportModelOperator):
    bl_idname = "heio.import_model"
    bl_label = "HE Model (*.model)"

    def import_(self, context):
        self.import_model_files(context)
        return {'FINISHED'}


class HEIO_OT_Import_TerrainModel(ImportTerrainModelOperator):
    bl_idname = "heio.import_terrainmodel"
    bl_label = "HE Terrain model (*.terrain-model)"

    def import_(self, context):
        self.import_terrain_model_files(context)
        return {'FINISHED'}


class HEIO_OT_Import_CollisionMesh(ImportBulletMeshOperator):
    bl_idname = "heio.import_collisionmesh"
    bl_label = "HE Collision model (*.btmesh)"

    def import_(self, context):
        self.import_collision_mesh_files(context)
        return {'FINISHED'}


class HEIO_OT_Import_PointCloud_Model(ImportPointCloudModelOperator):
    bl_idname = "heio.import_pointcloud_model"
    bl_label = "HE Point cloud (*.pcmodel)"

    def import_(self, context):
        self.import_point_cloud_files(context)
        return {'FINISHED'}
