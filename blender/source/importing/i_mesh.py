import bpy
from mathutils import Vector

from . import i_material, i_model, i_sca_parameters, i_transform

from ..dotnet import HEIO_NET, SharpNeedle
from ..register.definitions import TargetDefinition
from ..utility import progress_console
from ..exceptions import HEIODevException
from ..exporting import o_enum

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
    _create_mesh_layer_attributes: bool
    _import_tangents: bool

    converted_models: dict[any, i_model.ModelInfo]
    _mesh_name_lookup: dict[str, i_model.ModelInfo]

    def __init__(
            self,
            target_definition: TargetDefinition,
            material_converter: TargetDefinition,
            vertex_merge_mode: str,
            vertex_merge_distance: float,
            merge_split_edges: bool,
            create_mesh_layer_attributes: bool,
            import_tangents: bool):

        self._target_definition = target_definition
        self._material_converter = material_converter

        self._vertex_merge_mode = o_enum.to_vertex_merge_mode(
            vertex_merge_mode)

        self._vertex_merge_distance = vertex_merge_distance
        self._merge_split_edges = merge_split_edges
        self._create_mesh_layer_attributes = create_mesh_layer_attributes
        self._import_tangents = import_tangents

        self.converted_models = dict()
        self._mesh_name_lookup = dict()

    def _convert_weights(self, mesh: bpy.types.Mesh, mesh_data, model):

        if not isinstance(model, SharpNeedle.MODEL) or model.Nodes.Count == 0:
            return

        weight_dummy_obj = bpy.data.objects.new("DUMMY", mesh)

        groups: list[bpy.types.VertexGroup] = []

        for node in model.Nodes:
            groups.append(weight_dummy_obj.vertex_groups.new(name=node.Name))

        used_groups = [False] * len(groups)

        for i, vertex in enumerate(mesh_data.Vertices):
            for weight in vertex.Weights:
                groups[weight.Index].add([i], weight.Weight, 'REPLACE')
                used_groups[weight.Index] = True

        to_remove = []
        for i, used in enumerate(used_groups):
            if not used:
                to_remove.append(groups[i])

        for group in to_remove:
            weight_dummy_obj.vertex_groups.remove(group)

        bpy.data.objects.remove(weight_dummy_obj)

    def _convert_morphs(self, mesh: bpy.types.Mesh, mesh_data):
        if mesh_data.MorphNames is None or mesh_data.MorphNames.Count == 0:
            return

        shapekey_positions = [
            [None] * len(mesh_data.Vertices) for _ in mesh_data.MorphNames]

        for i, vertex in enumerate(mesh_data.Vertices):
            for s, position in enumerate(vertex.MorphPositions):
                shapekey_positions[s][i] = Vector(
                    (position.X, -position.Z, position.Y))

        shapekey_dummy_obj = bpy.data.objects.new("DUMMY", mesh)

        shapekey_dummy_obj.shape_key_add(name="basis")
        for s, morph_name in enumerate(mesh_data.MorphNames):
            shapekey = shapekey_dummy_obj.shape_key_add(name=morph_name)
            for i, pos in enumerate(shapekey_positions[s]):
                shapekey.data[i].co += pos

        bpy.data.objects.remove(shapekey_dummy_obj)

    def _assign_materials(self, mesh: bpy.types.Mesh, mesh_data):
        material_indices = []
        material_index_mapping = {}

        for meshSet in mesh_data.MeshSets:
            material = self._material_converter.get_material(meshSet.Material)
            if material in material_index_mapping:
                material_indices.append(material_index_mapping[material])
                continue

            material_index = len(mesh.materials)
            material_indices.append(material_index)
            material_index_mapping[material] = material_index

            mesh.materials.append(material)

            slot = meshSet.Slot
            if LAYER_LUT[material.heio_material.render_layer] < slot.Type.value__:
                material.heio_material.render_layer = LAYER_LUT[slot.Type.value__]
                if material.heio_material.render_layer == 'SPECIAL':
                    material.heio_material.special_render_layer_name = slot.Name

        face_index = 0
        for material_index, meshSet in zip(material_indices, mesh_data.MeshSets):
            for f in range(face_index, face_index + meshSet.Size):
                mesh.polygons[f].material_index = material_index
            face_index += meshSet.Size

    @staticmethod
    def _create_polygon_layer_attributes(mesh: bpy.types.Mesh, mesh_data):
        layers = mesh.heio_mesh.render_layers
        layers.initialize()
        set_slot_indices = []
        special_layer_map = {}

        for meshSet in mesh_data.MeshSets:
            slot = meshSet.Slot
            layer_index = slot.Type.value__

            if layer_index == 3:
                if slot.Name not in special_layer_map:
                    layer_index = 3 + len(special_layer_map)

                    special_layer_map[slot.Name] = layer_index

                    special_layer_name = layers.new()
                    special_layer_name.name = slot.Name

                else:
                    layer_index = special_layer_map[slot.Name]

            set_slot_indices.extend([layer_index] * meshSet.Size)

        layers.attribute.data.foreach_set("value", set_slot_indices)

    @staticmethod
    def _create_polygon_meshgroup_attributes(mesh: bpy.types.Mesh, mesh_data):
        if len(mesh_data.GroupNames) == 1 and len(mesh_data.GroupNames[0]) == 0:
            return

        groups = mesh.heio_mesh.groups
        groups.initialize()
        group_indices = []
        set_offset = 0

        for group_index, group in enumerate(zip(mesh_data.GroupNames, mesh_data.GroupSetCounts)):

            if group_index == 0:
                meshgroup = groups[0]
            else:
                meshgroup = groups.new()

            meshgroup.name = group[0]

            for i in range(group[1]):
                group_indices.extend(
                    [group_index] * mesh_data.MeshSets[set_offset + i].Size)
            set_offset += group[1]

        groups.attribute.data.foreach_set("value", group_indices)

    @staticmethod
    def _convert_texcords(mesh: bpy.types.Mesh, mesh_data):
        for i, uvmap in enumerate(mesh_data.TextureCoordinates):
            uv_layer = mesh.uv_layers.new(
                name="UVMap" + (str(i) if i > 0 else ""), do_init=False)

            for l, uv in enumerate(uvmap):
                uv_layer.uv[l].vector = (uv.X, uv.Y)

    @staticmethod
    def _convert_colors(mesh: bpy.types.Mesh, mesh_data):
        color_type = 'BYTE_COLOR' if mesh_data.UseByteColors else 'FLOAT_COLOR'

        for i, color_set in enumerate(mesh_data.Colors):
            color_set_name = "Colors"
            if i > 0:
                color_set_name += str(i + 1)

            color_attribute = mesh.color_attributes.new(
                "Color" + (str(i) if i > 0 else ""),
                color_type,
                'CORNER')

            for output, color in zip(color_attribute.data, color_set):
                output.color = (color.X, color.Y, color.Z, color.W)

    @staticmethod
    def _convert_tangents(mesh: bpy.types.Mesh, mesh_data):
        if mesh_data.PolygonTangents is None:
            tangents = mesh.attributes.new("Tangent", 'FLOAT_VECTOR', 'POINT')

            for output, v in zip(tangents.data, mesh_data.Vertices):
                output.vector = (v.Tangent.X, -v.Tangent.Z, v.Tangent.Y)

        else:
            tangents = mesh.attributes.new("Tangent", 'FLOAT_VECTOR', 'CORNER')

            for output, t in zip(tangents.data, mesh_data.PolygonTangents):
                output.vector = (t.X, -t.Z, t.Y)

    @staticmethod
    def _convert_normals(mesh: bpy.types.Mesh, mesh_data):
        if mesh_data.PolygonNormals is None:
            mesh.normals_split_custom_set_from_vertices(
                [(v.Normal.X, -v.Normal.Z, v.Normal.Y)
                 for v in mesh_data.Vertices]
            )
            mesh.validate()

        else:

            mesh.normals_split_custom_set(
                [(n.X, -n.Z, n.Y) for n in mesh_data.PolygonNormals]
            )

            mesh.validate()
            MeshConverter._clean_up_sharp_edges(mesh)

    @staticmethod
    def _clean_up_sharp_edges(mesh: bpy.types.Mesh):
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

    def _convert_mesh_data(self, mesh_data: any, model: any, name_suffix: str,):

        mesh = bpy.data.meshes.new(mesh_data.Name + name_suffix)

        if mesh_data.Vertices.Count == 0:
            return mesh

        vertices = [i_transform.net_to_bpy_position(x.Position) for x in mesh_data.Vertices]

        faces = []
        for i in range(0, len(mesh_data.TriangleIndices), 3):
            faces.append((
                mesh_data.TriangleIndices[i],
                mesh_data.TriangleIndices[i + 1],
                mesh_data.TriangleIndices[i + 2])
            )

        mesh.from_pydata(vertices, [], faces, shade_flat=False)

        self._convert_weights(mesh, mesh_data, model)
        self._convert_morphs(mesh, mesh_data)
        self._assign_materials(mesh, mesh_data)

        self._create_polygon_meshgroup_attributes(mesh, mesh_data)

        if self._create_mesh_layer_attributes:
            self._create_polygon_layer_attributes(mesh, mesh_data)

        self._convert_texcords(mesh, mesh_data)
        self._convert_colors(mesh, mesh_data)

        if self._import_tangents:
            self._convert_tangents(mesh, mesh_data)

        self._convert_normals(mesh, mesh_data)

        return mesh

    def _convert_model(self, model, name_suffix: str):
        model_info = i_model.ModelInfo(model.Name + name_suffix, model)

        if isinstance(model, SharpNeedle.TERRAIN_MODEL):
            mesh_data = HEIO_NET.MESH_DATA.FromHEModel(
                model,
                self._vertex_merge_mode,
                self._vertex_merge_distance,
                self._merge_split_edges
            )

            mesh = self._convert_mesh_data(mesh_data, model, name_suffix)
            model_info.meshes.append(mesh)

            i_sca_parameters.convert_from_data(
                model, mesh.heio_mesh.sca_parameters, self._target_definition, 'model')

        else:  # Model
            mesh_datas = HEIO_NET.MESH_DATA.FromHEMeshGroups(
                model,
                self._vertex_merge_mode,
                self._vertex_merge_distance,
                self._merge_split_edges
            )

            for mesh_data in mesh_datas:
                model_info.meshes.append(
                    self._convert_mesh_data(mesh_data, model, name_suffix))

            if model.Morphs != None:
                for morph in model.Morphs:
                    morph_data = HEIO_NET.MESH_DATA.FromHEMorph(
                        model,
                        morph,
                        self._vertex_merge_mode,
                        self._vertex_merge_distance,
                        self._merge_split_edges
                    )

                    morph_mesh = self._convert_mesh_data(
                        morph_data, model, name_suffix)
                    model_info.meshes.append(morph_mesh)

        return model_info

    def _convert_lod_models(self, model_info: i_model.ModelInfo, model_set):
        progress_console.start(
            "Converting LOD Models",
            len(model_set.Models) - 1)

        model_info.sn_lod_info = model_set.LODInfo

        for i, lod_model in enumerate(model_set.Models):
            if i == 0:
                continue

            progress_console.update(f"Converting LOD level {i}", i - 1)

            lod_model_info = self._convert_model(lod_model, f"_lv{i}")

            model_info.lod_models.append(lod_model_info)

        progress_console.end()

    def convert_model_sets(self, model_sets) -> list[i_model.ModelInfo]:
        sn_materials = HEIO_NET.MODEL_HELPER.GetMaterials(model_sets)
        self._material_converter.convert_materials(sn_materials)

        result = []

        progress_console.start("Converting Models", len(model_sets))

        for i, model_set in enumerate(model_sets):
            model = model_set.Models[0]
            progress_console.update(f"Converting model \"{model.Name}\"", i)

            if model in self.converted_models:
                model_info = self.converted_models[model]

            else:
                model_info = self._convert_model(model, "")
                self.converted_models[model] = model_info
                self._mesh_name_lookup[model.Name] = model_info

                if model_set.LODInfo is not None:
                    self._convert_lod_models(model_info, model_set)

            result.append(model_info)

        progress_console.end()

        return result

    def get_model_info(self, key: any):

        if isinstance(key, str):
            if key in self._mesh_name_lookup:
                return self._mesh_name_lookup[key]

            mesh = bpy.data.meshes.new(key)
            model_info = i_model.ModelInfo(key, None, mesh)
            self._mesh_name_lookup[key] = model_info
            return model_info

        if key in self.converted_models:
            return self.converted_models[key]

        if hasattr(key, "Name") and key.Name in self._mesh_name_lookup:
            return self._mesh_name_lookup[key.Name]

        raise HEIODevException("Model lookup failed")
