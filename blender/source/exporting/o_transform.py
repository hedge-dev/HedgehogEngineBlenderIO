from mathutils import Matrix, Quaternion, Vector
from ..external import HEIONET, CMatrix, CVector3


def bpy_to_c_matrix(matrix: Matrix):
    return CMatrix(
        matrix[0][0], matrix[2][0], -matrix[1][0], 0,
        matrix[0][2], matrix[2][2], -matrix[1][2], 0,
        -matrix[0][1], -matrix[2][1], matrix[1][1], 0,
        matrix[0][3], matrix[2][3], -matrix[1][3], 1
    )


def bpy_bone_xz_to_c_matrix(matrix: Matrix):
    return CMatrix(
        matrix[0][1], matrix[2][1], -matrix[1][1], 0,
        matrix[0][2], matrix[2][2], -matrix[1][2], 0,
        matrix[0][0], matrix[2][0], -matrix[1][0], 0,
        matrix[0][3], matrix[2][3], -matrix[1][3], 1
    )


def bpy_bone_xy_to_c_matrix(matrix: Matrix):
    return CMatrix(
        matrix[0][1], matrix[2][1], -matrix[1][1], 0,
        -matrix[0][0], -matrix[2][0], matrix[1][0], 0,
        matrix[0][2], matrix[2][2], -matrix[1][2], 0,
        matrix[0][3], matrix[2][3], -matrix[1][3], 1
    )


def bpy_bone_znx_to_c_matrix(matrix: Matrix):
    return CMatrix(
        matrix[0][0], matrix[2][0], -matrix[1][0], 0,
        -matrix[0][2], -matrix[2][2], matrix[1][2], 0,
        matrix[0][1], matrix[2][1], -matrix[1][1], 0,
        matrix[0][3], matrix[2][3], -matrix[1][3], 1
    )


def bpy_matrix_to_c_transforms(matrix: Matrix) -> tuple[any, any, any]:
    c_matrix = bpy_to_c_matrix(matrix)
    c_pos, _, c_scale = HEIONET.matrix_decompose(c_matrix)
    c_rot = HEIONET.matrix_to_euler(c_matrix)

    return c_pos, c_rot, c_scale


def bpy_to_c_position(position: Vector):
    return CVector3(position.x, position.z, -position.y)


def bpy_to_c_scale(scale: Vector):
    return CVector3(scale.x, scale.z, scale.y)


def bpy_to_c_quaternion(quaternion: Quaternion):
    return HEIONET.quaternion_create_from_rotation_matrix(bpy_to_c_matrix(quaternion.to_matrix().to_4x4()))
