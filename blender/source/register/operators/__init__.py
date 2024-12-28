from . import (
	import_operators,
	export_operators,
	filehandlers,
	mesh_layer_operators,
	meshgroup_operators,
	sca_parameter_operators,
	lod_operators,
	material_operators,
	material_parameter_operators,
	info_operators
)

to_register = [
	import_operators.HEIO_OT_Import_Material,
	import_operators.HEIO_OT_Import_Material_Active,
	import_operators.HEIO_OT_Import_Material_Active_if,
	import_operators.HEIO_OT_Import_Model,
	import_operators.HEIO_OT_Import_TerrainModel,
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

	mesh_layer_operators.HEIO_OT_MeshLayer_Initialize,
	mesh_layer_operators.HEIO_OT_MeshLayer_Delete,
	mesh_layer_operators.HEIO_OT_MeshLayer_Assign,
	mesh_layer_operators.HEIO_OT_MeshLayer_Select,
	mesh_layer_operators.HEIO_OT_MeshLayer_Deselect,
	mesh_layer_operators.HEIO_OT_MeshLayer_Add,
	mesh_layer_operators.HEIO_OT_MeshLayer_Remove,
	mesh_layer_operators.HEIO_OT_MeshLayer_Move,

	meshgroup_operators.HEIO_OT_Meshgroup_Initialize,
	meshgroup_operators.HEIO_OT_Meshgroup_Delete,
	meshgroup_operators.HEIO_OT_Meshgroup_Assign,
	meshgroup_operators.HEIO_OT_Meshgroup_Select,
	meshgroup_operators.HEIO_OT_Meshgroup_Deselect,
	meshgroup_operators.HEIO_OT_Meshgroup_Add,
	meshgroup_operators.HEIO_OT_Meshgroup_Remove,
	meshgroup_operators.HEIO_OT_Meshgroup_Move,

	material_operators.HEIO_OT_Material_SetupNodes,
	material_operators.HEIO_OT_Material_SetupNodes_Active,

	material_parameter_operators.HEIO_OT_MaterialParameters_Add,
	material_parameter_operators.HEIO_OT_MaterialParameters_Remove,
	material_parameter_operators.HEIO_OT_MaterialParameters_Move,

	info_operators.HEIO_OT_Info_Manual,
    info_operators.HEIO_OT_Info_Discord,
	info_operators.HEIO_OT_Info_Report,
	info_operators.HEIO_OT_Info_DDS_Addon,
]
