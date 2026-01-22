from ctypes import pointer
from ..external import TPointer, CSampleChunkNode
from ..register.property_groups.material_properties import HEIO_SCA_Parameters

def append_children_to_node(c_parent: CSampleChunkNode, children: list[CSampleChunkNode]):
    last_sibling = c_parent.child
    while last_sibling and last_sibling.contents.sibling:
        last_sibling = last_sibling.contents.sibling

    for child in children:
        node_pointer = pointer(child)

        if last_sibling:
            last_sibling.contents.sibling = node_pointer
        else:
            c_parent.child = node_pointer

        last_sibling = node_pointer

def convert_parameters_to_nodes(c_parent: CSampleChunkNode, sca_parameter_list: HEIO_SCA_Parameters, defaults: dict[str, any]):
    added = set()
    nodes = []

    last_sibling = c_parent.child
    while last_sibling and last_sibling.contents.sibling:
        last_sibling = last_sibling.contents.sibling

    def add_child(name: str, value: int):

        nodes.append(
            CSampleChunkNode(
                name = name,
                value = value
            )
        )

    if sca_parameter_list is not None:
        for sca_parameter in sca_parameter_list:
            if len(sca_parameter.name) > 0:
                add_child(sca_parameter.name, sca_parameter.value)
                added.add(sca_parameter.name)

    for name, value in defaults.items():
        if name not in added:
            add_child(name, value)

    append_children_to_node(c_parent, nodes)


def convert_to_node(c_parent: CSampleChunkNode, sca_parameter_list: HEIO_SCA_Parameters, defaults: dict[str, any]):
    sca_param_node = CSampleChunkNode(
        name = "SCAParam"
    )

    convert_parameters_to_nodes(sca_param_node, sca_parameter_list, defaults)

    if sca_param_node.child:
        sca_param_node.sibling = c_parent.child
        c_parent.child = pointer(sca_param_node)

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