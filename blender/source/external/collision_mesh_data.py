from ctypes import Structure, POINTER, c_size_t, c_uint, c_byte, c_bool, c_wchar_p
from .util import FieldsFromTypeHints
from .math import CVector3, CQuaternion

class CCollisionMeshDataGroup(Structure, metaclass=FieldsFromTypeHints):
    size: c_uint
    layer: c_uint
    is_convex: c_bool
    convex_type: c_uint

    convex_flag_values: POINTER(c_byte)
    convex_flag_values_size: c_size_t

class CBulletPrimitive(Structure, metaclass=FieldsFromTypeHints):
    shape_type: c_byte
    surface_layer: c_byte
    surface_type: c_byte
    surface_flags: c_uint
    position: CVector3
    rotation: CQuaternion
    dimensions: CVector3

class CCollisionMeshData(Structure, metaclass=FieldsFromTypeHints):
    name: c_wchar_p

    vertices: POINTER(CVector3)
    vertices_size: c_size_t

    triangle_indices: POINTER(c_uint)
    triangle_indices_size: c_size_t

    types: POINTER(c_uint)
    types_size: c_size_t

    type_values: POINTER(c_byte)
    type_values_size: c_size_t

    flags: POINTER(c_uint)
    flags_size: c_size_t

    flag_values: POINTER(c_byte)
    flag_values_size: c_size_t

    groups: POINTER(CCollisionMeshDataGroup)
    groups_size: c_size_t

    primitives: POINTER(CBulletPrimitive)
    primitives_size: c_size_t