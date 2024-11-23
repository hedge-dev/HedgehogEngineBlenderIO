from enum import Enum
from .json_util import HEIOJSONException, JSONWrapper
from ...exceptions import HEIOException


class ShaderLayer(Enum):
    OPAQUE = 1
    TRANSPARENT = 2
    PUNCHTHROUGH = 3
    SPECIAL = 4

    @staticmethod
    def parse_json_data(data: str):
        if data == 'Opaque':
            return ShaderLayer.OPAQUE
        elif data == 'Transparent':
            return ShaderLayer.TRANSPARENT
        elif data == 'PunchThrough':
            return ShaderLayer.PUNCHTHROUGH
        elif data == 'Special':
            return ShaderLayer.SPECIAL
        else:
            raise HEIOJSONException(
                f"Invalid shader layer \"{data}\"")


class ShaderParameterType(Enum):
    FLOAT = 1
    COLOR = 2
    BOOLEAN = 3

    @staticmethod
    def parse_json_data(data: str):
        if data == 'Color':
            return ShaderParameterType.COLOR
        elif data == 'Float':
            return ShaderParameterType.FLOAT
        elif data == 'Boolean':
            return ShaderParameterType.BOOLEAN
        else:
            raise HEIOJSONException(
                f"Invalid shader parameter type \"{data}\"")


class ShaderParameter:

    name: str
    type: ShaderParameterType
    default: any

    def __init__(self, name: str, type: ShaderParameterType, default: any):
        self.name = name
        self.type = type
        self.default = default

    @staticmethod
    def parse_json_data(data: JSONWrapper):
        type = data.parse_property("Type", ShaderParameterType)

        default = data["Default"]
        if type in [ShaderParameterType.FLOAT, ShaderParameterType.COLOR]:
            default = (default[0], default[1], default[2], default[3])
        elif type == ShaderParameterType.BOOLEAN:
            pass

        return ShaderParameter(data.identifier, type, default)


class ShaderDefinition:

    name: str
    all_items_index: int
    visible_items_index: int

    hide: bool
    layer: ShaderLayer
    variants: list[str]
    parameters: dict[str, ShaderParameter]
    textures: list[str]

    variant_items: list[tuple[str, str, str]]
    variant_items_fallback: list[tuple[str, str, str]]

    def __init__(self, name: str, all_items_index: int, visible_items_index: int):
        self.name = name
        self.all_items_index = all_items_index
        self.visible_items_index = visible_items_index

        self.hide = False
        self.layer = ShaderLayer.OPAQUE
        self.variants = []
        self.parameters = {}
        self.textures = []

        self.variant_items = None
        self.variant_items_fallback = None

    @staticmethod
    def parse_json_data(
            data: JSONWrapper,
            all_items_index: int = -1,
            visible_items_index: int = -1,
            base: 'ShaderDefinition | None' = None) -> 'ShaderDefinition':

        result = ShaderDefinition(
            data.identifier, all_items_index, visible_items_index)

        if base is not None:
            result.layer = base.layer
            result.hide = base.hide
            result.variants.extend(base.variants)
            result.parameters.update(base.parameters)
            result.textures.extend(base.textures)

        result.hide = data.get_item_fallback("Hide", result.hide)
        result.variants.extend(data.get_item_fallback("Variants", []))
        result.textures.extend(data.get_item_fallback("Textures", []))

        if result.hide:
            result.visible_items_index = -1

        if "Layer" in data:
            result.layer = data.parse_property("Layer", ShaderLayer)

        if "Parameters" in data:
            for key, value in data["Parameters"]:
                result.parameters[key] = value.parse(ShaderParameter)

        if len(result.variants) > 0:
            result.variant_items = []
            result.variant_items_fallback = [("ERROR_FALLBACK", "", "")]

            for variant in result.variants:
                if len(variant) == 0:
                    variant_item = ("/", "", "")
                else:
                    variant_item = (variant, variant, "")

                result.variant_items.append(variant_item)
                result.variant_items_fallback.append(variant_item)

        return result


class ShaderDefinitionCollection:

    definitions: dict[str, ShaderDefinition]

    items_visible: list[tuple[str, str, str]]
    items_visible_fallback: list[tuple[str, str, str]]
    items_all: list[tuple[str, str, str]]
    items_all_fallback: list[tuple[str, str, str]]

    def __init__(self):
        self.definitions = {}
        self.items_visible = []
        self.items_visible_fallback = [("ERROR_FALLBACK", "", "")]
        self.items_all = []
        self.items_all_fallback = [("ERROR_FALLBACK", "", "")]

    @staticmethod
    def parse_json_data(data: JSONWrapper):
        result = ShaderDefinitionCollection()

        base_definition = None
        if "" in data:
            base_definition = data.parse_property("", ShaderDefinition)

        for key, value in data:
            if key == "":
                continue

            definition = value.parse(
                ShaderDefinition,
                all_items_index=len(result.items_all),
                visible_items_index=len(result.items_visible),
                base=base_definition)

            item = (key, key, "")

            result.definitions[key] = definition
            result.items_all.append(item)
            result.items_all_fallback.append(item)

            if not definition.hide:
                result.items_visible.append(item)
                result.items_visible_fallback.append(item)

        return result
