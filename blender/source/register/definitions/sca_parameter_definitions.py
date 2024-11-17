from enum import Enum

from ...exceptions import HEIOException


class SCAParameterType(Enum):
    INTEGER = 1
    FLOAT = 2
    BOOLEAN = 3


class SCAParameterDefinition:
    name: str
    parameter_type: SCAParameterType
    description: str

    def __init__(self, name: str, parameter_type: SCAParameterType, description: str):
        self.name = name
        self.parameter_type = parameter_type
        self.description = description

    @staticmethod
    def from_json_data(name, data):

        if "Type" not in data:
            raise HEIOException(
                f"SCA parameter definition \"{name}\" does not have the mandatory field \"Type\"!")

        type = data["Type"]
        if type == 'Integer':
            type = SCAParameterType.INTEGER
        elif type == 'Float':
            type = SCAParameterType.FLOAT
        elif type == 'Boolean':
            type = SCAParameterType.BOOLEAN
        else:
            raise HEIOException(
                f"SCA parameter definition \"{name}\" has an invalid type \"{type}\"!")

        description = ""
        if "Description" in data:
            description = data["Description"]

        return SCAParameterDefinition(name, type, description)

    @staticmethod
    def dict_items_from_json_data(data: dict):
        dict = {}
        items = []

        for key, value in data.items():
            definition = SCAParameterDefinition.from_json_data(key, value)
            dict[key] = definition
            items.append((key, key, definition.description))

        return dict, items


class SCAParameterDefinitionCollection:

    name: str

    material: dict[str, SCAParameterDefinition]
    '''[name] = (type, description)'''

    material_items: list[tuple[str, str, str]]

    def __init__(self, name: str):
        self.name = name
        self.material = {}
        self.material_items = []

    @staticmethod
    def from_json_data(name, data):
        result = SCAParameterDefinitionCollection(name)

        if "Material" in data:
            result.material, result.material_items = SCAParameterDefinition.dict_items_from_json_data(
                data["Material"])

        return result
