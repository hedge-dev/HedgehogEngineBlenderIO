from ctypes import Structure, c_bool, c_int, c_wchar_p, POINTER

from .typing import TPointer


class CSampleChunkNode(Structure):
    name: c_wchar_p
    value: c_int
    is_data_node: c_bool
    child: TPointer['CSampleChunkNode']
    sibling: TPointer['CSampleChunkNode']

CSampleChunkNode._fields_ = [
    ("name", c_wchar_p),
    ("value", c_int),
    ("is_data_node", c_bool),
    ("child", POINTER(CSampleChunkNode)),
    ("sibling", POINTER(CSampleChunkNode))
]