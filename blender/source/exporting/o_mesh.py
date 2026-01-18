import bpy

from . import o_modelset, o_object_manager, o_util
from ..register.definitions import TargetDefinition
from ..exceptions import HEIODevException
from ..utility import progress_console

class BaseMeshProcessor:

    _target_definition: TargetDefinition
    _object_manager: o_object_manager.ObjectManager
    _modelset_manager: o_modelset.ModelSetManager

    _meshdata_lut: dict[o_modelset.ModelSet, any]
    _output: set[str]
    _output_queue: list

    def __init__(
            self,
            target_definition: TargetDefinition,
            object_manager: o_object_manager.ObjectManager,
            modelset_manager: o_modelset.ModelSetManager):

        self._target_definition = target_definition
        self._object_manager = object_manager
        self._modelset_manager = modelset_manager

        self._meshdata_lut = {}
        self._output = set()
        self._output_queue = []

    def _convert_model_set(self, model_set: o_modelset.ModelSet):
        raise NotImplementedError()

    def _pre_prepare_mesh_data(self, model_sets: list[o_modelset.ModelSet]):
        pass

    def prepare_all_meshdata(self):
        self._pre_prepare_mesh_data(self._modelset_manager.model_set_lut.values())

        progress_console.start("Preparing mesh data for export", len(self._modelset_manager.model_set_lut))

        for i, model_set in enumerate(self._modelset_manager.model_set_lut.values()):
            progress_console.update(f"Converting mesh data for object \"{model_set.obj.name}\"", i)

            if model_set in self._meshdata_lut:
                continue

            self._meshdata_lut[model_set] = self._convert_model_set(model_set)

        progress_console.end()

    def prepare_object_meshdata(self, objects: list[bpy.types.Object]):
        self._pre_prepare_mesh_data([self._modelset_manager.obj_mesh_mapping[obj] for obj in objects])

        progress_console.start("Preparing mesh data for export", len(self._modelset_manager.model_set_lut))

        for i, obj in enumerate(objects):
            progress_console.update(f"Converting mesh data for object \"{obj.name}\"", i)
            model_set = self._modelset_manager.obj_mesh_mapping[obj]

            if model_set in self._meshdata_lut:
                continue

            self._meshdata_lut[model_set] = self._convert_model_set(model_set)

        progress_console.end()

    def get_meshdata(self, obj: bpy.types.Object):
        model_set = self._modelset_manager.obj_mesh_mapping[obj]
        return self._meshdata_lut[model_set]

    @staticmethod
    def get_name(root: bpy.types.Object):
        if root.type == 'EMPTY' and root.instance_type == 'COLLECTION' and root.instance_collection is not None:
            result = root.instance_collection.name
        elif root.data is not None:
            result = root.data.name
        else:
            result = root.name

        return o_util.correct_filename(result)

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

        progress_console.start("Collecting compile data")
        progress_console.update(f"... for model \"{name}\"")

        if root is not None and root.type == 'EMPTY' and root.instance_type == 'COLLECTION' and root.instance_collection is not None:
            root, children = self._object_manager.collection_trees[root.instance_collection]

        compile_data = self._assemble_compile_data(root, children, name)

        progress_console.end()

        if compile_data is None:
            return None

        self._output_queue.append(compile_data)
        self._output.add(name)

        return name

    def compile_output_to_files(self, use_multicore_processing: bool, directory: str):
        raise NotImplementedError()