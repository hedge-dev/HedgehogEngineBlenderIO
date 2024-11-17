import bpy
from bpy.props import EnumProperty

from .base import (
    HEIOBaseOperator,
    HEIOBasePopupOperator,
    ListAdd,
    ListRemove,
    ListMove
)

from .. import definitions

from ...exceptions import HEIOException


class SCAParameterOperator(HEIOBaseOperator):
    bl_options = {'UNDO'}

    mode: EnumProperty(
        name="Mode",
        items=(
            ("MATERIAL", "Material", ""),
            ("NODE", "Node", "")
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



def _get_sca_parameter_items(operator, context: bpy.types.Context):
    return definitions.get_sca_parameter_definition_items(context, operator.mode.lower())


class HEIO_OT_SCAParameters_NewFromPreset(SCAParameterOperator, HEIOBasePopupOperator):
    bl_idname = "heio.sca_parameters_newfrompreset"
    bl_label = "New SCA parameter from preset"
    bl_description = "Creates a new SCA parameter from the presets defined for the target game"

    preset: EnumProperty(
        name="Preset",
        items=_get_sca_parameter_items
    )

    def list_execute(self, context, parameter_list):
        if self.preset == "":
            return

        definition = definitions.get_sca_parameter_definitions(context, self.mode.lower())[self.preset]

        entry = parameter_list.new()
        entry.name = definition.name
        entry.value_type = definition.parameter_type.name

