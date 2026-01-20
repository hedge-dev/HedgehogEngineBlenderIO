# !!! GENERATED USING HEIO.NET.Utils !!!
# Please do not touch manually!
import ctypes
from .. import nettypes
from ..typing import TPointer

class CTexture(ctypes.Structure):
    name: str
    picture_name: str
    tex_coord_index: int
    wrap_mode_u: int
    wrap_mode_v: int
    type: str

CTexture._fields_ = [
    ("name", ctypes.c_wchar_p),
    ("picture_name", ctypes.c_wchar_p),
    ("tex_coord_index", ctypes.c_ubyte),
    ("wrap_mode_u", ctypes.c_ubyte),
    ("wrap_mode_v", ctypes.c_ubyte),
    ("type", ctypes.c_wchar_p),
]

