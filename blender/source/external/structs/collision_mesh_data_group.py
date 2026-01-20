# !!! GENERATED USING HEIO.NET.Utils !!!
# Please do not touch manually!
import ctypes
from .. import nettypes
from ..typing import TPointer

class CCollisionMeshDataGroup(ctypes.Structure):
    size: int
    layer: int
    is_convex: bool
    convex_type: int
    convex_flag_values: TPointer['int']
    convex_flag_values_size: int

CCollisionMeshDataGroup.__fields__ = [
    ("size", ctypes.c_uint),
    ("layer", ctypes.c_uint),
    ("is_convex", ctypes.c_bool),
    ("convex_type", ctypes.c_uint),
    ("convex_flag_values", ctypes.POINTER(ctypes.c_ubyte)),
    ("convex_flag_values_size", ctypes.c_size_t),
]

