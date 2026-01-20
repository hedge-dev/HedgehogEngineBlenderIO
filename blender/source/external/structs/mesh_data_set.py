# !!! GENERATED USING HEIO.NET.Utils !!!
# Please do not touch manually!
import ctypes
from .. import nettypes
from ..typing import TPointer
from .mesh_data import CMeshData
from .model_node import CModelNode
from .sample_chunk_node import CSampleChunkNode

class CMeshDataSet(ctypes.Structure):
    name: str
    mesh_data: TPointer['CMeshData']
    mesh_data_size: int
    nodes: TPointer['CModelNode']
    nodes_size: int
    sample_chunk_node_root: TPointer['CSampleChunkNode']

CMeshDataSet.__fields__ = [
    ("name", ctypes.c_wchar_p),
    ("mesh_data", ctypes.POINTER(CMeshData)),
    ("mesh_data_size", ctypes.c_size_t),
    ("nodes", ctypes.POINTER(CModelNode)),
    ("nodes_size", ctypes.c_size_t),
    ("sample_chunk_node_root", ctypes.POINTER(CSampleChunkNode)),
]

