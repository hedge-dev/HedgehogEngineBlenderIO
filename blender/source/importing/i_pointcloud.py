import bpy
from mathutils import Vector, Euler, Matrix

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

	for point_collection in point_cloud_collection.TerrainCollections:
		collection = bpy.data.collections.new(point_collection.Name)
		result.append(collection)

		for point in point_collection.Points:
			collection.objects.link(_create_object_from_point(point, meshes))

	return result