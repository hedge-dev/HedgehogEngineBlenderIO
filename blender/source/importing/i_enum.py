from ..dotnet.enum_lut import (
    WRAP_MODE,
)

def from_wrap_mode(enum: any):
    return WRAP_MODE[enum.ToString()]