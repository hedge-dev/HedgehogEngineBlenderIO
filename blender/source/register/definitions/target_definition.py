import os
from .json_util import JSONWrapper
from . import (
    shader_definitions,
    sca_parameter_definitions,
    collision_definitions
)


class TargetDataVersions:
    material: int
    '''Material data version (1-3)'''

    material_sample_chunk: int
    '''Material sample chunk version (1-2)'''

    bullet_mesh: int | None
    '''Bulletmesh version (3)'''

    point_cloud: int | None
    '''Point cloud version (1-2)'''

    def __init__(
            self,
            material: int,
            material_sample_chunk: int,
            bullet_mesh: int | None,
            point_cloud: int | None):
        self.material = material
        self.material_sample_chunk = material_sample_chunk
        self.bullet_mesh = bullet_mesh
        self.point_cloud = point_cloud

    @staticmethod
    def parse_json_data(data: JSONWrapper):
        return TargetDataVersions(
            data["Material"],
            data["MaterialSampleChunk"],
            data["BulletMesh"],
            data["PointCloud"],
        )


class TargetDefinition:

    directory: str
    identifier: str
    name: str
    description: str
    release_year: int
    hedgehog_engine_version: int

    uses_ntsp: bool
    bone_orientation: str

    has_preferences: bool

    data_versions: TargetDataVersions
    default_texture_modes: dict[str, str]

    shaders: shader_definitions.ShaderDefinitionCollection
    sca_parameters: sca_parameter_definitions.SCAParameterDefinitionCollection | None
    collision_info: collision_definitions.CollisionInfoDefinition | None

    def __init__(
            self,
            directory: str,
            identifier: str,
            name: str,
            description: str,
            release_year: int,
            hedgehog_engine_version: int,
            uses_ntsp: bool,
            bone_orientation: str):

        self.directory = directory
        self.identifier = identifier
        self.name = name
        self.description = description
        self.release_year = release_year
        self.hedgehog_engine_version = hedgehog_engine_version

        self.uses_ntsp = uses_ntsp
        self.bone_orientation = bone_orientation

        self.has_preferences = uses_ntsp

        self.data_versions = None
        self.default_texture_modes = dict()

        self.shaders = None
        self.sca_parameters = None
        self.collision_info = None

    @staticmethod
    def parse_json_data(data: JSONWrapper, directory: str, identifier: str):
        result = TargetDefinition(
            directory,
            identifier,
            data["Name"],
            data["Description"],
            data["ReleaseYear"],
            data["HedgehogEngine"],
            data["UsesNTSP"],
            data["BoneOrientation"],
        )

        result.data_versions = data.parse_property(
            "DataVersions", TargetDataVersions)

        result.default_texture_modes.update(
            data.get_property_fallback("DefaultTextureModes", {}))

        return result

    @staticmethod
    def from_directory(directory: str, identifier: str) -> 'TargetDefinition':
        target_info_filepath = os.path.join(directory, "TargetInfo.json")
        target_info_data = JSONWrapper.read_file(target_info_filepath)

        result = target_info_data.parse(
            TargetDefinition,
            directory=directory,
            identifier=identifier)

        shaders_filepath = os.path.join(directory, "Shaders.json")
        shaders_data = JSONWrapper.read_file(shaders_filepath)
        result.shaders = shaders_data.parse(
            shader_definitions.ShaderDefinitionCollection)

        sca_parameter_filepath = os.path.join(directory, "SCAParameters.json")
        if os.path.exists(sca_parameter_filepath):
            sca_parameter_data = JSONWrapper.read_file(sca_parameter_filepath)
            result.sca_parameters = sca_parameter_data.parse(
                sca_parameter_definitions.SCAParameterDefinitionCollection)

        collision_info_filepath = os.path.join(directory, "CollisionInfo.json")
        if os.path.exists(collision_info_filepath):
            collision_info_data = JSONWrapper.read_file(
                collision_info_filepath)
            result.collision_info = collision_info_data.parse(
                collision_definitions.CollisionInfoDefinition)

        return result
