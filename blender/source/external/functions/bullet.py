import ctypes
from .. import nettypes

FUNCTIONS = {
    "btIndexedMesh_new": (
        None,
        ctypes.c_void_p
    ),
    "btIndexedMesh_setIndexType": (
        (
            ctypes.c_void_p, 
            ctypes.c_int
        ),
        None
    ),
    "btIndexedMesh_setNumTriangles": (
        (
            ctypes.c_void_p, 
            ctypes.c_int
        ),
        None
    ),
    "btIndexedMesh_setNumVertices": (
        (
            ctypes.c_void_p, 
            ctypes.c_int
        ),
        None
    ),
    "btIndexedMesh_setTriangleIndexBase": (
        (
            ctypes.c_void_p, 
            ctypes.c_void_p
        ),
        None
    ),
    "btIndexedMesh_setTriangleIndexStride": (
        (
            ctypes.c_void_p, 
            ctypes.c_int
        ),
        None
    ),
    "btIndexedMesh_setVertexBase": (
        (
            ctypes.c_void_p, 
            ctypes.c_void_p
        ),
        None
    ),
    "btIndexedMesh_setVertexStride": (
        (
            ctypes.c_void_p, 
            ctypes.c_int
        ),
        None
    ),
    "btIndexedMesh_setVertexType": (
        (
            ctypes.c_void_p, 
            ctypes.c_int
        ),
        None
    ),
    "btIndexedMesh_delete": (
        (
            ctypes.c_void_p,
        ),
        None
    ),
    "btTriangleIndexVertexArray_new": (
        None,
        ctypes.c_void_p
    ),
    "btTriangleIndexVertexArray_addIndexedMesh": (
        (
            ctypes.c_void_p,
            ctypes.c_void_p, 
            ctypes.c_int
        ),
        None
    ),
    "btStridingMeshInterface_delete": (
        (
            ctypes.c_void_p, 
        ),
        None
    ),
    "btOptimizedBvh_new": (
        None,
        ctypes.c_void_p
    ),
    "btOptimizedBvh_build": (
        (
            ctypes.c_void_p, 
            ctypes.c_void_p, 
            ctypes.c_bool, 
            ctypes.POINTER(nettypes.CVector3), 
            ctypes.POINTER(nettypes.CVector3)
        ),
        None
    ),
    "btQuantizedBvh_calculateSerializeBufferSize": (
        (
            ctypes.c_void_p,
        ),
        ctypes.c_int
    ),
    "btOptimizedBvh_serializeInPlace": (
        (
            ctypes.c_void_p, 
            ctypes.c_void_p, 
            ctypes.c_uint, 
            ctypes.c_bool
        ),
        ctypes.c_bool
    ),
    "btQuantizedBvh_delete": (
        (
            ctypes.c_void_p, 
        ),
        None
    ),
}
