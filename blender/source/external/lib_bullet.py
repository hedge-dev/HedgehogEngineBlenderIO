from ctypes import byref, c_void_p, c_bool, c_int, c_uint

from .nettypes import CVector3

from .library import ExternalLibrary
from .functions.bullet import FUNCTIONS

class Bullet(ExternalLibrary):
    
    @classmethod
    def _get_library_filename(cls):
        return "libbulletc"
    
    @classmethod
    def _get_library_function_args(cls):
        return FUNCTIONS
    
    @classmethod
    def btIndexedMesh_new(cls):
        return cls.bullet().btIndexedMesh_new()

    @classmethod
    def btIndexedMesh_setIndexType(cls, indexed_mesh: c_void_p, value: int):
        cls.bullet().btIndexedMesh_setIndexType(indexed_mesh, c_int(value))

    @classmethod
    def btIndexedMesh_setNumTriangles(cls, indexed_mesh: c_void_p, value: int):
        cls.bullet().btIndexedMesh_setNumTriangles(indexed_mesh, c_int(value))

    @classmethod
    def btIndexedMesh_setNumVertices(cls, indexed_mesh: c_void_p, value: int):
        cls.bullet().btIndexedMesh_setNumVertices(indexed_mesh, c_int(value))

    @classmethod
    def btIndexedMesh_setTriangleIndexBase(cls, indexed_mesh: c_void_p, value: c_void_p):
        cls.bullet().btIndexedMesh_setTriangleIndexBase(indexed_mesh, value)

    @classmethod
    def btIndexedMesh_setTriangleIndexStride(cls, indexed_mesh: c_void_p, value: int):
        cls.bullet().btIndexedMesh_setTriangleIndexStride(indexed_mesh, c_int(value))

    @classmethod
    def btIndexedMesh_setVertexBase(cls, indexed_mesh: c_void_p, value: c_void_p):
        cls.bullet().btIndexedMesh_setVertexBase(indexed_mesh, value)

    @classmethod
    def btIndexedMesh_setVertexStride(cls, indexed_mesh: c_void_p, value: int):
        cls.bullet().btIndexedMesh_setVertexStride(indexed_mesh, c_int(value))

    @classmethod
    def btIndexedMesh_setVertexType(cls, indexed_mesh: c_void_p, value: int):
        cls.bullet().btIndexedMesh_setVertexType(indexed_mesh, c_int(value))

    @classmethod
    def btIndexedMesh_delete(cls, indexed_mesh: c_void_p):
        cls.bullet().btIndexedMesh_delete(indexed_mesh)

    @classmethod
    def btTriangleIndexVertexArray_new(cls):
        return cls.bullet().btTriangleIndexVertexArray_new()
    
    @classmethod
    def btTriangleIndexVertexArray_addIndexedMesh(cls, triangle_vertex_array: c_void_p, indexed_mesh: c_void_p, triangle_index_type: int):
        cls.bullet().btTriangleIndexVertexArray_addIndexedMesh(triangle_vertex_array, indexed_mesh, c_int(triangle_index_type))

    @classmethod
    def btStridingMeshInterface_delete(cls, striding_mesh_interface: c_void_p):
        cls.bullet().btStridingMeshInterface_delete(striding_mesh_interface)

    @classmethod
    def btOptimizedBvh_new(cls):
        return cls.bullet().btOptimizedBvh_new()
    
    @classmethod
    def btOptimizedBvh_build(cls, optimized_bvh: c_void_p, triangles: c_void_p, use_quantized_aabb_compression: bool, bvh_aabb_min: CVector3, bvh_aabb_max: CVector3):
        cls.bullet().btOptimizedBvh_build(optimized_bvh, triangles, c_bool(use_quantized_aabb_compression), byref(bvh_aabb_min), byref(bvh_aabb_max))

    @classmethod
    def btQuantizedBvh_calculateSerializeBufferSize(cls, quantized_bvh: c_void_p):
        return cls.bullet().btQuantizedBvh_calculateSerializeBufferSize(quantized_bvh)

    @classmethod
    def btOptimizedBvh_serializeInPlace(cls, quantized_bvh: c_void_p, aligned_data_buffer: c_void_p, data_buffer_size: int, swap_endian: bool):
        return cls.bullet().btOptimizedBvh_serializeInPlace(quantized_bvh, aligned_data_buffer, c_uint(data_buffer_size), c_bool(swap_endian))

    @classmethod
    def btQuantizedBvh_delete(cls, quantized_bvh: c_void_p):
        cls.bullet().btQuantizedBvh_delete(quantized_bvh)
    