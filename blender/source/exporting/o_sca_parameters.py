from ..dotnet import SharpNeedle


def convert_parameters_to_nodes(sn_node, sca_parameter_list):
    for sca_parameter in sca_parameter_list:
        if len(sca_parameter.name) > 0:
            sn_node.AddChild(SharpNeedle.SAMPLE_CHUNK_NODE(
                sca_parameter.name, sca_parameter.value))


def convert_to_node(sn_parent, sca_parameter_list):
    node = SharpNeedle.SAMPLE_CHUNK_NODE("SCAParam")
    convert_parameters_to_nodes(node, sca_parameter_list)

    if node.Count > 0:
        sn_parent.InsertChild(0, node)


def convert_for_data(sn_data, sca_parameter_list):
    sn_parent = sn_data.Root.Children[0]
    convert_to_node(sn_parent, sca_parameter_list)
