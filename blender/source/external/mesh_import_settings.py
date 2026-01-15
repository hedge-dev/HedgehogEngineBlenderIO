from ctypes import Structure, c_uint, c_float, c_bool
from .util import FieldsFromTypeHints

class CMeshImportSettings(Structure, metaclass=FieldsFromTypeHints):
    vertex_merge_mode: c_uint
    merge_distance: c_float
    merge_split_edges: c_bool
    
    merge_collision_vertices: c_bool
    collision_vertex_merge_distance: c_float
    remove_unused_collision_vertices: c_bool
