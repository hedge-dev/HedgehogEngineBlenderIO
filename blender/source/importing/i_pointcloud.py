import bpy

from . import i_transform, i_model

from ..utility import progress_console

def _create_model_from_point(
		point,
		model_infos: list[i_model.ModelInfo],
		collection: bpy.types.Collection,
		context: bpy.types.Context):

	if point.ResourceIndex > -1:
		mesh_objs, armature_obj = model_infos[point.ResourceIndex].create_object(point.InstanceName, collection, context)
		if armature_obj is not None:
			result = armature_obj
		else:
			result = mesh_objs[0]
	else:
		result = bpy.data.objects.new(point.InstanceName, None)

	result.matrix_world = i_transform.net_transforms_to_bpy_matrix(
		point.Position,
		point.Rotation,
		point.Scale
	)

	return result

def convert_point_cloud_collection(context: bpy.types.Context, point_cloud_collection, model_infos: list[i_model.ModelInfo]):
	result = []

	progress_console.start("Importing Point Clouds", len(point_cloud_collection.ModelCollections))

	for i, point_collection in enumerate(point_cloud_collection.ModelCollections):
		progress_console.update(f"Importing \"{point_collection.Name}\"", i)
		collection = bpy.data.collections.new(point_collection.Name)
		result.append(collection)

		progress_console.start("Importing points", len(point_collection.Points))

		for j, point in enumerate(point_collection.Points):
			progress_console.update("", j)
			_create_model_from_point(point, model_infos, collection, context)

		progress_console.end()

	progress_console.end()

	return result