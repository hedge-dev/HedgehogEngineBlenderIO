import bpy
from ..register import definitions

def convert_from_node(sn_node: any, sca_parameter_list, context: bpy.types.Context, data_type: str):

	if context is None:
		context = bpy.context

	parameter_definitions = definitions.get_sca_parameter_definitions(context, data_type)

	for parameter in sn_node:
		sca_parameter = sca_parameter_list.new()
		sca_parameter.name = parameter.Name
		sca_parameter.value = parameter.SignedValue

		if sca_parameter.name in parameter_definitions:
			sca_parameter.value_type =  parameter_definitions[sca_parameter.name].parameter_type.name

def convert_from_root(sn_root: any, sca_parameter_list, context: bpy.types.Context, data_type: str):
	if sn_root is None:
		return

	node = sn_root.FindNode("SCAParam")
	if node is not None:
		convert_from_node(node, sca_parameter_list, context, data_type)

def convert_from_data(sn_data: any, sca_parameter_list, context: bpy.types.Context, data_type: str):
	convert_from_root(sn_data.Root, sca_parameter_list, context, data_type)