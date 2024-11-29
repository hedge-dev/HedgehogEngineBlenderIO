from . import (
	import_operators,
	export_operators,
	filehandlers,
	sca_parameter_operators,
	material_operators,
	material_parameter_operators,
	info_operators
)

to_register = [
	import_operators.HEIO_OT_Import_Material,
	import_operators.HEIO_OT_Import_Material_Active,
	import_operators.HEIO_OT_Import_Material_Active_if,

	export_operators.HEIO_OT_Export_Material,
	export_operators.HEIO_OT_Export_Material_Active,

	filehandlers.HEIO_FH_Material,

	sca_parameter_operators.HEIO_OT_SCAParameters_Add,
	sca_parameter_operators.HEIO_OT_SCAParameters_Remove,
	sca_parameter_operators.HEIO_OT_SCAParameters_Move,
	sca_parameter_operators.HEIO_OT_SCAParameters_NewFromPreset,

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
