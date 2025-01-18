from mathutils import Matrix, Quaternion, Vector
from ..dotnet import System, HEIO_NET


def bpy_to_net_matrix(matrix: Matrix):
    return System.MATRIX4X4(
        matrix[0][0], matrix[2][0], -matrix[1][0], 0,
        matrix[0][2], matrix[2][2], -matrix[1][2], 0,
        -matrix[0][1], -matrix[2][1], matrix[1][1], 0,
        matrix[0][3], matrix[2][3], -matrix[1][3], 1
    )


def bpy_bone_xz_to_net_matrix(matrix: Matrix):
    return System.MATRIX4X4(
        matrix[0][1], matrix[2][1], -matrix[1][1], 0,
        matrix[0][2], matrix[2][2], -matrix[1][2], 0,
        matrix[0][0], matrix[2][0], -matrix[1][0], 0,
        matrix[0][3], matrix[2][3], -matrix[1][3], 1
    )


def bpy_bone_xy_to_net_matrix(matrix: Matrix):
    return System.MATRIX4X4(
        matrix[0][1], matrix[2][1], -matrix[1][1], 0,
        -matrix[0][0], -matrix[2][0], matrix[1][0], 0,
        matrix[0][2], matrix[2][2], -matrix[1][2], 0,
        matrix[0][3], matrix[2][3], -matrix[1][3], 1
    )


def bpy_bone_znx_to_net_matrix(matrix: Matrix):
    return System.MATRIX4X4(
        matrix[0][0], matrix[2][0], -matrix[1][0], 0,
        -matrix[0][2], -matrix[2][2], matrix[1][2], 0,
        matrix[0][1], matrix[2][1], -matrix[1][1], 0,
        matrix[0][3], matrix[2][3], -matrix[1][3], 1
    )


def bpy_matrix_to_net_transforms(matrix: Matrix) -> tuple[any, any, any]:
    net_matrix = bpy_to_net_matrix(matrix)

    _, net_scale, _, net_pos = System.MATRIX4X4.Decompose(
        net_matrix,
        System.VECTOR3(0, 0, 0),
        System.QUATERNION(0, 0, 0, 1),
        System.VECTOR3(1, 1, 1))

    net_rot = HEIO_NET.PYTHON_HELPERS.ToEuler(net_matrix)

    return net_pos, net_rot, net_scale


def bpy_to_net_position(position: Vector):
    return System.VECTOR3(position.x, position.z, -position.y)


def bpy_to_net_scale(scale: Vector):
    return System.VECTOR3(scale.x, scale.z, scale.y)


def bpy_to_net_quaternion(quaternion: Quaternion):
    return System.QUATERNION.CreateFromRotationMatrix(bpy_to_net_matrix(quaternion.to_matrix().to_4x4()))
