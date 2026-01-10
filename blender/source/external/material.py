from ctypes import Structure, c_uint, c_bool, c_wchar_p, c_byte, c_size_t, POINTER
from .util import FieldsFromTypeHints
from .math import CVector4, CVector4Int

class CFloatMaterialParameter(Structure, metaclass=FieldsFromTypeHints):
    name: c_wchar_p
    value: CVector4

class CIntegerMaterialParameter(Structure, metaclass=FieldsFromTypeHints):
    name: c_wchar_p
    value: CVector4Int

class CBoolMaterialParameter(Structure, metaclass=FieldsFromTypeHints):
    name: c_wchar_p
    value: c_bool

class CTexture(Structure, metaclass=FieldsFromTypeHints):
    name: c_wchar_p
    picture_name: c_wchar_p
    texcoord_index: c_byte
    wrap_mode_u: c_byte
    wrap_mode_v: c_byte
    type: c_wchar_p

class CMaterial(Structure, metaclass=FieldsFromTypeHints):
    name: c_wchar_p
    data_version: c_uint
    file_path: c_wchar_p
    
    shader_name: c_wchar_p
    alpha_threshold: c_byte
    no_back_face_culling: c_bool
    blend_mode: c_byte

    float_parameters: POINTER(CFloatMaterialParameter)
    float_parameters_size: c_size_t

    integer_parameters: POINTER(CIntegerMaterialParameter)
    integer_parameters_size: c_size_t

    bool_parameters: POINTER(CBoolMaterialParameter)
    bool_parameters_size: c_size_t

    textures_name: c_wchar_p
    textures: POINTER(CTexture)
    textures_size: c_size_t