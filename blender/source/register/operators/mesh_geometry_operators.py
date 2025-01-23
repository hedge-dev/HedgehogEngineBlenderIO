import bpy
import bmesh
from bpy.props import BoolProperty, IntProperty
from mathutils import Vector, Quaternion, Matrix
import math
import bmesh

from .base import HEIOBaseOperator, HEIOBasePopupOperator
from ..property_groups.base_list import BaseList
from ..property_groups.mesh_properties import HEIO_RenderLayerList, HEIO_CollisionFlagList
from ...exceptions import HEIOUserException
from ...utility import attribute_utils, mesh_generators


class MeshInfoLut:

    mesh: bpy.types.Mesh
    output_info_list: BaseList

    value_lut: dict[any, int]
    remap_values: list[any]

    _get_info_list_func: any
    _is_mesh_layer: bool
    _is_flags: bool

    _key_name: str
    _fallback: any
    _fallback_list: list

    def __init__(self, get_info_list_func: any, mesh: bpy.types.Mesh):
        self.mesh = mesh
        self.output_info_list = get_info_list_func(mesh)

        self.value_lut = dict()
        self.remap_values = []

        self._get_info_list_func = get_info_list_func
        self._is_mesh_layer = isinstance(
            self.output_info_list, HEIO_RenderLayerList)
        self._is_flags = isinstance(
            self.output_info_list, HEIO_CollisionFlagList)

        if self.output_info_list.attribute_name.startswith("HEIOCollision"):
            self._key_name = 'value'
            self._fallback = 0
        else:
            self._key_name = 'name'
            self._fallback = "Opaque" if self._is_mesh_layer else ""

        self._fallback_list = [{self._key_name: self._fallback}]

        for i, element in enumerate(self.output_info_list):
            self.value_lut[element.get(self._key_name, self._fallback)] = i

    def ensure_mesh_info_values(self, source_list: list, check_init=True):
        for source in source_list:
            info_list = self._get_info_list_func(source)

            if check_init and hasattr(info_list, "initialized"):
                if info_list.attribute_invalid:
                    raise HEIOUserException((
                        f"Mesh {info_list.id_data.name} has an invalid \"{info_list.attribute_name}\" attribute!"
                        " Must use domain \"Face\" and type \"Integer\"!"
                        " Please remove or convert"
                    ))

                if not info_list.initialized:
                    if self._is_flags:
                        continue
                    else:
                        info_list = self._fallback_list

            for element in info_list:
                value = element.get(self._key_name, self._fallback)
                if value in self.value_lut:
                    continue

                self.value_lut[value] = (
                    -2
                    if element.get('custom', False)
                    else -1
                )

        lutn = len(self.value_lut)
        if lutn == 0 or (lutn == 1 and 0 in self.value_lut and not self._is_flags):
            return

        items = list(self.value_lut.items())

        if self._fallback == 0:
            items.sort(key=lambda x: x[0])

        for v, i in items:
            if i >= 0:
                continue

            self.value_lut[v] = len(self.output_info_list)
            out_element = self.output_info_list.new()
            setattr(out_element, self._key_name, v)

            if i == -2:
                out_element.custom = True

        self.output_info_list.initialize()

    @staticmethod
    def setup(get_info_list_func: any, mesh: bpy.types.Mesh, meshes: list[bpy.types.Mesh]):
        result = MeshInfoLut(get_info_list_func, mesh)
        result.ensure_mesh_info_values(meshes)
        return result

    def set_remap(self, mesh: bpy.types.Mesh):
        if len(self.output_info_list) < 2:
            return

        info_list = self._get_info_list_func(mesh)
        attribute = info_list.attribute
        facenum = len(mesh.polygons)

        if attribute is None:

            value = self.value_lut[0] if 0 in self.value_lut and not self._is_flags else 0
            remaps = [value] * facenum

        elif self._is_flags:
            flag_mapping = [
                (1 << i, 1 << self.value_lut[flag_element.value])
                for i, flag_element in enumerate(info_list)
            ]

            def get_flag(face_index):
                flags = attribute.data[face_index].value
                mapped_flags = 0

                for flag, mapped_flag in flag_mapping:
                    if (flags & flag) != 0:
                        mapped_flags |= mapped_flag

                return mapped_flags

            remaps = [get_flag(x) for x in range(facenum)]

        else:
            value_mapping = [
                self.value_lut[x.get(self._key_name, self._fallback)]
                for x in info_list]

            remaps = [
                value_mapping[attribute.data[x].value]
                for x in range(facenum)
            ]

        self.remap_values.extend(remaps)

    def apply_remapped_data(self, remap_attribute_name: str):
        if len(self.output_info_list) < 2:
            return

        remap_attribute = self.mesh.attributes[remap_attribute_name]
        attribute = self.output_info_list.attribute

        def get_value(face_index):
            remap_index = remap_attribute.data[face_index].value
            if remap_index == 0:
                return attribute.data[face_index].value
            else:
                return self.remap_values[remap_index - 1]

        mapping_applied_values = [get_value(x)
                                  for x in range(len(self.mesh.polygons))]
        attribute.data.foreach_set('value', mapping_applied_values)


class HEIO_OT_SplitMeshGroups(HEIOBasePopupOperator):
    bl_idname = "heio.split_meshgroups"
    bl_label = "Split mesh by groups"
    bl_options = {'UNDO'}

    root_mesh_copy: BoolProperty(
        name="Root mesh copy",
        description="Create a copy of the original mesh as the root, instead of clearing the original"
    )

    origins_to_bounding_box_centers: BoolProperty(
        name="Origins to bounding box centers",
        description="Set the origin of each split mesh to be at the center of the meshes bounding box",
        default=True
    )

    remove_empty_splits: BoolProperty(
        name="Remove empty splits",
        description="If a mesh ends up empty, remove it",
        default=True
    )

    remove_empty_info: BoolProperty(
        name="Remove empty info",
        description="Remove flags and types that don't get used by the split meshes",
        default=True
    )

    split_collision_primitives: BoolProperty(
        name="Split collision primitives",
        description="Split collision primitives into seperate objects",
        default=True
    )

    @classmethod
    def poll(cls, context: bpy.types.Context):
        return (
            context.mode == 'OBJECT'
            and context.active_object is not None
            and context.active_object.type == 'MESH'
        )

    def draw(self, context):
        self.layout.prop(self, "root_mesh_copy")
        self.layout.prop(self, "origins_to_bounding_box_centers")
        self.layout.prop(self, "remove_empty_splits")
        self.layout.prop(self, "remove_empty_info")
        self.layout.prop(self, "split_collision_primitives")

    def _remove_unused_collision_types(self, split_mesh):
        types = split_mesh.heio_mesh.collision_types

        if not types.initialized or types.attribute_invalid:
            return

        used_types = set()

        for type in types.attribute.data:
            used_types.add(type.value)

        if len(used_types) == 0 and 0 in used_types:
            types.delete()
            return

        has_any = False
        for i in reversed(range(len(types))):
            if i in used_types:
                has_any = True
                continue

            types.remove(i)

            if has_any:
                attribute_utils.decrease_int_values(
                    None, split_mesh, types.attribute_name, i)

    def _remove_unused_collision_flags(self, split_mesh):
        flags = split_mesh.heio_mesh.collision_flags

        if not flags.initialized or flags.attribute_invalid:
            return

        used_flags = 0
        for flag in flags.attribute.data:
            used_flags |= flag.value

        if used_flags == 0:
            flags.delete()
            return

        used_flag_values = []
        for i in range(32):
            if (used_flags & 1) != 0:
                used_flag_values.append(i)
            used_flags >> 1

        has_any = False
        for i in reversed(range(len(flags))):
            if i in used_flag_values:
                has_any = True
                continue

            flags.remove(i)

            if has_any:
                attribute_utils.rightshift_int_flags(
                    None, split_mesh, flags.attribute_name, i, 1)

    def _remove_unused_render_layers(self, split_mesh):
        layers = split_mesh.heio_mesh.render_layers

        if not layers.initialized or layers.attribute_invalid:
            return

        used_layers = set()

        for layer in layers.attribute.data:
            used_layers.add(layer.value)

        has_any = False
        for i in reversed(range(3, len(layers))):
            if i in used_layers:
                has_any = True
                continue

            layers.remove(i)

            if not has_any:
                continue

            if i == 3:
                attribute_utils.change_int_values(
                    None, split_mesh, layers.attribute_name, i, 0)

            if len(layers) > 3:
                attribute_utils.decrease_int_values(
                    None, split_mesh, layers.attribute_name, i)

    def _split_collision_primitives(self, context, base):
        for i, primitive in enumerate(base.data.heio_mesh.collision_primitives):
            split_mesh = bpy.data.meshes.new(f"{base.data.name}_primitive{i}")
            split_object = bpy.data.objects.new(
                f"{base.name}_primitive{i}", split_mesh)
            split_object.parent = base
            context.collection.objects.link(split_object)

            split_primitive = split_mesh.heio_mesh.collision_primitives.new()
            split_primitive.shape_type = primitive.shape_type
            split_primitive.dimensions = split_primitive.dimensions

            split_primitive.collision_type.value = primitive.collision_type.value

            for flag in primitive.collision_flags:
                split_flag = split_primitive.collision_flags.new(
                    value=flag.value)
                split_flag.custom = flag.custom

            if self.origins_to_bounding_box_centers:
                split_object.matrix_local = Matrix.LocRotScale(
                    primitive.position,
                    primitive.rotation,
                    None
                )

            else:
                split_primitive.position = primitive.position
                split_primitive.rotation = primitive.rotation

        base.data.heio_mesh.collision_primitives.clear()

    def _execute(self, context):
        obj = context.active_object
        mesh: bpy.types.Mesh = obj.data
        mesh_groups = mesh.heio_mesh.groups

        if not mesh_groups.initialized:
            raise HEIOUserException("Mesh groups not initialized!")

        if mesh_groups.attribute_invalid:
            raise HEIOUserException("Mesh group attribute invalid!")

        if len(mesh_groups) < 2:
            raise HEIOUserException(f"Mesh has less than 2 mesh groups!")

        base_matrix = context.active_object.matrix_world

        for i, mesh_group in enumerate(mesh_groups):
            split_mesh = mesh.copy()

            # delete faces

            bm = bmesh.new()
            bm.from_mesh(split_mesh)

            bm_layer = bm.faces.layers.int[mesh_groups.attribute_name]
            to_delete = [face for face in bm.faces if face[bm_layer] != i]
            bmesh.ops.delete(bm, geom=to_delete, context='FACES')
            used_materials = set()

            for face in bm.faces:
                face[bm_layer] = 0
                used_materials.add(face.material_index)

            center = Vector()

            if self.origins_to_bounding_box_centers:
                x_min = float('inf')
                y_min = x_min
                z_min = x_min

                x_max = float('-inf')
                y_max = x_max
                z_max = x_max

                for vert in bm.verts:
                    x_min = min(x_min, vert.co.x)
                    y_min = min(y_min, vert.co.y)
                    z_min = min(z_min, vert.co.z)

                    x_max = max(x_max, vert.co.x)
                    y_max = max(y_max, vert.co.y)
                    z_max = max(z_max, vert.co.z)

                center = Vector((
                    (x_min + x_max) * 0.5,
                    (y_min + y_max) * 0.5,
                    (z_min + z_max) * 0.5
                ))

                for vert in bm.verts:
                    vert.co -= center

            bm.to_mesh(split_mesh)
            bm.free()

            if self.remove_empty_splits and len(split_mesh.polygons) == 0:
                bpy.data.meshes.remove(split_mesh)
                continue

            for i in reversed(range(len(split_mesh.materials))):
                if i not in used_materials:
                    split_mesh.materials.pop(index=i)

            split_mesh.name = f"{mesh.name}_{mesh_group.name}"
            split_obj = bpy.data.objects.new(f"{obj.name}_{mesh_group.name}", split_mesh)
            split_obj.parent = obj
            split_obj.matrix_world = base_matrix @ Matrix.Translation(center)
            context.collection.objects.link(split_obj)

            split_mesh.heio_mesh.groups.delete()
            split_mesh.heio_mesh.groups.copy_from(mesh_group)
            split_mesh.heio_mesh.groups.initialize()

            split_mesh.heio_mesh.collision_primitives.clear()
            split_mesh.heio_mesh.lod_info.delete()
            split_mesh.heio_mesh.sca_parameters.clear()

            if self.remove_empty_info:
                self._remove_unused_collision_types(split_mesh)
                self._remove_unused_collision_flags(split_mesh)
                self._remove_unused_render_layers(split_mesh)

        if self.root_mesh_copy:
            obj.data = mesh.copy()
            obj.data.name = mesh.name + "_split"

        if self.split_collision_primitives:
            self._split_collision_primitives(context, obj)

        obj.data.clear_geometry()
        obj.data.materials.clear()

        if self.remove_empty_info:
            obj.data.heio_mesh.groups.delete()
            obj.data.heio_mesh.render_layers.delete()
            obj.data.heio_mesh.collision_types.delete()
            obj.data.heio_mesh.collision_flags.delete()

        return {'FINISHED'}


class HEIO_OT_MergeMeshGroups(HEIOBasePopupOperator):
    bl_idname = "heio.merge_submeshes"
    bl_label = "Merge meshes as groups"
    bl_description = "Merge a meshes children into itself while correctly retaining all HEIO data"
    bl_options = {'UNDO'}

    root_mesh_copy: BoolProperty(
        name="Root mesh copy",
        description="Create a copy of the original mesh as the root, instead of clearing the original"
    )

    @classmethod
    def poll(cls, context: bpy.types.Context):
        return (
            context.mode == 'OBJECT'
            and context.active_object is not None
            and context.active_object.type == 'MESH'
        )

    def draw(self, context):
        self.layout.prop(self, "root_mesh_copy")

    @staticmethod
    def _get_mesh_children(obj: bpy.types.Object, ignore_nonmesh: bool, output: list):
        if obj.type != 'MESH':
            if not ignore_nonmesh:
                raise HEIOUserException(
                    "Cannot merge as some submeshes have non-mesh children!")
            return

        output.append(obj)

        for child in obj.children:
            HEIO_OT_MergeMeshGroups._get_mesh_children(child, False, output)

    @staticmethod
    def _check_meshinfo_valid(context):
        obj = context.active_object
        heiomesh = obj.data.heio_mesh

        def check_attributes(list):
            if list.initialized and list.attribute_invalid:
                raise HEIOUserException((
                    f"Invalid \"{list.attribute_name}\" attribute!"
                    " Must use domain \"Face\" and type \"Integer\"!"
                    " Please remove or convert"
                ))

        check_attributes(heiomesh.groups)
        check_attributes(heiomesh.render_layers)
        check_attributes(heiomesh.collision_types)
        check_attributes(heiomesh.collision_flags)

    @staticmethod
    def _move_collision_primitives(obj: bpy.types.Object, mesh_children: list[bpy.types.Object]):
        inv_matrix = obj.matrix_world.normalized().inverted()
        inv_obj_rotation = inv_matrix.to_quaternion()
        out_primitives = obj.data.heio_mesh.collision_primitives

        for mesh_obj in mesh_children:
            matrix = mesh_obj.matrix_world.normalized()
            obj_rotation = matrix.to_quaternion()

            for primitive in mesh_obj.data.heio_mesh.collision_primitives:
                out_primitive = out_primitives.new()

                out_primitive.position = inv_matrix @ (
                    matrix @ Vector(primitive.position))

                out_primitive.rotation = inv_obj_rotation @ (
                    obj_rotation @ Quaternion(primitive.rotation))

                out_primitive.dimensions = primitive.dimensions

                out_primitive.collision_layer.value = primitive.collision_layer.value
                out_primitive.collision_layer.custom = primitive.collision_layer.custom

                out_primitive.collision_type.value = primitive.collision_type.value
                out_primitive.collision_type.custom = primitive.collision_type.custom

                for surface_flag in primitive.collision_flags:
                    out_surface_flag = out_primitive.collision_flags.new()
                    out_surface_flag.value = surface_flag.value
                    out_surface_flag.custom = surface_flag.custom

    @staticmethod
    def _setup_remap_indices(mesh_children: list[bpy.types.Object], luts: list[MeshInfoLut]):
        remap_index = 1

        for mesh_obj in mesh_children:
            for lut in luts:
                lut.set_remap(mesh_obj.data)

            remap_attribute = mesh_obj.data.attributes.new(
                'HEIO_TEMP_REMAP_INDEX', 'INT', 'FACE')

            remap_end = remap_index + len(mesh_obj.data.polygons)
            remap_attribute.data.foreach_set(
                'value', range(remap_index, remap_end))
            remap_index = remap_end

    @staticmethod
    def _evaluate_join_objects(context: bpy.types.Context, mesh_children: list[bpy.types.Object], mesh: bpy.types.Mesh):
        result = []
        depsgraph = context.evaluated_depsgraph_get()

        group_start_index = len(mesh.heio_mesh.groups)

        for mesh_obj in mesh_children:
            eval_mesh_obj = mesh_obj.evaluated_get(depsgraph)

            copy = eval_mesh_obj.copy()
            copy.data = eval_mesh_obj.to_mesh(
                preserve_all_data_layers=True, depsgraph=depsgraph).copy()
            copy.parent = None
            copy.matrix_world = eval_mesh_obj.matrix_world.copy()
            result.append(copy)

            attribs = mesh_obj.data.attributes
            attribs.remove(attribs['HEIO_TEMP_REMAP_INDEX'])

            copy.data.heio_mesh.groups.initialize()
            for group_index in copy.data.heio_mesh.groups.attribute.data:
                group_index.value += group_start_index
            group_start_index += len(copy.data.heio_mesh.groups)

            for group in copy.data.heio_mesh.groups:
                mesh.heio_mesh.groups.copy_from(group)

        return result

    @staticmethod
    def _remove_children(obj: bpy.types.Object):
        to_unlink: list[bpy.types.Object] = []
        for _, child in enumerate(obj.children):
            if child.type != 'MESH':
                continue

            matrix_world = child.matrix_world.copy()
            child.parent = None
            child.matrix_world = matrix_world

            to_unlink.append(child)
            to_unlink.extend(child.children_recursive)

        for child in to_unlink:
            collections = list(child.users_collection)
            for collection in collections:
                if collection not in obj.users_collection:
                    continue
                collection.objects.unlink(child)

            if child.users == 0:
                mesh = child.data
                bpy.data.objects.remove(child)

                if mesh.users == 0:
                    bpy.data.meshes.remove(mesh)

    def _execute(self, context):
        obj = context.active_object

        mesh_children: list[bpy.types.Object] = []
        for child in obj.children:
            self._get_mesh_children(child, True, mesh_children)

        if mesh_children is None:
            raise HEIOUserException("No meshes to merge!")

        self._check_meshinfo_valid(context)

        mesh = obj.data
        if self.root_mesh_copy:
            mesh = mesh.copy()
            mesh.name = obj.data.name + "_merged"
            obj.data = mesh

        mesh.heio_mesh.groups.initialize()

        self._move_collision_primitives(obj, mesh_children)

        def get_lut(get_info_list_func):
            result = MeshInfoLut(get_info_list_func, mesh)
            result.ensure_mesh_info_values([x.data for x in mesh_children])
            return result

        luts: list[MeshInfoLut] = [
            get_lut(lambda x: x.heio_mesh.render_layers),
            get_lut(lambda x: x.heio_mesh.collision_types),
            get_lut(lambda x: x.heio_mesh.collision_flags)
        ]

        self._setup_remap_indices(mesh_children, luts)
        to_join = self._evaluate_join_objects(context, mesh_children, mesh)
        to_join.insert(0, obj)

        self._remove_children(obj)

        with context.temp_override(selected_objects=to_join, selected_editable_objects=to_join):
            bpy.ops.object.join()

        remap_attribute = mesh.attributes['HEIO_TEMP_REMAP_INDEX']
        for lut in luts:
            lut.apply_remapped_data(remap_attribute.name)
        mesh.attributes.remove(remap_attribute)

        for join_obj in to_join[1:]:
            mesh = join_obj.data
            bpy.data.objects.remove(join_obj)
            bpy.data.meshes.remove(mesh)

        return {'FINISHED'}


class HEIO_OT_CollisionPrimitivesToGeometry(HEIOBaseOperator):
    bl_idname = "heio.collision_primitives_to_geometry"
    bl_label = "Collision primitives to geometry"
    bl_description = "Convert collision primitives to actual geometry on the mesh"
    bl_options = {'REGISTER', 'UNDO'}

    resolution: IntProperty(
        name="Resolution",
        description="Resolution of the generated meshes",
        min=0,
        max=4,
        default=2
    )

    mesh_copy: BoolProperty(
        name="Root mesh copy",
        description="Create a copy of the original, instead of overwriting the original"
    )

    @classmethod
    def poll(cls, context: bpy.types.Context):
        return (
            context.mode == 'OBJECT'
            and context.active_object is not None
            and context.active_object.type == 'MESH'
        )

    def _check_valid(self, context):
        obj = context.active_object
        heiomesh = obj.data.heio_mesh

        if len(heiomesh.collision_primitives) == 0:
            raise HEIOUserException("Mesh has no collision primitives")

        def check_attributes(list):
            if list.initialized and list.attribute_invalid:
                raise HEIOUserException((
                    f"Invalid \"{list.attribute_name}\" attribute!"
                    " Must use domain \"Face\" and type \"Integer\"!"
                    " Please remove or convert"
                ))

        check_attributes(heiomesh.collision_types)
        check_attributes(heiomesh.collision_flags)

    def _execute(self, context):
        self._check_valid(context)

        sphere = mesh_generators.icosphere(self.resolution)
        cube = mesh_generators.cube(strips=False)
        capsule = mesh_generators.capsule(self.resolution)
        cylinder = mesh_generators.cylinder(
            int(math.pow(2, self.resolution)) * 5, True)

        obj = context.active_object

        mesh = obj.data
        if self.mesh_copy:
            mesh = mesh.copy()
            mesh.name = obj.data.name
            obj.data = mesh

        heiomesh = mesh.heio_mesh
        primitives = heiomesh.collision_primitives

        def get_attribute_data(list):
            if not list.initialized:
                return None

            result = [0] * len(mesh.polygons)
            list.attribute.data.foreach_get('value', result)
            return result

        heiomesh.groups.initialize()
        group_attribute_values = get_attribute_data(heiomesh.groups)
        coltype_attribute_values = get_attribute_data(heiomesh.collision_types)
        colflag_attribute_values = get_attribute_data(heiomesh.collision_flags)

        type_lut = MeshInfoLut(
            lambda x: x.heio_mesh.collision_types
            if isinstance(x, bpy.types.Mesh)
            else x,
            mesh)

        type_lut.ensure_mesh_info_values([[prim.collision_type for prim in primitives]])

        flags_lut = MeshInfoLut(
            lambda x: x.heio_mesh.collision_flags
            if isinstance(x, bpy.types.Mesh)
            else x.collision_flags,
            mesh)

        flags_lut.ensure_mesh_info_values(primitives, False)

        bm = bmesh.new()
        bm.from_mesh(mesh)

        for i, primitive in enumerate(primitives):
            r = primitive.dimensions[0]
            h = primitive.dimensions[2]

            if primitive.shape_type == 'CAPSULE':
                shape_mesh = capsule

                verts = []
                matrix = Matrix.LocRotScale(
                    primitive.position, primitive.rotation, None)

                for vert in shape_mesh.vertices:

                    offset = Vector((0, 0, 1))
                    if vert.z < 0:
                        offset = -offset

                    capsule_vert = (vert - offset) * r + offset * h
                    verts.append(bm.verts.new(matrix @ capsule_vert))

            else:

                if primitive.shape_type == 'SPHERE':
                    shape_mesh = sphere
                    size = Vector((r, r, r))
                elif primitive.shape_type == 'BOX':
                    shape_mesh = cube
                    size = Vector(primitive.dimensions)
                else:  # CYLINDER
                    shape_mesh = cylinder
                    size = Vector((r, r, h))

                matrix = Matrix.LocRotScale(
                    primitive.position, primitive.rotation, size)

                verts = [bm.verts.new(matrix @ vert)
                         for vert in shape_mesh.vertices]

            faces = [bm.faces.new([verts[p] for p in poly])
                     for poly in shape_mesh.get_absolute_polygons()]

            if coltype_attribute_values is not None:
                index = type_lut.value_lut[primitive.collision_type.value]
                coltype_attribute_values.extend([index] * len(faces))

            if colflag_attribute_values is not None:
                flags = 0
                for flag in primitive.collision_flags:
                    flags |= 1 << type_lut.value_lut[flag.value]
                colflag_attribute_values.extend([flags] * len(faces))

            group_index = len(heiomesh.groups)
            group_attribute_values.extend([group_index] * len(faces))

            group = heiomesh.groups.new(name=f"Primitive {i}")
            group.collision_layer.value = primitive.collision_layer.value
            group.collision_layer.custom = primitive.collision_layer.custom
            group.is_convex_collision = True
            group.convex_type.value = primitive.collision_type.value
            group.convex_type.custom = primitive.collision_type.custom

            for flag in primitive.collision_flags:
                group.convex_flags.new(
                    value=flag.value,
                    custom=flag.custom
                )

        bm.to_mesh(mesh)
        bm.free()

        mesh.heio_mesh.groups.attribute.data.foreach_set(
            'value', group_attribute_values)

        if coltype_attribute_values is not None:
            mesh.heio_mesh.collision_types.attribute.data.foreach_set(
                'value', coltype_attribute_values)

        if colflag_attribute_values is not None:
            mesh.heio_mesh.collision_flags.attribute.data.foreach_set(
                'value', colflag_attribute_values)

        mesh.heio_mesh.collision_primitives.clear()

        # so that the ui list updates too
        for area in context.screen.areas:
            area.tag_redraw()

        return {'FINISHED'}
