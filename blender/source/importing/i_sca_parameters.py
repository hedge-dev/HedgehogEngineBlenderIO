from ..register.definitions import TargetDefinition
from ..external import HEIONET, CSampleChunkNode, TPointer

def convert_from_node(
        c_scn_node: TPointer[CSampleChunkNode],
        sca_parameter_list,
        target_definition: TargetDefinition | None,
        data_type: str):

    if not c_scn_node:
        return

    sca_parameter_definitions = None
    if target_definition is not None and target_definition.sca_parameters is not None:
        sca_parameter_definitions = getattr(
            target_definition.sca_parameters, data_type)

    current_child = c_scn_node.contents.child

    while current_child:
        child: CSampleChunkNode = current_child.contents
        current_child = child.sibling

        sca_parameter = sca_parameter_list.new()
        sca_parameter.name = child.name
        sca_parameter.value = child.value

        if sca_parameter_definitions is not None and sca_parameter.name in sca_parameter_definitions.infos:
            sca_parameter.value_type = sca_parameter_definitions.infos[
                sca_parameter.name].parameter_type.name
            

def convert_from_root(c_scn_root: TPointer[CSampleChunkNode], sca_parameter_list, target_definition: TargetDefinition | None, data_type: str):
    if not c_scn_root:
        return

    node = HEIONET.sample_chunk_node_find(c_scn_root, "SCAParam")
    convert_from_node(node, sca_parameter_list, target_definition, data_type)

