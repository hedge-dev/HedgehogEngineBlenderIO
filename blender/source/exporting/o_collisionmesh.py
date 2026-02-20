import os
from mathutils import Vector, Quaternion, Matrix
from ctypes import c_uint, c_ubyte, cast, POINTER
import bpy

from . import o_mesh, o_modelset, o_transform, o_object_manager
from ..external import HEIONET, Bullet, util, enums, CBulletPrimitive, CCollisionMeshData, CCollisionMeshDataGroup, CVector3, CBulletShape
from ..register.definitions import TargetDefinition
from ..register.property_groups.mesh_properties import MESH_DATA_TYPES
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

        self.shape_type = enums.BULLET_PRIMITIVE_SHAPE_TYPE.index(shape_type)
        self.surface_layer = surface_layer
        self.surface_type = surface_type
        self.surface_flag_values = surface_flags
        self.position = position
        self.rotation = rotation
        self.dimensions = dimensions

    def convert_to_c(self, transform_matrix: Matrix | None):
        position = self.position
        rotation = self.rotation

        if transform_matrix is not None:
            transform_matrix = transform_matrix.normalized()
            position = transform_matrix @ position
            rotation = transform_matrix.to_quaternion() @ rotation

        return CBulletPrimitive(
            shape_type = self.shape_type,
            surface_layer = self.surface_layer,
            surface_type = self.surface_type,
            surface_flags = self.surface_flag_values,
            position = o_transform.bpy_to_c_position(position),
            rotation = o_transform.bpy_to_c_quaternion(rotation),
            dimensions = o_transform.bpy_to_c_scale(self.dimensions)
        )


class RawCollisionMeshDataGroup:
    size: int
    layer: int
    is_convex: bool
    convex_type: int
    convex_flag_values: list[int]

    def __init__(
        self,
        size: int,
        layer: int,
        is_convex: bool):

        self.size = size
        self.layer = layer
        self.is_convex = is_convex
        self.convex_type = 0
        self.convex_flag_values = []
        
    def convert_to_c(self):
        
        return CCollisionMeshDataGroup(
            size = self.size,
            layer = self.layer,
            is_convex = self.is_convex,
            convex_type = self.convex_type,

            convex_flag_values = util.construct_array(self.convex_flag_values, c_ubyte),
            convex_flag_values_size = len(self.convex_flag_values)
        )


class RawCollisionMeshData:

    vertices: list[Vector]
    triangle_indices: list[int]

    types: list[int]
    type_values: list[int] | None

    flags: list[int]
    flag_values: list[int] | None

    groups: list[RawCollisionMeshDataGroup]
    primitives: list[RawCollisionPrimitiveData]

    def __init__(self):
        self.vertices = []
        self.triangle_indices = []
        self.types = []
        self.type_values = None
        self.flags = []
        self.flag_values = None
        self.groups = []
        self.primitives = []

    def convert_to_c(self, transform_matrix: Matrix | None):
        if transform_matrix is None:
            vertices = self.vertices
        else:
            vertices = [transform_matrix @ v for v in self.vertices]

        c_vertices = [o_transform.bpy_to_c_position(v) for v in vertices]
        c_groups = [x.convert_to_c() for x in self.groups]
        c_primitives = [x.convert_to_c(transform_matrix) for x in self.primitives]

        return CCollisionMeshData(
            name = "UNUSED",

            vertices = util.as_array(c_vertices, CVector3),
            vertices_size = len(vertices),

            triangle_indices = util.construct_array(self.triangle_indices, c_uint),
            triangle_indices_size = len(self.triangle_indices),

            types = util.construct_array(self.types, c_uint),
            types_size = len(self.types),

            type_values = util.construct_array(self.type_values, c_ubyte),
            type_values_size = len(self.type_values) if self.type_values is not None else 0,

            flags = util.construct_array(self.flags, c_uint),
            flags_size = len(self.flags),

            flag_values = util.construct_array(self.flag_values, c_ubyte),
            flag_values_size = len(self.flag_values) if self.flag_values is not None else 0,

            groups = util.as_array(c_groups, CCollisionMeshDataGroup),
            groups_size = len(c_groups),

            primitives = util.as_array(c_primitives, CBulletPrimitive),
            primitives_size = len(c_primitives)
        )


class CollisionMeshProcessor(o_mesh.BaseMeshProcessor):

    def __init__(
        self,
        target_definition: TargetDefinition,
        object_manager: o_object_manager.ObjectManager,
        model_set_manager: o_modelset.ModelSetManager):

        super().__init__(
            target_definition, 
            object_manager,
            model_set_manager,
            "_col"
        )

    def _convert_model_set(self, model_set: o_modelset.ModelSet):
        if len(model_set.evaluated_mesh.polygons) == 0:
            return None

        raw_meshdata = RawCollisionMeshData()
        raw_meshdata.vertices = [
            v.co for v in model_set.evaluated_mesh.vertices]

        heio_mesh = model_set.obj.data.heio_mesh

        triangle_order = []

        if not heio_mesh.groups.initialized or heio_mesh.groups.attribute_invalid:
            triangle_order = [x.polygon_index for x in model_set.evaluated_mesh.loop_triangles]

            raw_meshdata.triangle_indices = [
                vertex 
                for polygon in model_set.evaluated_mesh.loop_triangles 
                for vertex in polygon.vertices
            ]

            raw_meshdata.groups.append(
                RawCollisionMeshDataGroup(
                    len(triangle_order),
                    0, False
                )
            )

        else:
            layer_max = len(heio_mesh.groups) - 1
            triangles: list[list[bpy.types.MeshLoopTriangle]] = [list() for _ in heio_mesh.groups]
            invalid_triangles = []

            attribute = model_set.evaluated_mesh.attributes.get(heio_mesh.groups.attribute_name, None)

            if attribute is not None:
                for triangle in model_set.evaluated_mesh.loop_triangles:
                    group = attribute.data[triangle.polygon_index]
                    if group.value > layer_max:
                        invalid_triangles.append(triangle)
                    else:
                        triangles[group.value].append(triangle)
            else:
                triangles[0] = list(model_set.evaluated_mesh.loop_triangles)

            for i, group in enumerate(heio_mesh.groups):
                layer_triangles = triangles[i]
                if len(layer_triangles) == 0:
                    continue

                for triangle in layer_triangles:
                    raw_meshdata.triangle_indices.extend(triangle.vertices)
                    triangle_order.append(triangle.polygon_index)

                collision_group = RawCollisionMeshDataGroup(
                    len(layer_triangles),
                    group.collision_layer.value,
                    group.is_convex_collision
                )

                if group.is_convex_collision:
                    collision_group.convex_type = group.convex_type.value

                    if len(group.convex_flags) > 0:
                        collision_group.convex_flag_values = [f.value for f in group.convex_flags]

                raw_meshdata.groups.append(collision_group)

            if len(invalid_triangles) > 0:
                for triangle in layer_triangles:
                    raw_meshdata.triangle_indices.extend(triangle.vertices)
                    triangle_order.append(triangle.index)

                raw_meshdata.groups.append(
                    RawCollisionMeshDataGroup(
                        len(invalid_triangles), 0, False
                    )
                )

        if len(triangle_order) > 0:
            if heio_mesh.collision_types.initialized and not heio_mesh.collision_types.attribute_invalid:
                raw_meshdata.type_values = [
                    t.value for t in heio_mesh.collision_types]
                attribute = model_set.evaluated_mesh.attributes.get(heio_mesh.collision_types.attribute_name, None)

                if attribute is None:
                    raw_meshdata.types = [0] * len(triangle_order)
                else:
                    raw_meshdata.types = [
                        attribute.data[x].value for x in triangle_order]

            if heio_mesh.collision_flags.initialized and not heio_mesh.collision_flags.attribute_invalid:
                raw_meshdata.flag_values = [
                    t.value for t in heio_mesh.collision_flags]
                attribute = model_set.evaluated_mesh.attributes.get(heio_mesh.collision_flags.attribute_name, None)

                if attribute is None:
                    raw_meshdata.flags = [0] * len(triangle_order)
                else:
                    raw_meshdata.flags = [
                        attribute.data[x].value for x in triangle_order]

        for primitive in heio_mesh.collision_primitives:
            flags = 0
            for flag in primitive.collision_flags:
                flags |= 1 << flag.value

            raw_meshdata.primitives.append(
                RawCollisionPrimitiveData(
                    primitive.shape_type,
                    primitive.collision_layer.value,
                    primitive.collision_type.value,
                    flags,
                    Vector(primitive.position),
                    Quaternion(primitive.rotation),
                    Vector(primitive.dimensions),
                )
            )

        return raw_meshdata

    def _assemble_compile_data(self, root, children, name):
        c_meshdata = []

        if root is None:
            parent_matrix = Matrix.Identity(4)

        else:
            parent_matrix = root.matrix_world.inverted()

            if root.type in MESH_DATA_TYPES:
                root_meshdata = self.get_meshdata(root)
                if root_meshdata is not None:
                    meshdata = root_meshdata.convert_to_c(None)
                    c_meshdata.append(meshdata)

        for child in children:
            if child.type not in MESH_DATA_TYPES:
                continue

            child_meshdata = self.get_meshdata(child)

            if child_meshdata is None:
                continue

            matrix = parent_matrix @ child.matrix_world

            meshdata = child_meshdata.convert_to_c(matrix)
            c_meshdata.append(meshdata)

        if len(c_meshdata) == 0:
            return None

        return (name, c_meshdata)

    @staticmethod
    def generate_bvh_tree(shape: CBulletShape):

        if not shape.faces or shape.faces_size == 0 or shape.vertices_size == 0:
            return

        x_min = float("inf")
        y_min = float("inf")
        z_min = float("inf")
        x_max = float("-inf")
        y_max = float("-inf")
        z_max = float("-inf")

        for j in range(shape.vertices_size):
            vertex: CVector3 = shape.vertices[j]

            if vertex.x < x_min:
                x_min = vertex.x

            if vertex.y < y_min:
                y_min = vertex.y

            if vertex.z < z_min:
                z_min = vertex.z

            if vertex.x > x_max:
                x_max = vertex.x

            if vertex.y > y_max:
                y_max = vertex.y

            if vertex.z > z_max:
                z_max = vertex.z

        index_mesh = Bullet.btIndexedMesh_new()
        index_type = 2 # Int32
        Bullet.btIndexedMesh_setVertexType(index_mesh, 0) # Single
        Bullet.btIndexedMesh_setIndexType(index_mesh, index_type) # Int32
        Bullet.btIndexedMesh_setVertexStride(index_mesh, 12)
        Bullet.btIndexedMesh_setNumTriangles(index_mesh, int(shape.faces_size / 3))
        Bullet.btIndexedMesh_setTriangleIndexBase(index_mesh, shape.faces)
        Bullet.btIndexedMesh_setTriangleIndexStride(index_mesh, 12)
        Bullet.btIndexedMesh_setNumVertices(index_mesh, shape.vertices_size)
        Bullet.btIndexedMesh_setVertexBase(index_mesh, shape.vertices)

        triangle_vertex_array = Bullet.btTriangleIndexVertexArray_new()
        Bullet.btTriangleIndexVertexArray_addIndexedMesh(triangle_vertex_array, index_mesh, index_type)

        bvh_builder = Bullet.btOptimizedBvh_new()

        Bullet.btOptimizedBvh_build(
            bvh_builder, 
            triangle_vertex_array, 
            True, 
            CVector3(x_min, y_min, z_min),
            CVector3(x_max, y_max, z_max)
        )

        shape.bvh_size = Bullet.btQuantizedBvh_calculateSerializeBufferSize(bvh_builder)
        shape.bvh = cast((c_ubyte * shape.bvh_size)(), POINTER(c_ubyte))
        Bullet.btOptimizedBvh_serializeInPlace(bvh_builder, shape.bvh, shape.bvh_size, False)

        Bullet.btQuantizedBvh_delete(bvh_builder)
        Bullet.btStridingMeshInterface_delete(triangle_vertex_array)
        Bullet.btIndexedMesh_delete(index_mesh)

    def _compile_output_to_file(self, name: str, c_meshdata: CCollisionMeshData, directory: str):
        bullet_mesh = HEIONET.bullet_mesh_compile_mesh_data(c_meshdata)
        bullet_mesh.contents.name = name
        bullet_mesh.contents.bullet_mesh_version = self._target_definition.data_versions.bullet_mesh

        with Bullet.load():
            bullet_mesh_contents = bullet_mesh.contents
            for j in range(bullet_mesh_contents.shapes_size):
                CollisionMeshProcessor.generate_bvh_tree(bullet_mesh_contents.shapes[j])

        filepath = os.path.join(directory, name + ".btmesh")

        HEIONET.bullet_mesh_write_to_file(
            bullet_mesh,
            filepath
        )

    def compile_output_to_files(self, directory: str):
        # TODO: compile with multithreading in c#, maybe
        progress_console.start("Compiling & writing collision meshes", len(self._output_queue))
        for i, output in enumerate(self._output_queue):
            name = output[0]
            progress_console.update(f"Compiling collision mesh \"{name}\"", i)
            self._compile_output_to_file(name, output[1], directory)

        self._output_queue.clear()
        progress_console.end()

