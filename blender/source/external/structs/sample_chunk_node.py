# !!! GENERATED USING HEIO.NET.Utils !!!
# Please do not touch manually!
import ctypes
from .. import nettypes
from ..typing import TPointer

class CSampleChunkNode(ctypes.Structure):
    name: str
    value: int
    is_data_node: bool
    child: TPointer['CSampleChunkNode']
    sibling: TPointer['CSampleChunkNode']

CSampleChunkNode._fields_ = [
    ("name", ctypes.c_wchar_p),
    ("value", ctypes.c_int),
    ("is_data_node", ctypes.c_bool),
    ("child", ctypes.POINTER(CSampleChunkNode)),
    ("sibling", ctypes.POINTER(CSampleChunkNode)),
]

