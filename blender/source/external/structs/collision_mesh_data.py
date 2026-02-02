# !!! GENERATED USING HEIO.NET.Utils !!!
# Please do not touch manually!
import ctypes
from .. import nettypes
from ..typing import TPointer
from .collision_mesh_data_group import CCollisionMeshDataGroup
from .bullet_primitive import CBulletPrimitive

class CCollisionMeshData(ctypes.Structure):
    name: str
    vertices: TPointer['nettypes.CVector3']
    vertices_size: int
    triangle_indices: TPointer['int']
    triangle_indices_size: int
    types: TPointer['int']
    types_size: int
    type_values: TPointer['int']
    type_values_size: int
    flags: TPointer['int']
    flags_size: int
    flag_values: TPointer['int']
    flag_values_size: int
    groups: TPointer['CCollisionMeshDataGroup']
    groups_size: int
    primitives: TPointer['CBulletPrimitive']
    primitives_size: int

CCollisionMeshData._fields_ = [
    ("name", ctypes.c_wchar_p),
    ("vertices", ctypes.POINTER(nettypes.CVector3)),
    ("vertices_size", ctypes.c_int),
    ("triangle_indices", ctypes.POINTER(ctypes.c_uint)),
    ("triangle_indices_size", ctypes.c_int),
    ("types", ctypes.POINTER(ctypes.c_uint)),
    ("types_size", ctypes.c_int),
    ("type_values", ctypes.POINTER(ctypes.c_ubyte)),
    ("type_values_size", ctypes.c_int),
    ("flags", ctypes.POINTER(ctypes.c_uint)),
    ("flags_size", ctypes.c_int),
    ("flag_values", ctypes.POINTER(ctypes.c_ubyte)),
    ("flag_values_size", ctypes.c_int),
    ("groups", ctypes.POINTER(CCollisionMeshDataGroup)),
    ("groups_size", ctypes.c_int),
    ("primitives", ctypes.POINTER(CBulletPrimitive)),
    ("primitives_size", ctypes.c_int),
]

