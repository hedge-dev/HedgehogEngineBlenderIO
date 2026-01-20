# !!! GENERATED USING HEIO.NET.Utils !!!
# Please do not touch manually!
import ctypes
from .. import nettypes
from ..typing import TPointer

class CMeshImportSettings(ctypes.Structure):
    vertex_merge_mode: int
    merge_distance: float
    merge_split_edges: bool
    merge_collision_vertices: bool
    collision_vertex_merge_distance: float
    remove_unused_collision_vertices: bool

CMeshImportSettings._fields_ = [
    ("vertex_merge_mode", ctypes.c_uint),
    ("merge_distance", ctypes.c_float),
    ("merge_split_edges", ctypes.c_bool),
    ("merge_collision_vertices", ctypes.c_bool),
    ("collision_vertex_merge_distance", ctypes.c_float),
    ("remove_unused_collision_vertices", ctypes.c_bool),
]

