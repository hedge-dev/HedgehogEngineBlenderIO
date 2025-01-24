import bpy
from mathutils import Vector
from ..register.definitions import TargetDefinition
from ..register.property_groups.mesh_properties import MESH_DATA_TYPES


class ModelSet:

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

        shape_keys: bpy.types.Key = self.evaluated_object.data.get("shape_keys", None)
        if shape_keys is not None:
            self.evaluated_object.show_only_shape_key = True

            if eval_shapekeys:
                self.evaluated_shape_positions = []
                for i in range(1, len(shape_keys.key_blocks)):
                    self.evaluated_object.active_shape_key_index = i

                    self.evaluated_shape_positions.append(
                        [v.co.copy() for v in self.evaluated_object.to_mesh(
                            preserve_all_data_layers=True,
                            depsgraph=depsgraph).vertices]
                    )
                    self.evaluated_object.to_mesh_clear()

            self.evaluated_object.active_shape_key_index = 0

        self.evaluated_mesh = self.evaluated_object.to_mesh(
            preserve_all_data_layers=True,
            depsgraph=depsgraph)

    def cleanup_modifiers(self):
        self.obj.modifiers.remove(self._triangulate_modifier)
        if self._edge_split_modifier is not None:
            self.obj.modifiers.remove(self._edge_split_modifier)

        for modifier in self.obj.modifiers:
            modifier.show_viewport = self._viewport_modifier_states[modifier]


class ModelSetManager:

    target_definition: TargetDefinition
    eval_depsgraph: bpy.types.Depsgraph | None

    _apply_modifiers: bool
    _apply_armature: bool

    _registered_objects: set[bpy.types.Object]
    _registered_armatures: dict[bpy.types.Armature, str]
    model_set_lut: dict[bpy.types.Object | bpy.types.Mesh, ModelSet]
    obj_mesh_mapping: dict[bpy.types.Object, ModelSet]

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
        self._registered_armatures = {}
        self.model_set_lut = {}
        self.obj_mesh_mapping = {}

    def register_objects(self, objects: list[bpy.types.Object]):
        for obj in objects:
            if obj.type == 'ARMATURE':
                if obj.data not in self._registered_armatures:
                    self._registered_armatures[obj.data] = obj.data.pose_position
                continue

            if obj.type not in MESH_DATA_TYPES or obj in self.obj_mesh_mapping:
                continue

            lut_key = None
            model_set = None

            if len(obj.modifiers) > 0 and self._apply_modifiers:
                lut_key = obj

            else:
                lut_key = obj.data

                if lut_key in self.model_set_lut:
                    model_set = self.model_set_lut[obj.data]

            if model_set is None:
                model_set = ModelSet(obj)
                self.model_set_lut[lut_key] = model_set

            self.obj_mesh_mapping[obj] = model_set

        self._registered_objects.update(objects)
        for model_set in self.model_set_lut.values():

            child = model_set.obj
            parent = child.parent
            while parent is not None and parent.type != 'ARMATURE':
                child = parent
                parent = child.parent

            if parent is None:
                model_set.armature_object = None
                model_set.attached_bone_name = None
            else:
                model_set.armature_object = parent

                if len(child.parent_bone) > 0:
                    model_set.attached_bone_name = child.parent_bone
                else:
                    model_set.attached_bone_name = None

    def evaluate_begin(self, context: bpy.types.Context, eval_shapekeys: bool):

        model_meshes = self.model_set_lut.values()

        if not self._apply_armature:
            for armature in self._registered_armatures.keys():
                armature.pose_position = 'REST'

        for mesh in model_meshes:
            mesh.prepare_modifiers(self._apply_modifiers, self._apply_armature)

        self.depsgraph = context.evaluated_depsgraph_get()

        for mesh in model_meshes:
            mesh.evaluate(self.depsgraph, eval_shapekeys)


    def evaluate_end(self):
        for mesh in self.model_set_lut.values():
            mesh.cleanup_modifiers()

        if not self._apply_armature:
            for armature, pose in self._registered_armatures.items():
                armature.pose_position = pose

        self.depsgraph = None
