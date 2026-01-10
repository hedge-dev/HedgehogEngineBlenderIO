from ctypes import Structure, c_wchar_p, c_byte, c_size_t, POINTER
from .util import FieldsFromTypeHints

class CImage(Structure, metaclass=FieldsFromTypeHints):

    file_path: c_wchar_p
    streamed_data: POINTER(c_byte)
    streamed_data_size: c_size_t
