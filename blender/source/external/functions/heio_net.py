# !!! GENERATED USING HEIO.NET.Utils !!!
# Please do not touch manually!
import ctypes
from .. import nettypes, structs

FUNCTIONS = {
    "free_all": (
        None,
        None,
        "NO ERROR CHECK",
    ),
    "set_wchar_size": (
        (
            ctypes.c_int,
        ),
        None,
        "NO ERROR CHECK",
    ),
    "error_get": (
        None,
        ctypes.c_wchar_p,
        "NO ERROR CHECK",
    ),
    "matrix_multiply": (
        (
            nettypes.CMatrix,
            nettypes.CMatrix,
        ),
        nettypes.CMatrix,
    ),
    "matrix_invert": (
        (
            ctypes.POINTER(nettypes.CMatrix),
        ),
        ctypes.c_bool,
    ),
    "matrix_create_translation": (
        (
            nettypes.CVector3,
        ),
        nettypes.CMatrix,
    ),
    "matrix_create_rotation": (
        (
            nettypes.CVector3,
        ),
        nettypes.CMatrix,
    ),
    "matrix_create_from_quaternion": (
        (
            nettypes.CQuaternion,
        ),
        nettypes.CMatrix,
    ),
    "matrix_create_scale": (
        (
            nettypes.CVector3,
        ),
        nettypes.CMatrix,
    ),
    "matrix_decompose": (
        (
            nettypes.CMatrix,
            ctypes.POINTER(nettypes.CVector3),
            ctypes.POINTER(nettypes.CQuaternion),
            ctypes.POINTER(nettypes.CVector3),
        ),
        None,
    ),
    "matrix_to_euler": (
        (
            nettypes.CMatrix,
        ),
        nettypes.CVector3,
    ),
    "quaternion_create_from_rotation_matrix": (
        (
            nettypes.CMatrix,
        ),
        nettypes.CQuaternion,
    ),
    "resolve_info_combine": (
        (
            ctypes.POINTER(ctypes.POINTER(structs.CResolveInfo)),
            ctypes.c_int,
        ),
        ctypes.POINTER(structs.CResolveInfo),
    ),
    "sample_chunk_node_find": (
        (
            ctypes.POINTER(structs.CSampleChunkNode),
            ctypes.c_wchar_p,
        ),
        ctypes.POINTER(structs.CSampleChunkNode),
    ),
    "image_load_directory_images": (
        (
            ctypes.c_wchar_p,
            ctypes.POINTER(ctypes.c_wchar_p),
            ctypes.c_int,
            ctypes.c_wchar_p,
            ctypes.POINTER(ctypes.POINTER(structs.CResolveInfo)),
        ),
        structs.CArray,
    ),
    "image_load_material_images": (
        (
            ctypes.POINTER(ctypes.POINTER(structs.CMaterial)),
            ctypes.c_int,
            ctypes.c_wchar_p,
            ctypes.POINTER(ctypes.POINTER(structs.CResolveInfo)),
        ),
        structs.CArray,
    ),
    "image_invert_green_channel": (
        (
            ctypes.POINTER(ctypes.c_float),
            ctypes.c_int,
        ),
        None,
    ),
    "material_read_file": (
        (
            ctypes.c_wchar_p,
        ),
        ctypes.POINTER(structs.CMaterial),
    ),
    "material_write_file": (
        (
            ctypes.POINTER(structs.CMaterial),
            ctypes.c_wchar_p,
        ),
        None,
    ),
    "model_read_files": (
        (
            ctypes.POINTER(ctypes.c_wchar_p),
            ctypes.c_int,
            ctypes.c_bool,
            ctypes.POINTER(structs.CMeshImportSettings),
            ctypes.POINTER(ctypes.POINTER(structs.CResolveInfo)),
        ),
        structs.CArray,
    ),
    "model_get_materials": (
        (
            ctypes.POINTER(ctypes.POINTER(structs.CModelSet)),
            ctypes.c_int,
        ),
        structs.CArray,
    ),
    "model_compile_to_files": (
        (
            ctypes.POINTER(ctypes.POINTER(structs.CModelSet)),
            ctypes.c_int,
            ctypes.c_int,
            ctypes.c_int,
            ctypes.c_bool,
            ctypes.c_int,
            ctypes.c_wchar_p,
        ),
        None,
    ),
    "bullet_mesh_read_files": (
        (
            ctypes.POINTER(ctypes.c_wchar_p),
            ctypes.c_int,
            ctypes.POINTER(structs.CMeshImportSettings),
        ),
        structs.CArray,
    ),
    "bullet_mesh_compile_mesh_data": (
        (
            ctypes.POINTER(ctypes.POINTER(structs.CCollisionMeshData)),
            ctypes.c_int,
        ),
        ctypes.POINTER(structs.CBulletMesh),
    ),
    "bullet_mesh_write_to_file": (
        (
            ctypes.POINTER(structs.CBulletMesh),
            ctypes.c_wchar_p,
        ),
        None,
    ),
    "point_cloud_read_files": (
        (
            ctypes.POINTER(ctypes.c_wchar_p),
            ctypes.c_int,
            ctypes.c_bool,
            ctypes.POINTER(structs.CMeshImportSettings),
            ctypes.POINTER(ctypes.POINTER(structs.CResolveInfo)),
        ),
        ctypes.POINTER(structs.CPointCloudCollection),
    ),
    "point_cloud_write_file": (
        (
            ctypes.POINTER(structs.CPointCloudCloud),
            ctypes.POINTER(ctypes.c_wchar_p),
            ctypes.c_int,
            ctypes.c_uint,
            ctypes.c_wchar_p,
        ),
        None,
    ),
}
