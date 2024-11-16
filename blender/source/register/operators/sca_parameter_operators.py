from bpy.props import EnumProperty

from .base import (
    HEIOBaseOperator,
    ListAdd,
    ListRemove,
    ListMove
)

from ...exceptions import HEIOException


class SCAParameterOperator(HEIOBaseOperator):
    bl_options = {'UNDO'}

    mode: EnumProperty(
        name="Mode",
        items=(
            ("MATERIAL", "Float", ""),
            ("NODE", "Boolean", "")
        ),
        options={'HIDDEN'},
    )

    def get_sca_parameter_list(self, context):
        if self.mode == "MATERIAL":
            return context.active_object.active_material.heio_material.sca_parameters
        else:
            raise HEIOException("Invalid parameter operator mode!")

    def _execute(self, context):
        parameter_list = self.get_sca_parameter_list(context)
        self.list_execute(context, parameter_list)
        return {'FINISHED'}


class HEIO_OT_SCAParameters_Add(SCAParameterOperator, ListAdd):
    bl_idname = "heio.sca_parameters_add"
    bl_label = "Add SCA parameter"
    bl_description = "Adds an SCA parameter to the active list"


class HEIO_OT_SCAParameters_Remove(SCAParameterOperator, ListRemove):
    bl_idname = "heio.sca_parameters_remove"
    bl_label = "Remove SCA parameter"
    bl_description = "Removes the selected SCA parameter from the its list"


class HEIO_OT_SCAParameters_Move(SCAParameterOperator, ListMove):
    bl_idname = "heio.sca_parameters_move"
    bl_label = "Move SCA parameter"
    bl_description = "Moves the selected SCA parameter slot in the list"
