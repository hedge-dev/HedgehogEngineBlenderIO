import bpy

from . import o_model, o_collisionmesh, o_transform
from ..dotnet import SharpNeedle
from ..register.definitions import TargetDefinition


class PointCloudProcessor:

    target_definition: TargetDefinition
    model_processor: o_model.ModelProcessor
    collision_mesh_processor: o_collisionmesh.CollisionMeshProcessor

    def __init__(
            self,
            target_definition: TargetDefinition,
            model_processor: o_model.ModelProcessor,
            collision_mesh_processor: o_collisionmesh.CollisionMeshProcessor):

        self.target_definition = target_definition
        self.model_processor = model_processor
        self.collision_mesh_processor = collision_mesh_processor

    def object_trees_to_pointscloud(self, object_trees: dict[bpy.types.Object, list[bpy.types.Object]], type):
        pointcloud = SharpNeedle.POINTCLOUD()
        pointcloud.FormatVersion = self.target_definition.data_versions.point_cloud

        for root, children in object_trees.items():

            if type == 'COL':
                resource_name = self.collision_mesh_processor.compile_bulletmesh(
                    root, children)
            elif type == 'MODEL':
                resource_name = self.model_processor.enqueue_compile_model(root, children)

            if resource_name is None:
                continue

            point = SharpNeedle.POINTCLOUD.InstanceData()

            point.Name = root.name
            point.ResourceName = resource_name

            point.Position, point.Rotation, point.Scale = \
                o_transform.bpy_matrix_to_net_transforms(root.matrix_world)

            pointcloud.Instances.Add(point)

        return pointcloud
