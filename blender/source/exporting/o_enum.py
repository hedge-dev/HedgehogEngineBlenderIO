from ..dotnet.enum_lut import (
    WRAP_MODE,
)

from ..dotnet import SharpNeedle

def to_wrap_mode(wrap_mode: str):
    return getattr(SharpNeedle.WRAP_MODE, WRAP_MODE[wrap_mode])