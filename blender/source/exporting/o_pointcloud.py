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

    def object_trees_to_pointscloud(self, object_trees: dict[bpy.types.Object, list[bpy.types.Object]], type, write_resources):
        pointcloud = SharpNeedle.POINTCLOUD()
        pointcloud.FormatVersion = self.target_definition.data_versions.point_cloud

        if type == 'COL':
            processor = self.collision_mesh_processor
        elif type == 'MODEL':
            processor = self.model_processor

        for root, children in object_trees.items():

            if write_resources:
                resource_name = processor.enqueue_compile(root, children)
            else:
                resource_name = processor.get_name(root)

            if resource_name is None:
                continue

            point = SharpNeedle.POINTCLOUD.InstanceData()

            point.Name = root.name
            point.ResourceName = resource_name

            point.Position, point.Rotation, point.Scale = \
                o_transform.bpy_matrix_to_net_transforms(root.matrix_world)

            pointcloud.Instances.Add(point)

        return pointcloud
