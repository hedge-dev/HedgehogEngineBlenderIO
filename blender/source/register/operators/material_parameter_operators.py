from bpy.props import EnumProperty

from .base import (
    HEIOBaseOperator,
    ListAdd,
    ListRemove,
    ListMove
)

from ..property_groups.material_properties import HEIO_Material
from ...exceptions import HEIOException


class MaterialParameterOperator(HEIOBaseOperator):
    bl_options = {'UNDO'}

    mode: EnumProperty(
        name="Mode",
        items=(
            ("PARAMETER", "Parameters", ""),
            ("TEXTURE", "Textures", ""),
        ),
        options={'HIDDEN'},
    )

    def get_parameter_list(self, context):
        material: HEIO_Material = context.active_object.active_material.heio_material

        if self.mode == "PARAMETER":
            return material.parameters
        elif self.mode == "TEXTURE":
            return material.textures
        else:
            raise HEIOException("Invalid parameter operator mode!")

    def _execute(self, context):
        parameter_list = self.get_parameter_list(context)
        self.list_execute(context, parameter_list)
        return {'FINISHED'}

    @classmethod
    def poll(cls, context):
        return context.active_object.active_material.heio_material.custom_shader


class HEIO_OT_MaterialParameters_Add(MaterialParameterOperator, ListAdd):
    bl_idname = "heio.material_parameters_add"
    bl_label = "Add material parameter"
    bl_description = "Adds a material parameter to the active list"


class HEIO_OT_MaterialParameters_Remove(MaterialParameterOperator, ListRemove):
    bl_idname = "heio.material_parameters_remove"
    bl_label = "Remove material parameter"
    bl_description = "Removes the selected material parameter from the its list"


class HEIO_OT_MaterialParameters_Move(MaterialParameterOperator, ListMove):
    bl_idname = "heio.material_parameters_move"
    bl_label = "Move material parameter"
    bl_description = "Moves the selected material parameter slot in the list"
