import bpy
import bmesh
from bpy.props import BoolProperty
from mathutils import Vector, Matrix

from .base import HEIOBasePopupOperator
from ..property_groups.collision_mesh_properties import HEIO_CollisionLayerList
from ...exceptions import HEIOUserException, HEIODevException
from ...utility import attribute_utils


class MeshBaseSplitOperator(HEIOBasePopupOperator):
    bl_options = {'UNDO'}

    delete_original: BoolProperty(
        name="Delete original",
        description="Delete the original object after splitting",
        default=True
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
        self.layout.prop(self, "delete_original")
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

    def _post_split(self, context, parent):
        pass

    def _execute(self, context):
        name = context.active_object.name
        mesh = context.active_object.data
        mesh_info = self._get_mesh_info(mesh)

        if not mesh_info.initialized:
            raise HEIOUserException(self.type_name + "s not initialized!")

        if mesh_info.attribute_invalid:
            raise HEIOUserException(self.type_name + " attribute invalid!")

        if len(mesh_info) < 2:
            raise HEIOUserException(f"Mesh has less than 2 {self.type_name}s!")

        parent = context.active_object.parent
        base_matrix = context.active_object.matrix_world
        created_parent = False

        if parent is None:
            created_parent = True
            parent = bpy.data.objects.new(name + "_split", None)
            parent.matrix_world = base_matrix
            base_matrix = Matrix.Identity(4)
            context.collection.objects.link(parent)

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
            split_obj = bpy.data.objects.new(f"{name}_{i}", split_mesh)
            split_obj.parent = parent
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

        self._post_split(context, parent)

        if self.delete_original:
            original = context.active_object
            bpy.data.objects.remove(original)

            if created_parent:
                context.view_layer.objects.active = parent
                parent.name = name

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

    def _get_mesh_info(self, mesh):
        return mesh.heio_collision_mesh.layers

    def _get_split_name_suffixes(self, mesh_info):
        return [str(i) for i, _ in enumerate(mesh_info)]

    def _post_split(self, context, parent):
        name = context.active_object.name
        mesh = context.active_object.data

        for i, primitive in enumerate(mesh.heio_collision_mesh.primitives):
            split_mesh = bpy.data.meshes.new(f"{mesh.name}_primitive{i}")
            split_object = bpy.data.objects.new(f"{name}_primitive{i}", split_mesh)
            split_object.parent = parent
            context.collection.objects.link(split_object)

            split_primitive = split_mesh.heio_collision_mesh.primitives.new()
            split_primitive.shape_type = primitive.shape_type
            split_primitive.dimensions = split_primitive.dimensions

            split_primitive.surface_type.value = primitive.surface_type.value

            for flag in primitive.surface_flags:
                split_flag = split_primitive.surface_flags.new(value=flag.value)
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

