import bpy
from bpy.props import (
    StringProperty,
    IntProperty,
    FloatProperty,
    BoolProperty,
    EnumProperty,
    CollectionProperty,
    PointerProperty
)

from .base_list import BaseList
from .. import definitions

from ctypes import (
    c_int32,
    c_float,
    cast,
    pointer,
    POINTER,
)


def _get_float_value(self):
    return cast(pointer(c_int32(self.value)), POINTER(c_float)).contents.value


def _set_float_value(self, value):
    self.value = cast(pointer(c_float(value)), POINTER(c_int32)).contents.value


def _get_boolean_value(self):
    return self.value != 0


def _set_booleam_value(self, value):
    self.value = 1 if value else 0


class HEIO_SCA_Parameter(bpy.types.PropertyGroup):

    name: StringProperty(
        name="Name",
        maxlen=8
    )

    value_type: EnumProperty(
        name="Type",
        items=(
            ('INTEGER', "Integer", ""),
            ('FLOAT', "Float", ""),
            ('BOOLEAN', "Boolean", ""),
        ),
        default='INTEGER'
    )

    value: IntProperty(
        name="Value"
    )

    float_value: FloatProperty(
        name="Value",
        precision=3,
        get=_get_float_value,
        set=_set_float_value
    )

    boolean_value: BoolProperty(
        name="Value",
        get=_get_boolean_value,
        set=_set_booleam_value
    )


class HEIO_SCA_Parameters(BaseList):

    elements: CollectionProperty(
        type=HEIO_SCA_Parameter
    )


##################################################

FALLBACK_SCA_PARAMETER_ITEMS = [("ERROR_FALLBACK", "No Presets", "")]


def _get_sca_parameter_def(properties, context: bpy.types.Context):
    target_def = definitions.get_target_definition(context)
    if target_def is None or target_def.sca_parameters is None:
        return None

    if properties.mode == 'MATERIAL':
        result = target_def.sca_parameters.material
    elif properties.mode == 'MODEL':
        result = target_def.sca_parameters.model
    else:
        return None

    return result


def _get_sca_parameter_items(properties, context: bpy.types.Context):
    param_def = _get_sca_parameter_def(properties, context)

    if param_def is not None:
        return param_def.items

    return FALLBACK_SCA_PARAMETER_ITEMS


def _get_sca_parameter_value_name_enum(properties):
    param_def = _get_sca_parameter_def(properties, bpy.context)

    if param_def is None or properties.value_name not in param_def.infos:
        return 0

    param_info = param_def.infos.get(properties.value_name, None)
    if param_info is None:
        return 0

    return param_info.index


def _set_sca_parameter_value_name_enum(properties, enum_index):
    if not properties.use_preset:
        return

    param_def = _get_sca_parameter_def(properties, bpy.context)
    if param_def is None:
        return

    properties.value_name = param_def.items[enum_index][0]


def _update_sca_parameter_type(properties, context):
    if not properties.use_preset:
        return

    param_def = _get_sca_parameter_def(properties, context)
    if param_def is None:
        return

    if properties.value_name not in param_def.infos:
        properties.value_name = param_def.items[0][0]

    param_info = param_def.infos.get(properties.value_name, None)
    if param_info is None:
        return

    if properties.value_type != param_info.parameter_type.name:
        properties.value_type = param_info.parameter_type.name


class HEIO_SCAP_MassEdit(bpy.types.PropertyGroup):

    mode: EnumProperty(
        name="Mode",
        items=(
            ('MODEL', "Model", ""),
            ('MATERIAL', "Material", "")
        ),
        default='MODEL',
        update=_update_sca_parameter_type
    )

    use_preset: BoolProperty(
        name="Use Preset",
        update=_update_sca_parameter_type
    )

    value_name: StringProperty(
        name="Name",
        maxlen=8
    )

    value_name_enum: EnumProperty(
        name="Preset",
        items=_get_sca_parameter_items,
        get=_get_sca_parameter_value_name_enum,
        set=_set_sca_parameter_value_name_enum,
        update=_update_sca_parameter_type
    )

    value_type: EnumProperty(
        name="Type",
        items=(
            ('INTEGER', "Integer", ""),
            ('FLOAT', "Float", ""),
            ('BOOLEAN', "Boolean", ""),
        ),
        update=_update_sca_parameter_type,
        default='INTEGER'
    )

    value: IntProperty(
        name="Value"
    )

    float_value: FloatProperty(
        name="Value",
        precision=3,
        get=_get_float_value,
        set=_set_float_value
    )

    boolean_value: BoolProperty(
        name="Value",
        get=_get_boolean_value,
        set=_set_booleam_value
    )

    @classmethod
    def register(cls):
        bpy.types.Scene.heio_scap_massedit = PointerProperty(type=cls)
