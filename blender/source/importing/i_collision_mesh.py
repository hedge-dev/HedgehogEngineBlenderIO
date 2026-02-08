import bpy

from . import i_transform
from ..external import enums, util, TPointer, CCollisionMeshData, CCollisionMeshDataGroup, CBulletPrimitive
from ..register.definitions import TargetDefinition
from ..utility import progress_console


class CollisionMeshConverter:

    _target_definition: TargetDefinition

    _merge_vertices: bool
    _vertex_merge_distance: float
    _remove_unused_vertices: bool

    _converted_meshes: dict[int, bpy.types.Mesh]
    _mesh_name_lookup: dict[str, bpy.types.Mesh]

    def __init__(
            self,
            target_definition: TargetDefinition,
            merge_vertices: bool,
            vertex_merge_distance: float,
            remove_unused_vertices: bool):

        self._target_definition = target_definition

        self._merge_vertices = merge_vertices
        self._vertex_merge_distance = vertex_merge_distance
        self._remove_unused_vertices = remove_unused_vertices

        self._converted_meshes = {}
        self._mesh_name_lookup = {}

    @staticmethod
    def _convert_groups(mesh, collision_mesh_data: CCollisionMeshData):
        groups = mesh.heio_mesh.groups

        set_slot_indices = []
        for i in range(collision_mesh_data.groups_size):
            group = groups.new(name=f"Shape_{i}")
            mesh_group: CCollisionMeshDataGroup = collision_mesh_data.groups[i]

            group.collision_layer.value = mesh_group.layer

            if mesh_group.is_convex:
                group.is_convex_collision = True
                group.convex_type.value = mesh_group.convex_type

                for j in range(mesh_group.convex_flag_values_size):
                    group.convex_flags.new(value=mesh_group.convex_flag_values[j])

            set_slot_indices.extend([i] * mesh_group.size)

        groups.initialize()
        groups.attribute.data.foreach_set("value", set_slot_indices)

    @staticmethod
    def _convert_types(mesh, collision_mesh_data: CCollisionMeshData):
        if not collision_mesh_data.type_values:
            return

        types = mesh.heio_mesh.collision_types

        for i in range(collision_mesh_data.type_values_size):
            types.new(value=collision_mesh_data.type_values[i])

        types.initialize()
        types.attribute.data.foreach_set("value", [collision_mesh_data.types[i] for i in range(collision_mesh_data.types_size)])

    @staticmethod
    def _convert_flags(mesh, collision_mesh_data: CCollisionMeshData):
        if not collision_mesh_data.flag_values:
            return

        flags = mesh.heio_mesh.collision_flags

        for i in range(collision_mesh_data.flag_values_size):
            flags.new(value=collision_mesh_data.flag_values[i])

        flags.initialize()
        flags.attribute.data.foreach_set("value", [collision_mesh_data.flags[i] for i in range(collision_mesh_data.flags_size)])

    @staticmethod
    def _convert_primitives(mesh, collision_mesh_data: CCollisionMeshData):
        primitives = mesh.heio_mesh.collision_primitives

        for i in range(collision_mesh_data.primitives_size):
            c_primitive: CBulletPrimitive = collision_mesh_data.primitives[i]
            primitive = primitives.new()

            primitive.shape_type = enums.BULLET_PRIMITIVE_SHAPE_TYPE[c_primitive.shape_type]
            primitive.position = i_transform.c_to_bpy_position(c_primitive.position)
            primitive.rotation = i_transform.c_to_bpy_quaternion(c_primitive.rotation)
            primitive.dimensions = i_transform.c_to_bpy_scale(c_primitive.dimensions)

            primitive.collision_layer.value = c_primitive.surface_layer
            primitive.collision_type.value = c_primitive.surface_type

            flags = c_primitive.surface_flags
            for j in range(32):
                if (flags & 1) != 0:
                    primitive.collision_flags.new(value=j)
                flags >> 1

    def _convert_mesh(self, collision_mesh_data: CCollisionMeshData):

        mesh = bpy.data.meshes.new(collision_mesh_data.name)

        if collision_mesh_data.vertices_size == 0:
            return mesh

        vertices = [i_transform.c_to_bpy_position(collision_mesh_data.vertices[i]) for i in range(collision_mesh_data.vertices_size)]

        faces = []
        for i in range(0, collision_mesh_data.triangle_indices_size, 3):
            faces.append(
                (
                    collision_mesh_data.triangle_indices[i],
                    collision_mesh_data.triangle_indices[i + 1],
                    collision_mesh_data.triangle_indices[i + 2]
                )
            )

        mesh.from_pydata(vertices, [], faces, shade_flat=True)

        self._convert_groups(mesh, collision_mesh_data)
        self._convert_types(mesh, collision_mesh_data)
        self._convert_flags(mesh, collision_mesh_data)
        self._convert_primitives(mesh, collision_mesh_data)

        return mesh

    def convert_collision_meshes(self, collision_meshes: list[TPointer[CCollisionMeshData]]):
        result = []

        progress_console.start(
            "Converting Collision Meshes", len(collision_meshes))

        for i, collision_mesh_data in enumerate(collision_meshes):
            collision_mesh_data_address = util.pointer_to_address(collision_mesh_data)
            collision_mesh_data: CCollisionMeshData = collision_mesh_data.contents

            progress_console.update(
                f"Converting Collision Mesh \"{collision_mesh_data.name}\"", i)

            if collision_mesh_data_address in self._converted_meshes:
                mesh = self._converted_meshes[collision_mesh_data_address]

            else:
                mesh = self._convert_mesh(collision_mesh_data)
                self._converted_meshes[collision_mesh_data_address] = mesh
                self._mesh_name_lookup[collision_mesh_data.name] = mesh

            result.append(mesh)

        progress_console.end()

        return result
