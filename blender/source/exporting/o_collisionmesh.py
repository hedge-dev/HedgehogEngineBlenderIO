import os
from mathutils import Vector, Quaternion, Matrix
from ctypes import c_uint, c_ubyte

from . import o_mesh, o_modelset, o_transform
from ..external import Library, enums, CBulletPrimitive, CCollisionMeshData, CCollisionMeshDataGroup, CVector3
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

            convex_flag_values = Library.construct_array(self.convex_flag_values, c_ubyte),
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

            vertices = Library.as_array(c_vertices, CVector3),
            vertices_size = len(vertices),

            triangle_indices = Library.construct_array(self.triangle_indices, c_uint),
            triangle_indices_size = len(self.triangle_indices),

            types = Library.construct_array(self.types, c_uint),
            types_size = len(self.types),

            type_values = Library.construct_array(self.type_values, c_ubyte),
            type_values_size = len(self.type_values),

            flags = Library.construct_array(self.flags, c_uint),
            flags_size = len(self.flags),

            flag_values = Library.construct_array(self.flag_values, c_ubyte),
            flag_values_size = len(self.flag_values),

            groups = Library.as_array(c_groups, CCollisionMeshDataGroup),
            groups_size = len(c_groups),

            primitives = Library.as_array(c_primitives, CBulletPrimitive),
            primitives_size = len(c_primitives)
        )


class CollisionMeshProcessor(o_mesh.BaseMeshProcessor):

    def _convert_model_set(self, model_set: o_modelset.ModelSet):
        if len(model_set.evaluated_mesh.polygons) == 0:
            return None

        raw_meshdata = RawCollisionMeshData()
        raw_meshdata.vertices = [
            v.co for v in model_set.evaluated_mesh.vertices]

        heio_mesh = model_set.obj.data.heio_mesh

        triangle_order = []

        if not heio_mesh.groups.initialized or heio_mesh.groups.attribute_invalid:
            triangle_order = list(range(len(model_set.evaluated_mesh.polygons)))

            raw_meshdata.triangle_indices = [
                vertex 
                for polygon in model_set.evaluated_mesh.polygons 
                for vertex in polygon.vertices
            ]

            raw_meshdata.groups.append(
                RawCollisionMeshDataGroup(
                    len(model_set.evaluated_mesh.polygons),
                    0, False
                )
            )

        else:
            layer_max = len(heio_mesh.groups) - 1
            triangles = [list() for _ in heio_mesh.groups]
            invalid_triangles = []

            attribute = model_set.evaluated_mesh.attributes.get(heio_mesh.groups.attribute_name, None)

            if attribute is not None:
                for group, polygon in zip(attribute.data, model_set.evaluated_mesh.polygons):
                    if group.value > layer_max:
                        invalid_triangles.append(polygon)
                    else:
                        triangles[group.value].append(polygon)
            else:
                triangles[0] = list(model_set.evaluated_mesh.polygons)

            for i, group in enumerate(heio_mesh.groups):
                layer_triangles = triangles[i]
                if len(layer_triangles) == 0:
                    continue

                for triangle in layer_triangles:
                    raw_meshdata.triangle_indices.extend(triangle.vertices)
                    triangle_order.append(triangle.index)

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

    def compile_output_to_files(self, use_multicore_processing: bool, directory: str):
        # TODO: compile with multithreading in c#, maybe
        progress_console.start("Compiling & writing collision meshes", len(self._output_queue))
        for i, output in enumerate(self._output_queue):
            name, c_meshdata = output
            progress_console.update(f"Compiling collision mesh \"{name}\"", i)

            filepath = os.path.join(directory, name + ".btmesh")

            Library.collision_mesh_write_to_file(
                c_meshdata,
                name,
                self._target_definition.data_versions.bullet_mesh,
                filepath
            )

        self._output_queue.clear()

