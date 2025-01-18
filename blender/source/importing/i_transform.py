from mathutils import Matrix, Vector
from ..dotnet import System, HEIO_NET


def net_to_bpy_matrix(matrix):
    return Matrix((
        (matrix.M11, -matrix.M31, matrix.M21, matrix.M41),
        (-matrix.M13, matrix.M33, -matrix.M23, -matrix.M43),
        (matrix.M12, -matrix.M32, matrix.M22, matrix.M42),
        (0, 0, 0, 1),
    ))


def net_to_bpy_bone_xz_matrix(matrix):
    return Matrix((
        (matrix.M31, matrix.M11, matrix.M21, matrix.M41),
        (-matrix.M33, -matrix.M13, -matrix.M23, -matrix.M43),
        (matrix.M32, matrix.M12, matrix.M22, matrix.M42),
        (0, 0, 0, 1),
    ))


def net_to_bpy_bone_xy_matrix(matrix):
    return Matrix((
        (-matrix.M21, matrix.M11, matrix.M31, matrix.M41),
        (matrix.M23, -matrix.M13, -matrix.M33, -matrix.M43),
        (-matrix.M22, matrix.M12, matrix.M32, matrix.M42),
        (0, 0, 0, 1),
    ))


def net_to_bpy_bone_znx_matrix(matrix):
    return Matrix((
        (matrix.M11, matrix.M31, -matrix.M21, matrix.M41),
        (-matrix.M13, -matrix.M33, matrix.M23, -matrix.M43),
        (matrix.M12, matrix.M32, -matrix.M22, matrix.M42),
        (0, 0, 0, 1),
    ))


def net_transforms_to_bpy_matrix(position, euler_rotation, scale):

    position_mtx = System.MATRIX4X4.CreateTranslation(position)
    rotation_matrix = HEIO_NET.PYTHON_HELPERS.CreateRotationMatrix(euler_rotation)
    scale_mtx = System.MATRIX4X4.CreateScale(scale)

    matrix = scale_mtx * rotation_matrix * position_mtx
    return net_to_bpy_matrix(matrix)


def net_to_bpy_position(position):
    return Vector((position.X, -position.Z, position.Y))


def net_to_bpy_scale(scale):
    return Vector((scale.X, scale.Z, scale.Y))


def net_to_bpy_quaternion(quat):
    return net_to_bpy_matrix(System.MATRIX4X4.CreateFromQuaternion(quat)).to_quaternion()
