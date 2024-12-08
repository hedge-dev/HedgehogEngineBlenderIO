from ..dotnet.enum_lut import (
    WRAP_MODE,
    VERTEX_MERGE_MODE
)

from ..dotnet import SharpNeedle, HEIO_NET

def to_wrap_mode(wrap_mode: str):
    return getattr(SharpNeedle.WRAP_MODE, WRAP_MODE[wrap_mode])

def to_vertex_merge_mode(vertex_merge_mode: str):
    return getattr(HEIO_NET.VERTEX_MERGE_MODE, VERTEX_MERGE_MODE[vertex_merge_mode])