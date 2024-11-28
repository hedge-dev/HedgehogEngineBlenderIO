from .base_import_operators import (
    ImportMaterialOperator
)


class HEIO_OT_Import_Material(ImportMaterialOperator):
    bl_idname = "heio.import_material"
    bl_label = "HE Material (*.material)"

    def import_(self, context):
        self.import_materials(context)
        return {'FINISHED'}


class HEIO_OT_Import_Material_Active(ImportMaterialOperator):
    bl_idname = "heio.import_material_active"
    bl_label = "Import HE Material (*.material)"

    @classmethod
    def poll(cls, context):
        return (
            context.mode in ['OBJECT', 'MESH']
            and context.active_object is not None
            and context.active_object.type == 'MESH'
        )

    def import_(self, context):
        materials = self.import_materials(context)

        object = context.active_object
        for material in materials.values():
            object.data.materials.append(material)

        return {'FINISHED'}


class HEIO_OT_Import_Material_Active_if(ImportMaterialOperator):
    bl_idname = "heio.import_material_active_if"
    bl_label = "Import HE Material (*.material)"

    def import_(self, context):
        materials = self.import_materials(context)

        object = context.active_object
        if object is not None and object.select_get():
            for material in materials.values():
                object.data.materials.append(material)

        return {'FINISHED'}
