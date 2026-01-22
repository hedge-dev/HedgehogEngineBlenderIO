# !!! GENERATED USING HEIO.NET.Utils !!!
# Please do not touch manually!
import ctypes
from .. import nettypes
from ..typing import TPointer
from .bullet_shape import CBulletShape
from .bullet_primitive import CBulletPrimitive

class CBulletMesh(ctypes.Structure):
    name: str
    bullet_mesh_version: int
    shapes: TPointer['CBulletShape']
    shapes_size: int
    primitives: TPointer['CBulletPrimitive']
    primitives_size: int

CBulletMesh._fields_ = [
    ("name", ctypes.c_wchar_p),
    ("bullet_mesh_version", ctypes.c_int),
    ("shapes", ctypes.POINTER(CBulletShape)),
    ("shapes_size", ctypes.c_int),
    ("primitives", ctypes.POINTER(CBulletPrimitive)),
    ("primitives_size", ctypes.c_int),
]

