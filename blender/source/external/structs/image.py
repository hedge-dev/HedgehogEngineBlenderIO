# !!! GENERATED USING HEIO.NET.Utils !!!
# Please do not touch manually!
import ctypes
from .. import nettypes
from ..typing import TPointer

class CImage(ctypes.Structure):
    file_path: str
    streamed_data: TPointer['int']
    streamed_data_size: int

CImage._fields_ = [
    ("file_path", ctypes.c_wchar_p),
    ("streamed_data", ctypes.POINTER(ctypes.c_ubyte)),
    ("streamed_data_size", ctypes.c_size_t),
]

