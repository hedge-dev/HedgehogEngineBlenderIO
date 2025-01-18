from ..dotnet import SharpNeedle


def convert_parameters_to_nodes(sn_node, sca_parameter_list, defaults: dict[str, any]):
    added = set()

    for sca_parameter in sca_parameter_list:
        if len(sca_parameter.name) > 0:
            sn_node.AddChild(SharpNeedle.SAMPLE_CHUNK_NODE(
                sca_parameter.name, sca_parameter.value))

            added.add(sca_parameter.name)

    for name, value in defaults.items():
        if name in added:
            continue
        sn_node.AddChild(SharpNeedle.SAMPLE_CHUNK_NODE(name, value))


def convert_to_node(sn_parent, sca_parameter_list, defaults):
    node = SharpNeedle.SAMPLE_CHUNK_NODE("SCAParam")
    convert_parameters_to_nodes(node, sca_parameter_list, defaults)

    if node.Count > 0:
        sn_parent.InsertChild(0, node)

def convert_to_model_node_prm(sca_parameter_list, index, defaults):
    node = SharpNeedle.SAMPLE_CHUNK_NODE("NodePrms", index)
    convert_to_node(node, sca_parameter_list, defaults)

    if node.Count > 0:
        return node
    else:
        return None

def convert_for_data(sn_data, sca_parameter_list, defaults):
    sn_parent = sn_data.Root.Children[0]
    convert_to_node(sn_parent, sca_parameter_list, defaults)
