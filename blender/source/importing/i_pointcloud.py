import bpy

from . import i_transform, i_model

from ..utility import progress_console
from ..exceptions import HEIODevException

def _create_object_from_point(
		point,
		resources: list,
		collection: bpy.types.Collection,
		context: bpy.types.Context):

	added = False

	if point.ResourceIndex > -1:
		resource = resources[point.ResourceIndex]

		if isinstance(resource, i_model.ModelInfo):
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

def convert_point_clouds(context: bpy.types.Context, point_collections, resources: list):
	result = []

	progress_console.start("Importing Point Clouds", len(point_collections))

	for i, point_collection in enumerate(point_collections):
		progress_console.update(f"Importing \"{point_collection.Name}\"", i)
		collection = bpy.data.collections.new(point_collection.Name)
		result.append(collection)

		progress_console.start("Importing points", len(point_collection.Points))

		for j, point in enumerate(point_collection.Points):
			progress_console.update("", j)
			_create_object_from_point(point, resources, collection, context)

		progress_console.end()

	progress_console.end()

	return result