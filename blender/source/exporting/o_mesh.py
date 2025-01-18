import os
import bpy

from . import o_modelmesh, o_object_manager
from ..register.definitions import TargetDefinition
from ..dotnet import SharpNeedle
from ..exceptions import HEIODevException


class BaseMeshProcessor:

    _target_definition: TargetDefinition
    _object_manager: o_object_manager.ObjectManager
    _modelmesh_manager: o_modelmesh.ModelMeshManager

    _write_dependencies: bool

    _meshdata_lut: dict[o_modelmesh.ModelMesh, any]
    _output: dict[str, any]
    _output_queue: list

    def __init__(
            self,
            target_definition: TargetDefinition,
            object_manager: o_object_manager.ObjectManager,
            modelmesh_manager: o_modelmesh.ModelMeshManager,
            write_dependencies: bool):

        self._target_definition = target_definition
        self._object_manager = object_manager
        self._modelmesh_manager = modelmesh_manager

        self._write_dependencies = write_dependencies

        self._meshdata_lut = {}
        self._output = {}
        self._output_queue = []

    def _convert_modelmesh(self, modelmesh: o_modelmesh.ModelMesh):
        raise NotImplementedError()

    def prepare_all_meshdata(self):
        for modelmesh in self._modelmesh_manager.modelmesh_lut.values():
            if modelmesh in self._meshdata_lut:
                continue

            self._meshdata_lut[modelmesh] = self._convert_modelmesh(modelmesh)

    def prepare_object_meshdata(self, objects: list[bpy.types.Object]):
        for obj in objects:
            modelmesh = self._modelmesh_manager.obj_mesh_mapping[obj]

            if modelmesh in self._meshdata_lut:
                continue

            self._meshdata_lut[modelmesh] = self._convert_modelmesh(modelmesh)

    def get_meshdata(self, obj: bpy.types.Object):
        modelmesh = self._modelmesh_manager.obj_mesh_mapping[obj]
        return self._meshdata_lut[modelmesh]

    @staticmethod
    def get_name(root: bpy.types.Object):
        if root.type == 'EMPTY' and root.instance_type == 'COLLECTION' and root.instance_collection is not None:
            return root.instance_collection.name
        elif root.type in {'ARMATURE', 'MESH'}:
            return root.data.name
        else:
            return root.name

    def _assemble_compile_data(self, root: bpy.types.Object | None, children: list[bpy.types.Object] | None, name: str):
        raise NotImplementedError()

    def enqueue_compile(self, root: bpy.types.Object | None, children: list[bpy.types.Object] | None, name: str | None = None):
        if root is None and (children is None or len(children) == 0):
            raise HEIODevException("No input!")

        if name is None and root is not None:
            name = self.get_name(root)

        if name is None:
            raise HEIODevException("No export name!")

        if name in self._output:
            return name

        if root is not None and root.type == 'EMPTY' and root.instance_type == 'COLLECTION' and root.instance_collection is not None:
            root, children = self._object_manager.collection_trees[root.instance_collection]

        compile_data = self._assemble_compile_data(root, children, name)

        if compile_data is None:
            return None

        self._output_queue.append(compile_data)
        self._output[name] = None

        return name

    def compile_output(self):
        raise NotImplementedError()

    @classmethod
    def _get_extension(cls, data):
        raise NotImplementedError()

    def write_output_to_files(self, directory: str):
        for name, data in self._output.items():
            filepath = os.path.join(directory, name + self._get_extension(data))
            SharpNeedle.RESOURCE_EXTENSIONS.Write(data, filepath, self._write_dependencies)