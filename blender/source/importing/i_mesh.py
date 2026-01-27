import bpy
from mathutils import Vector

from . import i_material, i_model, i_sca_parameters, i_transform

from ..external import HEIONET, util, TPointer, CModelSet, CMeshDataSet, CMeshData, CVertex, CVertexWeight, CMeshDataMeshSetInfo, CMeshDataMeshGroupInfo
from ..register.definitions import TargetDefinition
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

    _create_mesh_layer_attributes: bool

    _converted_models: dict[int, i_model.ModelInfo]
    _mesh_name_lookup: dict[str, i_model.ModelInfo]

    def __init__(
            self,
            target_definition: TargetDefinition,
            material_converter: TargetDefinition,
            create_mesh_layer_attributes: bool):

        self._target_definition = target_definition
        self._material_converter = material_converter

        self._create_mesh_layer_attributes = create_mesh_layer_attributes

        self._converted_models = dict()
        self._mesh_name_lookup = dict()

    def _convert_weights(self, mesh: bpy.types.Mesh, mesh_data_set: CMeshDataSet, vertex_data: list[CVertex]):

        if not mesh_data_set.nodes:
            return

        weight_dummy_obj = bpy.data.objects.new("DUMMY", mesh)

        groups: list[bpy.types.VertexGroup] = []

        for i in range(mesh_data_set.nodes_size):
            node = mesh_data_set.nodes[i]
            groups.append(weight_dummy_obj.vertex_groups.new(name=node.name))

        used_groups = [False] * len(groups)

        for i, vertex in enumerate(vertex_data):
            for j in range(vertex.weights_size):
                weight: CVertexWeight = vertex.weights[j]
                groups[weight.index].add([i], weight.weight, 'REPLACE')
                used_groups[weight.index] = True

        to_remove = []
        for i, used in enumerate(used_groups):
            if not used:
                to_remove.append(groups[i])

        for group in to_remove:
            weight_dummy_obj.vertex_groups.remove(group)

        bpy.data.objects.remove(weight_dummy_obj)

    def _convert_morphs(self, mesh: bpy.types.Mesh, mesh_data: CMeshData, vertex_data: list[CVertex]):
        if not mesh_data.morph_names:
            return

        shapekey_positions = [
            [None] * mesh_data.vertices_size for _ in range(mesh_data.morph_names_size)]

        for i, vertex in enumerate(vertex_data):
            for s in range(vertex.morph_positions_size):
                position = vertex.morph_positions[s]
                shapekey_positions[s][i] = i_transform.c_to_bpy_position(position)

        shapekey_dummy_obj = bpy.data.objects.new("DUMMY", mesh)

        shapekey_dummy_obj.shape_key_add(name="basis")
        for s in range(mesh_data.morph_names_size):
            morph_name = mesh_data.morph_names[s]
            shapekey = shapekey_dummy_obj.shape_key_add(name=morph_name)
            for i, pos in enumerate(shapekey_positions[s]):
                shapekey.data[i].co += pos
            shapekey.value = 0

        bpy.data.objects.remove(shapekey_dummy_obj)

    def _assign_materials(self, mesh: bpy.types.Mesh, mesh_data: CMeshData):
        material_indices = []
        material_index_mapping = {}

        for i in range(mesh_data.mesh_sets_size):
            mesh_set: CMeshDataMeshSetInfo = mesh_data.mesh_sets[i]
            material = self._material_converter.get_material(mesh_set.material_reference)

            if material in material_index_mapping:
                material_indices.append(material_index_mapping[material])
                continue

            material_index = len(mesh.materials)
            material_indices.append(material_index)
            material_index_mapping[material] = material_index

            mesh.materials.append(material)

            if LAYER_LUT[material.heio_material.render_layer] < mesh_set.mesh_slot_type:
                material.heio_material.render_layer = LAYER_LUT[mesh_set.mesh_slot_type]
                if material.heio_material.render_layer == 'SPECIAL':
                    material.heio_material.special_render_layer_name = mesh_set.mesh_slot_name

        face_index = 0
        for i, material_index in enumerate(material_indices):
            mesh_set = mesh_data.mesh_sets[i]
            for f in range(face_index, face_index + mesh_set.size):
                mesh.polygons[f].material_index = material_index
            face_index += mesh_set.size

    @staticmethod
    def _create_polygon_layer_attributes(mesh: bpy.types.Mesh, mesh_data: CMeshData):
        layers = mesh.heio_mesh.render_layers
        layers.initialize()
        set_slot_indices = []
        special_layer_map = {}

        for i in range(mesh_data.mesh_sets_size):
            mesh_set: CMeshDataMeshSetInfo = mesh_data.mesh_sets[i]

            if mesh_set.mesh_slot_type == 3:
                if mesh_set.mesh_slot_name not in special_layer_map:
                    layer_index = 3 + len(special_layer_map)

                    special_layer_map[mesh_set.mesh_slot_name] = layer_index

                    special_layer_name = layers.new()
                    special_layer_name.name = mesh_set.mesh_slot_name

                else:
                    layer_index = special_layer_map[mesh_set.mesh_slot_name]

            set_slot_indices.extend([layer_index] * mesh_set.size)

        layers.attribute.data.foreach_set("value", set_slot_indices)

    @staticmethod
    def _create_polygon_meshgroup_attributes(mesh: bpy.types.Mesh, mesh_data: CMeshData):
        if mesh_data.groups_size == 1 and len(mesh_data.groups[0].name) == 0:
            return

        groups = mesh.heio_mesh.groups
        groups.initialize()
        group_indices = []
        set_offset = 0

        for i in range(mesh_data.groups_size):
            group: CMeshDataMeshGroupInfo = mesh_data.groups[i]

            if i == 0:
                meshgroup = groups[0]
            else:
                meshgroup = groups.new()

            meshgroup.name = group.name

            for j in range(group.size):
                group_indices.extend([i] * mesh_data.mesh_sets[set_offset + j].size)
            set_offset += group.size

        groups.attribute.data.foreach_set("value", group_indices)

    @staticmethod
    def _convert_texcords(mesh: bpy.types.Mesh, mesh_data: CMeshData):
        for i in range(mesh_data.texture_coordinates_size):
            texture_coordinates = mesh_data.texture_coordinates[i]

            uv_layer = mesh.uv_layers.new(
                name="UVMap" + (str(i) if i > 0 else ""), do_init=False)

            for l, output in enumerate(uv_layer.uv):
                uv = texture_coordinates[l]
                output.vector = (uv.x, uv.y)

    @staticmethod
    def _convert_colors(mesh: bpy.types.Mesh, mesh_data: CMeshData):
        color_type = 'BYTE_COLOR'

        for i in range(mesh_data.mesh_sets_size):
            if not mesh_data.mesh_sets[i].use_byte_colors:
                color_type = 'FLOAT_COLOR'
                break

        for i in range(mesh_data.colors_size):
            colors = mesh_data.colors[i]

            color_set_name = "Colors"
            if i > 0:
                color_set_name += str(i + 1)

            color_attribute = mesh.color_attributes.new(
                "Color" + (str(i) if i > 0 else ""),
                color_type,
                'CORNER')

            for l, output in enumerate(color_attribute.data):
                color = colors[l]
                output.color = (color.x, color.y, color.z, color.w)

    @staticmethod
    def _convert_normals(mesh: bpy.types.Mesh, mesh_data: CMeshData, vertices: list[CVertex]):
        if not mesh_data.polygon_normals:


            mesh.normals_split_custom_set_from_vertices(
                [(v.normal.x, -v.normal.z, v.normal.y)
                 for v in vertices]
            )
            mesh.validate()

        else:
            normals = []
            for i in range(mesh_data.triangle_index_count):
                normals.append(mesh_data.polygon_normals[i])

            mesh.normals_split_custom_set(
                [i_transform.c_to_bpy_position(n) for n in normals]
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

    def _convert_mesh_data(self, mesh_data: CMeshData, mesh_data_set: CMeshDataSet, name_suffix: str,):

        mesh = bpy.data.meshes.new(mesh_data.name + name_suffix)

        if mesh_data.vertices_size == 0:
            return mesh
        
        # caching the actual vertex data since we use it several times
        vertex_data: list[CVertex] = []
        for i in range(mesh_data.vertices_size):
            vertex_data.append(mesh_data.vertices[i])

        vertices = [i_transform.c_to_bpy_position(x.position) for x in vertex_data]

        faces = []
        for i in range(0, mesh_data.triangle_index_count, 3):
            faces.append((
                mesh_data.triangle_indices[i],
                mesh_data.triangle_indices[i + 1],
                mesh_data.triangle_indices[i + 2]
            ))

        mesh.from_pydata(vertices, [], faces, shade_flat=False)

        self._convert_weights(mesh, mesh_data_set, vertex_data)
        self._convert_morphs(mesh, mesh_data, vertex_data)
        self._assign_materials(mesh, mesh_data)

        self._create_polygon_meshgroup_attributes(mesh, mesh_data)

        if self._create_mesh_layer_attributes:
            self._create_polygon_layer_attributes(mesh, mesh_data)

        self._convert_texcords(mesh, mesh_data)
        self._convert_colors(mesh, mesh_data)

        self._convert_normals(mesh, mesh_data, vertex_data)

        return mesh

    def _convert_model(self, mesh_data_set: CMeshDataSet, name_suffix: str):
        
        model_info = i_model.ModelInfo(mesh_data_set.name + name_suffix, mesh_data_set)

        for i in range(mesh_data_set.mesh_data_size):
            mesh_data: CMeshData = mesh_data_set.mesh_data[i]
            mesh = self._convert_mesh_data(mesh_data, mesh_data_set, name_suffix)
            model_info.meshes.append(mesh)

            if not mesh_data_set.nodes:
                i_sca_parameters.convert_from_root(
                    mesh_data_set.sample_chunk_node_root, 
                    mesh.heio_mesh.sca_parameters, 
                    self._target_definition, 
                    'model'
                )

        return model_info

    def _convert_lod_models(self, model_info: i_model.ModelInfo, model_set: CModelSet):
        progress_console.start(
            "Converting LOD Models",
            model_set.mesh_data_sets_size - 1
        )

        model_info.c_lod_items = []
        model_info.c_lod_unknown1 = model_set.lod_unknown1

        for i in range(model_set.lod_items_size):
            model_info.c_lod_items.append(model_set.lod_items[i])

        for i in range(1, model_set.mesh_data_sets_size):
            progress_console.update(f"Converting LOD level {i}", i - 1)

            lod_model_info = self._convert_model(model_set.mesh_data_sets[i].contents, f"_lv{i}")

            model_info.lod_models.append(lod_model_info)

        progress_console.end()

    def convert_model_sets(self, model_sets: list[TPointer[CModelSet]]) -> list[i_model.ModelInfo]:
        c_materials = HEIONET.model_get_materials(model_sets)
        self._material_converter.convert_materials(c_materials)

        result = []

        progress_console.start("Converting Models", len(model_sets))

        for i, model_set in enumerate(model_sets):
            model_set_address = util.pointer_to_address(model_set)
            model_set: CModelSet = model_set.contents
        
            main_mesh_set: CMeshDataSet =  model_set.mesh_data_sets[0].contents
            model_name = main_mesh_set.name

            progress_console.update(f"Converting model \"{model_name}\"", i)

            if model_set_address in self._converted_models:
                model_info = self._converted_models[model_set_address]

            else:
                model_info = self._convert_model(main_mesh_set, "")
                self._converted_models[model_set_address] = model_info
                self._mesh_name_lookup[model_name] = model_info

                if model_set.lod_items:
                    self._convert_lod_models(model_info, model_set)

            result.append(model_info)

        progress_console.end()

        return result
