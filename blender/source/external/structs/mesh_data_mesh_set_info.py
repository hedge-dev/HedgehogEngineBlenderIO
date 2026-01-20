# !!! GENERATED USING HEIO.NET.Utils !!!
# Please do not touch manually!
import ctypes
from .. import nettypes
from ..typing import TPointer
from .string_pointer_pair import CStringPointerPair

class CMeshDataMeshSetInfo(ctypes.Structure):
    use_byte_colors: bool
    enable8weights: bool
    enable_multi_tangent: bool
    material_reference: CStringPointerPair
    mesh_slot_type: int
    mesh_slot_name: str
    size: int

CMeshDataMeshSetInfo.__fields__ = [
    ("use_byte_colors", ctypes.c_bool),
    ("enable8weights", ctypes.c_bool),
    ("enable_multi_tangent", ctypes.c_bool),
    ("material_reference", CStringPointerPair),
    ("mesh_slot_type", ctypes.c_uint),
    ("mesh_slot_name", ctypes.c_wchar_p),
    ("size", ctypes.c_int),
]

