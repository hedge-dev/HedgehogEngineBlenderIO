import bpy

from ..operators.import_operators import HEIO_OT_Import_Material

class TOPBAR_MT_HEIO_Export(bpy.types.Menu):
    '''The heio submenu in the export menu'''
    bl_label = "HEIO Formats"

    def draw(self, context):
        layout = self.layout

        layout.label(text="Export as...")

    @staticmethod
    def menu_func(self, context):
        self.layout.menu(TOPBAR_MT_HEIO_Export.__name__)

    @classmethod
    def register(cls):
        bpy.types.TOPBAR_MT_file_export.append(TOPBAR_MT_HEIO_Export.menu_func)

    @classmethod
    def unregister(cls):
        bpy.types.TOPBAR_MT_file_export.remove(TOPBAR_MT_HEIO_Export.menu_func)


class TOPBAR_MT_HEIO_Import(bpy.types.Menu):
    '''The heio submenu in the import menu'''
    bl_label = "HEIO Formats"

    def draw(self, context):
        layout = self.layout

        layout.label(text="Import...")
        layout.operator(HEIO_OT_Import_Material.bl_idname)

    @staticmethod
    def menu_func(self, context):
        self.layout.menu(TOPBAR_MT_HEIO_Import.__name__)

    @classmethod
    def register(cls):
        bpy.types.TOPBAR_MT_file_import.append(TOPBAR_MT_HEIO_Import.menu_func)

    @classmethod
    def unregister(cls):
        bpy.types.TOPBAR_MT_file_import.remove(TOPBAR_MT_HEIO_Import.menu_func)

class NativeHooks:

    DONT_REGISTER_CLASS = True

    @staticmethod
    def material_context_menu_func(self, context):
        self.layout.separator(type='LINE')
        operator = self.layout.operator(HEIO_OT_Import_Material.bl_idname, icon='IMPORT')
        operator.add_to_active = True

    @classmethod
    def register(cls):
        bpy.types.MATERIAL_MT_context_menu.append(NativeHooks.material_context_menu_func)

    @classmethod
    def unregister(cls):
        bpy.types.MATERIAL_MT_context_menu.remove(NativeHooks.material_context_menu_func)