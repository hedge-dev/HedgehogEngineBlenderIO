import os
import json
import bpy

from . import (
    shader_definitions as shader,
    sca_parameter_definitions as scap
)

from ...utility import general

SHADER_DEFINITIONS: dict[str, shader.ShaderDefinitionCollection] = None
SCA_PARAMETER_DEFINITIONS: dict[str, scap.SCAParameterDefinitionCollection] = None


def _load_definitions_of_type(filename, json_converter):
    result = {}

    definitions_path = os.path.join(general.get_path(), "Definitions")
    for root, directories, _ in os.walk(definitions_path):
        for directory in directories:
            filepath = os.path.join(root, directory, filename)
            with open(filepath, "r") as file:
                definition_json: dict = json.load(file)

            result[directory] = json_converter(
                directory, definition_json)

    return result


def load_definitions():
    global SHADER_DEFINITIONS
    global SCA_PARAMETER_DEFINITIONS

    SHADER_DEFINITIONS = _load_definitions_of_type(
        "Shaders.json", shader.ShaderDefinitionCollection.from_json_data)
    SCA_PARAMETER_DEFINITIONS = _load_definitions_of_type(
        "SCAParameters.json", scap.SCAParameterDefinitionCollection.from_json_data)


def _get_target_game(context: bpy.types.Context) -> str:
    if context is None:
        context = bpy.context

    return context.scene.heio_scene.target_game


def get_shader_definitions(context: bpy.types.Context) -> shader.ShaderDefinitionCollection | None:
    target = _get_target_game(context)

    if target not in SHADER_DEFINITIONS:
        return None

    return SHADER_DEFINITIONS[target]


def get_sca_parameter_definitions(context: bpy.types.Context | None, data_type: str) -> dict[str, scap.SCAParameterDefinition]:
    target = _get_target_game(context)

    if target not in SCA_PARAMETER_DEFINITIONS:
        return {}

    return getattr(SCA_PARAMETER_DEFINITIONS[target], data_type)


def get_sca_parameter_definition_items(context: bpy.types.Context | None, data_type: str) -> list[tuple[str, str, str]]:
    target = _get_target_game(context)

    if target not in SCA_PARAMETER_DEFINITIONS:
        return []

    return getattr(SCA_PARAMETER_DEFINITIONS[target], data_type + "_items")
