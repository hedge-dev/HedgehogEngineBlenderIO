# !!! GENERATED USING HEIO.NET.Utils !!!
# Please do not touch manually!
import ctypes
from .. import nettypes
from ..typing import TPointer
from .sample_chunk_node import CSampleChunkNode
from .float_material_parameter import CFloatMaterialParameter
from .integer_material_parameter import CIntegerMaterialParameter
from .bool_material_parameter import CBoolMaterialParameter
from .texture import CTexture

class CMaterial(ctypes.Structure):
    name: str
    data_version: int
    file_path: str
    root_node: TPointer['CSampleChunkNode']
    shader_name: str
    alpha_threshold: int
    no_back_face_culling: bool
    blend_mode: int
    float_parameters: TPointer['CFloatMaterialParameter']
    float_parameters_size: int
    integer_parameters: TPointer['CIntegerMaterialParameter']
    integer_parameters_size: int
    bool_parameters: TPointer['CBoolMaterialParameter']
    bool_parameters_size: int
    textures_name: str
    textures: TPointer['CTexture']
    textures_size: int

CMaterial.__fields__ = [
    ("name", ctypes.c_wchar_p),
    ("data_version", ctypes.c_uint),
    ("file_path", ctypes.c_wchar_p),
    ("root_node", ctypes.POINTER(CSampleChunkNode)),
    ("shader_name", ctypes.c_wchar_p),
    ("alpha_threshold", ctypes.c_ubyte),
    ("no_back_face_culling", ctypes.c_bool),
    ("blend_mode", ctypes.c_ubyte),
    ("float_parameters", ctypes.POINTER(CFloatMaterialParameter)),
    ("float_parameters_size", ctypes.c_size_t),
    ("integer_parameters", ctypes.POINTER(CIntegerMaterialParameter)),
    ("integer_parameters_size", ctypes.c_size_t),
    ("bool_parameters", ctypes.POINTER(CBoolMaterialParameter)),
    ("bool_parameters_size", ctypes.c_size_t),
    ("textures_name", ctypes.c_wchar_p),
    ("textures", ctypes.POINTER(CTexture)),
    ("textures_size", ctypes.c_size_t),
]

