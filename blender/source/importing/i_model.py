import bpy
from mathutils import Matrix

from ..external import TPointer, CMeshDataSet, CLODItem
from ..exceptions import HEIODevException


class ModelInfo:

    name: str

    c_mesh_data_set: CMeshDataSet
    meshes: list[bpy.types.Mesh]

    armature: bpy.types.Armature | None
    bone_matrices: list[Matrix]

    mesh_objects: list[bpy.types.Object]
    armatures_objects: list[bpy.types.Object]

    c_lod_items: list[CLODItem]
    c_lod_unknown1: int
    lod_models: list['ModelInfo']
    lod_info_set_up: bool

    def __init__(self, name: str, c_model: CMeshDataSet):
        self.name = name
        self.c_mesh_data_set = c_model
        self.meshes = []

        self.armature = None
        self.bone_matrices = []

        self.mesh_objects = []
        self.armatures_objects = []

        self.c_lod_items = None
        self.c_lod_unknown1 = 0
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
                pose_bone.matrix = self.bone_matrices[i]

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
            raise HEIODevException("Model has no meshes!")

        else:
            raise HEIODevException("Model has too many meshes!")

        return mesh_objs, armature_obj

    def setup_lod_info(self, lod_collection: bpy.types.Collection, context: bpy.types.Context):
        if self.c_lod_items is None or self.lod_info_set_up:
            return

        if self.c_mesh_data_set.is_terrain:
            lod_info = self.meshes[0].heio_mesh.lod_info
        elif self.armature is not None:
            lod_info = self.armature.heio_armature.lod_info
        else:
            return

        self.lod_info_set_up = True
        lod_info.initialize()

        for i, c_lod_info_item in enumerate(self.c_lod_items):
            if i == 0:
                lod_info_level = lod_info.levels[0]
                lod_info_level.cascade = c_lod_info_item.cascade_level
                lod_info_level.unknown = c_lod_info_item.unknown2
                continue

            lod_info_level = lod_info.levels.new()
            lod_info_level.cascade = c_lod_info_item.cascade_level
            lod_info_level.unknown = c_lod_info_item.unknown2

            lod_model = self.lod_models[i - 1]
            mesh_objs, armature_obj = lod_model.create_object(lod_model.name, lod_collection, context)

            if armature_obj is not None:
                lod_info_level.target = armature_obj
            else:
                lod_info_level.target = mesh_objs[0]