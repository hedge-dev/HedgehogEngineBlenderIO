import bpy
from ctypes import c_int32

from ..register.definitions.sca_parameter_definitions import SCA_PARAMETER_DEFINITIONS

def convert_from_node(node: any, sca_parameter_list, context: bpy.types.Context, data_type: str):

	if context is None:
		context = bpy.context

	parameter_definitions = None
	if context.scene.heio_scene.target_game in SCA_PARAMETER_DEFINITIONS:
		definition_collection = SCA_PARAMETER_DEFINITIONS[context.scene.heio_scene.target_game]
		parameter_definitions = getattr(definition_collection, data_type)

	for parameter in node:
		sca_parameter = sca_parameter_list.new()
		sca_parameter.name = parameter.Name
		sca_parameter.value = c_int32(parameter.Value).value

		if sca_parameter.name in parameter_definitions:
			sca_parameter.value_type =  parameter_definitions[sca_parameter.name].parameter_type.name

def convert_from_root(root: any, sca_parameter_list, context: bpy.types.Context, data_type: str):
	for node in root.Children[0]:
		if node.Name == "SCAParam":
			convert_from_node(node, sca_parameter_list, context, data_type)
			return

def convert_from_data(data: any, sca_parameter_list, context: bpy.types.Context, data_type: str):
	convert_from_root(data.Root, sca_parameter_list, context, data_type)