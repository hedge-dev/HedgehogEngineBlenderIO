# !!! GENERATED USING HEIO.NET.Utils !!!
# Please do not touch manually!
import ctypes
from .. import nettypes
from ..typing import TPointer
from .model_set import CModelSet
from .point_cloud_cloud import CPointCloudCloud
from .collision_mesh_data import CCollisionMeshData

class CPointCloudCollection(ctypes.Structure):
    models: TPointer[TPointer['CModelSet']]
    models_size: int
    model_clouds: TPointer['CPointCloudCloud']
    model_clouds_size: int
    collision_meshes: TPointer[TPointer['CCollisionMeshData']]
    collision_meshes_size: int
    collision_mesh_clouds: TPointer['CPointCloudCloud']
    collision_mesh_clouds_size: int

CPointCloudCollection._fields_ = [
    ("models", ctypes.POINTER(ctypes.POINTER(CModelSet))),
    ("models_size", ctypes.c_size_t),
    ("model_clouds", ctypes.POINTER(CPointCloudCloud)),
    ("model_clouds_size", ctypes.c_size_t),
    ("collision_meshes", ctypes.POINTER(ctypes.POINTER(CCollisionMeshData))),
    ("collision_meshes_size", ctypes.c_size_t),
    ("collision_mesh_clouds", ctypes.POINTER(CPointCloudCloud)),
    ("collision_mesh_clouds_size", ctypes.c_size_t),
]

