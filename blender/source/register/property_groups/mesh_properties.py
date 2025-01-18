import bpy
from bpy.props import (
    EnumProperty,
    BoolProperty,
    IntProperty,
    StringProperty,
    FloatVectorProperty,
    PointerProperty,
    CollectionProperty
)

from .base_list import BaseList
from .sca_parameter_properties import HEIO_SCA_Parameters
from .lod_info_properties import HEIO_LODInfo
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

    if not info_set.has_value(collision_info.value):
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


class BaseMeshInfo(bpy.types.PropertyGroup):
    name: StringProperty(name="name")


class BaseMeshInfoList(BaseList):

    def _on_created(self, element, **args):
        for name, value in args.items():
            if hasattr(element, name):
                setattr(element, name, value)

    def initialize(self):
        if len(self) == 0:
            self._on_init()

        if self.attribute_name not in self.id_data.attributes:
            self.id_data.attributes.new(self.attribute_name, "INT", "FACE")

    def _on_init(self):
        self.new()

    def delete(self):
        self.clear()
        attribute = self.attribute
        if attribute is not None and not self._check_attribute_invalid(attribute):
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


############################################################


class HEIO_MeshLayer(BaseMeshInfo):
    pass


class HEIO_RenderLayerList(BaseMeshInfoList):

    elements: CollectionProperty(
        type=HEIO_MeshLayer
    )

    def _on_init(self):
        self.new(name="Opaque")
        self.new(name="Transparent")
        self.new(name="PunchThrough")

    @property
    def attribute_name(self):
        return "HEIORenderLayer"


class HEIO_CollisionLayer(bpy.types.PropertyGroup, BaseCollisionInfo):
    type = 0


class HEIO_CollisionType(bpy.types.PropertyGroup, BaseCollisionInfo):
    type = 1


class HEIO_CollisionTypeList(BaseMeshInfoList):

    elements: CollectionProperty(
        type=HEIO_CollisionType
    )

    @property
    def attribute_name(self):
        return 'HEIOCollisionType'


class HEIO_CollisionFlag(bpy.types.PropertyGroup, BaseCollisionInfo):
    type = 2


class HEIO_CollisionFlagList(BaseMeshInfoList):

    elements: CollectionProperty(
        type=HEIO_CollisionFlag
    )

    @property
    def attribute_name(self):
        return 'HEIOCollisionFlags'


############################################################


class HEIO_MeshGroup(BaseMeshInfo):

    collision_layer: PointerProperty(
        type=HEIO_CollisionLayer
    )

    is_convex_collision: BoolProperty(
        name="Is convex collision",
        description="Whether the group is a convex collision shape, and thus only uses vertices. Convex collision shapes can only have one type and the same set of flags"
    )

    convex_type: PointerProperty(
        type=HEIO_CollisionType
    )

    convex_flags: PointerProperty(
        type=HEIO_CollisionFlagList
    )


class HEIO_MeshGroupList(BaseMeshInfoList):

    elements: CollectionProperty(
        type=HEIO_MeshGroup
    )

    def copy_from(self, group):
        copy = self.new()
        copy.name = group.name
        copy.collision_layer.value = group.collision_layer.value
        copy.collision_layer.custom = group.collision_layer.custom
        copy.is_convex_collision = group.is_convex_collision
        copy.convex_type.value = group.convex_type.value
        copy.convex_type.custom = group.convex_type.custom

        for convex_flag in group.convex_flags:
            copy.convex_flags.new(
                value=convex_flag.value,
                custom=convex_flag.custom
            )

    @property
    def attribute_name(self):
        return "HEIOMeshGroup"


class HEIO_CollisionPrimitive(bpy.types.PropertyGroup):

    shape_type: EnumProperty(
        name="Shape type",
        description="The shape of the primitive",
        items=(
            ('SPHERE', "Sphere", ""),
            ('BOX', "Box", ""),
            ('CAPSULE', "Capsule", ""),
            ('CYLINDER', "Cylinder", ""),
        )
    )

    position: FloatVectorProperty(
        name="Position",
        description="Local position of the primitive",
        precision=3
    )

    rotation: FloatVectorProperty(
        name="Rotation",
        description="Local rotation of the primitive",
        default=(1, 0, 0, 0),
        size=4,
        subtype="QUATERNION",
        precision=3
    )

    dimensions: FloatVectorProperty(
        name="Dimensions",
        description="Dimensions of the primitive",
        default=(1, 1, 1),
        min=0,
        precision=3
    )

    collision_layer: PointerProperty(
        type=HEIO_CollisionLayer
    )

    collision_type: PointerProperty(
        type=HEIO_CollisionType
    )

    collision_flags: PointerProperty(
        type=HEIO_CollisionFlagList
    )


class HEIO_CollisionPrimitiveList(BaseList):

    elements: CollectionProperty(
        type=HEIO_CollisionPrimitive
    )


############################################################


class HEIO_Mesh(bpy.types.PropertyGroup):

    force_enable_8_weights: BoolProperty(
        name="Force enable 8-weight export",
        description="Force enable models to export with 8 weights instead of 4. Does not change material parameters"
    )

    force_enable_multi_tangent: BoolProperty(
        name="Force enable multi tangent export",
        description="Force enable models to export with a second tangent set (uses third UV map). Does not change material parameters"
    )

    groups: PointerProperty(
        type=HEIO_MeshGroupList
    )

    render_layers: PointerProperty(
        type=HEIO_RenderLayerList
    )

    sca_parameters: PointerProperty(
        type=HEIO_SCA_Parameters
    )

    lod_info: PointerProperty(
        type=HEIO_LODInfo
    )

    collision_types: PointerProperty(
        type=HEIO_CollisionTypeList
    )

    collision_flags: PointerProperty(
        type=HEIO_CollisionFlagList
    )

    collision_primitives: PointerProperty(
        type=HEIO_CollisionPrimitiveList
    )

    @classmethod
    def register(cls):
        bpy.types.Mesh.heio_mesh = PointerProperty(type=cls)
