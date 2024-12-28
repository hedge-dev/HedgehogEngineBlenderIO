import bpy
from mathutils import Vector

from ..dotnet import SharpNeedle

from ..exceptions import HEIOException


class ModelInfo:

    name: str

    sn_model: any
    meshes: list[bpy.types.Mesh]

    armature: bpy.types.Armature | None
    pose_bone_scales: list[Vector]

    mesh_objects: list[bpy.types.Object]
    armatures_objects: list[bpy.types.Object]

    sn_lod_info: any
    lod_models: list['ModelInfo']
    lod_info_set_up: bool

    def __init__(self, name: str, sn_model):
        self.name = name
        self.sn_model = sn_model
        self.meshes = []

        self.armature = None
        self.pose_bone_scales = []

        self.mesh_objects = []
        self.armatures_objects = []

        self.sn_lod_info = None
        self.lod_models = []
        self.lod_info_set_up = False

    def create_object(self, name: str, collection: bpy.types.Collection, context: bpy.types.Context):

        mesh_objs = []

        def add_mesh(obj):
            mesh_objs.append(obj)
            collection.objects.link(obj)
            self.mesh_objects.append(obj)

        if self.armature is not None:
            armature_obj = bpy.data.objects.new(name, self.armature)
            collection.objects.link(armature_obj)
            self.armatures_objects.append(armature_obj)

            if collection != bpy.context.scene.collection:
                bpy.context.scene.collection.objects.link(armature_obj)
            context.view_layer.depsgraph.update()

            for i, pose_bone in enumerate(armature_obj.pose.bones):
                pose_bone.scale = self.pose_bone_scales[i]

            for mesh in self.meshes:

                mesh_name = mesh.name
                if mesh_name == name:
                    mesh_name += "_Mesh"

                mesh_obj = bpy.data.objects.new(mesh_name, mesh)
                mesh_obj.parent = armature_obj

                armature_modifier: bpy.types.ArmatureModifier = mesh_obj.modifiers.new(
                    "Armature", 'ARMATURE')
                armature_modifier.object = armature_obj

                add_mesh(mesh_obj)

            if collection != bpy.context.scene.collection:
                bpy.context.scene.collection.objects.unlink(armature_obj)

        elif len(self.meshes) == 1:
            armature_obj = None
            add_mesh(bpy.data.objects.new(name, self.meshes[0]))

        elif len(self.meshes) == 0:
            HEIOException("Model has no meshes!")

        else:
            HEIOException("Model has too many meshes!")

        return mesh_objs, armature_obj

    def setup_lod_info(self):
        if self.sn_lod_info is None or self.lod_info_set_up:
            return

        if isinstance(self.sn_model, SharpNeedle.TERRAIN_MODEL):
            lod_info = self.meshes[0].heio_mesh.lod_info
        elif self.armature is not None:
            lod_info = self.armature.heio_armature.lod_info
        else:
            return

        self.lod_info_set_up = True
        lod_info.unknown = self.sn_lod_info.Unknown1
        lod_info.initialize()

        for i, sn_lod_info_item in enumerate(self.sn_lod_info.Items):
            if i == 0:
                lod_info_level = lod_info.levels[0]
                lod_info_level.cascade = sn_lod_info_item.CascadeLevel
                lod_info_level.unknown = sn_lod_info_item.Unknown2
                continue

            lod_info_level = lod_info.levels.new()
            lod_info_level.cascade = sn_lod_info_item.CascadeLevel
            lod_info_level.unknown = sn_lod_info_item.Unknown2

            lod_model = self.lod_models[i - 1]

            if self.armature is not None:
                lod_info_level.armature = lod_model.armature
            else:
                lod_info_level.mesh = lod_model.meshes[0]