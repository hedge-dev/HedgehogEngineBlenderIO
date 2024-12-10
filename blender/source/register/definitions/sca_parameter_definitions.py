from enum import Enum
from .json_util import HEIOJSONException, JSONWrapper


class SCAParameterType(Enum):
    INTEGER = 1
    FLOAT = 2
    BOOLEAN = 3

    @staticmethod
    def parse_json_data(data: str):
        if data == 'Integer':
            return SCAParameterType.INTEGER
        elif data == 'Float':
            return SCAParameterType.FLOAT
        elif data == 'Boolean':
            return SCAParameterType.BOOLEAN
        else:
            raise HEIOJSONException(
                f"Invalid SCA parameter type \"{data}\"")


class SCAParameterDefinition:
    name: str
    parameter_type: SCAParameterType
    description: str

    def __init__(self, name: str, parameter_type: SCAParameterType, description: str):
        self.name = name
        self.parameter_type = parameter_type
        self.description = description

    @staticmethod
    def parse_json_data(data: JSONWrapper):
        return SCAParameterDefinition(
            data.identifier,
            data.parse_property("Type", SCAParameterType),
            data.get_property_fallback("Description", "")
        )

    @staticmethod
    def dict_items_from_json_data(data: JSONWrapper):
        dict = {}
        items = []

        for key, value in data:
            definition = value.parse(SCAParameterDefinition)
            dict[key] = definition
            items.append((key, key, definition.description))

        return dict, items


class SCAParameterDefinitionCollection:

    material: dict[str, SCAParameterDefinition]
    '''[name] = (type, description)'''

    material_items: list[tuple[str, str, str]]

    def __init__(self):
        self.material = {}
        self.material_items = []

    @staticmethod
    def parse_json_data(data):
        result = SCAParameterDefinitionCollection()

        if "Material" in data:
            result.material, result.material_items = SCAParameterDefinition.dict_items_from_json_data(
                data["Material"])

        return result
