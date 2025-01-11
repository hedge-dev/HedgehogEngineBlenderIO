import bpy
from ..register.definitions import TargetDefinition


class ModelMesh:

    obj: bpy.types.Object

    _viewport_modifier_states: dict[bpy.types.Modifier, bool]
    _armature_modifier: bpy.types.ArmatureModifier
    _edge_split_modifier: bpy.types.EdgeSplitModifier
    _triangulate_modifier: bpy.types.TriangulateModifier

    evaluated_object: bpy.types.Object
    evaluated_mesh: bpy.types.Mesh

    def __init__(self, obj: bpy.types.Object):

        self.obj = obj

        self._armature_modifier = None
        self._edge_split_modifier = None
        self._triangulate_modifier = None
        self._viewport_modifier_states = {}

        self.evaluated_object = None
        self.evaluated_mesh = None

    @property
    def supports_weights(self):
        raise NotImplementedError()

    def prepare_modifiers(self, apply_modifiers: bool, apply_armature: bool):
        for modifier in self.obj.modifiers:
            self._viewport_modifier_states[modifier] = modifier.show_viewport

            if (self.supports_weights
                    and modifier.type == 'ARMATURE'
                    and modifier.object == self.obj.parent):
                self._armature_modifier = modifier
                modifier.show_viewport &= apply_armature

            elif not apply_modifiers:
                modifier.show_viewport = False

        # add edge split modifier
        self._edge_split_modifier = self.obj.modifiers.new(
            "ExportEdgeSplit",
            'EDGE_SPLIT')

        self._edge_split_modifier.use_edge_angle = False
        self._edge_split_modifier.use_edge_sharp = True

        # add triangulate modifier
        self._triangulate_modifier = self.obj.modifiers.new(
            "ExportTriangulate",
            'TRIANGULATE')
        self._triangulate_modifier.quad_method = 'FIXED'
        self._triangulate_modifier.ngon_method = 'CLIP'
        self._triangulate_modifier.min_vertices = 4
        self._triangulate_modifier.keep_custom_normals = True

    def evaluate(self, depsgraph: bpy.types.Depsgraph):
        self.evaluated_object = self.obj.evaluated_get(depsgraph)

        if self.evaluated_object.data.shape_keys is not None:
            for shape_key in self.evaluated_object.data.shape_keys.key_blocks:
                shape_key.value = 0

        self.evaluated_mesh = self.evaluated_object.to_mesh(
            preserve_all_data_layers=True,
            depsgraph=depsgraph)

    def cleanup_modifiers(self):
        self.obj.modifiers.remove(self._triangulate_modifier)
        if self._edge_split_modifier is not None:
            self.obj.modifiers.remove(self._edge_split_modifier)

        for modifier in self.obj.modifiers:
            modifier.show_viewport = self._viewport_modifier_states[modifier]

    def get_shape_mesh(
            self,
            keyframe_name: str,
            depsgraph: bpy.types.Depsgraph):

        shape_keys = self.evaluated_object.data.shape_keys.key_blocks
        if keyframe_name not in shape_keys:
            return None

        for shape_key in shape_keys:
            if shape_key.name == keyframe_name:
                shape_key.value = 1
            else:
                shape_key.value = 0

        return self.evaluated_object.to_mesh(
            depsgraph=depsgraph)


class ModelMeshManager:

    target_definition: TargetDefinition
    eval_depsgraph: bpy.types.Depsgraph | None

    _apply_modifiers: bool
    _apply_armature: bool

    modelmesh_lut: dict[bpy.types.Object | bpy.types.Mesh, ModelMesh]
    object_mesh_mapping: dict[bpy.types.Object, ModelMesh]

    def __init__(
            self,
            target_definition: TargetDefinition,
            apply_modifiers: bool,
            apply_armature: bool):

        self.target_definition = target_definition
        self.eval_depsgraph = None

        self._apply_modifiers = apply_modifiers
        self._apply_armature = apply_armature

        self.modelmesh_lut = {}
        self.obj_mesh_mapping = {}

    def register_objects(self, objects: list[bpy.types.Object]):
        for obj in objects:
            if obj in self.obj_mesh_mapping:
                continue

            lut_key = None
            modelmesh = None

            if len(obj.modifiers) > 0 and self._apply_modifiers:
                lut_key = obj

            else:
                lut_key = obj.data

                if lut_key in self.modelmesh_lut:
                    modelmesh = self.modelmesh_lut[obj.data]

            if modelmesh is None:
                modelmesh = ModelMesh(obj)
                self.modelmesh_lut[lut_key] = modelmesh

            self.obj_mesh_mapping[obj] = modelmesh

    def evaluate_begin(self, context: bpy.types.Context):

        model_meshes = self.modelmesh_lut.values()

        for mesh in model_meshes:
            mesh.prepare_modifiers(self._apply_modifiers, self._apply_armature)

        self.depsgraph = context.evaluated_depsgraph_get()

        for mesh in model_meshes:
            mesh.evaluate(self.depsgraph)

    def evaluate_end(self):
        for mesh in self.modelmesh_lut.values():
            mesh.cleanup_modifiers()

        self.depsgraph = None
