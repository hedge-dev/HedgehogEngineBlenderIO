import os
import bpy
from ctypes import pointer

from . import o_mesh, o_transform, o_modelset
from ..external import HEIONET, util, CPointCloudCloud, CPointCloudPoint
from ..register.definitions import TargetDefinition
from ..utility import progress_console

class PointCloudProcessor:

    type: str
    write_resources: bool
    target_definition: TargetDefinition
    model_set_manager: o_modelset.ModelSetManager
    mesh_processor: o_mesh.BaseMeshProcessor

    def __init__(
            self,
            type: str,
            write_resources: bool,
            model_set_manager: o_modelset.ModelSetManager,
            mesh_processor: o_mesh.BaseMeshProcessor,
            target_definition: TargetDefinition):

        self.type = type
        self.write_resources = write_resources
        self.model_set_manager = model_set_manager
        self.mesh_processor = mesh_processor
        self.target_definition = target_definition

    def prepare(self, context: bpy.types.Context):
        if self.write_resources:
            self.model_set_manager.evaluate_begin(context, self.type == 'MODEL')
            self.mesh_processor.prepare_all_meshdata()
            self.model_set_manager.evaluate_end()

    def object_trees_to_pointcloud_file(self, filepath: str, object_trees: dict[bpy.types.Object, list[bpy.types.Object]]):

        name = os.path.splitext(os.path.basename(filepath))[0]

        points = []
        resource_names = []

        progress_console.start(f"Assembling point cloud \"{name}\"", len(object_trees))

        for i, object_tree in enumerate(object_trees.items()):
            root, children = object_tree
            progress_console.update(f"Processing instance \"{root.name}\"", i)

            if self.write_resources:
                resource_name = self.mesh_processor.enqueue_compile(root, children)
            else:
                resource_name = self.mesh_processor.get_name(root)

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

    def compile_resources_to_files(self, use_multicore_processing: bool, directory: str):
        if self.write_resources:
            self.mesh_processor.compile_output_to_files(use_multicore_processing, directory)