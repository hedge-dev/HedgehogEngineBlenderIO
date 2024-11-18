from .base_export_operators import (
    ExportMaterialOperator
)


class HEIO_OT_Export_Material(ExportMaterialOperator):
    bl_idname = "heio.export_material"
    bl_label = "HE Material (*.material)"

    def export(self, context):
        materials = self.get_materials(context)
        self.export_materials(context, materials)
        return {'FINISHED'}


class HEIO_OT_Export_Material_Active(ExportMaterialOperator):
    bl_idname = "heio.export_material_active"
    bl_label = "Export as HE Material (*.material)"

    @classmethod
    def poll(cls, context):
        return (
            context.active_object is not None
            and context.active_object.type == 'MESH'
            and context.active_object.active_material is not None
        )

    def draw(self, context):
        self.draw_panel_material()

    def export(self, context):
        self.export_materials(context, [context.active_object.active_material])
        return {'FINISHED'}