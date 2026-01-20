# !!! GENERATED USING HEIO.NET.Utils !!!
# Please do not touch manually!
import ctypes
from .. import nettypes
from ..typing import TPointer

class CBulletPrimitive(ctypes.Structure):
    shape_type: int
    surface_layer: int
    surface_type: int
    surface_flags: int
    position: nettypes.CVector3
    rotation: nettypes.CQuaternion
    dimensions: nettypes.CVector3

CBulletPrimitive.__fields__ = [
    ("shape_type", ctypes.c_ubyte),
    ("surface_layer", ctypes.c_ubyte),
    ("surface_type", ctypes.c_ubyte),
    ("surface_flags", ctypes.c_uint),
    ("position", nettypes.CVector3),
    ("rotation", nettypes.CQuaternion),
    ("dimensions", nettypes.CVector3),
]

