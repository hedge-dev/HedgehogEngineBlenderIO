# !!! GENERATED USING HEIO.NET.Utils !!!
# Please do not touch manually!
import ctypes
from .. import nettypes
from ..typing import TPointer
from .vertex import CVertex
from .uv_direction import CUVDirection
from .mesh_data_mesh_set_info import CMeshDataMeshSetInfo
from .mesh_data_mesh_group_info import CMeshDataMeshGroupInfo

class CMeshData(ctypes.Structure):
    name: str
    vertices: TPointer['CVertex']
    vertices_size: int
    triangle_index_count: int
    triangle_indices: TPointer['int']
    polygon_normals: TPointer['nettypes.CVector3']
    polygon_uv_directions: TPointer['CUVDirection']
    polygon_uv_directions2: TPointer['CUVDirection']
    texture_coordinates: TPointer[TPointer['nettypes.CVector2']]
    texture_coordinates_size: int
    colors: TPointer[TPointer['nettypes.CVector4']]
    colors_size: int
    mesh_sets: TPointer['CMeshDataMeshSetInfo']
    mesh_sets_size: int
    groups: TPointer['CMeshDataMeshGroupInfo']
    groups_size: int
    morph_names: TPointer['str']
    morph_names_size: int

CMeshData.__fields__ = [
    ("name", ctypes.c_wchar_p),
    ("vertices", ctypes.POINTER(CVertex)),
    ("vertices_size", ctypes.c_size_t),
    ("triangle_index_count", ctypes.c_size_t),
    ("triangle_indices", ctypes.POINTER(ctypes.c_int)),
    ("polygon_normals", ctypes.POINTER(nettypes.CVector3)),
    ("polygon_uv_directions", ctypes.POINTER(CUVDirection)),
    ("polygon_uv_directions2", ctypes.POINTER(CUVDirection)),
    ("texture_coordinates", ctypes.POINTER(ctypes.POINTER(nettypes.CVector2))),
    ("texture_coordinates_size", ctypes.c_size_t),
    ("colors", ctypes.POINTER(ctypes.POINTER(nettypes.CVector4))),
    ("colors_size", ctypes.c_size_t),
    ("mesh_sets", ctypes.POINTER(CMeshDataMeshSetInfo)),
    ("mesh_sets_size", ctypes.c_size_t),
    ("groups", ctypes.POINTER(CMeshDataMeshGroupInfo)),
    ("groups_size", ctypes.c_size_t),
    ("morph_names", ctypes.POINTER(ctypes.c_wchar_p)),
    ("morph_names_size", ctypes.c_size_t),
]

