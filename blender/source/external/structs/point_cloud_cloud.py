# !!! GENERATED USING HEIO.NET.Utils !!!
# Please do not touch manually!
import ctypes
from .. import nettypes
from ..typing import TPointer
from .point_cloud_point import CPointCloudPoint

class CPointCloudCloud(ctypes.Structure):
    name: str
    points: TPointer['CPointCloudPoint']
    points_size: int

CPointCloudCloud.__fields__ = [
    ("name", ctypes.c_wchar_p),
    ("points", ctypes.POINTER(CPointCloudPoint)),
    ("points_size", ctypes.c_size_t),
]

