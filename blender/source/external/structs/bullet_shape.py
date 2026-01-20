# !!! GENERATED USING HEIO.NET.Utils !!!
# Please do not touch manually!
import ctypes
from .. import nettypes
from ..typing import TPointer

class CBulletShape(ctypes.Structure):
    flags: int
    layer: int
    vertices: TPointer['nettypes.CVector3']
    vertices_size: int
    faces: TPointer['int']
    faces_size: int
    bvh: TPointer['int']
    bvh_size: int
    types: TPointer['int']
    types_size: int
    unknown1: int
    unknown2: int

CBulletShape.__fields__ = [
    ("flags", ctypes.c_ubyte),
    ("layer", ctypes.c_uint),
    ("vertices", ctypes.POINTER(nettypes.CVector3)),
    ("vertices_size", ctypes.c_size_t),
    ("faces", ctypes.POINTER(ctypes.c_uint)),
    ("faces_size", ctypes.c_size_t),
    ("bvh", ctypes.POINTER(ctypes.c_ubyte)),
    ("bvh_size", ctypes.c_size_t),
    ("types", ctypes.POINTER(ctypes.c_ulonglong)),
    ("types_size", ctypes.c_size_t),
    ("unknown1", ctypes.c_uint),
    ("unknown2", ctypes.c_uint),
]

