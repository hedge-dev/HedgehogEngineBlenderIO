from ctypes import Structure, c_int, c_wchar_p, c_size_t, POINTER
from .util import FieldsFromTypeHints
from .math import CVector3
from .mesh_data import CModelSet
from .collision_mesh_data import CCollisionMeshData

class CPointCloudPoint(Structure, metaclass=FieldsFromTypeHints):
    instance_name: c_wchar_p
    resource_index: c_int
    position: CVector3
    rotation: CVector3
    scale: CVector3

class CPointCloudCloud(Structure, metaclass=FieldsFromTypeHints):
    name: c_wchar_p
    points: POINTER(CPointCloudPoint)
    points_size: c_size_t

class CPointCloudCollection(Structure, metaclass=FieldsFromTypeHints):
    models: POINTER(POINTER(CModelSet))
    models_size: c_size_t

    model_clouds: POINTER(CPointCloudCloud)
    model_clouds_size: c_size_t

    collision_meshes: POINTER(POINTER(CCollisionMeshData))
    collision_meshes_size: c_size_t
    
    collision_mesh_clouds: POINTER(CPointCloudCloud)
    collision_mesh_clouds_size: c_size_t