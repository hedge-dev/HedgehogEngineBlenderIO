import bpy
from mathutils import Vector, Euler, Matrix
from ..utility import progress_console

def _create_object_from_point(point, datalist):
	data = None
	if point.ResourceIndex > -1:
		data = datalist[point.ResourceIndex]

	result = bpy.data.objects.new(point.InstanceName, data)

	position = Vector((point.Position.X, -point.Position.Z, point.Position.Y))
	scale = Vector((point.Scale.X, point.Scale.Z, point.Scale.Y))

	raw_rotation = Euler((point.Rotation.X, point.Rotation.Y, point.Rotation.Z))
	proc_rotation = raw_rotation.to_quaternion().to_euler("XZY")
	rotation = Euler((proc_rotation.x, -proc_rotation.z, proc_rotation.y))

	result.matrix_world = Matrix.LocRotScale(position, rotation, scale)

	return result

def convert_point_cloud_collection(point_cloud_collection, meshes: list[bpy.types.Mesh]):
	result = []

	progress_console.start("Importing Point Clouds", len(point_cloud_collection.TerrainCollections))

	for i, point_collection in enumerate(point_cloud_collection.TerrainCollections):
		progress_console.update(f"Importing \"{point_collection.Name}\"", i)
		collection = bpy.data.collections.new(point_collection.Name)
		result.append(collection)

		progress_console.start("Importing points", len(point_collection.Points))

		for j, point in enumerate(point_collection.Points):
			progress_console.update("", j)
			collection.objects.link(_create_object_from_point(point, meshes))

		progress_console.end()

	progress_console.end()

	return result