import bpy

from . import i_enum, i_transform
from ..dotnet import HEIO_NET
from ..register.definitions import TargetDefinition
from ..utility import progress_console
from ..exceptions import HEIODevException


class CollisionMeshConverter:

    _target_definition: TargetDefinition

    _merge_vertices: bool
    _vertex_merge_distance: float
    _remove_unused_vertices: bool

    converted_meshes: dict[any, bpy.types.Mesh]
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

        self.converted_meshes = {}
        self._mesh_name_lookup = {}

    @staticmethod
    def _convert_layers(mesh, mesh_data):
        layers = mesh.heio_collision_mesh.layers
        layers.initialize()

        set_slot_indices = []
        for i, mesh_layer in enumerate(mesh_data.Layers):
            if i == 0:
                layer = layers[0]
                layer.value = mesh_layer.Value
            else:
                layer = layers.new(value=mesh_layer.Value)

            layer.is_convex = mesh_layer.IsConvex

            if layer.is_convex:
                layer.convex_type.value = mesh_layer.Type

                for i, value in enumerate(mesh_layer.FlagValues):
                    layer.convex_flags.new(value=value)

            set_slot_indices.extend([i] * mesh_layer.Size)

        layers.attribute.data.foreach_set("value", set_slot_indices)

    @staticmethod
    def _convert_types(mesh, mesh_data):
        if mesh_data.TypeValues is None:
            return

        types = mesh.heio_collision_mesh.types
        types.initialize()
        types.attribute.data.foreach_set("value", [x for x in mesh_data.Types])

        for i, value in enumerate(mesh_data.TypeValues):
            if i == 0:
                types[0].value = value
            else:
                types.new(value=value)

    @staticmethod
    def _convert_flags(mesh, mesh_data):
        if mesh_data.FlagValues is None:
            return

        flags = mesh.heio_collision_mesh.flags
        flags.initialize()
        flags.attribute.data.foreach_set("value", [x for x in mesh_data.Flags])

        for i, value in enumerate(mesh_data.FlagValues):
            if i == 0:
                flags[0].value = value
            else:
                flags.new(value=value)

    @staticmethod
    def _convert_primitives(mesh, collision_mesh):
        primitives = mesh.heio_collision_mesh.primitives

        for sn_primitive in collision_mesh.Primitives:
            primitive = primitives.new()

            primitive.shape_type = i_enum.from_bullet_shape_type(
                sn_primitive.ShapeType)

            primitive.position = (
                sn_primitive.Position.X, -sn_primitive.Position.Z, sn_primitive.Position.Y)

            primitive.rotation = i_transform.net_to_bpy_quaternion(
                sn_primitive.Rotation)

            primitive.dimensions = (
                sn_primitive.Dimensions.X, sn_primitive.Dimensions.Z, sn_primitive.Dimensions.Y)

            primitive.surface_type.value = sn_primitive.SurfaceType

            flags = sn_primitive.SurfaceFlags
            for i in range(32):
                if (flags & 1) != 0:
                    primitive.surface_flags.new(value=i)
                flags >> 1

    def _convert_mesh(self, collision_mesh):

        mesh_data = HEIO_NET.COLLISION_MESH_DATA.FromBulletMesh(
            collision_mesh,
            self._merge_vertices,
            self._vertex_merge_distance,
            self._remove_unused_vertices)

        mesh = bpy.data.meshes.new(collision_mesh.Name)

        if mesh_data.Vertices.Count == 0:
            return mesh

        vertices = [(x.X, -x.Z, x.Y) for x in mesh_data.Vertices]

        faces = []
        for i in range(0, len(mesh_data.TriangleIndices), 3):
            faces.append((
                mesh_data.TriangleIndices[i],
                mesh_data.TriangleIndices[i + 1],
                mesh_data.TriangleIndices[i + 2])
            )

        mesh.from_pydata(vertices, [], faces, shade_flat=True)

        self._convert_layers(mesh, mesh_data)
        self._convert_types(mesh, mesh_data)
        self._convert_flags(mesh, mesh_data)
        self._convert_primitives(mesh, collision_mesh)

        return mesh

    def convert_collision_meshes(self, collision_meshes):
        result = []

        progress_console.start(
            "Converting Collision Meshes", len(collision_meshes))

        for i, collision_mesh in enumerate(collision_meshes):
            progress_console.update(
                f"Converting Collision Mesh \"{collision_mesh.Name}\"", i)

            if collision_mesh in self.converted_meshes:
                mesh = self.converted_meshes[collision_mesh]

            else:
                mesh = self._convert_mesh(collision_mesh)
                self.converted_meshes[collision_mesh] = mesh
                self._mesh_name_lookup[collision_mesh.Name] = mesh

            result.append(mesh)

        progress_console.end()

        return result

    def get_mesh(self, key: any):

        if isinstance(key, str):
            if key in self._mesh_name_lookup:
                return self._mesh_name_lookup[key]

            mesh = bpy.data.meshes.new(key)
            self._mesh_name_lookup[key] = mesh
            return mesh

        if key in self.converted_meshes:
            return self.converted_meshes[key]

        if hasattr(key, "Name") and key.Name in self._mesh_name_lookup:
            return self._mesh_name_lookup[key.Name]

        raise HEIODevException("Model lookup failed")
