# !!! GENERATED USING HEIO.NET.Utils !!!
# Please do not touch manually!
import ctypes
from .. import nettypes
from ..typing import TPointer

class CModelNode(ctypes.Structure):
    name: str
    parent_index: int
    transform: nettypes.CMatrix

CModelNode._fields_ = [
    ("name", ctypes.c_wchar_p),
    ("parent_index", ctypes.c_int),
    ("transform", nettypes.CMatrix),
]

