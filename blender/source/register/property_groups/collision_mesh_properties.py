import bpy
from bpy.props import (
    EnumProperty,
    BoolProperty,
    IntProperty,
    PointerProperty,
    CollectionProperty
)

from .base_list import BaseList
from .. import definitions

ITEM_ERROR_FALLBACK = [("ERROR_FALLBACK", "", "")]


def _get_collision_info_set(context: bpy.types.Context, type: int):
    target_definition = definitions.get_target_definition(context)

    if target_definition is None or target_definition.collision_info is None:
        return None

    ci = target_definition.collision_info

    if type == 0:
        return ci.layers
    elif type == 1:
        return ci.types
    else:  # type == 2
        return ci.flags


def _get_items(collision_info, context: bpy.types.Context):
    info_set = _get_collision_info_set(context, collision_info.type)

    if info_set is None:
        return ITEM_ERROR_FALLBACK

    if info_set.has_value(collision_info.value):
        return info_set.items

    result = info_set.items_fallback
    result[0] = ("ERROR_FALLBACK", f"Custom: {collision_info.value}", "")
    return result


def _get_item(collision_info):
    info_set = _get_collision_info_set(bpy.context, collision_info.type)

    if info_set is None or not info_set.has_value(collision_info.value):
        return 0

    return info_set.value_to_item_index[collision_info.value]


def _set_item(collision_info, enum_index):
    if collision_info.custom:
        return

    info_set = _get_collision_info_set(bpy.context, collision_info.type)

    if info_set is None:
        return

    prev_value = collision_info.value

    if not info_set.has_value(prev_value):
        enum_index -= 1

    collision_info.value = info_set.item_index_to_value[enum_index]


class BaseCollisionInfo:

    custom: BoolProperty(
        name="Use custom value"
    )

    value_enum: EnumProperty(
        name="Value",
        items=_get_items,
        get=_get_item,
        set=_set_item
    )

    value: IntProperty(
        name="Value",
        min=0
    )


class BaseCollisionInfoList(BaseList):

    def _on_created(self, element, **args):
        if "value" in args:
            element.value = args["value"]

    def initialize(self):
        if len(self) == 0:
            self.new()

        if self.attribute_name not in self.id_data.attributes:
            self.id_data.attributes.new(self.attribute_name, "INT", "FACE")

    def delete(self):
        self.clear()
        attribute = self.attribute
        if not self._check_attribute_invalid(attribute):
            self.id_data.attributes.remove(attribute)

    @staticmethod
    def _check_attribute_invalid(attribute: bpy.types.Attribute | None):
        return attribute is not None and (attribute.domain != 'FACE' or attribute.data_type != 'INT')

    @property
    def initialized(self):
        return len(self) > 0 and self.attribute_name in self.id_data.attributes

    @property
    def attribute_name(self):
        return None

    @property
    def attribute(self):
        return self.id_data.attributes.get(self.attribute_name, None)

    @property
    def attribute_invalid(self):
        return self._check_attribute_invalid(self.attribute)


class HEIO_CollisionType(bpy.types.PropertyGroup, BaseCollisionInfo):
    type = 1


class HEIO_CollisionTypeList(BaseCollisionInfoList):

    elements: CollectionProperty(
        type=HEIO_CollisionType
    )

    @property
    def attribute_name(self):
        return 'HEIOCollisionType'


class HEIO_CollisionFlag(bpy.types.PropertyGroup, BaseCollisionInfo):
    type = 2


class HEIO_CollisionFlagList(BaseCollisionInfoList):

    elements: CollectionProperty(
        type=HEIO_CollisionFlag
    )

    @property
    def attribute_name(self):
        return 'HEIOCollisionFlags'


class HEIO_CollisionLayer(bpy.types.PropertyGroup, BaseCollisionInfo):
    type = 0

    is_convex: BoolProperty(
        name="Is Convex",
        description="Whether the layer is convex, and thus only uses vertices. Convex shapes can only have one type and the same set of flags"
    )

    convex_type: PointerProperty(
        type=HEIO_CollisionType
    )

    convex_flags: PointerProperty(
        type=HEIO_CollisionFlagList
    )


class HEIO_CollisionLayerList(BaseCollisionInfoList):

    elements: CollectionProperty(
        type=HEIO_CollisionLayer
    )

    @property
    def attribute_name(self):
        return 'HEIOCollisionLayer'


class HEIO_CollisionMesh(bpy.types.PropertyGroup):

    layers: PointerProperty(
        type=HEIO_CollisionLayerList
    )

    types: PointerProperty(
        type=HEIO_CollisionTypeList
    )

    flags: PointerProperty(
        type=HEIO_CollisionFlagList
    )

    @classmethod
    def register(cls):
        bpy.types.Mesh.heio_collision_mesh = PointerProperty(type=cls)
