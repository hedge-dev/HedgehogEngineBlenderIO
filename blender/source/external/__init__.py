import os
from typing import Iterable
from ctypes import cdll, CDLL, POINTER, pointer, byref, cast, c_wchar_p, c_size_t, c_int, c_float, c_bool
from contextlib import contextmanager

# importing everything so we can import from external directly
from .util import get_dll_close, pointer_to_address
from .typing import TPointer
from .pair import CStringPointerPair, CArray
from .math import CVector2, CVector3, CVector4, CVector4Int, CQuaternion, CMatrix
from .resolve_info import CResolveInfo
from .mesh_import_settings import CMeshImportSettings
from .image import CImage
from .sample_chunk_node import CSampleChunkNode
from .material import CFloatMaterialParameter, CIntegerMaterialParameter, CBoolMaterialParameter, CTexture, CMaterial
from .mesh_data import CUVDirection, CVertexWeight, CVertex, CMeshDataMeshSetInfo, CMeshDataGroupInfo, CMeshData, CModelNode, CMeshDataSet, CLODItem, CModelSet
from .collision_mesh_data import CCollisionMeshDataGroup, CBulletPrimitive, CCollisionMeshData
from .point_cloud import CPointCloudPoint, CPointCloudCloud, CPointCloudCollection

from ..utility import general
from ..exceptions import HEIOException

LIB_DIRECTORY = os.path.join(general.ADDON_DIR, "DLL")
LIB_NAME = "HEIO.NET"

LIB_EXT = ""
if general.is_windows():
    LIB_EXT = ".dll"
elif general.is_mac():
    LIB_EXT = ".dylib"
elif general.is_linux():
    LIB_EXT = ".so"

LIB_FILEPATH = os.path.join(LIB_DIRECTORY, LIB_NAME + LIB_EXT)

class HEIOLibraryException(HEIOException):
    function_name: str

    def __init__(self, message: str, function_name: str, *args: object):
        super().__init__(f"Library Exception when calling \"{function_name}\": {message}", *args)
        self.function_name = function_name

class Library:

    _LOADED_LIBRARY = None  

    @classmethod
    def lib(cls):
        if cls._LOADED_LIBRARY is None:
            raise Exception("Library not loaded")
        return cls._LOADED_LIBRARY

    @classmethod
    @contextmanager
    def load(cls):
        try:
            cls._LOADED_LIBRARY = cdll.LoadLibrary(LIB_FILEPATH)
            cls._setup(cls._LOADED_LIBRARY)
            yield cls
        finally:
            cls._LOADED_LIBRARY.free_all()
            get_dll_close()(cls._LOADED_LIBRARY._handle)
            cls._LOADED_LIBRARY = None

    @classmethod
    def _setup(cls, lib: CDLL):

        lib.error_get.restype = c_wchar_p

        lib.matrix_decompose.argtypes = (CMatrix, POINTER(CVector3), POINTER(CQuaternion), POINTER(CVector3))
        lib.matrix_decompose.errcheck = cls._check_error

        lib.matrix_create_translation.argtypes = (CVector3,)
        lib.matrix_create_translation.restype = CMatrix
        lib.matrix_create_translation.errcheck = cls._check_error

        lib.matrix_create_rotation.argtypes = (CVector3,)
        lib.matrix_create_rotation.restype = CMatrix
        lib.matrix_create_rotation.errcheck = cls._check_error

        lib.matrix_create_scale.argtypes = (CVector3,)
        lib.matrix_create_scale.restype = CMatrix
        lib.matrix_create_scale.errcheck = cls._check_error

        lib.matrix_multiply.argtypes = (CMatrix, CMatrix)
        lib.matrix_multiply.restype = CMatrix
        lib.matrix_multiply.errcheck = cls._check_error

        lib.quaternion_create_from_rotation_matrix.argtypes = (CMatrix,)
        lib.quaternion_create_from_rotation_matrix.restype = CQuaternion
        lib.quaternion_create_from_rotation_matrix.errcheck = cls._check_error

        lib.material_read_file.argtypes = (c_wchar_p,)
        lib.material_read_file.restype = POINTER(CMaterial)
        lib.material_read_file.errcheck = cls._check_error

        lib.resolve_info_combine.argtypes = (POINTER(POINTER(CResolveInfo)), c_size_t)
        lib.resolve_info_combine.restype = POINTER(CResolveInfo)
        lib.resolve_info_combine.errcheck = cls._check_error

        lib.image_load_directory_images.argtypes = (c_wchar_p, POINTER(c_wchar_p), c_size_t, c_wchar_p, POINTER(POINTER(CResolveInfo)))
        lib.image_load_directory_images.restype = CArray
        lib.image_load_directory_images.errcheck = cls._check_error

        lib.image_load_material_images.argtypes = (POINTER(POINTER(CMaterial)), c_size_t, c_wchar_p, POINTER(POINTER(CResolveInfo)))
        lib.image_load_material_images.restype = CArray
        lib.image_load_material_images.errcheck = cls._check_error

        lib.image_invert_green_channel.argtypes = (POINTER(c_float), c_size_t)
        lib.image_invert_green_channel.errcheck = cls._check_error

        lib.sample_chunk_node_find.argtypes = (POINTER(CSampleChunkNode), c_wchar_p)
        lib.sample_chunk_node_find.restype = POINTER(CSampleChunkNode)
        lib.sample_chunk_node_find.errcheck = cls._check_error

        lib.model_read_files.argtypes = (POINTER(c_wchar_p), c_size_t, c_bool, POINTER(CMeshImportSettings), POINTER(POINTER(CResolveInfo)))
        lib.model_read_files.restype = CArray
        lib.model_read_files.errcheck = cls._check_error

        lib.model_get_materials.argtypes = (POINTER(POINTER(CModelSet)), c_size_t)
        lib.model_get_materials.restype = CArray
        lib.model_get_materials.errcheck = cls._check_error

        lib.matrix_invert.argtypes = (CMatrix,)
        lib.matrix_invert.restype = CMatrix
        lib.matrix_invert.errcheck = cls._check_error

        lib.collision_mesh_read_files.argtypes = (POINTER(c_wchar_p), c_size_t, POINTER(CMeshImportSettings))
        lib.collision_mesh_read_files.restype = CArray
        lib.collision_mesh_read_files.errcheck = cls._check_error

        lib.matrix_create_from_quaternion.argtypes = (CQuaternion,)
        lib.matrix_create_from_quaternion.restype = CMatrix
        lib.matrix_create_from_quaternion.errcheck = cls._check_error

        lib.point_cloud_read_files.argtypes = (POINTER(c_wchar_p), c_size_t, c_bool, POINTER(CMeshImportSettings), POINTER(POINTER(CResolveInfo)))
        lib.point_cloud_read_files.restype = POINTER(CPointCloudCollection)
        lib.point_cloud_read_files.errcheck = cls._check_error

        lib.material_write_file.argtypes = (POINTER(CMaterial), c_wchar_p)
        lib.material_write_file.errcheck = cls._check_error

        lib.matrix_to_euler.argtypes = (CMatrix,)
        lib.matrix_to_euler.restype = CVector3
        lib.matrix_to_euler.errcheck = cls._check_error

        lib.collision_mesh_write_to_file.argtypes = (POINTER(POINTER(CCollisionMeshData)), c_size_t, c_wchar_p, c_int, c_wchar_p)
        lib.collision_mesh_write_to_file.errcheck = cls._check_error

    @classmethod
    def as_array(cls, iterable: Iterable, type):
        array = (type * len(iterable))(*iterable)
        return cast(array, POINTER(type))

    @classmethod
    def construct_array(cls, iterable: Iterable, type):
        return cls.as_array([type(x) for x in iterable], type)

    @classmethod
    def _check_error(cls, result, func, arguments):
        error = cls._LOADED_LIBRARY.error_get()
        if error:
            raise HEIOLibraryException(error, func.__name__)
        
        return result

    @classmethod
    def _string_pointer_pairs_to_dict(cls, array: CArray, target_type):
        result = {}
        
        item_pointer = cast(array.array, POINTER(CStringPointerPair))
        for i in range(array.size):
            pair: CStringPointerPair = item_pointer[i]
            result[pair.name] = cast(pair.pointer, POINTER(target_type))

        return result
    
    @classmethod
    def _array_to_list(cls, array: CArray, target_type):
        result = []

        item_pointer = cast(array.array, POINTER(target_type))
        for i in range(array.size):
            result.append(item_pointer[i])

        return result

    @classmethod
    def matrix_decompose(cls, matrix: CMatrix):
        position = CVector3(0, 0, 0)
        rotation = CQuaternion(0, 0, 0, 1)
        scale = CVector3(1, 1, 1)

        cls.lib().matrix_decompose(matrix, byref(position), byref(rotation), byref(scale))

        return position, rotation, scale
    
    @classmethod
    def matrix_create_translation(cls, position: CVector3):
        return cls.lib().matrix_create_translation(position)

    @classmethod
    def matrix_create_rotation(cls, euler_rotation: CVector3):
        return cls.lib().matrix_create_rotation(euler_rotation)

    @classmethod
    def matrix_create_scale(cls, scale: CVector3):
        return cls.lib().matrix_create_scale(scale)

    @classmethod
    def matrix_multiply(cls, a: CMatrix, b: CMatrix):
        return cls.lib().matrix_multiply(a, b)

    @classmethod
    def quaternion_create_from_rotation_matrix(cls, matrix: CMatrix):
        return cls.lib().quaternion_create_from_rotation_matrix(matrix)
    
    @classmethod
    def material_read_file(cls, filepath: str) -> TPointer[CMaterial]:
        c_filepath = c_wchar_p(filepath)
        return cls.lib().material_read_file(c_filepath)
    
    @classmethod
    def resolve_info_combine(cls, resolve_infos: list[TPointer[CResolveInfo]]) -> TPointer[CResolveInfo]:

        c_resolve_infos = cls.as_array(resolve_infos, POINTER(CResolveInfo))
        c_resolve_infos_size = c_size_t(len(resolve_infos))

        return cls.lib().resolve_info_combine(
            c_resolve_infos,
            c_resolve_infos_size
        )


    @classmethod
    def image_load_directory_images(cls, directory: str, images: Iterable[str], streaming_directory: str) -> tuple[dict[str, TPointer[CImage]], TPointer[CResolveInfo]]:

        c_directory = c_wchar_p(directory)
        c_images = cls.as_array([c_wchar_p(image) for image in images], c_wchar_p)
        c_images_size = c_size_t(len(images))
        c_streaming_directory = c_wchar_p(streaming_directory)
        c_resolve_info = pointer(POINTER(CResolveInfo)())

        pairs = cls.lib().image_load_directory_images(
            c_directory,
            c_images,
            c_images_size,
            c_streaming_directory,
            c_resolve_info 
        )
        
        result = cls._string_pointer_pairs_to_dict(pairs, CImage)

        return result, c_resolve_info.contents

    @classmethod
    def image_load_material_images(cls, materials: Iterable[TPointer[CMaterial]], streaming_directory: str) -> tuple[dict[str, TPointer[CImage]], TPointer[CResolveInfo]]:
        c_materials = cls.as_array(materials, POINTER(CMaterial))
        c_materials_size = c_size_t(len(materials))
        c_streaming_directory = c_wchar_p(streaming_directory)
        c_resolve_info = pointer(POINTER(CResolveInfo)())

        pairs = cls.lib().image_load_material_images(
            c_materials,
            c_materials_size,
            c_streaming_directory,
            c_resolve_info 
        )

        result = cls._string_pointer_pairs_to_dict(pairs, CImage)

        return result, c_resolve_info.contents
    
    @classmethod
    def image_invert_green_channel(cls, pixels):
        cls.lib().image_invert_green_channel(pixels.ctypes.data, len(pixels))

    @classmethod
    def sample_chunk_node_find(cls, sample_chunk_node: TPointer[CSampleChunkNode], name: str) -> TPointer[CSampleChunkNode]:
        c_name = c_wchar_p(name)
        return cls.lib().sample_chunk_node_find(sample_chunk_node, c_name)
    
    @classmethod
    def model_read_files(cls, filepaths: list[str], include_lod: bool, settings: CMeshImportSettings) -> tuple[list[TPointer[CModelSet]], TPointer[CResolveInfo]]:
        c_filepaths = cls.as_array([c_wchar_p(filepath) for filepath in filepaths], c_wchar_p)
        c_filepaths_size = c_size_t(len(filepaths))
        c_include_lod = c_bool(include_lod)
        c_settings = byref(settings)
        c_resolve_info = pointer(POINTER(CResolveInfo)())

        array = cls.lib().model_read_files(
            c_filepaths, 
            c_filepaths_size,
            c_include_lod,
            c_settings,
            c_resolve_info
        )

        result = cls._array_to_list(array, POINTER(CModelSet))

        return result, c_resolve_info.contents
    
    @classmethod
    def model_get_materials(cls, model_sets: list[TPointer[CModelSet]]) -> list[TPointer[CMaterial]]:
        c_model_sets = cls.as_array(model_sets, POINTER(CModelSet))
        c_model_sets_size = c_size_t(len(model_sets))

        array = cls.lib().model_get_materials(
            c_model_sets, 
            c_model_sets_size
        )

        return cls._array_to_list(array, POINTER(CMaterial))
    
    @classmethod
    def matrix_invert(cls, matrix: CMatrix):
        return cls.lib().matrix_invert(matrix)
    
    @classmethod
    def matrix_create_from_quaternion(cls, quaternion: CQuaternion):
        return cls.lib().matrix_create_from_quaternion(quaternion)

    @classmethod
    def collision_mesh_read_files(cls, filepaths: list[str], settings: CMeshImportSettings) -> list[TPointer[CCollisionMeshData]]:
        c_filepaths = cls.as_array([c_wchar_p(filepath) for filepath in filepaths], c_wchar_p)
        c_filepaths_size = c_size_t(len(filepaths))
        c_settings = byref(settings)

        array = cls.lib().collision_mesh_read_files(
            c_filepaths, 
            c_filepaths_size,
            c_settings
        )

        return cls._array_to_list(array, POINTER(CCollisionMeshData))

    @classmethod
    def point_cloud_read_files(cls, filepaths: list[str], include_lod: bool, settings: CMeshImportSettings) -> tuple[TPointer[CPointCloudCollection], TPointer[CResolveInfo]]:
        c_filepaths = cls.as_array([c_wchar_p(filepath) for filepath in filepaths], c_wchar_p)
        c_filepaths_size = c_size_t(len(filepaths))
        c_include_lod = c_bool(include_lod)
        c_settings = byref(settings)
        c_resolve_info = pointer(POINTER(CResolveInfo)())

        result = cls.lib().point_cloud_read_files(
            c_filepaths, 
            c_filepaths_size,
            c_include_lod,
            c_settings,
            c_resolve_info
        )

        return result, c_resolve_info.contents

    @classmethod
    def material_write_file(cls, material: TPointer[CMaterial], filepath: str):
        c_filepath = c_wchar_p(filepath)

        cls.lib().material_write_file(
            material,
            c_filepath
        )

    @classmethod
    def matrix_to_euler(cls, matrix: CMatrix):
        return cls.lib().matrix_to_euler(matrix)
    
    @classmethod
    def collision_mesh_write_to_file(cls, collision_mesh_data: list[CCollisionMeshData], name: str, bullet_mesh_version: int, filepath: str):
        c_collision_mesh_data = cls.as_array([pointer(mesh_data) for mesh_data in collision_mesh_data], POINTER(CCollisionMeshData))
        c_collision_mesh_data_size = c_size_t(len(collision_mesh_data))
        c_name = c_wchar_p(name)
        c_bullet_mesh_version = c_int(bullet_mesh_version)
        c_filepath = c_wchar_p(filepath)

        cls.lib().collision_mesh_write_to_file(
            c_collision_mesh_data,
            c_collision_mesh_data_size,
            c_name,
            c_bullet_mesh_version,
            c_filepath
        )