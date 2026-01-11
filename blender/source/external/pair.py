from ctypes import Structure, c_wchar_p, c_void_p, c_size_t, POINTER
from .util import FieldsFromTypeHints

class CStringPointerPair(Structure, metaclass=FieldsFromTypeHints):

    name: c_wchar_p
    pointer: c_void_p

class CArray(Structure, metaclass=FieldsFromTypeHints):

    array: c_void_p
    size: c_size_t