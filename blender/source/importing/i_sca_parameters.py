from ..register.definitions.target_info import TargetDefinition

def convert_from_node(
        sn_node: any,
        sca_parameter_list,
        target_definition: TargetDefinition | None,
        data_type: str):

    if sn_node is None:
        return

    sca_parameter_definitions = None
    if target_definition is not None:
        sca_parameter_definitions = getattr(
            target_definition.sca_parameters, data_type)

    for parameter in sn_node:
        sca_parameter = sca_parameter_list.new()
        sca_parameter.name = parameter.Name
        sca_parameter.value = parameter.SignedValue

        if sca_parameter_definitions is not None and sca_parameter.name in sca_parameter_definitions:
            sca_parameter.value_type = sca_parameter_definitions[
                sca_parameter.name].parameter_type.name


def convert_from_container(sn_container: any, sca_parameter_list, target_definition: TargetDefinition | None, data_type: str):
    if sn_container is None:
        return

    node = sn_container.FindNode("SCAParam")
    convert_from_node(node, sca_parameter_list, target_definition, data_type)


def convert_from_data(sn_data: any, sca_parameter_list, target_definition: TargetDefinition | None, data_type: str):
    convert_from_container(sn_data.Root, sca_parameter_list, target_definition, data_type)
