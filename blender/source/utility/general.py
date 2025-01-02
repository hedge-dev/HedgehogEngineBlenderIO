import os
import bpy

from os.path import dirname

ADDON_DIR = dirname(dirname(dirname(os.path.realpath(__file__))))
ADDON_NAME = os.path.basename(ADDON_DIR)
PACKAGE_NAME = '.'.join(__package__.split('.')[:3])
ICON_DIR = os.path.join(ADDON_DIR, "icons")


def get_addon_preferences(context: bpy.types.Context | None):
    if context is None:
        context = bpy.context
    return context.preferences.addons[PACKAGE_NAME].preferences
