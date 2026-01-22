# !!! GENERATED USING HEIO.NET.Utils !!!
# Please do not touch manually!
import ctypes
from .. import nettypes
from ..typing import TPointer

class CResolveInfo(ctypes.Structure):
    unresolved_files: TPointer['str']
    unresolved_files_size: int
    missing_dependencies: TPointer['str']
    missing_dependencies_size: int
    packed_dependencies: TPointer['str']
    packed_dependencies_size: int
    unresolved_ntsp_files: TPointer['str']
    unresolved_ntsp_files_size: int
    missing_streamed_images: TPointer['str']
    missing_streamed_images_size: int

CResolveInfo._fields_ = [
    ("unresolved_files", ctypes.POINTER(ctypes.c_wchar_p)),
    ("unresolved_files_size", ctypes.c_int),
    ("missing_dependencies", ctypes.POINTER(ctypes.c_wchar_p)),
    ("missing_dependencies_size", ctypes.c_int),
    ("packed_dependencies", ctypes.POINTER(ctypes.c_wchar_p)),
    ("packed_dependencies_size", ctypes.c_int),
    ("unresolved_ntsp_files", ctypes.POINTER(ctypes.c_wchar_p)),
    ("unresolved_ntsp_files_size", ctypes.c_int),
    ("missing_streamed_images", ctypes.POINTER(ctypes.c_wchar_p)),
    ("missing_streamed_images_size", ctypes.c_int),
]

