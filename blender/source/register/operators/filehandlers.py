import bpy

from bpy_extras.io_utils import poll_file_object_drop

class HEIO_FH_Material(bpy.types.FileHandler):
    bl_idname = "HEIO_FH_material"
    bl_label = "HE Material (*.material)"
    bl_import_operator = "heio.import_material_active_if"
    bl_export_operator = "heio.export_material"
    bl_file_extensions = ".material"

    @classmethod
    def poll_drop(cls, context):
        return poll_file_object_drop(context)