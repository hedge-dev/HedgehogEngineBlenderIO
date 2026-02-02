# !!! GENERATED USING HEIO.NET.Utils !!!
# Please do not touch manually!
import ctypes
from .. import nettypes
from ..typing import TPointer

class CPointCloudPoint(ctypes.Structure):
    instance_name: str
    resource_index: int
    position: nettypes.CVector3
    rotation: nettypes.CVector3
    scale: nettypes.CVector3

CPointCloudPoint._fields_ = [
    ("instance_name", ctypes.c_wchar_p),
    ("resource_index", ctypes.c_int),
    ("position", nettypes.CVector3),
    ("rotation", nettypes.CVector3),
    ("scale", nettypes.CVector3),
]

