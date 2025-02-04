import bpy

from . import i_transform, i_model

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
            point,
            resources: list,
            collection: bpy.types.Collection,
            context: bpy.types.Context):

        added = False

        if point.ResourceIndex > -1:
            resource = resources[point.ResourceIndex]

            if isinstance(resource, i_model.ModelInfo):
                if self._model_instance_collection_collection is not None and resource.armature is not None:
                    instance_collection = self._model_instance_collections.get(resource.name, None)
                    if instance_collection is None:
                        instance_collection = bpy.data.collections.new(resource.name)
                        self._model_instance_collections[resource.name] = instance_collection
                        self._model_instance_collection_collection.children.link(instance_collection)
                        resource.create_object(resource.name, instance_collection, context)

                    result = bpy.data.objects.new(point.InstanceName, None)
                    result.instance_type = 'COLLECTION'
                    result.instance_collection = instance_collection

                else:

                    mesh_objs, armature_obj = resource.create_object(point.InstanceName, collection, context)
                    if armature_obj is not None:
                        result = armature_obj
                    else:
                        result = mesh_objs[0]
                    added = True

            elif isinstance(resource, bpy.types.Mesh):
                result = bpy.data.objects.new(point.InstanceName, resource)

            else:
                raise HEIODevException("Invalid Resource")

        else:
            result = bpy.data.objects.new(point.InstanceName, None)

        result.matrix_world = i_transform.net_transforms_to_bpy_matrix(
            point.Position,
            point.Rotation,
            point.Scale
        )

        if not added:
            collection.objects.link(result)

        return result

    def convert_point_clouds(self, context: bpy.types.Context, point_collections, resources: list):
        result = []

        progress_console.start("Importing Point Clouds", len(point_collections))

        for i, point_collection in enumerate(point_collections):
            progress_console.update(f"Importing \"{point_collection.Name}\"", i)
            collection = bpy.data.collections.new(point_collection.Name)
            result.append(collection)

            progress_console.start("Importing points", len(point_collection.Points))

            for j, point in enumerate(point_collection.Points):
                progress_console.update("", j)
                self._create_object_from_point(point, resources, collection, context)

            progress_console.end()

        progress_console.end()

        return result

    def cleanup(self):
        if (
            self._model_instance_collection_collection is not None
            and self._model_instance_collection_deletable
            and len(self._model_instance_collection_collection.all_objects) == 0):
            bpy.data.collections.remove(self._model_instance_collection_collection)