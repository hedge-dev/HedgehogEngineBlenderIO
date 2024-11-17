import bpy
from bpy.props import (
	StringProperty,
	IntProperty,
	FloatProperty,
	BoolProperty,
	EnumProperty,
	CollectionProperty
)

from .base_list import BaseList

from ctypes import(
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