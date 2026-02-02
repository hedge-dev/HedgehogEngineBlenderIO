from .json_util import JSONWrapper


class CollisionInfoDefinitionSet:
    value_to_item_index: list[int | None]
    item_index_to_value: list[int]

    items: list[tuple[str, str, str]]
    items_fallback: list[tuple[str, str, str]]

    def __init__(self):
        self.value_to_item_index = []
        self.item_index_to_value = []

        self.items = []
        self.items_fallback = [("ERROR_FALLBACK", "", "")]

    @staticmethod
    def parse_json_data(data):
        result = CollisionInfoDefinitionSet()

        for i, json_item in enumerate(data):
            if json_item is None:
                result.value_to_item_index.append(None)
                continue

            result.value_to_item_index.append(len(result.items))
            result.item_index_to_value.append(i)

            name = json_item["Name"]
            item = (name, name, json_item["Description"])

            result.items.append(item)
            result.items_fallback.append(item)

        return result

    def has_value(self, value: int):
        return (
            value < len(self.value_to_item_index)
            and self.value_to_item_index[value] is not None
        )


class CollisionInfoDefinition:

    layers: CollisionInfoDefinitionSet
    types: CollisionInfoDefinitionSet
    flags: CollisionInfoDefinitionSet

    def __init__(self):
        self.layers = CollisionInfoDefinitionSet()
        self.types = CollisionInfoDefinitionSet()
        self.flags = CollisionInfoDefinitionSet()

    @staticmethod
    def parse_json_data(data: JSONWrapper):
        result = CollisionInfoDefinition()

        result.layers = data.parse_property(
            "Layers", CollisionInfoDefinitionSet)
        result.types = data.parse_property("Types", CollisionInfoDefinitionSet)
        result.flags = data.parse_property("Flags", CollisionInfoDefinitionSet)

        return result
