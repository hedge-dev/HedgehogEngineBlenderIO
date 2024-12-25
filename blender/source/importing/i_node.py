import bpy
from mathutils import Matrix

from . import i_transform, i_mesh, i_model
from ..dotnet import SharpNeedle, HEIO_NET
from ..utility import progress_console


class NodeConverter:

    _context: bpy.types.Context
    _mesh_converter: i_mesh.MeshConverter

    def __init__(self, context: bpy.types.Context, mesh_converter: i_mesh.MeshConverter):
        self._context = context
        self._mesh_converter = mesh_converter

        self._converted_models = dict()
        self._armature_name_lookup = dict()

    @staticmethod
    def _create_bones(model_info: i_model.ModelInfo):
        inv_world_matrices = []

        for node in model_info.sn_model.Nodes:
            bone = model_info.armature.edit_bones.new(node.Name)
            bone.head = (0, 0, 0)
            bone.tail = (0, 1, 0)

            node_matrix = HEIO_NET.PYTHON_HELPERS.InvertMatrix(node.Transform)

            world_space = i_transform.net_to_bpy_bone_matrix(node_matrix)
            inv_world_matrices.append(world_space.inverted())

            local_space = world_space

            if node.ParentIndex >= 0:
                parent = model_info.armature.edit_bones[node.ParentIndex]
                bone.parent = parent
                local_space = inv_world_matrices[node.ParentIndex] @ local_space

            _, _, local_scale = local_space.decompose()
            local_scale_matrix = Matrix.LocRotScale(None, None, local_scale)
            model_info.pose_matrices.append(local_scale_matrix)

            pos, rot, _ = world_space.decompose()
            bone.matrix = Matrix.LocRotScale(pos, rot, None)

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

    def _correct_scales(self, model_info: i_model.ModelInfo, dummy_armature_obj: bpy.types.Object):
        # correcting pose bone scales. we invert them first, so that we can
        # apply the armature modifier to get the "correct" mesh
        for i, pose_bone in enumerate(dummy_armature_obj.pose.bones):
            pose_bone.matrix_basis = model_info.pose_matrices[i]
            pose_bone.matrix_basis.invert()

        mesh_dummy_object = bpy.data.objects.new("DUMMY_MESH", model_info.mesh)
        self._context.scene.collection.objects.link(mesh_dummy_object)
        mesh_dummy_object.parent = dummy_armature_obj

        armature_modifier: bpy.types.ArmatureModifier = mesh_dummy_object.modifiers.new(
            "Armature", 'ARMATURE')
        armature_modifier.object = dummy_armature_obj

        bpy.context.view_layer.objects.active = mesh_dummy_object
        bpy.ops.object.modifier_apply(modifier=armature_modifier.name)

        bpy.data.objects.remove(mesh_dummy_object)

        # correcting them after applying armature modifier
        for pose_bone in dummy_armature_obj.pose.bones:
            pose_bone.matrix_basis.invert()

    def _convert_model(self, model_info: i_model.ModelInfo):
        if model_info.sn_model.Nodes.Count == 0:
            return None

        armature = bpy.data.armatures.new(model_info.sn_model.Name)
        model_info.armature = armature

        dummy_object = bpy.data.objects.new("DUMMY", armature)
        self._context.scene.collection.objects.link(dummy_object)

        prev_active = self._context.view_layer.objects.active
        self._context.view_layer.objects.active = dummy_object

        bpy.ops.object.mode_set(mode='EDIT', toggle=False)

        self._create_bones(model_info)
        self._correct_bone_lengths(model_info.armature)

        bpy.ops.object.mode_set(mode='OBJECT')

        self._correct_scales(model_info, dummy_object)

        self._context.view_layer.objects.active = prev_active
        bpy.data.objects.remove(dummy_object)

    def convert_model_sets(self, model_sets):

        result = self._mesh_converter.convert_model_sets(model_sets)

        progress_console.start("Converting Armatures", len(model_sets))

        for i, model_info in enumerate(result):
            progress_console.update(
                f"Converting armature \"{model_info.sn_model.Name}\"", i)

            if model_info.armature is not None or not isinstance(model_info.sn_model, SharpNeedle.MODEL):
                continue

            self._convert_model(model_info)

        progress_console.end()

        return result

    def get_model_info(self, key: any):
        return self._mesh_converter.get_model_info(key)
