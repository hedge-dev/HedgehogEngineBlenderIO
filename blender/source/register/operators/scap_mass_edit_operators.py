import bpy
from bpy.props import BoolProperty

from .base import HEIOBaseOperator
from ..property_groups.mesh_properties import MESH_DATA_TYPES

class BaseSCAPMassEditOperator(HEIOBaseOperator):
    bl_options = {'UNDO', 'INTERNAL'}

    @classmethod
    def poll(cls, context):
        props = context.scene.heio_scap_massedit
        if props.mode == 'MATERIAL' and context.mode != 'OBJECT':
            return False
        elif props.mode == 'MODEL' and context.mode not in ['OBJECT', 'POSE']:
            return False
        elif props.use_preset:
            return props.value_name_enum != "ERROR_FALLBACK"
        else:
            return len(props.value_name.strip()) > 0

    @staticmethod
    def _get_parameter_lists(context: bpy.types.Context):
        props = context.scene.heio_scap_massedit
        parameters_list = set()

        if context.mode == 'POSE':
            for bone in context.active_object.pose.bones:
                if bone.bone.hide or not bone.bone.select:
                    continue
                parameters_list.add(bone.bone.heio_node.sca_parameters)
        else:
            for obj in context.view_layer.objects:
                if obj.type not in MESH_DATA_TYPES or not obj.visible_get(view_layer=context.view_layer) or not obj.select_get(view_layer=context.view_layer):
                    continue

                if props.mode == 'MATERIAL':
                    parameters_list.update([
                        material_slot.material.heio_material.sca_parameters
                        for material_slot in obj.material_slots
                        if material_slot.material is not None
                    ])
                else:
                    parameters_list.add(obj.data.heio_mesh.sca_parameters)

        return parameters_list

class HEIO_OT_SCAP_MassEdit_Select(BaseSCAPMassEditOperator):
    bl_idname = "heio.scap_massedit_select"
    bl_label = "Select"
    bl_description = "Select all mesh objects/armature bones that contain the specified SCA parameter"

    exact: BoolProperty()

    @classmethod
    def poll(cls, context):
        return super().poll(context) and context.scene.heio_scap_massedit.mode == 'MODEL'

    def _execute(self, context):
        props = context.scene.heio_scap_massedit

        def check_has_param(params):
            for param in params:
                if param.name == props.value_name and (not self.exact or param.value == props.value):
                    return True
            return False

        if context.mode == 'OBJECT':
            for obj in context.view_layer.objects:
                if obj.type not in MESH_DATA_TYPES or not obj.visible_get(view_layer=context.view_layer):
                    continue
                if check_has_param(obj.data.heio_mesh.sca_parameters):
                    obj.select_set(True, view_layer=context.view_layer)

        else: # bones
            for bone in context.active_object.pose.bones:
                if bone.bone.hide:
                    continue

                if check_has_param(bone.bone.heio_node.sca_parameters):
                    bone.bone.select = True

        return {'FINISHED'}


class HEIO_OT_SCAP_MassEdit_Set(BaseSCAPMassEditOperator):
    bl_idname = "heio.scap_massedit_set"
    bl_label = "Set"
    bl_description = "Add/update the SCA parameter on all selected mesh objects/materials/armature bones"

    def _execute(self, context):
        props = context.scene.heio_scap_massedit
        parameter_list = self._get_parameter_lists(context)

        for parameters in parameter_list:
            found = False
            for parameter in parameters:
                if parameter.name == props.value_name:
                    parameter.value_type = props.value_type
                    parameter.value = props.value
                    found = True
                    break

            if not found:
                parameter = parameters.new()
                parameter.name = props.value_name
                parameter.value_type = props.value_type
                parameter.value = props.value

        # so that the ui list updates too
        for area in context.screen.areas:
            area.tag_redraw()

        return {'FINISHED'}


class HEIO_OT_SCAP_MassEdit_Remove(BaseSCAPMassEditOperator):
    bl_idname = "heio.scap_massedit_remove"
    bl_label = "Remove"
    bl_description = "Remove SCA parameters with the same name from all selected mesh objects/materials/armature bones"

    def _execute(self, context):
        props = context.scene.heio_scap_massedit
        parameter_list = self._get_parameter_lists(context)

        for parameters in parameter_list:
            found = False
            for parameter in parameters:
                if parameter.name == props.value_name:
                    found = True
                    break

            if found:
                parameters.remove(parameter)

        # so that the ui list updates too
        for area in context.screen.areas:
            area.tag_redraw()


        return {'FINISHED'}
