import os
import bpy

from . import target_info
from .json_util import HEIOJSONException
from ...utility import general
from ...exceptions import HEIOException

TARGET_DEFINITIONS: dict[str, target_info.TargetDefinition] = None
TARGET_ENUM_ITEMS: list[tuple[str, str, str]] = None
TARGET_ENUM_ITEMS_INVALID: list[tuple[str, str, str]] = None


def register_definition(directory: str, identifier: str | None = None):
    if identifier is None:
        identifier = os.path.basename(directory)

    try:
        target_definition = target_info.TargetDefinition.from_directory(
            directory, identifier)
        TARGET_DEFINITIONS[target_definition.identifier] = target_definition

    except HEIOException as exception:
        print(f"Failed to register target \"{identifier}\"")
        if isinstance(exception, HEIOJSONException):
            print(f"Error at " + exception.get_json_path())
        print(exception)
        return

    target_item = (
        target_definition.identifier,
        target_definition.name,
        target_definition.description
    )

    TARGET_ENUM_ITEMS.append(target_item)
    TARGET_ENUM_ITEMS_INVALID.append(target_item)


def load_definitions():
    global TARGET_DEFINITIONS
    global TARGET_ENUM_ITEMS
    global TARGET_ENUM_ITEMS_INVALID

    TARGET_DEFINITIONS = {}
    TARGET_ENUM_ITEMS = []
    TARGET_ENUM_ITEMS_INVALID = [("ERROR_FALLBACK", "", "")]

    definitions_path = os.path.join(general.get_path(), "Definitions")
    for root, directories, _ in os.walk(definitions_path):
        for directory in directories:
            register_definition(os.path.join(root, directory))


def get_target_definition(context: bpy.types.Context | None):
    if context is None:
        context = bpy.context

    target_game = context.scene.heio_scene.target_game
    if target_game not in TARGET_DEFINITIONS:
        raise HEIOException(f"Target game \"{target_game}\" is not defined")

    return TARGET_DEFINITIONS[target_game]
