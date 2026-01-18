from ctypes import pointer
from ..external import TPointer, CSampleChunkNode
from ..register.property_groups.material_properties import HEIO_SCA_Parameters

def convert_parameters_to_nodes(c_parent: CSampleChunkNode, sca_parameter_list: HEIO_SCA_Parameters, defaults: dict[str, any]):
    added = set()

    last_sibling = c_parent.child
    if last_sibling and last_sibling.contents.sibling:
        last_sibling = last_sibling.contents.sibling

    def add_child(name: str, value: int):

        node = CSampleChunkNode(
            name = name,
            value = value
        )
        node_pointer = pointer(node)

        if last_sibling:
            last_sibling.contents.sibling = node_pointer
        else:
            c_parent.child = node_pointer

        return node_pointer

    if sca_parameter_list is not None:
        for sca_parameter in sca_parameter_list:
            if len(sca_parameter.name) > 0:
                last_sibling = add_child(sca_parameter.name, sca_parameter.value)
                added.add(sca_parameter.name)

    for name, value in defaults.items():
        if name in added:
            continue
        last_sibling = add_child(name, value)


def convert_to_node(c_parent: TPointer[CSampleChunkNode], sca_parameter_list: HEIO_SCA_Parameters, defaults: dict[str, any]):
    sca_param_node = CSampleChunkNode(
        name = "SCAParam"
    )

    convert_parameters_to_nodes(sca_param_node, sca_parameter_list, defaults)

    if sca_param_node.child:
        c_parent_contents = c_parent[0]
        sca_param_node.sibling = c_parent_contents.child
        c_parent_contents.child = pointer(sca_param_node)

def convert_to_model_node_prm(sca_parameter_list, index, defaults):
    prms_node = CSampleChunkNode(
        name = "NodePrms",
        value = index
    )

    convert_to_node(prms_node, sca_parameter_list, defaults)

    if prms_node.child:
        return prms_node
    return None

def setup(name: str, data_version: int):

    contexts_node = CSampleChunkNode(
        name = "Contexts",
        is_data_node = True,
        value = data_version
    )

    data_root = CSampleChunkNode(
        name = name,
        value = 1,
        child = pointer(contexts_node)
    )

    root = CSampleChunkNode(
        value = 0x133054A,
        child = pointer(data_root)
    )

    return pointer(root)