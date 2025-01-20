from mathutils import Vector, Quaternion, Matrix

from . import o_enum, o_mesh, o_modelset, o_transform
from ..dotnet import HEIO_NET, SharpNeedle
from ..utility import progress_console

class RawCollisionPrimitiveData:

    shape_type: any
    surface_layer: int
    surface_type: int
    surface_flag_values: int
    position: Vector
    rotation: Quaternion
    dimensions: Vector

    def __init__(
            self,
            shape_type: str,
            surface_layer: int,
            surface_type: int,
            surface_flags: int,
            position: Vector,
            rotation: Quaternion,
            dimensions: Vector):

        self.shape_type = o_enum.to_bullet_primitive_shape_type(shape_type)
        self.surface_layer = surface_layer
        self.surface_type = surface_type
        self.surface_flag_values = surface_flags
        self.position = position
        self.rotation = rotation
        self.dimensions = dimensions

    def convert_to_sn(self, transform_matrix: Matrix | None):
        position = self.position
        rotation = self.rotation

        if transform_matrix is not None:
            transform_matrix = transform_matrix.normalized()
            position = transform_matrix @ position
            rotation = transform_matrix.to_quaternion() @ rotation

        result = SharpNeedle.BULLET_PRIMITIVE()
        result.ShapeType = self.shape_type
        result.SurfaceLayer = self.surface_layer
        result.SurfaceType = self.surface_type
        result.SurfaceFlags = self.surface_flag_values
        result.Position = o_transform.bpy_to_net_position(position)
        result.Rotation = o_transform.bpy_to_net_quaternion(rotation)
        result.Dimensions = o_transform.bpy_to_net_scale(self.dimensions)

        return result


class RawCollisionMeshData:

    vertices: list[Vector]
    triangle_indices: list[int]

    types: list[int]
    type_values: list[int] | None

    flags: list[int]
    flag_values: list[int] | None

    layers: list[any]

    primitives: list[RawCollisionPrimitiveData]

    def __init__(self):
        self.vertices = []
        self.triangle_indices = []
        self.types = []
        self.type_values = None
        self.flags = []
        self.flag_values = None
        self.layers = []
        self.primitives = []

    def convert_to_net(self, transform_matrix: Matrix | None):
        if transform_matrix is None:
            vertices = self.vertices
        else:
            vertices = [transform_matrix @ v for v in self.vertices]

        sn_vertices = [o_transform.bpy_to_net_position(v) for v in vertices]

        sn_meshdata = HEIO_NET.COLLISION_MESH_DATA(
            sn_vertices,
            self.triangle_indices,
            self.types,
            self.type_values,
            self.flags,
            self.flag_values,
            self.layers
        )

        sn_primitives = [x.convert_to_sn(transform_matrix)
                         for x in self.primitives]

        return sn_meshdata, sn_primitives


class CollisionMeshProcessor(o_mesh.BaseMeshProcessor):

    def _convert_model_set(self, model_set: o_modelset.ModelSet):
        if len(model_set.evaluated_mesh.polygons) == 0:
            return None

        raw_meshdata = RawCollisionMeshData()
        raw_meshdata.vertices = [
            v.co for v in model_set.evaluated_mesh.vertices]

        heiomesh = model_set.obj.data.heio_mesh

        triangle_order = []

        if not heiomesh.groups.initialized or heiomesh.groups.attribute_invalid:
            triangle_order = list(
                range(len(model_set.evaluated_mesh.polygons)))
            raw_meshdata.triangle_indices = [
                vertex for polygon in model_set.evaluated_mesh.polygons for vertex in polygon.vertices]
            raw_meshdata.layers.append(
                HEIO_NET.COLLISION_MESH_DATA_GROUP(
                    len(model_set.evaluated_mesh.polygons), 0, False
                ))

        else:
            layer_max = len(heiomesh.groups) - 1
            triangles = [list() for _ in heiomesh.groups]
            invalid_triangles = []
            attribute = model_set.evaluated_mesh.attributes[heiomesh.groups.attribute_name]

            for group, polygon in zip(attribute.data, model_set.evaluated_mesh.polygons):
                if group.value > layer_max:
                    invalid_triangles.append(polygon)
                else:
                    triangles[group.value].append(polygon)

            for i, group in enumerate(heiomesh.groups):
                layer_triangles = triangles[i]
                if len(layer_triangles) == 0:
                    continue

                for triangle in layer_triangles:
                    raw_meshdata.triangle_indices.extend(triangle.vertices)
                    triangle_order.append(triangle.index)

                meshdata_layer = HEIO_NET.COLLISION_MESH_DATA_GROUP(
                    len(layer_triangles),
                    group.collision_layer.value,
                    group.is_convex_collision
                )

                if group.is_convex_collision:
                    meshdata_layer.ConvexType = group.convex_type.value

                    if len(group.convex_flags) > 0:
                        meshdata_layer.ConvexFlagValues = [
                            f.value for f in group.convex_flags]

                raw_meshdata.layers.append(meshdata_layer)

            if len(invalid_triangles) > 0:
                for triangle in layer_triangles:
                    raw_meshdata.triangle_indices.extend(triangle.vertices)
                    triangle_order.append(triangle.index)

                raw_meshdata.layers.append(HEIO_NET.COLLISION_MESH_DATA_GROUP(
                    len(invalid_triangles), 0, False
                ))

        if len(triangle_order) > 0:
            if heiomesh.collision_types.initialized and not heiomesh.collision_types.attribute_invalid:
                raw_meshdata.type_values = [
                    t.value for t in heiomesh.collision_types]
                attribute = model_set.evaluated_mesh.attributes[heiomesh.collision_types.attribute_name]
                raw_meshdata.types = [
                    attribute.data[x].value for x in triangle_order]

            if heiomesh.collision_flags.initialized and not heiomesh.collision_flags.attribute_invalid:
                raw_meshdata.flag_values = [
                    t.value for t in heiomesh.collision_flags]
                attribute = model_set.evaluated_mesh.attributes[heiomesh.collision_flags.attribute_name]
                raw_meshdata.flags = [
                    attribute.data[x].value for x in triangle_order]

        for primitive in heiomesh.collision_primitives:
            flags = 0
            for flag in primitive.collision_flags:
                flags |= 1 << flag.value

            raw_meshdata.primitives.append(RawCollisionPrimitiveData(
                primitive.shape_type,
                primitive.collision_layer.value,
                primitive.collision_type.value,
                flags,
                Vector(primitive.position),
                Quaternion(primitive.rotation),
                Vector(primitive.dimensions),
            ))

        return raw_meshdata

    def _assemble_compile_data(self, root, children, name):
        sn_meshdata = []
        sn_primitives = []

        if root is None:
            parent_matrix = Matrix.Identity(4)

        else:
            parent_matrix = root.matrix_world.inverted()

            if root.type == 'MESH':
                root_meshdata = self.get_meshdata(root)
                if root_meshdata is not None:
                    meshdata, primitives = root_meshdata.convert_to_net(None)
                    sn_meshdata.append(meshdata)
                    sn_primitives.extend(primitives)

        for child in children:
            if child.type != 'MESH':
                continue

            child_meshdata = self.get_meshdata(child)

            if child_meshdata is None:
                continue

            matrix = parent_matrix @ child.matrix_world

            meshdata, primitives = child_meshdata.convert_to_net(matrix)
            sn_meshdata.append(meshdata)
            sn_primitives.extend(primitives)

        if len(sn_meshdata) == 0:
            return None

        return (name, sn_meshdata, sn_primitives)

    def compile_output(self):
        # TODO: compile with multithreading in c#, maybe
        progress_console.start("Compiling collision meshes", len(self._output_queue))

        for i, output in enumerate(self._output_queue):
            name, sn_meshdata, sn_primitives = output
            progress_console.update(f"Compiling collision mesh \"{name}\"", i)

            bullet_mesh = HEIO_NET.COLLISION_MESH_DATA.ToBulletMesh(
                sn_meshdata, sn_primitives)

            bullet_mesh.Name = name
            bullet_mesh.BulletMeshVersion = self._target_definition.data_versions.bullet_mesh

            self._output[bullet_mesh.Name] = (bullet_mesh, ".btmesh")

        self._output_queue.clear()

        progress_console.end()