"""Blender operators, ui and property groups declared in this addon"""

import bpy
from . import (
    property_groups,
    operators,
    gizmos,
    ui,
    rendering,
    definitions,
    manual
)

classes = []

classes.extend(property_groups.to_register)
classes.extend(gizmos.to_register)
classes.extend(operators.to_register)
classes.extend(ui.to_register)
classes.extend(rendering.to_register)


def register():
    """Loading API classes into blender"""

    definitions.load_definitions()

    for cls in classes:
        if hasattr(cls, "class_setup"):
            cls.class_setup()

    for cls in classes:
        if not hasattr(cls, "DONT_REGISTER_CLASS"):
            bpy.utils.register_class(cls)
        elif hasattr(cls, "register"):
            cls.register()

    # kc = bpy.context.window_manager.keyconfigs.addon
    # if kc is not None:
    #     km = kc.keymaps.new(name="Hedgehog Engine I/O", space_type='EMPTY')

    #     for cls in classes:
    #         if hasattr(cls, "register_keymap"):
    #             cls.register_keymap(km)

    bpy.utils.register_manual_map(manual.add_manual_map)


def unregister():
    """Unloading classes loaded in register(), as well as various cleanup"""

    bpy.utils.unregister_manual_map(manual.add_manual_map)

    for cls in classes:
        if not hasattr(cls, "DONT_REGISTER_CLASS"):
            bpy.utils.unregister_class(cls)
        elif hasattr(cls, "unregister"):
            cls.unregister()

    # kc = bpy.context.window_manager.keyconfigs.addon
    # if kc is not None:
    #     keymap = kc.keymaps.get("Hedgehog Engine I/O", None)
    #     if keymap is not None:
    #         kc.keymaps.remove(keymap)


def reload_package(module_dict_main):
    import importlib
    from pathlib import Path

    def reload_package_recursive(current_dir: Path, module_dict: dict[str, any]):
        for path in current_dir.iterdir():
            if "__init__" in str(path) or path.stem not in module_dict:
                continue

            if path.is_file() and path.suffix == ".py":
                importlib.reload(module_dict[path.stem])
            elif path.is_dir():
                reload_package_recursive(path, module_dict[path.stem].__dict__)

    reload_package_recursive(Path(__file__).parent, module_dict_main)
