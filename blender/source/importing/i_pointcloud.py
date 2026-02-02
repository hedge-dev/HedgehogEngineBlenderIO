import bpy

from . import i_transform, i_model

from ..external import TPointer, CPointCloudCloud, CPointCloudPoint
from ..utility import progress_console
from ..exceptions import HEIODevException

class PointCloudConverter:

    _model_instance_collection_collection: bpy.types.Collection | None
    _model_instance_collections: dict[str, bpy.types.Collection]
    _model_instance_collection_deletable: bool

    def __init__(
            self,
            model_instance_collection_collection: bpy.types.Collection | None,
            model_instance_collection_deletable: bool):

        self._model_instance_collection_collection = model_instance_collection_collection
        self._model_instance_collection_deletable = model_instance_collection_deletable
        self._model_instance_collections = {}

    def _create_object_from_point(
            self,
            point: CPointCloudPoint,
            resources: list,
            collection: bpy.types.Collection,
            context: bpy.types.Context):

        added = False

        if point.resource_index > -1:
            resource = resources[point.resource_index]

            if isinstance(resource, i_model.ModelInfo):
                if self._model_instance_collection_collection is not None and resource.armature is not None:
                    instance_collection = self._model_instance_collections.get(resource.name, None)
                    if instance_collection is None:
                        _, _, instance_collection = resource.create_object(resource.name, self._model_instance_collection_collection, True, context)
                        self._model_instance_collections[resource.name] = instance_collection

                    result = bpy.data.objects.new(point.instance_name, None)
                    result.instance_type = 'COLLECTION'
                    result.instance_collection = instance_collection

                else:

                    mesh_objs, armature_obj, _ = resource.create_object(point.instance_name, collection, False, context)
                    if armature_obj is not None:
                        result = armature_obj
                    else:
                        result = mesh_objs[0]
                    added = True

            elif isinstance(resource, bpy.types.Mesh):
                result = bpy.data.objects.new(point.instance_name, resource)

            else:
                raise HEIODevException("Invalid Resource")

        else:
            result = bpy.data.objects.new(point.instance_name, None)

        result.matrix_world = i_transform.c_transforms_to_bpy_matrix(
            point.position,
            point.rotation,
            point.scale
        )

        if not added:
            collection.objects.link(result)

        return result

    def convert_point_clouds(self, context: bpy.types.Context, clouds: TPointer[CPointCloudCloud], clouds_size: int, resources: list):
        result = []

        progress_console.start("Importing Point Clouds", clouds_size)

        for i in range(clouds_size):
            cloud: CPointCloudCloud = clouds[i]
            progress_console.update(f"Importing \"{cloud.name}\"", i)
            collection = bpy.data.collections.new(cloud.name)
            result.append(collection)

            progress_console.start("Importing points", cloud.points_size)

            for j in range(cloud.points_size):
                progress_console.update("", j)
                self._create_object_from_point(cloud.points[j], resources, collection, context)

            progress_console.end()

        progress_console.end()

        return result

    def cleanup(self):
        if (
            self._model_instance_collection_collection is not None
            and self._model_instance_collection_deletable
            and len(self._model_instance_collection_collection.all_objects) == 0):
            bpy.data.collections.remove(self._model_instance_collection_collection)