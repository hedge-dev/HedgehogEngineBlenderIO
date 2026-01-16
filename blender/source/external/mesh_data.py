from ctypes import Structure, c_ubyte, c_int, c_uint, c_short, c_float, c_bool, c_wchar_p, c_size_t, POINTER
from .util import FieldsFromTypeHints
from .math import CVector2, CVector3, CVector4, CMatrix
from .pair import CStringPointerPair
from .sample_chunk_node import CSampleChunkNode

class CUVDirection(Structure, metaclass=FieldsFromTypeHints):
    tangent: CVector3
    binormal: CVector3

class CVertexWeight(Structure, metaclass=FieldsFromTypeHints):
    index: c_short
    weight: c_float

class CVertex(Structure, metaclass=FieldsFromTypeHints):
    
    position: CVector3
    normal: CVector3
    uv_direction: CUVDirection
    uv_direction2: CUVDirection

    weights: POINTER(CVertexWeight)
    weights_size: c_size_t

    morph_positions: POINTER(CVector3)
    morph_positions_size: c_size_t

class CMeshDataMeshSetInfo(Structure, metaclass=FieldsFromTypeHints):
    use_byte_colors: c_bool
    enable_8_weights: c_bool
    enable_multi_tangent: c_bool
    material_reference: CStringPointerPair
    mesh_slot_type: c_uint
    mesh_slot_name: c_wchar_p
    size: c_int

class CMeshDataGroupInfo(Structure, metaclass=FieldsFromTypeHints):
    name: c_wchar_p
    size: c_int

class CMeshData(Structure, metaclass=FieldsFromTypeHints):
    name: c_wchar_p

    vertices: POINTER(CVertex)
    vertices_size: c_size_t

    triangle_index_count: c_size_t

    triangle_indices: POINTER(c_int)
    polygon_normals: POINTER(CVector3)
    polygon_uv_directions: POINTER(CUVDirection)
    polygon_uv_directions_2: POINTER(CUVDirection)

    texture_coordinates: POINTER(POINTER(CVector2))
    texture_coordinates_size: c_size_t

    colors: POINTER(POINTER(CVector4))
    colors_size: c_size_t

    mesh_sets: POINTER(CMeshDataMeshSetInfo)
    mesh_sets_size: c_size_t

    groups: POINTER(CMeshDataGroupInfo)
    groups_size: c_size_t

    morph_names: POINTER(c_wchar_p)
    morph_names_size: c_size_t

class CModelNode(Structure, metaclass=FieldsFromTypeHints):
    name: c_wchar_p
    parent_index: c_int
    transform: CMatrix

class CMeshDataSet(Structure, metaclass=FieldsFromTypeHints):
    name: c_wchar_p
    is_terrain: c_bool
    mesh_data: POINTER(POINTER(CMeshData))
    mesh_data_size: c_size_t
    nodes: POINTER(CModelNode)
    nodes_size: c_size_t
    sample_chunk_node_root: POINTER(CSampleChunkNode)

class CLODItem(Structure, metaclass=FieldsFromTypeHints):
    cascade_flag: c_int
    unknown2: c_float
    cascade_level: c_ubyte

class CModelSet(Structure, metaclass=FieldsFromTypeHints):
    mesh_data_sets: POINTER(CMeshDataSet)
    mesh_data_sets_size: c_size_t

    lod_items: POINTER(CLODItem)
    lod_items_size: c_size_t
    lod_unknown1: c_ubyte