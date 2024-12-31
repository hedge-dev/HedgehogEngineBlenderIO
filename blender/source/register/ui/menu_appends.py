import bpy

from ..operators import import_operators, export_operators

class TOPBAR_MT_HEIO_Export(bpy.types.Menu):
    '''The heio submenu in the export menu'''
    bl_label = "HEIO Formats"

    def draw(self, context):
        layout = self.layout

        layout.label(text="Export as...")
        layout.operator(export_operators.HEIO_OT_Export_Material.bl_idname)

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
        layout.operator(import_operators.HEIO_OT_Import_Material.bl_idname)
        layout.operator(import_operators.HEIO_OT_Import_Model.bl_idname)
        layout.operator(import_operators.HEIO_OT_Import_TerrainModel.bl_idname)
        layout.operator(import_operators.HEIO_OT_Import_CollisionMesh.bl_idname)
        layout.operator(import_operators.HEIO_OT_Import_PointCloud.bl_idname)

    @staticmethod
    def menu_func(self, context):
        self.layout.menu(TOPBAR_MT_HEIO_Import.__name__)

    @classmethod
    def register(cls):
        bpy.types.TOPBAR_MT_file_import.append(TOPBAR_MT_HEIO_Import.menu_func)

    @classmethod
    def unregister(cls):
        bpy.types.TOPBAR_MT_file_import.remove(TOPBAR_MT_HEIO_Import.menu_func)

class MenuAppends:

    DONT_REGISTER_CLASS = True

    @staticmethod
    def material_context_menu_func(self, context):
        self.layout.separator(type='LINE')
        self.layout.operator(import_operators.HEIO_OT_Import_Material_Active.bl_idname, icon='IMPORT')
        self.layout.operator(export_operators.HEIO_OT_Export_Material_Active.bl_idname, icon='EXPORT')

    @classmethod
    def register(cls):
        bpy.types.MATERIAL_MT_context_menu.append(MenuAppends.material_context_menu_func)

    @classmethod
    def unregister(cls):
        bpy.types.MATERIAL_MT_context_menu.remove(MenuAppends.material_context_menu_func)