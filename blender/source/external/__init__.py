import os
from typing import Iterable
from ctypes import cdll, CDLL, POINTER, pointer, c_wchar_p, c_size_t, cast, c_float, c_void_p
from contextlib import contextmanager

from .typing import TPointer
from .math import CVector3, CQuaternion, CMatrix
from .material import CFloatMaterialParameter, CIntegerMaterialParameter, CBoolMaterialParameter, CTexture, CMaterial
from .image import CImage
from .stringPointerPair import CStringPointerPair, CStringPointerPairs
from .resolveInfo import CResolveInfo

from .util import get_dll_close

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
    def __init__(self, message: str, *args: object):
        super().__init__("Library Exception:" + message, *args)

class Library:

    _LOADED_LIBRARY = None  
    _to_free: list[tuple[any, any]] = []

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
            for func, pointer in cls._to_free:
                func(pointer)
            cls._to_free.clear()

            cls._LOADED_LIBRARY.error_free()

            get_dll_close()(cls._LOADED_LIBRARY._handle)
            cls._LOADED_LIBRARY = None

    @classmethod
    def _setup(cls, lib: CDLL):

        lib.error_get.restype = c_wchar_p

        lib.matrix_decompose.argtypes = (CMatrix, POINTER(CVector3), POINTER(CQuaternion), POINTER(CVector3))

        lib.matrix_create_translation.argtypes = (CVector3,)
        lib.matrix_create_translation.restype = CMatrix

        lib.matrix_create_rotation.argtypes = (CVector3,)
        lib.matrix_create_rotation.restype = CMatrix

        lib.matrix_create_scale.argtypes = (CVector3,)
        lib.matrix_create_scale.restype = CMatrix

        lib.matrix_multiply.argtypes = (CMatrix, CMatrix)
        lib.matrix_multiply.restype = CMatrix

        lib.quaternion_create_from_rotation_matrix.argtypes = (CMatrix,)
        lib.quaternion_create_from_rotation_matrix.restype = CQuaternion

        lib.material_read_file.argtypes = (c_wchar_p,)
        lib.material_read_file.restype = POINTER(CMaterial)

        lib.material_free.argtypes = (POINTER(CMaterial),)

        lib.resolve_info_combine.argtypes = (POINTER(POINTER(CResolveInfo)), c_size_t)
        lib.resolve_info_combine.restype = POINTER(CResolveInfo)

        lib.resolve_info_free.argtypes = (POINTER(CResolveInfo),)

        lib.image_free.argtypes = (POINTER(CImage),)

        lib.image_load_directory_images.argtypes = (c_wchar_p, POINTER(c_wchar_p), c_size_t, c_wchar_p, POINTER(POINTER(CResolveInfo)))
        lib.image_load_directory_images.restype = POINTER(CStringPointerPairs)

        lib.image_load_material_images.argtypes = (POINTER(POINTER(CMaterial)), c_size_t, c_wchar_p, POINTER(POINTER(CResolveInfo)))
        lib.image_load_material_images.restype = POINTER(CStringPointerPairs)

        lib.image_free_list.argtypes = (POINTER(CStringPointerPairs),)

        lib.image_invert_green_channel.argtypes = (POINTER(c_float), c_size_t)

    @classmethod
    def _as_array(cls, iterable: Iterable, type):
        return cast((type * len(iterable))(*iterable), POINTER(type))

    @classmethod
    def _check_error(cls):
        error = cls._LOADED_LIBRARY.error_get()
        if error:
            raise HEIOLibraryException(error.value)

    @classmethod
    def matrix_decompose(cls, matrix: CMatrix):
        position = CVector3(0, 0, 0)
        rotation = CQuaternion(0, 0, 0, 1)
        scale = CVector3(1, 1, 1)

        cls.lib().matrix_decompose(matrix, pointer(position), pointer(rotation), pointer(scale))
        cls._check_error()

        return position, rotation, scale
    
    @classmethod
    def matrix_create_translation(cls, position: CVector3):
        result = cls.lib().matrix_create_translation(position)
        cls._check_error()
        return result

    @classmethod
    def matrix_create_rotation(cls, euler_rotation: CVector3):
        result = cls.lib().matrix_create_rotation(euler_rotation)
        cls._check_error()
        return result

    @classmethod
    def matrix_create_scale(cls, scale: CVector3):
        result = cls.lib().matrix_create_scale(scale)
        cls._check_error()
        return result

    @classmethod
    def matrix_multiply(cls, a: CMatrix, b: CMatrix):
        result = cls.lib().matrix_multiply(a, b)
        cls._check_error()
        return result

    @classmethod
    def quaternion_create_from_rotation_matrix(cls, matrix: CMatrix):
        result = cls.lib().quaternion_create_from_rotation_matrix(matrix)
        cls._check_error()
        return result
    
    @classmethod
    def material_read_file(cls, filepath: str) -> TPointer[CMaterial]:
        lib = cls.lib()
        c_filepath = c_wchar_p(filepath)
        result = lib.material_read_file(c_filepath)
        cls._check_error()
        cls._to_free.append((lib.material_free, result))
        return result
    
    @classmethod
    def resolve_info_combine(cls, resolve_infos: list[TPointer[CResolveInfo]]) -> TPointer[CResolveInfo]:
        lib = cls.lib()

        c_resolve_infos = cls._as_array(resolve_infos, POINTER(CResolveInfo))
        c_resolve_infos_size = c_size_t(len(resolve_infos))

        result = lib.resolve_info_combine(
            c_resolve_infos,
            c_resolve_infos_size
        )
        cls._check_error()

        cls._to_free.append((lib.resolve_info_free, result))

        return result


    @classmethod
    def image_load_directory_images(cls, directory: str, images: Iterable[str], streaming_directory: str) -> tuple[dict[str, TPointer[CImage]], TPointer[CResolveInfo]]:
        lib = cls.lib()

        c_directory = c_wchar_p(directory)
        c_images = cls._as_array([c_wchar_p(image) for image in images], c_wchar_p)
        c_images_size = c_size_t(len(images))
        c_streaming_directory = c_wchar_p(streaming_directory)
        c_resolve_info = pointer(POINTER(CResolveInfo)())

        pairs = lib.image_load_directory_images(
            c_directory,
            c_images,
            c_images_size,
            c_streaming_directory,
            c_resolve_info 
        )
        cls._check_error()

        c_resolve_info = c_resolve_info.contents

        cls._to_free.append((lib.image_free_list, pairs))
        cls._to_free.append((lib.resolve_info_free, c_resolve_info))

        result = {}
        pair_data: CStringPointerPairs = pairs.contents
        for i in range(pair_data.size):
            pair: CStringPointerPair = pair_data.pairs[i]
            result[pair.name] = cast(pair.pointer, POINTER(CImage))

        return result, c_resolve_info

    @classmethod
    def image_load_material_images(cls, materials: Iterable[TPointer[CMaterial]], streaming_directory: str) -> tuple[dict[str, TPointer[CImage]], TPointer[CResolveInfo]]:
        lib = cls.lib()

        c_materials = cls._as_array(materials, POINTER(CMaterial))
        c_materials_size = c_size_t(len(materials))
        c_streaming_directory = c_wchar_p(streaming_directory)
        c_resolve_info = pointer(POINTER(CResolveInfo)())

        pairs = lib.image_load_material_images(
            c_materials,
            c_materials_size,
            c_streaming_directory,
            c_resolve_info 
        )
        cls._check_error()

        c_resolve_info = c_resolve_info.contents

        cls._to_free.append((lib.image_free_list, pairs))
        cls._to_free.append((lib.resolve_info_free, c_resolve_info))

        result = {}
        pair_data: CStringPointerPairs = pairs.contents
        for i in range(pair_data.size):
            pair: CStringPointerPair = pair_data.pairs[i]
            result[pair.name] = cast(pair.pointer, POINTER(CImage))

        return result, c_resolve_info
    
    @classmethod
    def image_invert_green_channel(cls, pixels):
        cls.lib().image_invert_green_channel(pixels.ctypes.data, len(pixels))
        cls._check_error()