import os
import bpy
from bpy.props import (
    StringProperty,
    CollectionProperty,
)

from .base_import_operators import (
    ImportMaterialOperator
)

from ...dotnet import load_dotnet, SharpNeedle


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

    def import_materials(self, context):
        load_dotnet()

        directory = os.path.dirname(self.filepath)
        sn_materials = []
        resource_manager = SharpNeedle.RESOURCE_MANAGER()

        for file in self.files:
            filepath = os.path.join(directory, file.name)

            try:
                material = SharpNeedle.RESOURCE_EXTENSIONS.Open[SharpNeedle.MATERIAL](
                    resource_manager, filepath, True)
            except Exception as error:
                print(f"An error occured while importing {file.name}")
                raise error

            sn_materials.append(material)

        from ...importing import i_material

        return i_material.convert_sharpneedle_materials(
            context,
            sn_materials,
            self.create_undefined_parameters,
            self.use_existing_images,
            directory if self.import_images else None)

    def _execute(self, context):
        self.import_materials(context)
        return {'FINISHED'}


class HEIO_OT_Import_Material_Active(HEIO_OT_Import_Material):
    bl_idname = "heio.import_material_active"
    bl_label = "Import HE Material (*.material)"

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
