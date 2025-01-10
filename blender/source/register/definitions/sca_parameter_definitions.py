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


class SCAParameterDefinitionInfo:
    index: int
    name: str
    parameter_type: SCAParameterType
    description: str

    def __init__(self, name: str, parameter_type: SCAParameterType, description: str):
        self.name = name
        self.parameter_type = parameter_type
        self.description = description

    @staticmethod
    def parse_json_data(data: JSONWrapper):
        return SCAParameterDefinitionInfo(
            data.identifier,
            data.parse_property("Type", SCAParameterType),
            data.get_property_fallback("Description", "")
        )

class SCAParameterDefinition:

    infos: dict[str, SCAParameterDefinitionInfo]
    items: list[tuple[str, str, str]]

    def __init__(self):
        self.infos = {}
        self.items = []

    @staticmethod
    def parse_json_data(data: JSONWrapper):
        result = SCAParameterDefinition()

        for key, value in data:
            definition = value.parse(SCAParameterDefinitionInfo)
            definition.index = len(result.items)

            result.infos[key] = definition

            item = (key, key, definition.description)
            result.items.append(item)

        return result

class SCAParameterDefinitionCollection:

    material: SCAParameterDefinition
    model: SCAParameterDefinition

    def __init__(self):
        self.material = None
        self.model = None

    @staticmethod
    def parse_json_data(data: JSONWrapper):
        result = SCAParameterDefinitionCollection()
        result.material = data.parse_property("Material", SCAParameterDefinition)
        result.model = data.parse_property("Model", SCAParameterDefinition)
        return result
