import bpy
from bpy.props import EnumProperty

from .base import HEIOBaseOperator
from ..property_groups.mesh_properties import MESH_DATA_TYPES
from .. import definitions
from ...exceptions import HEIOUserException


class MaterialMassEditBaseOperator(HEIOBaseOperator):
    bl_options = {'UNDO', 'INTERNAL'}

    @classmethod
    def poll(cls, context):
        return context.mode == 'OBJECT' and len(context.selected_objects) > 0

    def get_materials(self, context: bpy.types.Context):
        result = set()

        for obj in context.selected_objects:
            if obj.type not in MESH_DATA_TYPES:
                continue

            result.update(
                [slot.material for slot in obj.material_slots if slot.material is not None])

        return result


class HEIO_OT_MaterialMassEdit_Update(MaterialMassEditBaseOperator):
    bl_idname = "heio.material_massedit_udpate"
    bl_label = "Add/Update"
    bl_description = "Add and/or update the selected properties on the materials of all selected meshes"

    mode: EnumProperty(
        name="Mode",
        items=(
            ("SHADER", "Shader", ""),
            ("GENERAL", "Shader", ""),
            ("PARAMETERS", "Shader", ""),
            ("TEXTURES", "Shader", ""),
        )
    )

    def _update_shader(self, mme_props, material: bpy.types.Material):
        mme_material = mme_props.material_properties

        prev_shader = material.heio_material.shader_name

        material.heio_material.custom_shader = mme_material.custom_shader
        material.heio_material.shader_name = mme_material.shader_name
        material.heio_material.variant_name = mme_material.variant_name

        if prev_shader != mme_material.shader_name and self.shader_definition is not None:
            material.heio_material.setup_definition(self.shader_definition)

    def _update_general(self, mme_props, material: bpy.types.Material):

        if mme_props.update_alpha_threshold:
            material.alpha_threshold = mme_props.alpha_threshold

        if mme_props.update_backface_culling:
            material.use_backface_culling = mme_props.use_backface_culling

        if mme_props.update_render_layer:
            material.heio_material.render_layer = mme_props.material_properties.render_layer
            material.heio_material.special_render_layer_name = mme_props.material_properties.special_render_layer_name

        if mme_props.update_blend_mode:
            material.heio_material.blend_mode = mme_props.material_properties.blend_mode

    def _update_parameters(self, mme_props, material: bpy.types.Material):
        def update_parameter(target_parameter):
            target_parameter.value_type = mme_props.parameter_properties.value_type
            target_parameter.float_value = mme_props.parameter_properties.float_value
            target_parameter.boolean_value = mme_props.parameter_properties.boolean_value

        parameter = material.heio_material.parameters.elements.get(mme_props.parameter_name, None)

        if parameter is not None:
            update_parameter(parameter)
            return

        if not material.heio_material.custom_shader:
            return

        parameter = material.heio_material.parameters.new(
            name=mme_props.parameter_name)
        update_parameter(parameter)

    def _update_textures(self, mme_props, material: bpy.types.Material):
        def update_tex(target_tex):
            target_tex.image = mme_props.texture_properties.image
            target_tex.texcoord_index = mme_props.texture_properties.texcoord_index
            target_tex.wrapmode_u = mme_props.texture_properties.wrapmode_u
            target_tex.wrapmode_v = mme_props.texture_properties.wrapmode_v

        i = 0

        for texture in material.heio_material.textures:
            if texture.name != mme_props.texture_name:
                continue

            if i == mme_props.texture_index:
                update_tex(texture)
                return

            i += 1

        if not material.heio_material.custom_shader:
            return

        while i <= mme_props.texture_index:
            texture = material.heio_material.textures.new(
                name=mme_props.texture_name)
            i += 1

        update_tex(texture)

    def _execute(self, context):
        materials = self.get_materials(context)
        mme_props = context.scene.heio_material_massedit


        if self.mode == 'SHADER':
            update_func = self._update_shader

            self.shader_definition = None
            target_def = definitions.get_target_definition(context)
            if not mme_props.material_properties.custom_shader and target_def is not None:
                self.shader_definition = target_def.shaders.definitions.get(mme_props.material_properties.shader_name, None)

        elif self.mode == 'GENERAL':
            update_func = self._update_general

        elif self.mode == 'PARAMETERS':
            update_func = self._update_parameters
            if len(mme_props.parameter_name) == 0:
                raise HEIOUserException("Please specify a parameter name!")

        elif self.mode == 'TEXTURES':
            update_func = self._update_textures
            if len(mme_props.texture_name) == 0:
                raise HEIOUserException("Please specify a texture name!")

        for material in materials:
            update_func(mme_props, material)

        return {'FINISHED'}


class HEIO_OT_MaterialMassEdit_Remove(MaterialMassEditBaseOperator):
    bl_idname = "heio.material_massedit_remove"
    bl_label = "Remove"
    bl_description = "Remove the selected list elements on the materials of all selected meshes (only works on materials with custom shaders)"

    mode: EnumProperty(
        name="Mode",
        items=(
            ("PARAMETERS", "Shader", ""),
            ("TEXTURES", "Shader", ""),
        )
    )

    def _update_parameters(self, mme_props, material: bpy.types.Material):
        if not material.heio_material.custom_shader:
            return

        parameter = material.heio_material.parameters.elements.get(mme_props.parameter_name, None)

        if parameter is not None:
            material.heio_material.parameters.remove(parameter)


    def _update_textures(self, mme_props, material: bpy.types.Material):
        i = 0
        found_texture = None

        for texture in material.heio_material.textures:
            if texture.name != mme_props.texture_name:
                continue

            if i == mme_props.texture_index:
                found_texture = texture

            i += 1

        if found_texture is None:
            return

        if not material.heio_material.custom_shader or (i - 1) > mme_props.texture_index:
            found_texture.image = None
            found_texture.texcoord_index = 0
            found_texture.wrapmode_u = "REPEAT"
            found_texture.wrapmode_v = "REPEAT"

        else:
            material.heio_material.textures.remove(found_texture)


    def _execute(self, context):
        materials = self.get_materials(context)
        mme_props = context.scene.heio_material_massedit

        if self.mode == 'PARAMETERS':
            update_func = self._update_parameters
            if len(mme_props.parameter_name) == 0:
                raise HEIOUserException("Please specify a parameter name!")

        elif self.mode == 'TEXTURES':
            update_func = self._update_textures
            if len(mme_props.texture_name) == 0:
                raise HEIOUserException("Please specify a texture name!")

        for material in materials:
            update_func(mme_props, material)

        return {'FINISHED'}