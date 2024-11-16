import os
import bpy
from bpy.props import (
    StringProperty,
    BoolProperty,
    CollectionProperty,
)
from bpy.types import Context

from .base import HEIOBaseFileLoadOperator

from ...dotnet import load_dotnet, SharpNeedle


class HEIO_OT_Import_Material(HEIOBaseFileLoadOperator):
    bl_idname = "heio.import_material"
    bl_label = "HE Material (*.material)"
    bl_options = {'PRESET', 'UNDO'}

    filter_glob: StringProperty(
        default="*.material",
        options={'HIDDEN'},
    )

    files: CollectionProperty(
        name='File paths',
        type=bpy.types.OperatorFileListElement
    )

    create_undefined_parameters: BoolProperty(
        name="Create undefined parameters/textures",
        description="If the shader of a material is defined, create parameters inside the material that are not part of the definition, otherwise ignore them.",
        default=False
    )

    import_images: BoolProperty(
        name="Import Images",
        description="Import images if found, otherwise use placeholders",
        default=True
    )

    use_existing_images: BoolProperty(
        name="Use existing images",
        description="When the active file contains a image with a matching image file name, use that instead of importing an image file",
        default=False
    )

    add_to_active: BoolProperty(
        options={'HIDDEN'}
    )

    @classmethod
    def poll(cls, context: Context):
        return context.mode in ['OBJECT', 'MESH']

    def draw(self, context):
        header, body = self.layout.panel(
            "SAIO_import_material_general")
        header.label(text="General")

        if body:
            body.prop(self, "create_undefined_parameters")
            body.prop(self, "import_images")
            body.prop(self, "use_existing_images")

    def _execute(self, context):
        load_dotnet()

        directory = os.path.dirname(self.filepath)
        sn_materials = []
        resource_manager = SharpNeedle.RESOURCE_MANAGER()

        for file in self.files:
            filepath = os.path.join(directory, file.name)

            try:
                material = SharpNeedle.RESOURCE_EXTENSIONS.Open[SharpNeedle.MATERIAL](resource_manager, filepath, True)
            except Exception as error:
                print(f"An error occured while importing {file.name}")
                raise error

            sn_materials.append(material)

        from ...importing import i_material

        materials = i_material.convert_sharpneedle_materials(
            context,
            sn_materials,
            self.create_undefined_parameters,
            self.use_existing_images,
            directory if self.import_images else None,)

        if self.add_to_active:
            object = context.active_object
            for material in materials.values():
                object.data.materials.append(material)

        return {'FINISHED'}
