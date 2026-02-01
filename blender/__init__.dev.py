"""Main entry point for the Hedgehog Engine I/O blender addon"""

if "register" in locals():
    from .source.register import reload_package
    reload_package(locals())

from .source.register import register, unregister
from .source.register.definitions import register_definition

bl_info = {
    "name": "Hedgehog Engine I/O DEV BUILD",
    "author": "Justin113D, hedge-dev",
    "description": "Import/Exporter for Hedgehog Engine 3D related formats",
    "version": (0, 1, 127),
    "blender": (4, 2, 0),
    "doc_url": "https://hedge-dev.github.io/HedgehogEngineBlenderIO/",
    "tracker_url": "https://github.com/hedge-dev/HedgehogEngineBlenderIO/issues/new",
    "category": "Import-Export"
}
