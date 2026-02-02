# !!! GENERATED USING HEIO.NET.Utils !!!
# Please do not touch manually!
import ctypes
from .. import nettypes
from ..typing import TPointer
from .mesh_data_set import CMeshDataSet
from .lod_item import CLODItem

class CModelSet(ctypes.Structure):
    mesh_data_sets: TPointer[TPointer['CMeshDataSet']]
    mesh_data_sets_size: int
    lod_items: TPointer['CLODItem']
    lod_items_size: int
    lod_unknown1: int

CModelSet._fields_ = [
    ("mesh_data_sets", ctypes.POINTER(ctypes.POINTER(CMeshDataSet))),
    ("mesh_data_sets_size", ctypes.c_int),
    ("lod_items", ctypes.POINTER(CLODItem)),
    ("lod_items_size", ctypes.c_int),
    ("lod_unknown1", ctypes.c_ubyte),
]

