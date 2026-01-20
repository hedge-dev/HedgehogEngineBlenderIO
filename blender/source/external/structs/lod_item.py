# !!! GENERATED USING HEIO.NET.Utils !!!
# Please do not touch manually!
import ctypes
from .. import nettypes
from ..typing import TPointer

class CLODItem(ctypes.Structure):
    cascade_flag: int
    unknown2: float
    cascade_level: int

CLODItem.__fields__ = [
    ("cascade_flag", ctypes.c_int),
    ("unknown2", ctypes.c_float),
    ("cascade_level", ctypes.c_ubyte),
]

