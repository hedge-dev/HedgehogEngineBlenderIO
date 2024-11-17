from enum import Enum
import json
import os

from ...utility import general
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
            raise HEIOException(f"SCA parameter definition \"{name}\" does not have the mandatory field \"Type\"!")

        type = data["Type"]
        if type == 'Integer':
            type = SCAParameterType.INTEGER
        elif type == 'Float':
            type = SCAParameterType.FLOAT
        elif type == 'Boolean':
            type = SCAParameterType.BOOLEAN
        else:
            raise HEIOException(f"SCA parameter definition \"{name}\" has an invalid type \"{type}\"!")

        description = ""
        if "Description" in data:
            description = data["Description"]

        return SCAParameterDefinition(name, type, description)

    @staticmethod
    def dict_from_json_data(data: dict):
        result = {}

        for key, value in data.items():
            result[key] = SCAParameterDefinition.from_json_data(key, value)

        return result


class SCAParameterDefinitionCollection:

    name: str

    material: dict[str, tuple[SCAParameterType, str]]
    '''[name] = (type, description)'''

    def __init__(self, name: str):
        self.name = name
        self.material = {}

    @staticmethod
    def from_json_data(name, data):
        result = SCAParameterDefinitionCollection(name)

        if "Material" in data:
            result.material = SCAParameterDefinition.dict_from_json_data(data["Material"])

        return result

SCA_PARAMETER_DEFINITIONS: dict[str, SCAParameterDefinitionCollection] = None

def load_sca_parameter_definitions():
    global SCA_PARAMETER_DEFINITIONS
    SCA_PARAMETER_DEFINITIONS = {}

    definitions_path = os.path.join(general.get_path(), "Definitions")
    for root, directories, _ in os.walk(definitions_path):
        for directory in directories:
            filepath = os.path.join(root, directory, "SCAParameters.json")
            with open(filepath, "r") as file:
                definition_json: dict = json.load(file)

            SCA_PARAMETER_DEFINITIONS[directory] = SCAParameterDefinitionCollection.from_json_data(
                directory, definition_json)