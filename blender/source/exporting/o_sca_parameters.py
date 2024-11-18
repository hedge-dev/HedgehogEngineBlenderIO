from ctypes import c_uint32

def convert_parameters_to_nodes(sn_node, sca_parameter_list):
	for sca_parameter in sca_parameter_list:
		sn_node.Add(sca_parameter.name, c_uint32(sca_parameter.value).value, None)

def convert_to_node(sn_parent, sca_parameter_list):
	node = sn_parent.Add("SCAParam")
	sn_parent.Children.Remove(node)
	sn_parent.Children.Insert(0, node)

	convert_parameters_to_nodes(node, sca_parameter_list)

def convert_for_data(sn_data, sca_parameter_list):
	sn_parent = sn_data.Root.Children[0]
	convert_to_node(sn_parent, sca_parameter_list)