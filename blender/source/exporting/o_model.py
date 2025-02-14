import bpy
from mathutils import Vector, Matrix

from . import o_mesh, o_modelset, o_transform, o_material, o_object_manager, o_sca_parameters
from ..register.definitions import TargetDefinition
from ..register.property_groups.mesh_properties import MESH_DATA_TYPES
from ..dotnet import HEIO_NET, SharpNeedle, System
from ..exceptions import HEIOUserException
from ..utility import progress_console


class RawVertex:

    position: Vector
    normal: Vector
    morph_positions: None | list[Vector]
    weights: list[tuple[str, float]]

    def __init__(
            self,
            position: Vector,
            normal: Vector,
            morph_positions: None | list[Vector],
            weights: list[tuple[str, float]]):

        self.position = position
        self.normal = normal.normalized()
        self.morph_positions = morph_positions
        self.weights = weights

    def convert_to_net(self, matrix: tuple[Matrix, Matrix] | None, weight_index_map: dict[str, int] | None):

        position = self.position
        normal = self.normal
        morph_positions = self.morph_positions

        if matrix is not None:
            position = matrix[0] @ position
            normal = (matrix[1] @ normal).normalized()

            if morph_positions is not None:
                morph_positions = [matrix[0] @ mp for mp in morph_positions]

        weights = []

        if weight_index_map is not None:
            for name, weight in self.weights:
                index = weight_index_map.get(name, None)
                if index is not None:
                    weights.append(HEIO_NET.VERTEX_WEIGHT(index, weight))

        return HEIO_NET.VERTEX(
            o_transform.bpy_to_net_position(position),

            ([o_transform.bpy_to_net_position(mp)
              for mp in morph_positions]
             if morph_positions is not None
             else None),

            o_transform.bpy_to_net_position(normal),
            HEIO_NET.UV_DIRECTION(System.VECTOR3(
                0, 0, 0), System.VECTOR3(0, 0, 0)),
            HEIO_NET.UV_DIRECTION(System.VECTOR3(
                0, 0, 0), System.VECTOR3(0, 0, 0)),
            weights
        )


class RawMeshData:

    vertices: list[RawVertex]
    triangle_indices: list[int]

    polygon_uv_directions: list[tuple[Vector, Vector]]
    polygon_uv_directions2: list[tuple[Vector, Vector]] | None

    texture_coordinates: list[any]
    colors: list[any]

    mesh_sets: list[any]
    group_names: list[str]
    group_set_counts: list[int]

    morph_names: None

    def __init__(self):
        self.vertices = []
        self.triangle_indices = []

        self.polygon_uv_directions = []
        self.polygon_uv_directions2 = None

        self.texture_coordinates = []
        self.colors = []

        self.mesh_sets = []
        self.group_names = []
        self.group_set_counts = []

        self.morph_names = None

    def convert_to_net(self, matrix: tuple[Matrix, Matrix] | None, weight_index_map: dict[str, int] | None):

        polygon_tangents = self.polygon_uv_directions
        polygon_tangents2 = self.polygon_uv_directions2

        if matrix is not None:
            normal_matrix = matrix[1]
            polygon_tangents = [
                ((normal_matrix @ t).normalized(),
                 (normal_matrix @ b).normalized())
                for t, b in polygon_tangents
            ]

            if polygon_tangents2 is not None:
                polygon_tangents2 = [
                    ((normal_matrix @ t).normalized(),
                     (normal_matrix @ b).normalized())
                    for t, b in polygon_tangents2
                ]

        to_net = o_transform.bpy_to_net_position

        return HEIO_NET.MESH_DATA(
            "",  # name is only important for import

            [v.convert_to_net(matrix, weight_index_map)
             for v in self.vertices],

            self.triangle_indices,
            None,

            [HEIO_NET.UV_DIRECTION(to_net(t), to_net(b))
             for t, b in polygon_tangents],

            [HEIO_NET.UV_DIRECTION(to_net(t), to_net(b))
             for t, b in polygon_tangents2] if polygon_tangents2 is not None else None,

            self.texture_coordinates,
            self.colors,

            self.mesh_sets,
            self.group_names,
            self.group_set_counts,

            self.morph_names
        )


class ModelProcessor(o_mesh.BaseMeshProcessor):

    mode: str

    _material_processor: o_material.MaterialProcessor

    _auto_sca_parameters: bool
    _use_pose_bone_matrices: bool
    _bone_orientation: str
    _topology: any
    _optimized_vertex_data: bool

    _lod_output: dict[bpy.types.Object, any]

    def __init__(
            self,
            target_definition: TargetDefinition,
            object_manager: o_object_manager.ObjectManager,
            model_set_manager: o_modelset.ModelSetManager,
            write_dependencies: bool,

            material_processor: o_material.MaterialProcessor,
            auto_sca_parameters: bool,
            use_pose_bone_matrices: bool,
            bone_orientation: str,
            topology: any,
            optimized_vertex_data: bool):

        super().__init__(target_definition, object_manager,
                         model_set_manager, write_dependencies)

        self.mode = 'AUTO'

        self._material_processor = material_processor

        self._auto_sca_parameters = auto_sca_parameters
        self._use_pose_bone_matrices = use_pose_bone_matrices
        self._bone_orientation = bone_orientation
        self._topology = topology
        self._optimized_vertex_data = optimized_vertex_data

        self._lod_output = {}

    ##################################################

    def _pre_prepare_mesh_data(self, model_sets):
        all_materials = set()

        for model_set in model_sets:
            if len(model_set.evaluated_mesh.polygons) == 0:
                continue

            materials = [
                x.material for x in model_set.evaluated_object.material_slots]
            if any([m is None for m in materials]):
                raise HEIOUserException(
                    f"Object \"{model_set.obj.name}\" has empty material slots!")

            all_materials.update(materials)

        self._material_processor.convert_materials(all_materials)

    def _convert_vertices(self, model_set: o_modelset.ModelSet):
        groupnames = [g.name for g in model_set.evaluated_object.vertex_groups]

        if model_set.is_weighted:
            minWeight = 0.5 / 255

            def get_weights(vertex: bpy.types.MeshVertex):
                return [(groupnames[g.group], g.weight) for g in vertex.groups if g.weight > minWeight]

        elif model_set.attached_bone_name is not None:
            attached_bone_weight = [(model_set.attached_bone_name, 1)]

            def get_weights(vertex: bpy.types.MeshVertex):
                return attached_bone_weight

        else:
            empty_weights = []

            def get_weights(vertex: bpy.types.MeshVertex):
                return empty_weights

        if model_set.evaluated_shape_positions is not None:
            def get_shape_positions(vertex: bpy.types.MeshVertex):
                return [b[vertex.index] - vertex.co for b in model_set.evaluated_shape_positions]

        else:
            def get_shape_positions(vertex: bpy.types.MeshVertex):
                return None

        loop_normals: list[Vector] = [x.vector.copy()
                                      for x in model_set.evaluated_mesh.vertex_normals]
        for loop in model_set.evaluated_mesh.loops:
            # loops on the same vertex must share the same normal, no need to merge or compare
            loop_normals[loop.vertex_index] = loop.normal

        return [RawVertex(
            vertex.co.copy(),
            loop_normals[vertex.index].copy(),
            get_shape_positions(vertex),
            get_weights(vertex)
        ) for vertex in model_set.evaluated_mesh.vertices]

    def _map_polygons(self, model_set: o_modelset.ModelSet):
        group_names = []
        layer_names = []
        materials = []

        heiomesh = model_set.obj.data.heio_mesh

        if not heiomesh.groups.initialized or heiomesh.groups.attribute_invalid:
            group_names.append("")

            def get_group_index(polygon: bpy.types.MeshPolygon):
                return 0

        else:
            group_name_lut = {}
            group_name_map = []

            for group in heiomesh.groups:
                if group.name not in group_name_lut:
                    index = len(group_names)
                    group_name_lut[group.name] = index
                    group_names.append(group.name)
                else:
                    index = group_name_lut[group.name]

                group_name_map.append(index)

            group_attribute = model_set.evaluated_mesh.attributes.get(
                heiomesh.groups.attribute_name, None)

            if group_attribute is None:
                def get_group_index(polygon: bpy.types.MeshPolygon):
                    return 0
            else:
                def get_group_index(polygon: bpy.types.MeshPolygon):
                    return group_name_map[group_attribute.data[polygon.index].value]

        layer_name_lut = {}
        layer_name_map = []

        if heiomesh.render_layers.initialized and not heiomesh.render_layers.attribute_invalid:

            for layer in heiomesh.render_layers:
                if layer.name not in layer_name_lut:
                    index = len(layer_names)
                    layer_name_lut[layer.name] = index
                    layer_names.append(layer.name)
                else:
                    index = layer_name_lut[layer.name]

                layer_name_map.append(index)

            layer_attribute = model_set.evaluated_mesh.attributes.get(
                heiomesh.render_layers.attribute_name, None)

            if layer_attribute is None:
                def get_layer_index(polygon: bpy.types.MeshPolygon):
                    return 0
            else:
                def get_layer_index(polygon: bpy.types.MeshPolygon):
                    return layer_name_map[layer_attribute.data[polygon.index].value]

        else:
            for material_slot in model_set.evaluated_object.material_slots:
                material = material_slot.material.heio_material

                if material.render_layer == 'SPECIAL':
                    render_layer_name = material.special_render_layer_name
                elif material.render_layer != 'AUTO':
                    render_layer_name = material.render_layer
                elif material.shader_name in self._target_definition.shaders.definitions:
                    render_layer_name = self._target_definition.shaders.definitions[
                        material.shader_name].layer.name
                else:
                    render_layer_name = 'OPAQUE'

                render_layer_name = render_layer_name.lower()

                if render_layer_name not in layer_name_lut:
                    index = len(layer_names)
                    layer_name_lut[render_layer_name] = index
                    layer_names.append(render_layer_name)
                else:
                    index = layer_name_lut[render_layer_name]

                layer_name_map.append(index)

            layer_count = len(layer_name_map)

            def get_layer_index(polygon: bpy.types.MeshPolygon):
                if polygon.material_index >= layer_count:
                    return 0

                return layer_name_map[polygon.material_index]

        material_lut = {}
        material_map = []

        for material_slot in model_set.evaluated_object.material_slots:
            if material_slot.material not in material_lut:
                index = len(materials)
                material_lut[material_slot.material] = index
                materials.append(material_slot.material)
            else:
                index = material_lut[material_slot.material]

            material_map.append(index)

        material_count = len(material_map)

        def get_material_index(polygon: bpy.types.MeshPolygon):
            if polygon.material_index >= material_count:
                return 0
            return material_map[polygon.material_index]

        polygon_mapping = [(
            polygon.index,
            get_group_index(polygon),
            get_layer_index(polygon),
            get_material_index(polygon)
        ) for polygon in model_set.evaluated_mesh.polygons]
        polygon_mapping.sort(key=lambda x: (x[1], x[2], x[3]))

        return group_names, layer_names, materials, polygon_mapping

    def _convert_colors(self, mesh: bpy.types.Mesh, loop_order: list[bpy.types.MeshLoop]):
        if len(mesh.color_attributes) == 0:
            return [System.VECTOR4(1, 1, 1, 1)] * len(loop_order), True

        color_attribute = mesh.color_attributes[0]
        colors = []

        if color_attribute.domain == 'POINT':
            def get_color(loop: bpy.types.MeshLoop):
                return color_attribute.data[loop.vertex_index].color

        elif color_attribute.domain == 'FACE':
            loop_to_polygon_index = [0] * len(loop_order)
            for polygon in mesh.polygons:
                for loop_index in polygon.loop_indices:
                    loop_to_polygon_index[loop_index] = polygon.index

            def get_color(loop: bpy.types.MeshLoop):
                return color_attribute.data[loop_to_polygon_index[loop.index]].color

        elif color_attribute.domain == 'CORNER':
            def get_color(loop: bpy.types.MeshLoop):
                return color_attribute.data[loop.index].color

        else:
            raise HEIOUserException(
                f"Invalid color attribute domain \"{color_attribute.domain}\" on mesh \"{mesh.name}\"!")

        for loop in loop_order:
            color = get_color(loop)
            colors.append(System.VECTOR4(
                color[0],
                color[1],
                color[2],
                color[3],
            ))

        return colors, color_attribute.data_type == 'BYTE_COLOR'

    def _convert_uv_maps(self, mesh: bpy.types.Mesh, loop_order: list[bpy.types.MeshLoop]):
        if len(mesh.uv_layers) == 0:
            return [[System.VECTOR2(0, 0)] * len(loop_order)]

        result = []

        for uv_layer in mesh.uv_layers:
            texcoords = []
            for loop in loop_order:
                uv = uv_layer.data[loop.index].uv
                texcoords.append(System.VECTOR2(uv.x, uv.y))
            result.append(texcoords)

        return result

    def _convert_uv_directions(self, mesh: bpy.types.Mesh, loop_order: list[bpy.types.MeshLoop]):
        if len(mesh.uv_layers) == 0:

            loop_normals: list[Vector] = [x.vector.copy()
                                          for x in mesh.vertex_normals]
            for loop in mesh.loops:
                loop_normals[loop.vertex_index] = loop.normal

            up_vec = Vector((0, 0, 1))

            uv_directions = []
            for n in loop_normals:
                tangent = n.cross(up_vec).normalized()
                binormal = n.cross(tangent).normalized()
                tangent = n.cross(binormal).normalized()
                uv_directions.append((tangent, binormal))

            return [uv_directions[l.vertex_index] for l in loop_order], None

        mesh.calc_tangents(uvmap=mesh.uv_layers[0].name)
        uv_directions = [(l.tangent.normalized(), l.bitangent.normalized())
                         for l in loop_order]
        mesh.free_tangents()

        uv_directions2 = None
        if len(mesh.uv_layers) > 2:
            mesh.calc_tangents(uvmap=mesh.uv_layers[2].name)
            uv_directions2 = [(l.tangent.normalized(), l.bitangent.normalized())
                              for l in loop_order]
            mesh.free_tangents()

        return uv_directions, uv_directions2

    def _convert_model_set(self, model_set: o_modelset.ModelSet):
        mesh = model_set.evaluated_mesh
        if len(mesh.polygons) == 0:
            return None

        if len(model_set.evaluated_object.material_slots) == 0:
            raise HEIOUserException(
                f"Object \"{model_set.obj.name}\" has no materials!")

        raw_meshdata = RawMeshData()
        raw_meshdata.vertices = self._convert_vertices(model_set)
        group_names, layer_names, materials, polygon_mapping = self._map_polygons(
            model_set)

        loop_order: list[bpy.types.MeshLoop] = [
            mesh.loops[loop]
            for polygon_map in polygon_mapping
            for loop in mesh.polygons[polygon_map[0]].loop_indices
        ]

        raw_meshdata.triangle_indices = [l.vertex_index for l in loop_order]

        raw_meshdata.polygon_uv_directions, raw_meshdata.polygon_uv_directions2 = self._convert_uv_directions(
            mesh, loop_order)

        raw_meshdata.texture_coordinates = self._convert_uv_maps(
            mesh, loop_order)

        colors, byte_colors = self._convert_colors(mesh, loop_order)
        raw_meshdata.colors.append(colors)

        _, current_group, current_layer, current_material = polygon_mapping[0]
        group_size = 0
        set_size = 0

        def add_set():
            if set_size == 0:
                return

            materaial = materials[current_material]
            sn_material = self._material_processor.get_converted_material(
                materaial)

            def get_param_or(fallback, param_name):
                if self._target_definition.hedgehog_engine_version == 1:
                    return False

                if fallback:
                    return fallback

                parameter = materaial.heio_material.parameters.find_next(
                    param_name, 0, set(["BOOLEAN"]))
                if parameter is not None:
                    return parameter.boolean_value

                return False

            enable_8_weight = get_param_or(
                model_set.obj.data.heio_mesh.force_enable_8_weights, "enable_max_bone_influences_8")
            enable_multi_tangent = get_param_or(
                model_set.obj.data.heio_mesh.force_enable_multi_tangent, "enable_multi_tangent_space")

            raw_meshdata.mesh_sets.append(HEIO_NET.MESH_DATA_SET_INFO(
                byte_colors,
                enable_8_weight,
                enable_multi_tangent,
                SharpNeedle.RESOURCE_REFERENCE[SharpNeedle.MATERIAL](
                    sn_material),
                SharpNeedle.MESH_SLOT(layer_names[current_layer]),
                set_size
            ))

            nonlocal group_size
            group_size += 1

        def add_group():
            if group_size == 0:
                return

            raw_meshdata.group_names.append(group_names[current_group])
            raw_meshdata.group_set_counts.append(group_size)

        for _, poly_group, poly_layer, poly_material in polygon_mapping:

            if (poly_group != current_group
                or current_layer != poly_layer
                    or current_material != poly_material):
                add_set()
                set_size = 0

            if poly_group != current_group:
                add_group()
                group_size = 0

            set_size += 1
            current_group = poly_group
            current_layer = poly_layer
            current_material = poly_material

        add_set()
        add_group()

        if model_set.evaluated_shape_positions is not None:
            raw_meshdata.morph_names = [
                x.name for x in model_set.obj.data.shape_keys.key_blocks[1:]]

        return raw_meshdata

    ##################################################

    def _get_model_nodes(self, armature_obj):
        weight_index_map: dict[str, int] = {}
        model_nodes = []

        bone_orientation = self._bone_orientation
        if bone_orientation == 'AUTO':
            bone_orientation = self._target_definition.bone_orientation

        if bone_orientation == 'XY':
            matrix_remap = o_transform.bpy_bone_xy_to_net_matrix
        elif bone_orientation == 'XZ':
            matrix_remap = o_transform.bpy_bone_xz_to_net_matrix
        else:  # ZNX
            matrix_remap = o_transform.bpy_bone_znx_to_net_matrix

        for i, bone in enumerate(armature_obj.pose.bones):
            weight_index_map[bone.name] = i

            if self._use_pose_bone_matrices:
                matrix = bone.matrix
            else:
                matrix = bone.bone.matrix_local

            node = SharpNeedle.MODEL.Node()
            node.Name = bone.name

            if bone.parent is not None:
                node.ParentIndex = weight_index_map[bone.parent.name]
            else:
                node.ParentIndex = -1

            net_matrix = matrix_remap(matrix)
            valid, net_matrix = System.MATRIX4X4.Invert(
                net_matrix, System.MATRIX4X4.Identity)
            if not valid:
                raise HEIOUserException(
                    f"Bone \"{bone.name}\" on armature \"{armature_obj.data.name}\" has an invalid matrix! Make sure all scale channels are not 0")
            node.Transform = net_matrix

            model_nodes.append(node)

        return weight_index_map, model_nodes

    def _get_sca_parameters(self, root, model_nodes):
        if self._target_definition.data_versions.sample_chunk < 2:
            return None

        sca_parameters = []

        defaults = {}
        if self._auto_sca_parameters and self._target_definition.sca_parameters is not None:
            defaults = self._target_definition.sca_parameters.model_defaults
            if model_nodes is None:
                defaults = self._target_definition.sca_parameters.terrain_defaults

        if root is not None and root.type == 'ARMATURE':
            for i, bone in enumerate(root.pose.bones):
                node = o_sca_parameters.convert_to_model_node_prm(
                    bone.bone.heio_node.sca_parameters, i, defaults)
                sca_parameters.append(node)

        elif root is not None and root.type in MESH_DATA_TYPES:
            node = o_sca_parameters.convert_to_model_node_prm(
                root.data.heio_mesh.sca_parameters, 0, defaults)
            sca_parameters.append(node)

        else:
            node = o_sca_parameters.convert_to_model_node_prm(
                None, 0, defaults)
            sca_parameters.append(node)

        return [x for x in sca_parameters if x is not None]

    def _assemble_compile_data_set(self, root, children, name: str):
        sn_meshdata = []
        weight_index_map = None
        model_nodes = None

        if root is not None and root.type == 'ARMATURE' and self.mode != 'TERRAIN':
            weight_index_map, model_nodes = self._get_model_nodes(root)

        elif self.mode == 'MODEL':

            node = SharpNeedle.MODEL.Node()
            node.Name = name
            node.ParentIndex = -1
            node.Transform = System.MATRIX4X4.Identity
            model_nodes = [node]

        if root is None:
            parent_matrix = Matrix.Identity(4)

        else:
            parent_matrix = root.matrix_world.inverted()

            if root.type in MESH_DATA_TYPES:
                root_meshdata = self.get_meshdata(root)
                if root_meshdata is not None:
                    sn_meshdata.append(
                        root_meshdata.convert_to_net(None, weight_index_map))

        for child in children:
            if child.type not in MESH_DATA_TYPES:
                continue

            child_meshdata = self.get_meshdata(child)

            if child_meshdata is None:
                continue

            if model_nodes is not None and child_meshdata.morph_names is not None and len(child_meshdata.group_names) > 1:
                raise HEIOUserException(
                    f"Mesh \"{child.data.name}\" is a shape model, which cannot have more than one mesh group!")

            matrix = parent_matrix @ child.matrix_world
            normal_matrix = matrix.to_3x3().normalized()
            sn_meshdata.append(child_meshdata.convert_to_net(
                (matrix, normal_matrix), weight_index_map))

        if len(sn_meshdata) == 0:
            return None

        if any([x.MorphNames is not None and x.GroupNames.Count > 1 for x in sn_meshdata]):
            raise HEIOUserException("Model")

        sca_parameters = self._get_sca_parameters(root, model_nodes)

        return HEIO_NET.MESH_COMPILE_DATA(
            name,
            sn_meshdata,
            model_nodes,
            sca_parameters
        )

    def _assemble_compile_data(self, root, children, name: str):
        compile_data = self._assemble_compile_data_set(root, children, name)

        if compile_data is None:
            return None

        result = (name, compile_data, None)

        if root is None or self._target_definition.hedgehog_engine_version < 2:
            return result

        if root.type == 'ARMATURE':
            lod_info = root.data.heio_armature.lod_info
        elif root.type in MESH_DATA_TYPES:
            lod_info = root.data.heio_mesh.lod_info
        else:
            return result

        if len(lod_info.levels) == 0:
            return result

        progress_console.start(
            "Preparing LOD mesh data for export", len(lod_info.levels) - 1)

        for i, level in enumerate(lod_info.levels.elements[1:]):
            if level.target is None or level.target in self._lod_output:
                continue

            progress_console.update(
                f"Converting mesh data for LOD object \"{level.target.name}\"", i)

            lod_children = self._object_manager.lod_trees[level.target]
            self._output_queue.append(
                (level.target, self._assemble_compile_data_set(level.target, lod_children, name)))
            self._lod_output[level.target] = None

        progress_console.end()

        return (name, compile_data, lod_info)

    ##################################################

    def compile_output(self, use_multicore_processing: bool):
        progress_console.start("Compiling models")
        progress_console.update("This may take a while")

        models = HEIO_NET.MESH_COMPILE_DATA.ToHEModels(
            [x[1] for x in self._output_queue],
            self._target_definition.hedgehog_engine_version == 2,
            self._topology,
            self._optimized_vertex_data,
            use_multicore_processing
        )

        for queued, model in zip(self._output_queue, models):
            if len(queued) == 3:
                continue

            self._lod_output[queued[0]] = model

        for queued, model in zip(self._output_queue, models):
            if len(queued) == 2:
                continue

            extension = ".terrain-model" if isinstance(
                model, SharpNeedle.TERRAIN_MODEL) else ".model"

            if queued[2] is None:
                self._output[queued[0]] = (model, extension)
                continue

            lod_models = []
            lod_cascades = []
            lod_unknowns = []

            lod_models.append(model)

            for i, level in enumerate(queued[2].levels):
                if i > 0 and level.target is None:
                    continue

                lod_cascades.append(level.cascade)
                lod_unknowns.append(level.unknown)

                if i > 0:
                    lod_models.append(self._lod_output[level.target])

            self._output[queued[0]] = (HEIO_NET.MODEL_HELPER.CreateLODArchive(
                lod_models, lod_cascades, lod_unknowns), extension)

        self._output_queue.clear()
        progress_console.end()

    def write_output_to_files(self, directory):
        super().write_output_to_files(directory)

        if self._write_dependencies:
            self._material_processor.write_output_images_to_files(directory)
