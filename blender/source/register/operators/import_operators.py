import bpy
from bpy.props import (
    StringProperty,
    CollectionProperty,
)

from .base_import_operators import (
    ImportMaterialOperator
)



class HEIO_OT_Import_Material(ImportMaterialOperator):
    bl_idname = "heio.import_material"
    bl_label = "HE Material (*.material)"

    filter_glob: StringProperty(
        default="*.material",
        options={'HIDDEN'},
    )

    files: CollectionProperty(
        name='File paths',
        type=bpy.types.OperatorFileListElement
    )

    def _execute(self, context):
        self.import_materials(context)
        return {'FINISHED'}


class HEIO_OT_Import_Material_Active(ImportMaterialOperator):
    bl_idname = "heio.import_material_active"
    bl_label = "Import HE Material (*.material)"

    filter_glob: StringProperty(
        default="*.material",
        options={'HIDDEN'},
    )

    files: CollectionProperty(
        name='File paths',
        type=bpy.types.OperatorFileListElement
    )

    @classmethod
    def poll(cls, context):
        return (
            context.mode in ['OBJECT', 'MESH']
            and context.active_object is not None
            and context.active_object.type == 'MESH'
        )

    def _execute(self, context):
        materials = self.import_materials(context)

        object = context.active_object
        for material in materials.values():
            object.data.materials.append(material)

        return {'FINISHED'}
