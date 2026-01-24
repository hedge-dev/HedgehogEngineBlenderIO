import bpy
from bpy.types import Object as BObject

from ..register.property_groups.mesh_properties import MESH_DATA_TYPES

class ObjectManager:

    all_objects: set[BObject]
    base_objects: set[BObject]
    object_trees: dict[BObject, set[BObject]]
    collection_trees: dict[bpy.types.Collection,
                           tuple[BObject | None, list[BObject]]]
    lod_trees: dict[BObject, set[BObject]]

    def __init__(self, include_lod_trees: bool):
        self.all_objects = set()
        self.base_objects = set()
        self.object_trees = {}
        self.collection_trees = {}
        self.lod_trees = {} if include_lod_trees else None

    @staticmethod
    def _get_armature_root(objects: set[BObject]):
        roots = set()
        for obj in objects:
            parent = obj
            while parent.parent is not None:
                parent = parent.parent
            roots.add(parent)

        if len(roots) == 1:
            for root in roots:
                if root.type == 'ARMATURE':
                    objects.add(root)



    @staticmethod
    def assemble_object_trees(objects):
        trees: dict[BObject, set[BObject]] = {}

        for obj in objects:
            available_root_parent = None
            parent = obj.parent
            while parent is not None:
                if parent in objects:
                    available_root_parent = parent
                parent = parent.parent

            if available_root_parent is not None:
                tree = trees.get(available_root_parent, None)
                if tree is None:
                    tree = set()
                    trees[available_root_parent] = tree
                tree.add(obj)

            elif obj not in trees:
                trees[obj] = set()

        return trees

    @staticmethod
    def _get_lod_trees(root):
        result = {}

        if root.type in MESH_DATA_TYPES:
            lod_info = root.data.heio_mesh.lod_info
        elif root.type == 'ARMATURE':
            lod_info = root.data.heio_armature.lod_info
        else:
            return result

        result = {}

        for level in lod_info.levels.elements[1:]:
            if level.target is None:
                continue

            result[level.target] = list(level.target.children_recursive)

        return result

    def _update_objects(self, new_objects: set[BObject]):
        self._get_armature_root(new_objects)
        self.all_objects.update(new_objects)
        self.base_objects.update(new_objects)

        self.object_trees = self.assemble_object_trees(self.base_objects)

        for root in self.object_trees.keys():
            if root.type != 'EMPTY' or root.instance_type != 'COLLECTION' or root.instance_collection is None:
                continue

            coll = root.instance_collection

            if coll in self.collection_trees:
                continue

            collection_objects = set(coll.all_objects)
            self._get_armature_root(collection_objects)
            trees = self.assemble_object_trees(collection_objects)

            if len(trees) == 0:
                continue
            elif len(trees) == 1:
                key = next(iter(trees.keys()))
                self.collection_trees[coll] = (key, trees[key])
            else:
                self.collection_trees[coll] = (None, collection_objects)

            self.all_objects.update(collection_objects)

        # Handling LOD trees

        roots = list(self.object_trees.keys())
        roots.extend([root for root, _ in self.collection_trees.values() if root is not None])

        for root in roots:
            trees = self._get_lod_trees(root)

            for root, children in trees.items():

                if self.lod_trees is not None:
                    self.all_objects.add(root)
                    self.all_objects.update(children)

                if root in self.object_trees:
                    del self.object_trees[root]

            if self.lod_trees is not None:
                self.lod_trees.update(trees)


    def collect_objects(
            self,
            context: bpy.types.Context,
            use_selection: bool,
            use_visible: bool,
            use_active_collection: bool,
            use_active_scene: bool):

        new_objects = set()

        if use_active_collection:
            objects = context.collection.all_objects
        elif use_active_scene:
            objects = context.scene.objects
        else:
            objects = bpy.data.objects

        for obj in objects:
            if (use_visible and not obj.visible_get(view_layer=context.view_layer)
                    or use_selection and not obj.select_get(view_layer=context.view_layer)):
                continue
            new_objects.add(obj)

        self._update_objects(new_objects)
        return new_objects

    def collect_objects_from_collection(self, collection: bpy.types.Collection):
        col_objects = set(collection.all_objects)
        new_objects = set()

        for obj in col_objects:
            if obj in new_objects:
                continue
            new_objects.add(obj)
            new_objects.update(obj.children_recursive)

        self._update_objects(new_objects)
        return new_objects
