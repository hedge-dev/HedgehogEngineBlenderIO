from mathutils import Matrix, Quaternion, Vector
from ..dotnet import System, SharpNeedle


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

    pos = System.VECTOR3(0, 0, 0)
    rot = System.QUATERNION(0, 0, 0, 1)
    scale = System.VECTOR3(1, 1, 1)

    _, net_scale, net_rot, net_pos = System.MATRIX4X4.Decompose(net_matrix, pos, rot, scale)

    net_rot_euler_pyr = SharpNeedle.MATH_HELPER.ToEuler(net_rot)
    net_rot_euler_ypr = System.VECTOR3(net_rot_euler_pyr.Y, net_rot_euler_pyr.X, net_rot_euler_pyr.Z)

    return net_pos, net_rot_euler_ypr, net_scale


def bpy_to_net_position(position: Vector):
    return System.VECTOR3(position.x, position.z, -position.y)


def bpy_to_net_scale(scale: Vector):
    return System.VECTOR3(scale.x, scale.z, scale.y)


def bpy_to_net_quaternion(quaternion: Quaternion):
    return System.QUATERNION.CreateFromRotationMatrix(bpy_to_net_matrix(quaternion.to_matrix().to_4x4()))
