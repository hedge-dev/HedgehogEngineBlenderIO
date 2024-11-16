import os
import bpy

from os.path import dirname

from ..register.property_groups.addon_preferences import HEIO_AddonPreferences

ADDON_DIR = dirname(dirname(dirname(os.path.realpath(__file__))))
ADDON_NAME = os.path.basename(ADDON_DIR)


def get_path():
    return ADDON_DIR


def get_name():
    return ADDON_NAME


def compare_path(a: str, b: str):
    absolute = bpy.path.abspath(b)
    absolute = os.path.abspath(absolute)
    return a == absolute

def get_addon_preferences(context: bpy.types.Context | None) -> HEIO_AddonPreferences:
    if context is None:
        context = bpy.context
    return context.preferences.addons[HEIO_AddonPreferences.bl_idname].preferences