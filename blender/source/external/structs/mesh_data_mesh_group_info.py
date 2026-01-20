# !!! GENERATED USING HEIO.NET.Utils !!!
# Please do not touch manually!
import ctypes
from .. import nettypes
from ..typing import TPointer

class CMeshDataMeshGroupInfo(ctypes.Structure):
    name: str
    size: int

CMeshDataMeshGroupInfo.__fields__ = [
    ("name", ctypes.c_wchar_p),
    ("size", ctypes.c_int),
]

