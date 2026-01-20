# !!! GENERATED USING HEIO.NET.Utils !!!
# Please do not touch manually!
import ctypes
from .. import nettypes
from ..typing import TPointer

class CVertexWeight(ctypes.Structure):
    index: int
    weight: float

CVertexWeight.__fields__ = [
    ("index", ctypes.c_short),
    ("weight", ctypes.c_float),
]

