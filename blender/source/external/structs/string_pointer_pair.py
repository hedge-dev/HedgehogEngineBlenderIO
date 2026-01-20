# !!! GENERATED USING HEIO.NET.Utils !!!
# Please do not touch manually!
import ctypes
from .. import nettypes
from ..typing import TPointer

class CStringPointerPair(ctypes.Structure):
    name: str
    pointer: ctypes.c_void_p

CStringPointerPair.__fields__ = [
    ("name", ctypes.c_wchar_p),
    ("pointer", ctypes.c_void_p),
]

