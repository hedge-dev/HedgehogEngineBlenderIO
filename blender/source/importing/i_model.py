import bpy
from mathutils import Vector


class ModelInfo:

    name: str

    sn_model: any
    mesh: bpy.types.Mesh

    armature: bpy.types.Armature | None
    pose_bone_scales: list[Vector]

    mesh_objects: list[bpy.types.Object]
    armatures_objects: list[bpy.types.Object]

    def __init__(self, name: str, sn_model, mesh):
        self.name = name
        self.sn_model = sn_model
        self.mesh = mesh

        self.armature = None
        self.pose_bone_scales = []

        self.mesh_objects = []
        self.armatures_objects = []

    def create_object(self, name: str, collection: bpy.types.Collection, context: bpy.types.Context):
        if self.armature is not None:
            armature_obj = bpy.data.objects.new(name, self.armature)
            collection.objects.link(armature_obj)
            self.armatures_objects.append(armature_obj)

            if collection != bpy.context.scene.collection:
                bpy.context.scene.collection.objects.link(armature_obj)
            context.view_layer.depsgraph.update()

            for i, pose_bone in enumerate(armature_obj.pose.bones):
                pose_bone.scale = self.pose_bone_scales[i]

            mesh_obj = bpy.data.objects.new(name + "_mesh", self.mesh)
            mesh_obj.parent = armature_obj

            armature_modifier: bpy.types.ArmatureModifier = mesh_obj.modifiers.new(
                "Armature", 'ARMATURE')
            armature_modifier.object = armature_obj

            if collection != bpy.context.scene.collection:
                bpy.context.scene.collection.objects.unlink(armature_obj)

        else:
            armature_obj = None
            mesh_obj = bpy.data.objects.new(name, self.mesh)

        collection.objects.link(mesh_obj)
        self.mesh_objects.append(mesh_obj)

        return mesh_obj, armature_obj
