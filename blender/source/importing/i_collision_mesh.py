import bpy
from mathutils import Vector

from ..dotnet import HEIO_NET, SharpNeedle
from ..register.definitions import TargetDefinition
from ..register.property_groups.collision_mesh_properties import HEIO_CollisionMesh
from ..utility import progress_console
from ..exceptions import HEIODevException


class CollisionMeshConverter:

    _target_definition: TargetDefinition

    converted_meshes: dict[any, bpy.types.Mesh]
    _mesh_name_lookup: dict[str, bpy.types.Mesh]

    def __init__(self, target_definition: TargetDefinition):

        self._target_definition = target_definition

        self.converted_meshes = {}
        self._mesh_name_lookup = {}

    def _convert_mesh(self, collision_mesh):

        mesh_data = HEIO_NET.COLLISION_MESH_DATA.FromBulletMesh(collision_mesh)

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

        col_mesh: HEIO_CollisionMesh = mesh.heio_collision_mesh

        col_mesh.layers.initialize()
        set_slot_indices = []
        for i, mesh_layer in enumerate(mesh_data.Layers):
            if i == 0:
                layer = col_mesh.layers[0]
                layer.value = mesh_layer.Value
            else:
                layer = col_mesh.layers.new(value=mesh_layer.Value)

            layer.is_convex = mesh_layer.IsConvex

            if layer.is_convex:
                layer.convex_type.value = mesh_layer.Type

                for i, value in enumerate(mesh_layer.FlagValues):
                    layer.convex_flags.new(value=value)

            set_slot_indices.extend([i] * mesh_layer.Size)

        col_mesh.layers.attribute.data.foreach_set("value", set_slot_indices)

        if mesh_data.TypeValues is not None:
            col_mesh.types.initialize()

            attribute = col_mesh.types.attribute
            attribute.data.foreach_set("value", [x for x in mesh_data.Types])

            for i, value in enumerate(mesh_data.TypeValues):
                if i == 0:
                    col_mesh.types[0].value = value
                else:
                    col_mesh.types.new(value=value)

        if mesh_data.FlagValues is not None:
            col_mesh.flags.initialize()

            attribute = col_mesh.flags.attribute
            attribute.data.foreach_set("value", [x for x in mesh_data.Flags])

            for i, value in enumerate(mesh_data.FlagValues):
                if i == 0:
                    col_mesh.flags[0].value = value
                else:
                    col_mesh.flags.new(value=value)

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
