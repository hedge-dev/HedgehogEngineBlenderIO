from . import (
    import_operators,
    export_operators,
    filehandlers,
    mesh_info_operators,
    sca_parameter_operators,
    lod_operators,
    material_operators,
    material_parameter_operators,
    mesh_split_merge_operators,
    info_operators
)

to_register = [
    import_operators.HEIO_OT_Import_Material,
    import_operators.HEIO_OT_Import_Material_Active,
    import_operators.HEIO_OT_Import_Material_Active_if,
    import_operators.HEIO_OT_Import_Model,
    import_operators.HEIO_OT_Import_TerrainModel,
    import_operators.HEIO_OT_Import_CollisionMesh,
    import_operators.HEIO_OT_Import_PointCloud,

    export_operators.HEIO_OT_Export_Material,
    export_operators.HEIO_OT_Export_Material_Active,

    filehandlers.HEIO_FH_Material,

    sca_parameter_operators.HEIO_OT_SCAParameters_Add,
    sca_parameter_operators.HEIO_OT_SCAParameters_Remove,
    sca_parameter_operators.HEIO_OT_SCAParameters_Move,
    sca_parameter_operators.HEIO_OT_SCAParameters_NewFromPreset,

    lod_operators.HEIO_OT_LODInfo_Initialize,
    lod_operators.HEIO_OT_LODInfo_Delete,
    lod_operators.HEIO_OT_LODInfo_Add,
    lod_operators.HEIO_OT_LODInfo_Remove,
    lod_operators.HEIO_OT_LODInfo_Move,

	mesh_info_operators.HEIO_OT_MeshInfo_Initialize,
    mesh_info_operators.HEIO_OT_MeshInfo_Delete,
    mesh_info_operators.HEIO_OT_MeshInfo_Assign,
    mesh_info_operators.HEIO_OT_CollisionFlag_Remove,
    mesh_info_operators.HEIO_OT_MeshInfo_DeSelect,
    mesh_info_operators.HEIO_OT_MeshInfo_Add,
    mesh_info_operators.HEIO_OT_MeshInfo_Remove,
    mesh_info_operators.HEIO_OT_MeshInfo_Move,

    material_operators.HEIO_OT_Material_SetupNodes,
    material_operators.HEIO_OT_Material_SetupNodes_Active,

    material_parameter_operators.HEIO_OT_MaterialParameters_Add,
    material_parameter_operators.HEIO_OT_MaterialParameters_Remove,
    material_parameter_operators.HEIO_OT_MaterialParameters_Move,

    mesh_split_merge_operators.HEIO_OT_SplitMeshGroups,
    mesh_split_merge_operators.HEIO_OT_SplitCollisionMeshLayers,

    info_operators.HEIO_OT_Info_Manual,
    info_operators.HEIO_OT_Info_Discord,
    info_operators.HEIO_OT_Info_Report,
]
