import bpy

from . import i_transform, i_mesh, i_model, i_sca_parameters
from ..register.definitions import TargetDefinition
from ..dotnet import SharpNeedle, HEIO_NET, System
from ..utility import progress_console


class NodeConverter:

    _context: bpy.types.Context
    _target_definition: TargetDefinition
    _mesh_converter: i_mesh.MeshConverter

    def __init__(self, context: bpy.types.Context, target_definition: TargetDefinition, mesh_converter: i_mesh.MeshConverter, bone_orientation: str):
        self._context = context
        self._target_definition = target_definition
        self._mesh_converter = mesh_converter

        self._bone_orientation = bone_orientation

        self._converted_models = dict()
        self._armature_name_lookup = dict()

    def _create_bones(self, model_info: i_model.ModelInfo):
        bone_orientation = self._bone_orientation
        if bone_orientation == 'AUTO':
            bone_orientation = self._target_definition.bone_orientation

        if bone_orientation == 'XY':
            matrix_remap = i_transform.net_to_bpy_bone_xy_matrix
        elif bone_orientation == 'XZ':
            matrix_remap = i_transform.net_to_bpy_bone_xz_matrix
        else: # ZNX
            matrix_remap = i_transform.net_to_bpy_bone_znx_matrix

        for node in model_info.sn_model.Nodes:
            bone = model_info.armature.edit_bones.new(node.Name)
            bone.head = (0, 0, 0)
            bone.tail = (0, 1, 0)
            bone.inherit_scale = 'ALIGNED'

            if node.ParentIndex >= 0:
                parent = model_info.armature.edit_bones[node.ParentIndex]
                bone.parent = parent

            _, node_matrix = System.MATRIX4X4.Invert(node.Transform, System.MATRIX4X4.Identity)
            world_space = matrix_remap(node_matrix)
            model_info.bone_matrices.append(world_space)
            bone.matrix = world_space.normalized()


    @staticmethod
    def _correct_bone_lengths(armature: bpy.types.Armature):
        for bone in armature.edit_bones:
            if len(bone.children) > 0:
                distance = float("inf")
                for child in bone.children:
                    new_distance = (bone.head - child.head).magnitude
                    if new_distance < distance:
                        distance = new_distance

                if distance < 0.01:
                    distance = 0.01

            elif bone.parent is not None:
                distance = bone.parent.length

            else:
                continue

            bone.length = distance

    def _convert_sca_parameters(self, model_info: i_model.ModelInfo):
        if model_info.sn_model.Root is None:
            return

        node = model_info.sn_model.Root.FindNode("NodesExt")
        if node is None:
            return

        for child in node.Children:
            bone = model_info.armature.edit_bones[child.Value]
            i_sca_parameters.convert_from_container(
                child, bone.heio_node.sca_parameters, self._target_definition, 'model')

    def _convert_model(self, model_info: i_model.ModelInfo):
        if model_info.sn_model.Nodes.Count == 0:
            return None

        armature = bpy.data.armatures.new(model_info.name)
        model_info.armature = armature

        dummy_object = bpy.data.objects.new("DUMMY", armature)
        self._context.scene.collection.objects.link(dummy_object)

        prev_active = self._context.view_layer.objects.active
        self._context.view_layer.objects.active = dummy_object

        bpy.ops.object.mode_set(mode='EDIT', toggle=False)

        self._create_bones(model_info)
        self._correct_bone_lengths(model_info.armature)
        self._convert_sca_parameters(model_info)

        bpy.ops.object.mode_set(mode='OBJECT')

        self._context.view_layer.objects.active = prev_active
        bpy.data.objects.remove(dummy_object)

    def _convert_lod_models(self, model_info: i_model.ModelInfo):
        progress_console.start(
            "Converting LOD Armatures",
            len(model_info.lod_models))

        for i, lod_model_info in enumerate(model_info.lod_models):
            progress_console.update(f"Converting LOD level {i}", i)
            self._convert_model(lod_model_info)

        progress_console.end()

    def convert_model_sets(self, model_sets):

        result = self._mesh_converter.convert_model_sets(model_sets)

        progress_console.start("Converting Armatures", len(model_sets))

        for i, model_info in enumerate(result):
            progress_console.update(
                f"Converting armature \"{model_info.sn_model.Name}\"", i)

            if model_info.armature is not None or not isinstance(model_info.sn_model, SharpNeedle.MODEL):
                continue

            self._convert_model(model_info)

            if model_info.sn_lod_info is not None:
                self._convert_lod_models(model_info)

        progress_console.end()

        return result

    def get_model_info(self, key: any):
        return self._mesh_converter.get_model_info(key)
