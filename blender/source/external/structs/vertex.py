# !!! GENERATED USING HEIO.NET.Utils !!!
# Please do not touch manually!
import ctypes
from .. import nettypes
from ..typing import TPointer
from .uv_direction import CUVDirection
from .vertex_weight import CVertexWeight

class CVertex(ctypes.Structure):
    position: nettypes.CVector3
    normal: nettypes.CVector3
    uv_direction: CUVDirection
    uv_direction2: CUVDirection
    weights: TPointer['CVertexWeight']
    weights_size: int
    morph_positions: TPointer['nettypes.CVector3']
    morph_positions_size: int

CVertex._fields_ = [
    ("position", nettypes.CVector3),
    ("normal", nettypes.CVector3),
    ("uv_direction", CUVDirection),
    ("uv_direction2", CUVDirection),
    ("weights", ctypes.POINTER(CVertexWeight)),
    ("weights_size", ctypes.c_int),
    ("morph_positions", ctypes.POINTER(nettypes.CVector3)),
    ("morph_positions_size", ctypes.c_int),
]

