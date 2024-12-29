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

from ...exceptions import HEIODevException, HEIOUserException


class SCAParameterOperator(HEIOBaseOperator):
    bl_options = {'UNDO'}

    mode: EnumProperty(
        name="Mode",
        items=(
            ('MATERIAL', "Material", ""),
            ('MESH', "Mesh", ""),
            ('BONE', "Bone", ""),
            ('NONE', "None", "Fallback")
        ),
        default='NONE',
        options={'HIDDEN'},
    )

    def get_sca_parameter_list(self, context: bpy.types.Context):
        obj = context.active_object
        if obj is None:
            raise HEIODevException("No active object!")

        if self.mode == "MATERIAL":
            if obj.active_material is None:
                raise HEIODevException("No active material!")

            return obj.active_material.heio_material.sca_parameters

        elif self.mode == "MESH":
            if obj.type != 'MESH':
                raise HEIODevException("Active object is not a mesh!")

            return obj.data.heio_mesh.sca_parameters

        elif self.mode == 'BONE':
            if obj.type != 'ARMATURE':
                raise HEIODevException("Active object is not an armature!")

            if context.active_bone is None:
                raise HEIODevException("No active bone!")

            return context.active_bone.heio_node.sca_parameters

        else:
            raise HEIOUserException("Invalid parameter operator mode!")

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
    target_def = definitions.get_target_definition(context)
    if target_def is None:
        return []

    if operator.mode == 'MATERIAL':
        return target_def.sca_parameters.material_items
    elif operator.mode in ['MESH', 'BONE']:
        return target_def.sca_parameters.model_items
    return []


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

        target_def = definitions.get_target_definition(context)
        if target_def is None:
            return

        if self.mode == 'MATERIAL':
            defs = target_def.sca_parameters.material
        elif self.mode in ['MESH', 'BONE']:
            defs = target_def.sca_parameters.model
        else:
            return

        definition = defs[self.preset]

        entry = parameter_list.new()
        entry.name = definition.name
        entry.value_type = definition.parameter_type.name

