# !!! GENERATED USING HEIO.NET.Utils !!!
# Please do not touch manually!
import ctypes
from .. import nettypes
from ..typing import TPointer

class CIntegerMaterialParameter(ctypes.Structure):
    name: str
    value: nettypes.Vector4Int

CIntegerMaterialParameter.__fields__ = [
    ("name", ctypes.c_wchar_p),
    ("value", nettypes.Vector4Int),
]

