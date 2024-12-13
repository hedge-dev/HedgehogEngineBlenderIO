import bpy

from . import i_material

from ..dotnet import HEIO_NET
from ..register.definitions.target_info import TargetDefinition
from ..utility import progress_console

LAYER_LUT = {
    "AUTO": -1,
    "OPAQUE": 0,
    "TRANSPARENT": 1,
    "PUNCHTHROUGH": 2,
    "SPECIAL": 3,

    -1: "AUTO",
    0: "OPAQUE",
    1: "TRANSPARENT",
    2: "PUNCHTHROUGH",
    3: "SPECIAL"
}


class MeshConverter:

    _target_definition: TargetDefinition
    _material_converter: i_material.MaterialConverter

    _vertex_merge_mode: any
    _vertex_merge_distance: float
    _merge_split_edges: bool
    _create_mesh_slot_attributes: bool

    _converted_models: dict[any, bpy.types.Mesh]

    def __init__(
            self,
            target_definition: TargetDefinition,
            material_converter: TargetDefinition,
            vertex_merge_mode: str,
            vertex_merge_distance: float,
            merge_split_edges: bool,
            create_mesh_slot_attributes: bool):

        self._target_definition = target_definition
        self._material_converter = material_converter

        from ..exporting import o_enum
        self._vertex_merge_mode = o_enum.to_vertex_merge_mode(
            vertex_merge_mode)

        self._vertex_merge_distance = vertex_merge_distance
        self._merge_split_edges = merge_split_edges
        self._create_mesh_slot_attributes = create_mesh_slot_attributes

        self._converted_models = dict()

    def _convert_mesh_data(self, mesh_data: any):

        mesh = bpy.data.meshes.new(mesh_data.Name)

        if mesh_data.Vertices.Count == 0:
            return mesh

        ##################################################
        # Mesh initialization

        vertices = [(x.Position.X, -x.Position.Z, x.Position.Y)
                    for x in mesh_data.Vertices]

        faces = []
        for i in range(0, len(mesh_data.TriangleIndices), 3):
            faces.append((
                mesh_data.TriangleIndices[i],
                mesh_data.TriangleIndices[i + 1],
                mesh_data.TriangleIndices[i + 2])
            )

        mesh.from_pydata(vertices, [], faces, shade_flat=False)

        ##################################################
        # Material Data

        for sn_material, slot in zip(mesh_data.SetMaterials, mesh_data.SetSlots):
            material = self._material_converter.get_material(sn_material)
            mesh.materials.append(material)

            if LAYER_LUT[material.heio_material.layer] < slot.Type.value__:
                material.heio_material.layer = LAYER_LUT[slot.Type.value__]
                if material.heio_material.layer == 'SPECIAL':
                    material.heio_material.special_layer_name = slot.Name

        face_index = 0
        for i, face_count in enumerate(mesh_data.SetSizes):
            for f in range(face_index, face_index + face_count):
                mesh.polygons[f].material_index = i
            face_index += face_count

        ##################################################
        # Polygon layer attribute

        if self._create_mesh_slot_attributes:
            mesh.heio_mesh.initalize_layers()
            set_slot_indices = []
            special_layer_map = {}

            for layer, size in zip(mesh_data.SetSlots, mesh_data.SetSizes):
                layer_index = layer.Type.value__

                if layer_index == 3:
                    if layer.Name not in special_layer_map:
                        layer_index = 3 + len(special_layer_map)

                        special_layer_map[layer.Name] = layer_index

                        special_layer_name = mesh.heio_mesh.special_layer_names.new()
                        special_layer_name.name = layer.Name

                    else:
                        layer_index = special_layer_map[layer.Name]

                set_slot_indices.extend([layer_index] * size)

            mesh.attributes["Layer"].data.foreach_set("value", set_slot_indices)


        ##################################################
        # Texture coordinates

        for i, uvmap in enumerate(mesh_data.TextureCoordinates):
            uv_layer = mesh.uv_layers.new(
                name="UVMap" + (str(i + 1) if i > 0 else ""), do_init=False)

            for l, uv in enumerate(uvmap):
                uv_layer.uv[l].vector = (uv.X, uv.Y)

        ##################################################
        # Colors

        color_type = None

        if mesh_data.ByteColors is not None:
            color_type = 'BYTE_COLOR'
            color_data = mesh_data.ByteColors
        elif mesh_data.FloatColors is not None:
            color_type = 'FLOAT_COLOR'
            color_data = mesh_data.FloatColors

        if color_type is not None:
            for i, color_set in enumerate(color_data):
                color_set_name = "Colors"
                if i > 0:
                    color_set_name += str(i + 1)

                color_attribute = mesh.color_attributes.new(
                    "Color" + (str(i + 1) if i > 0 else ""),
                    color_type,
                    'CORNER')

                for j, color in enumerate(color_set):
                    color_attribute.data[j].color = (
                        color.X, color.Y, color.Z, color.W)

        ##################################################
        # Normal

        if mesh_data.PolygonNormals is None:
            mesh.normals_split_custom_set_from_vertices(
                [(v.Normal.X, -v.Normal.Z, v.Normal.Y) for v in mesh_data.Vertices]
            )
            mesh.validate()

        else:

            mesh.normals_split_custom_set(
                [(n.X, -n.Z, n.Y) for n in mesh_data.PolygonNormals]
            )

            # Cleaning up split edges

            mesh.validate()

            edge_loop_map = [([], []) for _ in mesh.edges]

            for polygon in mesh.polygons:

                for i, loop_index in enumerate(polygon.loop_indices):
                    next_loop_index = polygon.loop_indices[i - 2]

                    loop = mesh.loops[loop_index]

                    edge = mesh.edges[loop.edge_index]
                    edge_map = edge_loop_map[loop.edge_index]

                    if edge.vertices[0] == loop.vertex_index:
                        edge_map[0].append(loop_index)
                        edge_map[1].append(next_loop_index)
                    else:
                        edge_map[0].append(next_loop_index)
                        edge_map[1].append(loop_index)

            for edge in (x for x in mesh.edges if x.use_edge_sharp):
                loop_map = edge_loop_map[edge.index]
                if len(loop_map[0]) != 2:
                    continue

                nrm0 = mesh.corner_normals[loop_map[0][0]].vector
                nrm1 = mesh.corner_normals[loop_map[0][1]].vector
                nrm2 = mesh.corner_normals[loop_map[1][0]].vector
                nrm3 = mesh.corner_normals[loop_map[1][1]].vector

                if nrm0.dot(nrm1) > 0.995 and nrm2.dot(nrm3) > 0.995:
                    edge.use_edge_sharp = False

        return mesh

    def convert_model_sets(self, model_sets):
        result = []

        progress_console.start("Converting Models", len(model_sets))

        for i, model_set in enumerate(model_sets):
            model = model_set[0]
            progress_console.update(f"Converting model \"{model.Name}\"", i)

            if model in self._converted_models:
                mesh = self._converted_models[model]

            else:
                mesh_data = HEIO_NET.MESH_DATA.FromHEModel(
                    model,
                    self._vertex_merge_mode,
                    self._vertex_merge_distance,
                    self._merge_split_edges)

                mesh = self._convert_mesh_data(mesh_data)
                self._converted_models[model] = mesh

            result.append(mesh)

        progress_console.end()

        return result
