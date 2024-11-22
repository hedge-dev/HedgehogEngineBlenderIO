import os
from .json_util import JSONWrapper
from . import (
    shader_definitions,
    sca_parameter_definitions
)


class TargetDataVersions:
    material: int
    '''Material data version (1-3)'''

    material_sample_chunk: int
    '''Material sample chunk version (1-2)'''

    def __init__(
            self,
            material: int,
            material_sample_chunk: int):
        self.material = material
        self.material_sample_chunk = material_sample_chunk

    @staticmethod
    def parse_json_data(data: JSONWrapper):
        return TargetDataVersions(
            data["Material"],
            data["MaterialSampleChunk"]
        )


class TargetDefinition:

    directory: str
    identifier: str
    name: str
    description: str
    release_year: int
    hedgehog_engine_version: int

    data_versions: dict[str, int]

    shaders: shader_definitions.ShaderDefinitionCollection
    sca_parameters: sca_parameter_definitions.SCAParameterDefinitionCollection | None

    def __init__(
            self,
            directory: str,
            identifier: str,
            name: str,
            description: str,
            release_year: int,
            hedgehog_engine_version: int):

        self.directory = directory
        self.identifier = identifier
        self.name = name
        self.description = description
        self.release_year = release_year
        self.hedgehog_engine_version = hedgehog_engine_version

        self.data_versions = {}
        self.shaders = None
        self.sca_parameters = None

    @staticmethod
    def parse_json_data(data: JSONWrapper, directory: str, identifier: str):
        result = TargetDefinition(
            directory,
            identifier,
            data["Name"],
            data["Description"],
            data["ReleaseYear"],
            data["HedgehogEngine"]
        )

        result.data_versions = data.parse_property(
            "DataVersions", TargetDataVersions)

        return result

    @staticmethod
    def from_directory(directory: str, identifier: str | None = None) -> 'TargetDefinition':
        if identifier is None:
            identifier = os.path.basename(directory)

        target_info_filepath = os.path.join(directory, "TargetInfo.json")
        target_info_data = JSONWrapper.read_file(target_info_filepath)

        result = target_info_data.parse(
            TargetDefinition,
            directory=directory,
            identifier=identifier)

        shaders_filepath = os.path.join(directory, "Shaders.json")
        shaders_data = JSONWrapper.read_file(shaders_filepath)
        result.shaders = shaders_data.parse(shader_definitions.ShaderDefinitionCollection)

        sca_parameter_filepath = os.path.join(directory, "SCAParameters.json")
        if os.path.exists(sca_parameter_filepath):
            sca_parameter_data = JSONWrapper.read_file(sca_parameter_filepath)
            result.sca_parameters = sca_parameter_data.parse(
                sca_parameter_definitions.SCAParameterDefinitionCollection)

        return result
