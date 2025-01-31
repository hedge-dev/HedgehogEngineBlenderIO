from ..dotnet.enum_lut import (
    WRAP_MODE,
    BULLET_PRIMITIVE_SHAPE_TYPE,
    MATERIAL_BLEND_MODE
)


def from_wrap_mode(enum: any):
    return WRAP_MODE[enum.ToString()]


def from_bullet_shape_type(enum: any):
    return BULLET_PRIMITIVE_SHAPE_TYPE[enum.ToString()]


def from_material_blend_mode(enum: any):
    return MATERIAL_BLEND_MODE[enum.ToString()]
