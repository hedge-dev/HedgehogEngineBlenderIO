from ctypes import Structure, c_float, c_int
from .util import FieldsFromTypeHints

class CVector3(Structure, metaclass=FieldsFromTypeHints):
    x: c_float
    y: c_float
    z: c_float

class CVector4(Structure, metaclass=FieldsFromTypeHints):
    x: c_float
    y: c_float
    z: c_float
    w: c_float

class CVector4Int(Structure, metaclass=FieldsFromTypeHints):
    x: c_int
    y: c_int
    z: c_int
    w: c_int

class CQuaternion(Structure, metaclass=FieldsFromTypeHints):
    x: c_float
    y: c_float
    z: c_float
    w: c_float

class CMatrix(Structure, metaclass=FieldsFromTypeHints):
    m11: c_float
    m12: c_float
    m13: c_float
    m14: c_float
    m21: c_float
    m22: c_float
    m23: c_float
    m24: c_float
    m31: c_float
    m32: c_float
    m33: c_float
    m34: c_float
    m41: c_float
    m42: c_float
    m43: c_float
    m44: c_float


