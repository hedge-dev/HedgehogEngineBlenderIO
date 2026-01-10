from .math import CVector3, CQuaternion
from ctypes import Structure, c_byte, c_uint

class CBulletPrimitive(Structure):
    _fields_ = [
        ("shape_type", c_byte),
        ("surface_layer", c_byte),
        ("surface_type", c_byte),
        ("surface_flags", c_uint),
        ("position", CVector3),
        ("rotation", CQuaternion),
        ("dimensions", CVector3)
    ]