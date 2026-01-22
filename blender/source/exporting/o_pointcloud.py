import os
import bpy
from ctypes import pointer

from . import o_model, o_collisionmesh, o_transform
from ..external import HEIONET, util, CPointCloudCloud, CPointCloudPoint
from ..register.definitions import TargetDefinition
from ..utility import progress_console

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

    def object_trees_to_pointcloud_file(self, filepath: str, object_trees: dict[bpy.types.Object, list[bpy.types.Object]], type: str, write_resources: bool):

        name = os.path.splitext(os.path.basename(filepath))[0]

        points = []
        resource_names = []

        if type == 'COL':
            processor = self.collision_mesh_processor
        elif type == 'MODEL':
            processor = self.model_processor

        progress_console.start(f"Assembling point cloud \"{name}\"", len(object_trees))

        for i, object_tree in enumerate(object_trees.items()):
            root, children = object_tree
            progress_console.update(f"Processing instance \"{root.name}\"", i)

            if write_resources:
                resource_name = processor.enqueue_compile(root, children)
            else:
                resource_name = processor.get_name(root)

            if resource_name is None:
                continue

            position, rotation, scale = \
                o_transform.bpy_matrix_to_c_transforms(root.matrix_world)

            try:
                resource_index = resource_names.index(resource_name)
            except ValueError:
                resource_index = len(resource_names)
                resource_names.append(resource_name)

            points.append(
                CPointCloudPoint(
                    instance_name =  root.name,
                    resource_index = resource_index,
                    position = position,
                    rotation = rotation,
                    scale = scale
                )
            )

        cloud = CPointCloudCloud(
            name = name,
            points = util.as_array(points, CPointCloudPoint),
            points_size = len(points)
        )

        HEIONET.point_cloud_write_file(
            pointer(cloud),
            resource_names,
            self.target_definition.data_versions.point_cloud,
            filepath
        )   

        progress_console.end()
