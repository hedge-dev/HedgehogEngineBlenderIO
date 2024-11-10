from enum import Enum
import json
import os

from ...utility import general
from ...exceptions import HEIOException


class ShaderParameterType(Enum):
    FLOAT = 1
    COLOR = 2
    BOOLEAN = 3



class ShaderLayer(Enum):
    OPAQUE = 1
    TRANSPARENT = 2
    PUNCHTHROUGH = 3
    SPECIAL = 4


class ShaderDefinition:

    name: str
    all_items_index: int
    visible_items_index: int

    hide: bool
    layer: ShaderLayer
    parameters: dict[str, ShaderParameterType]
    textures: list[str]

    def __init__(self, name: str, all_items_index: int, visible_items_index: int):
        self.name = name
        self.all_items_index = all_items_index
        self.visible_items_index = visible_items_index

        self.hide = False
        self.layer = ShaderLayer.OPAQUE
        self.parameters = {}
        self.textures = []

    @staticmethod
    def from_json_data(
            name: str,
            all_items_index: int,
            visible_items_index: int,
            data: dict,
            base: 'ShaderDefinition | None') -> 'ShaderDefinition':

        result = ShaderDefinition(
            name, all_items_index, visible_items_index)

        if base is not None:
            result.parameters.update(base.parameters)
            result.textures.extend(base.textures)

        if "Hide" in data:
            result.hide = data["Hide"]
            if result.hide:
                result.visible_items_index = -1

        if "Layer" in data:
            layer = data["Layer"]
            if layer == "Opaque":
                result.layer = ShaderLayer.OPAQUE
            elif layer == "Transparent":
                result.layer = ShaderLayer.TRANSPARENT
            elif layer == "PunchThrough":
                result.layer = ShaderLayer.PUNCHTHROUGH
            elif layer == "Special":
                result.layer = ShaderLayer.SPECIAL
            else:
                raise HEIOException(
                    f"Invalid shader layer \"{layer}\" for shader \"{name}\"")

        if "Parameters" in data:
            parameters: dict[str, str] = data["Parameters"]
            for key, value in parameters.items():
                if value == 'Float':
                    parameter_type = ShaderParameterType.FLOAT
                elif value == 'Color':
                    parameter_type = ShaderParameterType.COLOR
                elif value == 'Boolean':
                    parameter_type = ShaderParameterType.BOOLEAN
                else:
                    raise HEIOException(
                        f"Invalid shader definition parameter type \"{value}\" for shader \"{name}\"")

                result.parameters[key] = parameter_type

        if "Textures" in data:
            result.textures.extend(data["Textures"])

        return result


class ShaderDefinitionCollection:

    name: str
    definitions: dict[str, ShaderDefinition]

    items_visible: list[tuple[str, str, str]]
    items_visible_fallback: list[tuple[str, str, str]]
    items_all: list[tuple[str, str, str]]
    items_all_fallback: list[tuple[str, str, str]]

    def __init__(self, name):
        self.name = name
        self.definitions = {}
        self.items_visible = []
        self.items_visible_fallback = [("ERROR_FALLBACK", "", "")]
        self.items_all = []
        self.items_all_fallback = [("ERROR_FALLBACK", "", "")]


SHADER_DEFINITIONS: dict[str, ShaderDefinitionCollection] = None


def load_shader_definitions():
    global SHADER_DEFINITIONS
    SHADER_DEFINITIONS = {}

    definitions_path = os.path.join(general.get_path(), "ShaderDefinitions")
    for root, _, files in os.walk(definitions_path):
        for filename in files:
            filepath = os.path.join(root, filename)
            with open(filepath, "r") as file:
                definition_json: dict = json.load(file)

            base_definition = None
            if "" in definition_json:
                base_definition = ShaderDefinition.from_json_data(
                    "", -1, -1, definition_json[""], None)

            definitions_name, _ = os.path.splitext(filename)
            definition_collection = ShaderDefinitionCollection(
                definitions_name)

            for key, value in definition_json.items():
                if key == "":
                    continue

                definition = ShaderDefinition.from_json_data(
                    key,
                    len(definition_collection.items_all),
                    len(definition_collection.items_visible),
                    value,
                    base_definition)

                item = (key, key, "")

                definition_collection.definitions[key] = definition
                definition_collection.items_all.append(item)
                definition_collection.items_all_fallback.append(item)

                if not definition.hide:
                    definition_collection.items_visible.append(item)
                    definition_collection.items_visible_fallback.append(item)

            SHADER_DEFINITIONS[definitions_name] = definition_collection
