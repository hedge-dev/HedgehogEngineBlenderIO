from mathutils import Matrix, Quaternion, Vector
from ..external import CMatrix as cMatrix, CQuaternion as cQuaternion, CVector3 as cVector3


def bpy_to_c_matrix(matrix: Matrix):
    return cMatrix(
        matrix[0][0], matrix[2][0], -matrix[1][0], 0,
        matrix[0][2], matrix[2][2], -matrix[1][2], 0,
        -matrix[0][1], -matrix[2][1], matrix[1][1], 0,
        matrix[0][3], matrix[2][3], -matrix[1][3], 1
    )


def bpy_bone_xz_to_c_matrix(matrix: Matrix):
    return cMatrix(
        matrix[0][1], matrix[2][1], -matrix[1][1], 0,
        matrix[0][2], matrix[2][2], -matrix[1][2], 0,
        matrix[0][0], matrix[2][0], -matrix[1][0], 0,
        matrix[0][3], matrix[2][3], -matrix[1][3], 1
    )


def bpy_bone_xy_to_c_matrix(matrix: Matrix):
    return cMatrix(
        matrix[0][1], matrix[2][1], -matrix[1][1], 0,
        -matrix[0][0], -matrix[2][0], matrix[1][0], 0,
        matrix[0][2], matrix[2][2], -matrix[1][2], 0,
        matrix[0][3], matrix[2][3], -matrix[1][3], 1
    )


def bpy_bone_znx_to_c_matrix(matrix: Matrix):
    return cMatrix(
        matrix[0][0], matrix[2][0], -matrix[1][0], 0,
        -matrix[0][2], -matrix[2][2], matrix[1][2], 0,
        matrix[0][1], matrix[2][1], -matrix[1][1], 0,
        matrix[0][3], matrix[2][3], -matrix[1][3], 1
    )


def bpy_matrix_to_c_transforms(matrix: Matrix) -> tuple[any, any, any]:
    net_matrix = bpy_to_c_matrix(matrix)

    _, net_scale, _, net_pos = System.MATRIX4X4.Decompose(
        net_matrix,
        System.VECTOR3(0, 0, 0),
        System.QUATERNION(0, 0, 0, 1),
        System.VECTOR3(1, 1, 1))

    net_rot = HEIO_NET.PYTHON_HELPERS.ToEuler(net_matrix)

    return net_pos, net_rot, net_scale


def bpy_to_c_position(position: Vector):
    return cVector3(position.x, position.z, -position.y)


def bpy_to_c_scale(scale: Vector):
    return cVector3(scale.x, scale.z, scale.y)


def bpy_to_c_quaternion(quaternion: Quaternion):
    return System.QUATERNION.CreateFromRotationMatrix(bpy_to_c_matrix(quaternion.to_matrix().to_4x4()))
