import bpy
import bmesh
from bpy.props import BoolProperty, IntProperty
from mathutils import Vector, Matrix
import math
import bmesh

from .base import HEIOBaseOperator, HEIOBasePopupOperator
from ...exceptions import HEIOUserException, HEIODevException
from ...utility import attribute_utils, mesh_generators


def _ensure_mesh_info_values(lists, force_zero, out_list):

    lut = {}
    for list in lists:
        for element in list:
            if element.value in lut:
                continue

            found = False
            for index, out_type in enumerate(out_list):
                if element.value == out_type.value:
                    found = True
                    break

            if not found:
                index = -2 if element.custom else -1

            lut[element.value] = index

    lutn = len(lut)
    if lutn == 0 or (lutn == 1 and 0 in lut and not force_zero):
        return None

    for v, i in lut.items():
        if i >= 0:
            continue

        lut[v] = len(out_list)
        out_element = out_list.new(value=v)
        out_element.custom = i == -2

    out_list.initialize()
    return lut


class MeshBaseSplitOperator(HEIOBasePopupOperator):
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

    def _get_mesh_info(self, mesh):
        raise HEIODevException("Not implemented")

    def _get_split_name_suffixes(self, mesh_info) -> list[str]:
        raise HEIODevException("Not implemented")

    def _remove_unused_collision_types(self, split_mesh):
        types = split_mesh.heio_collision_mesh.types

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
        flags = split_mesh.heio_collision_mesh.flags

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

    def _remove_unused_mesh_layers(self, split_mesh):
        layers = split_mesh.heio_mesh.layers

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

    def _post_split(self, context, base):
        pass

    def _execute(self, context):
        obj = context.active_object
        mesh: bpy.types.Mesh = obj.data
        mesh_info = self._get_mesh_info(mesh)

        if not mesh_info.initialized:
            raise HEIOUserException(self.type_name + "s not initialized!")

        if mesh_info.attribute_invalid:
            raise HEIOUserException(self.type_name + " attribute invalid!")

        if len(mesh_info) < 2:
            raise HEIOUserException(f"Mesh has less than 2 {self.type_name}s!")

        base_matrix = context.active_object.matrix_world

        for i, suffix in enumerate(self._get_split_name_suffixes(mesh_info)):
            split_mesh = mesh.copy()

            # delete faces

            bm = bmesh.new()
            bm.from_mesh(split_mesh)

            bm_layer = bm.faces.layers.int[mesh_info.attribute_name]
            to_delete = [face for face in bm.faces if face[bm_layer] != i]
            bmesh.ops.delete(bm, geom=to_delete, context='FACES')

            for face in bm.faces:
                face[bm_layer] = 0

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

            split_mesh.name = f"{mesh.name}_{suffix}"
            split_obj = bpy.data.objects.new(f"{obj.name}_{i}", split_mesh)
            split_obj.parent = obj
            split_obj.matrix_world = base_matrix @ Matrix.Translation(center)
            context.collection.objects.link(split_obj)

            split_mesh_info = self._get_mesh_info(split_mesh)

            for j in range(i):
                split_mesh_info.remove(j)

            while len(split_mesh_info) > 1:
                split_mesh_info.remove(1)

            split_mesh.heio_collision_mesh.primitives.clear()
            split_mesh.heio_mesh.lod_info.delete()
            split_mesh.heio_mesh.sca_parameters.clear()

            if self.remove_empty_info:
                self._remove_unused_collision_types(split_mesh)
                self._remove_unused_collision_flags(split_mesh)
                self._remove_unused_mesh_layers(split_mesh)

        if self.root_mesh_copy:
            obj.data = mesh.copy()
            obj.data.name = mesh.name + "_split"

        self._post_split(context, obj)
        obj.data.clear_geometry()

        if self.remove_empty_info:
            obj.data.heio_mesh.groups.delete()
            obj.data.heio_mesh.layers.delete()
            obj.data.heio_collision_mesh.layers.delete()
            obj.data.heio_collision_mesh.types.delete()
            obj.data.heio_collision_mesh.flags.delete()

        return {'FINISHED'}


class HEIO_OT_SplitMeshGroups(MeshBaseSplitOperator):
    bl_idname = "heio.split_meshgroups"
    bl_label = "Split mesh by groups"

    type_name = 'Mesh group'

    def _get_mesh_info(self, mesh):
        return mesh.heio_mesh.groups

    def _get_split_name_suffixes(self, mesh_info):
        return [item.name for item in mesh_info]


class HEIO_OT_SplitCollisionMeshLayers(MeshBaseSplitOperator):
    bl_idname = "heio.split_collisionmeshlayers"
    bl_label = "Split mesh by collision layers"

    type_name = 'Collision layer'

    split_primitives: BoolProperty(
        name="Split primitives",
        description="Split primitives into seperate objects",
        default=True
    )

    def draw(self, context):
        super().draw(context)
        self.layout.prop(self, "split_primitives")

    def _get_mesh_info(self, mesh):
        return mesh.heio_collision_mesh.layers

    def _get_split_name_suffixes(self, mesh_info):
        return [str(i) for i, _ in enumerate(mesh_info)]

    def _post_split(self, context, base):
        if not self.split_primitives:
            return

        for i, primitive in enumerate(base.data.heio_collision_mesh.primitives):
            split_mesh = bpy.data.meshes.new(f"{base.data.name}_primitive{i}")
            split_object = bpy.data.objects.new(
                f"{base.name}_primitive{i}", split_mesh)
            split_object.parent = base
            context.collection.objects.link(split_object)

            split_primitive = split_mesh.heio_collision_mesh.primitives.new()
            split_primitive.shape_type = primitive.shape_type
            split_primitive.dimensions = split_primitive.dimensions

            split_primitive.surface_type.value = primitive.surface_type.value

            for flag in primitive.surface_flags:
                split_flag = split_primitive.surface_flags.new(
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

        base.data.heio_collision_mesh.primitives.clear()


class HEIO_OT_CollisionPrimitivesToGeometry(HEIOBaseOperator):
    bl_idname = "heio.collision_primitives_to_geometry"
    bl_label = "Collision primitives to geometry"
    bl_description = "Convert collision primitives to actual geometry on the mesh"
    bl_options = {'REGISTER', 'UNDO'}

    resolution: IntProperty(
        name="Resolution",
        description="Resolution of the generated meshes",
        min=0,
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
        colmesh = obj.data.heio_collision_mesh

        if len(colmesh.primitives) == 0:
            raise HEIOUserException("Mesh has no collision primitives")

        def check_attributes(list):
            if list.initialized and list.attribute_invalid:
                raise HEIOUserException((
                    f"Invalid \"{list.attribute_name}\" attribute!"
                    " Must use domain \"Face\" and type \"Integer\"!"
                    " Please remove or convert"
                ))

        check_attributes(colmesh.layers)
        check_attributes(colmesh.types)
        check_attributes(colmesh.flags)

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

        colmesh = mesh.heio_collision_mesh
        primitives = colmesh.primitives

        layer_lut = _ensure_mesh_info_values(
            [[prim.surface_layer for prim in primitives]],
            False, colmesh.layers)

        type_lut = _ensure_mesh_info_values(
            [[prim.surface_type for prim in primitives]],
            False, colmesh.types)

        flags_lut = _ensure_mesh_info_values(
            [prim.surface_flags for prim in primitives],
            True, colmesh.flags)

        bm = bmesh.new()
        bm.from_mesh(mesh)

        fli = bm.faces.layers.int
        bm_layer = None if layer_lut is None else fli[colmesh.layers.attribute_name]
        bm_type = None if type_lut is None else fli[colmesh.types.attribute_name]
        bm_flags = None if flags_lut is None else fli[colmesh.flags.attribute_name]

        for primitive in primitives:
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

            attribs = []
            if bm_layer is not None:
                attribs.append(
                    (bm_layer, layer_lut[primitive.surface_layer.value]))

            if bm_type is not None:
                attribs.append(
                    (bm_type, type_lut[primitive.surface_type.value]))

            if bm_flags is not None:
                flags = 0
                for flag in primitive.surface_flags:
                    flags |= 1 << flags_lut[flag.value]
                attribs.append((bm_flags, flags))

            for face in shape_mesh.get_absolute_polygons():
                bm_face = bm.faces.new([verts[f] for f in face])
                for attrib in attribs:
                    bm_face[attrib[0]] = attrib[1]

        bm.to_mesh(mesh)
        bm.free()

        mesh.heio_collision_mesh.primitives.clear()

        # so that the ui list updates too
        for area in context.screen.areas:
            area.tag_redraw()

        return {'FINISHED'}
