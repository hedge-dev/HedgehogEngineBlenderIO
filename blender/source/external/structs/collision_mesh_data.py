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

CCollisionMeshData.__fields__ = [
    ("name", ctypes.c_wchar_p),
    ("vertices", ctypes.POINTER(nettypes.CVector3)),
    ("vertices_size", ctypes.c_size_t),
    ("triangle_indices", ctypes.POINTER(ctypes.c_uint)),
    ("triangle_indices_size", ctypes.c_size_t),
    ("types", ctypes.POINTER(ctypes.c_uint)),
    ("types_size", ctypes.c_size_t),
    ("type_values", ctypes.POINTER(ctypes.c_ubyte)),
    ("type_values_size", ctypes.c_size_t),
    ("flags", ctypes.POINTER(ctypes.c_uint)),
    ("flags_size", ctypes.c_size_t),
    ("flag_values", ctypes.POINTER(ctypes.c_ubyte)),
    ("flag_values_size", ctypes.c_size_t),
    ("groups", ctypes.POINTER(CCollisionMeshDataGroup)),
    ("groups_size", ctypes.c_size_t),
    ("primitives", ctypes.POINTER(CBulletPrimitive)),
    ("primitives_size", ctypes.c_size_t),
]

