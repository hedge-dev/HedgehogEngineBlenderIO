import bpy
from mathutils import Vector
from ..register.definitions import TargetDefinition


class ModelMesh:

    obj: bpy.types.Object

    _viewport_modifier_states: dict[bpy.types.Modifier, bool]
    _armature_modifier: bpy.types.ArmatureModifier | None
    _edge_split_modifier: bpy.types.EdgeSplitModifier | None
    _triangulate_modifier: bpy.types.TriangulateModifier | None

    evaluated_object: bpy.types.Object | None
    evaluated_mesh: bpy.types.Mesh | None
    evaluated_shape_positions: list[list[Vector]] | None

    def __init__(self, obj: bpy.types.Object):

        self.obj = obj
        self.armature_object = None
        self.attached_bone_name = None

        self._viewport_modifier_states = {}
        self._armature_modifier = None
        self._edge_split_modifier = None
        self._triangulate_modifier = None

        self.evaluated_object = None
        self.evaluated_mesh = None
        self.evaluated_shape_positions = None

    @property
    def is_weighted(self):
        return self.armature_object is not None and self.attached_bone_name is None

    def prepare_modifiers(self, apply_modifiers: bool, apply_armature: bool):
        for modifier in self.obj.modifiers:
            self._viewport_modifier_states[modifier] = modifier.show_viewport

            if (self.is_weighted
                    and modifier.type == 'ARMATURE'
                    and modifier.object == self.armature_object):
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

    def evaluate(self, depsgraph: bpy.types.Depsgraph, eval_shapekeys: bool):
        self.evaluated_object = self.obj.evaluated_get(depsgraph)

        if self.evaluated_object.data.shape_keys is not None:
            for shape_key in self.evaluated_object.data.shape_keys.key_blocks:
                shape_key.value = 0

            if eval_shapekeys:
                self.evaluated_shape_positions = []
                for block in self.evaluated_object.data.shape_keys.key_blocks[1:]:
                    block.value = 1
                    self.evaluated_shape_positions.append(
                        [v.co.copy() for v in self.evaluated_object.to_mesh(
                            preserve_all_data_layers=True,
                            depsgraph=depsgraph).vertices]
                    )
                    self.evaluated_object.to_mesh_clear()
                    block.value = 0

        self.evaluated_mesh = self.evaluated_object.to_mesh(
            preserve_all_data_layers=True,
            depsgraph=depsgraph)

    def cleanup_modifiers(self):
        self.obj.modifiers.remove(self._triangulate_modifier)
        if self._edge_split_modifier is not None:
            self.obj.modifiers.remove(self._edge_split_modifier)

        for modifier in self.obj.modifiers:
            modifier.show_viewport = self._viewport_modifier_states[modifier]


class ModelMeshManager:

    target_definition: TargetDefinition
    eval_depsgraph: bpy.types.Depsgraph | None

    _apply_modifiers: bool
    _apply_armature: bool

    _registered_objects: set[bpy.types.Object]
    modelmesh_lut: dict[bpy.types.Object | bpy.types.Mesh, ModelMesh]
    obj_mesh_mapping: dict[bpy.types.Object, ModelMesh]

    def __init__(
            self,
            target_definition: TargetDefinition,
            apply_modifiers: bool,
            apply_armature: bool):

        self.target_definition = target_definition
        self.eval_depsgraph = None

        self._apply_modifiers = apply_modifiers
        self._apply_armature = apply_armature

        self._registered_objects = set()
        self.modelmesh_lut = {}
        self.obj_mesh_mapping = {}

    def register_objects(self, objects: list[bpy.types.Object]):
        for obj in objects:
            if obj.type != 'MESH' or obj in self.obj_mesh_mapping:
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

        self._registered_objects.update(objects)
        for modelmesh in self.modelmesh_lut.values():

            child = modelmesh.obj
            parent = child.parent
            while parent is not None and parent.type != 'ARMATURE':
                child = parent
                parent = child.parent

            if parent is None:
                modelmesh.armature_object = None
                modelmesh.attached_bone_name = None
            else:
                modelmesh.armature_object = parent

                if len(child.parent_bone) > 0:
                    modelmesh.attached_bone_name = child.parent_bone
                else:
                    modelmesh.attached_bone_name = None

    def evaluate_begin(self, context: bpy.types.Context, eval_shapekeys: bool):

        model_meshes = self.modelmesh_lut.values()

        for mesh in model_meshes:
            mesh.prepare_modifiers(self._apply_modifiers, self._apply_armature)

        self.depsgraph = context.evaluated_depsgraph_get()

        for mesh in model_meshes:
            mesh.evaluate(self.depsgraph, eval_shapekeys)

    def evaluate_end(self):
        for mesh in self.modelmesh_lut.values():
            mesh.cleanup_modifiers()

        self.depsgraph = None
