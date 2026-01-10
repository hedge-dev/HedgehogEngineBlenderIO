from ctypes import Structure, c_wchar_p, c_size_t, POINTER
from .util import FieldsFromTypeHints

class CResolveInfo(Structure, metaclass=FieldsFromTypeHints):

    unresolved_files: POINTER(c_wchar_p)
    unresolved_files_size: c_size_t

    missing_dependencies: POINTER(c_wchar_p)
    missing_dependencies_size: c_size_t

    packed_dependencies: POINTER(c_wchar_p)
    packed_dependencies_size: c_size_t

    unresolved_ntsp_files: POINTER(c_wchar_p)
    unresolved_ntsp_files_size: c_size_t

    missing_streamed_images: POINTER(c_wchar_p)
    missing_streamed_images_size: c_size_t