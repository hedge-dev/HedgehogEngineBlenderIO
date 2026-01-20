# !!! GENERATED USING HEIO.NET.Utils !!!
# Please do not touch manually!
import ctypes
from .. import nettypes
from ..typing import TPointer

class CUVDirection(ctypes.Structure):
    tangent: nettypes.CVector3
    binormal: nettypes.CVector3

CUVDirection.__fields__ = [
    ("tangent", nettypes.CVector3),
    ("binormal", nettypes.CVector3),
]

