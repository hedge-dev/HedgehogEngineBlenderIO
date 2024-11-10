from . import (
	material_parameter_operators,
	info_operators
)

to_register = [
	material_parameter_operators.HEIO_OT_MaterialParameters_Add,
	material_parameter_operators.HEIO_OT_MaterialParameters_Remove,
	material_parameter_operators.HEIO_OT_MaterialParameters_Move,

	info_operators.HEIO_OT_Info_Manual,
    info_operators.HEIO_OT_Info_Discord,
]
