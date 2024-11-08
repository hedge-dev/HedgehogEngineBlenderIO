import os
import bpy

from os.path import dirname
ADDON_DIR = dirname(dirname(dirname(os.path.realpath(__file__))))
ADDON_NAME = os.path.basename(ADDON_DIR)


def get_path():
    return ADDON_DIR


def get_name():
    return ADDON_NAME


def get_template_path():
    return os.path.join(get_path(), "HEIOTemplates.blend")


def compare_path(a: str, b: str):
    absolute = bpy.path.abspath(b)
    absolute = os.path.abspath(absolute)
    return a == absolute


def load_template_blend(context: bpy.types.Context):
    lib_path = get_template_path()

    found = False
    for library in bpy.data.libraries:
        if compare_path(lib_path, library.filepath):
            found = True
            break

    if not found:
        bpy.ops.wm.link(
            filename="HEIO Templates",
            directory=f"{lib_path}{os.path.sep}Scene{os.path.sep}"
        )


def is_from_template(data):
    template_path = get_template_path()
    return (
        data.library is not None
        and compare_path(template_path, data.library.filepath))
