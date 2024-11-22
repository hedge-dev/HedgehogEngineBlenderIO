import os
import bpy

from os.path import dirname

ADDON_DIR = dirname(dirname(dirname(os.path.realpath(__file__))))
ADDON_NAME = os.path.basename(ADDON_DIR)
PACKAGE_NAME = '.'.join(__package__.split('.')[:3])


def get_path():
    return ADDON_DIR


def get_name():
    return ADDON_NAME


def compare_path(a: str, b: str):
    absolute = bpy.path.abspath(b)
    absolute = os.path.abspath(absolute)
    return a == absolute

def get_addon_preferences(context: bpy.types.Context | None):
    if context is None:
        context = bpy.context
    return context.preferences.addons[PACKAGE_NAME].preferences