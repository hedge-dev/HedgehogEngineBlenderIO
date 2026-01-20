# !!! GENERATED USING HEIO.NET.Utils !!!
# Please do not touch manually!
import ctypes
from .. import nettypes
from ..typing import TPointer

class CBoolMaterialParameter(ctypes.Structure):
    name: str
    value: bool

CBoolMaterialParameter.__fields__ = [
    ("name", ctypes.c_wchar_p),
    ("value", ctypes.c_bool),
]

