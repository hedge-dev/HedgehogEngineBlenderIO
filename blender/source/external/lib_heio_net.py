from ctypes import POINTER, pointer, byref, cast, c_wchar_p, c_bool, c_uint
from typing import Iterable

from . import util
from .structs import *
from .nettypes import *
from .typing import TPointer

from .library import ExternalLibrary
from .functions.heio_net import FUNCTIONS

from ..exceptions import HEIOException


class HEIOLibraryException(HEIOException):
    function_name: str

    def __init__(self, message: str, function_name: str, *args: object):
        super().__init__(f"Library Exception when calling \"{function_name}\": {message}", *args)
        self.function_name = function_name


class HEIONET(ExternalLibrary):
    
    @classmethod
    def _get_library_filename(cls):
        return "HEIO.NET"
    
    @classmethod
    def _get_library_function_args(cls):
        return FUNCTIONS
    
    @classmethod
    def _check_error(cls, result, func, arguments):
        error = cls._LIBRARY.error_get()
        if error:
            raise HEIOLibraryException(error, func.__name__)
        
        return super()._check_error(result, func, arguments)
    
    @classmethod
    def _cleanup(cls):
        cls._LIBRARY.free_all()

    ################################################################################################
    # Matrix

    @classmethod
    def matrix_multiply(cls, a: CMatrix, b: CMatrix):
        return cls._lib().matrix_multiply(a, b)

    @classmethod
    def matrix_invert(cls, matrix: CMatrix):
        return cls._lib().matrix_invert(byref(matrix))

    @classmethod
    def matrix_create_translation(cls, position: CVector3):
        return cls._lib().matrix_create_translation(position)

    @classmethod
    def matrix_create_rotation(cls, euler_rotation: CVector3):
        return cls._lib().matrix_create_rotation(euler_rotation)

    @classmethod
    def matrix_create_from_quaternion(cls, quaternion: CQuaternion):
        return cls._lib().matrix_create_from_quaternion(quaternion)
    
    @classmethod
    def matrix_create_scale(cls, scale: CVector3):
        return cls._lib().matrix_create_scale(scale)

    @classmethod
    def matrix_decompose(cls, matrix: CMatrix):
        position = CVector3(0, 0, 0)
        rotation = CQuaternion(0, 0, 0, 1)
        scale = CVector3(1, 1, 1)

        cls._lib().matrix_decompose(matrix, byref(position), byref(rotation), byref(scale))

        return position, rotation, scale

    @classmethod
    def matrix_to_euler(cls, matrix: CMatrix):
        return cls._lib().matrix_to_euler(matrix)


    ################################################################################################
    # Quaternion

    @classmethod
    def quaternion_create_from_rotation_matrix(cls, matrix: CMatrix):
        return cls._lib().quaternion_create_from_rotation_matrix(matrix)
    

    ################################################################################################
    # Resolve Info
    
    @classmethod
    def resolve_info_combine(cls, resolve_infos: list[TPointer[CResolveInfo]]) -> TPointer[CResolveInfo]:

        c_resolve_infos = util.as_array(resolve_infos, POINTER(CResolveInfo))
        c_resolve_infos_size = c_int(len(resolve_infos))

        return cls._lib().resolve_info_combine(
            c_resolve_infos,
            c_resolve_infos_size
        )
    

    ################################################################################################
    # Sample Chunk Node

    @classmethod
    def sample_chunk_node_find(cls, sample_chunk_node: TPointer[CSampleChunkNode], name: str) -> TPointer[CSampleChunkNode]:
        c_name = c_wchar_p(name)
        return cls._lib().sample_chunk_node_find(sample_chunk_node, c_name)


    ################################################################################################
    # Image

    @classmethod
    def image_load_directory_images(cls, directory: str, images: Iterable[str], streaming_directory: str) -> tuple[dict[str, TPointer[CImage]], TPointer[CResolveInfo]]:

        c_directory = c_wchar_p(directory)
        c_images = util.as_array([c_wchar_p(image) for image in images], c_wchar_p)
        c_images_size = c_int(len(images))
        c_streaming_directory = c_wchar_p(streaming_directory)
        c_resolve_info = pointer(POINTER(CResolveInfo)())

        pairs = cls._lib().image_load_directory_images(
            c_directory,
            c_images,
            c_images_size,
            c_streaming_directory,
            c_resolve_info 
        )
        
        result = util.string_pointer_pairs_to_dict(pairs, CImage)

        return result, c_resolve_info.contents

    @classmethod
    def image_load_material_images(cls, materials: Iterable[TPointer[CMaterial]], streaming_directory: str) -> tuple[dict[str, TPointer[CImage]], TPointer[CResolveInfo]]:
        c_materials = util.as_array(materials, POINTER(CMaterial))
        c_materials_size = c_int(len(materials))
        c_streaming_directory = c_wchar_p(streaming_directory)
        c_resolve_info = pointer(POINTER(CResolveInfo)())

        pairs = cls._lib().image_load_material_images(
            c_materials,
            c_materials_size,
            c_streaming_directory,
            c_resolve_info 
        )

        result = util.string_pointer_pairs_to_dict(pairs, CImage)

        return result, c_resolve_info.contents
    
    @classmethod
    def image_invert_green_channel(cls, pixels):
        cls._lib().image_invert_green_channel(cast(pixels.ctypes.data, POINTER(c_float)), len(pixels))

    
    ################################################################################################
    # Material

    @classmethod
    def material_read_file(cls, filepath: str) -> TPointer[CMaterial]:
        c_filepath = c_wchar_p(filepath)
        return cls._lib().material_read_file(c_filepath)
    
    @classmethod
    def material_write_file(cls, material: TPointer[CMaterial], filepath: str):
        c_filepath = c_wchar_p(filepath)

        cls._lib().material_write_file(
            material,
            c_filepath
        )

    
    ################################################################################################
    # Model
    
    @classmethod
    def model_read_files(cls, filepaths: list[str], include_lod: bool, settings: CMeshImportSettings) -> tuple[list[TPointer[CModelSet]], TPointer[CResolveInfo]]:
        c_filepaths = util.as_array([c_wchar_p(filepath) for filepath in filepaths], c_wchar_p)
        c_filepaths_size = c_int(len(filepaths))
        c_include_lod = c_bool(include_lod)
        c_settings = byref(settings)
        c_resolve_info = pointer(POINTER(CResolveInfo)())

        array = cls._lib().model_read_files(
            c_filepaths, 
            c_filepaths_size,
            c_include_lod,
            c_settings,
            c_resolve_info
        )

        result = util.array_to_list(array, POINTER(CModelSet))

        return result, c_resolve_info.contents
    
    @classmethod
    def model_get_materials(cls, model_sets: list[TPointer[CModelSet]]) -> list[TPointer[CMaterial]]:
        c_model_sets = util.as_array(model_sets, POINTER(CModelSet))
        c_model_sets_size = c_int(len(model_sets))

        array = cls._lib().model_get_materials(
            c_model_sets, 
            c_model_sets_size
        )

        return util.array_to_list(array, POINTER(CMaterial))

    @classmethod
    def model_compile_to_files(cls, model_sets: list[TPointer[CModelSet]], version_mode: int, topology: int, compress_vertex_data: bool, multi_threading: bool, output_directory: str):
        c_model_sets = util.as_array(model_sets, POINTER(CModelSet))
        c_model_sets_size = c_int(len(model_sets))
        c_version_mode = c_int(version_mode)
        c_topology = c_int(topology)
        c_compress_vertex_data = c_bool(compress_vertex_data)
        c_multi_threading = c_bool(multi_threading)
        c_output_directory = c_wchar_p(output_directory)

        cls._lib().model_compile_to_files(
            c_model_sets,
            c_model_sets_size,
            c_version_mode,
            c_topology,
            c_compress_vertex_data,
            c_multi_threading,
            c_output_directory
        )
    

    ################################################################################################
    # Bullet Mesh

    @classmethod
    def bullet_mesh_read_files(cls, filepaths: list[str], settings: CMeshImportSettings) -> list[TPointer[CCollisionMeshData]]:
        c_filepaths = util.as_array([c_wchar_p(filepath) for filepath in filepaths], c_wchar_p)
        c_filepaths_size = c_int(len(filepaths))
        c_settings = byref(settings)

        array = cls._lib().bullet_mesh_read_files(
            c_filepaths, 
            c_filepaths_size,
            c_settings
        )

        return util.array_to_list(array, POINTER(CCollisionMeshData))
    
    @classmethod
    def bullet_mesh_compile_mesh_data(cls, collision_mesh_data: list[CCollisionMeshData]) -> TPointer[CBulletMesh]:
        c_collision_mesh_data = util.as_array([pointer(mesh_data) for mesh_data in collision_mesh_data], POINTER(CCollisionMeshData))
        c_collision_mesh_data_size = c_int(len(collision_mesh_data))

        return cls._lib().bullet_mesh_compile_mesh_data(
            c_collision_mesh_data,
            c_collision_mesh_data_size
        )

    @classmethod
    def bullet_mesh_write_to_file(cls, bullet_mesh: TPointer[CBulletMesh], filepath: str):
        c_filepath = c_wchar_p(filepath)

        cls._lib().bullet_mesh_write_to_file(
            bullet_mesh,
            c_filepath
        )
    

    ################################################################################################
    # Point Cloud

    @classmethod
    def point_cloud_read_files(cls, filepaths: list[str], include_lod: bool, settings: CMeshImportSettings) -> tuple[TPointer[CPointCloudCollection], TPointer[CResolveInfo]]:
        c_filepaths = util.as_array([c_wchar_p(filepath) for filepath in filepaths], c_wchar_p)
        c_filepaths_size = c_int(len(filepaths))
        c_include_lod = c_bool(include_lod)
        c_settings = byref(settings)
        c_resolve_info = pointer(POINTER(CResolveInfo)())

        result = cls._lib().point_cloud_read_files(
            c_filepaths, 
            c_filepaths_size,
            c_include_lod,
            c_settings,
            c_resolve_info
        )

        return result, c_resolve_info.contents
    
    @classmethod
    def point_cloud_write_file(cls, cloud: TPointer[CPointCloudCloud], resource_names: list[str], format_version: int, filepath: str):
        c_resource_names = util.as_array([c_wchar_p(resource_name) for resource_name in resource_names], c_wchar_p)
        c_resource_names_size = c_int(len(resource_names))
        c_format_version = c_uint(format_version)
        c_filepath = c_wchar_p(filepath)

        cls._lib().point_cloud_write_file(
            cloud,
            c_resource_names,
            c_resource_names_size,
            c_format_version,
            c_filepath
        )