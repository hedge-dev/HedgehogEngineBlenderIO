from ctypes import Structure, c_wchar_p, c_void_p, c_size_t, POINTER
from .util import FieldsFromTypeHints

class CStringPointerPair(Structure, metaclass=FieldsFromTypeHints):

    name: c_wchar_p
    pointer: c_void_p

class CStringPointerPairs(Structure, metaclass=FieldsFromTypeHints):

    pairs: POINTER(CStringPointerPair)
    size: c_size_t