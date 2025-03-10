from ..dotnet.enum_lut import (
    WRAP_MODE,
    VERTEX_MERGE_MODE,
    BULLET_PRIMITIVE_SHAPE_TYPE,
    TOPOLOGY,
    MATERIAL_BLEND_MODE,
    MODEL_VERSION_MODE
)

from ..dotnet import SharpNeedle, HEIO_NET


def to_wrap_mode(wrap_mode: str):
    return getattr(SharpNeedle.WRAP_MODE, WRAP_MODE[wrap_mode])


def to_vertex_merge_mode(vertex_merge_mode: str):
    return getattr(HEIO_NET.VERTEX_MERGE_MODE, VERTEX_MERGE_MODE[vertex_merge_mode])


def to_bullet_primitive_shape_type(bullet_primitive_shape_type: str):
    return getattr(
        SharpNeedle.BULLET_PRIMITIVE_SHAPE_TYPE,
        BULLET_PRIMITIVE_SHAPE_TYPE[bullet_primitive_shape_type]
    )


def to_topology(topology: str):
    return getattr(
        HEIO_NET.TOPOLOGY,
        TOPOLOGY[topology]
    )

def to_material_blend_mode(blend_mode: str):
    return getattr(
        SharpNeedle.MATERIAL_BLEND_MODE,
        MATERIAL_BLEND_MODE[blend_mode]
    )

def to_model_version_mode(model_version_mode: str):
    return getattr(
        HEIO_NET.MODEL_VERSION_MODE,
        MODEL_VERSION_MODE[model_version_mode]
    )