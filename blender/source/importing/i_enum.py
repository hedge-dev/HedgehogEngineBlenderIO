from ..dotnet.enum_lut import (
    WRAP_MODE,
    BULLET_PRIMITIVE_SHAPE_TYPE
)


def from_wrap_mode(enum: any):
    return WRAP_MODE[enum.ToString()]


def from_bullet_shape_type(enum: any):
    return BULLET_PRIMITIVE_SHAPE_TYPE[enum.ToString()]
