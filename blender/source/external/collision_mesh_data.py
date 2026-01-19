from ctypes import Structure, POINTER, c_size_t, c_int, c_uint, c_ubyte, c_bool, c_wchar_p, c_ulonglong
from .util import FieldsFromTypeHints
from .math import CVector3, CQuaternion

class CCollisionMeshDataGroup(Structure, metaclass=FieldsFromTypeHints):
    size: c_uint
    layer: c_uint
    is_convex: c_bool
    convex_type: c_uint

    convex_flag_values: POINTER(c_ubyte)
    convex_flag_values_size: c_size_t

class CBulletPrimitive(Structure, metaclass=FieldsFromTypeHints):
    shape_type: c_ubyte
    surface_layer: c_ubyte
    surface_type: c_ubyte
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

    type_values: POINTER(c_ubyte)
    type_values_size: c_size_t

    flags: POINTER(c_uint)
    flags_size: c_size_t

    flag_values: POINTER(c_ubyte)
    flag_values_size: c_size_t

    groups: POINTER(CCollisionMeshDataGroup)
    groups_size: c_size_t

    primitives: POINTER(CBulletPrimitive)
    primitives_size: c_size_t

class CBulletShape(Structure, metaclass=FieldsFromTypeHints):
    flags: c_ubyte
    layer: c_uint

    vertices: POINTER(CVector3)
    vertices_size: c_size_t

    faces: POINTER(c_uint)
    faces_size: c_size_t

    bvh: POINTER(c_ubyte)
    bvh_size: c_size_t

    types: POINTER(c_ulonglong)
    types_size: c_size_t

    unknown1: c_uint
    unknown2: c_uint
    
class CBulletMesh(Structure, metaclass=FieldsFromTypeHints):
    name: c_wchar_p
    bullet_mesh_version: c_int
    
    shapes: POINTER(CBulletShape)
    shapes_size: c_size_t
    
    primitives: POINTER(CBulletPrimitive)
    primitives_size: c_size_t