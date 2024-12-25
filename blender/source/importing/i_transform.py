from mathutils import Matrix, Vector, Euler, Quaternion
from ..dotnet import System


def parse_net_to_bpy_matrix(matrix):
    '''Casts a .NET matrix directly to a Blender matrix'''
    return Matrix((
        (matrix.M11, matrix.M21, matrix.M31, matrix.M41),
        (matrix.M12, matrix.M22, matrix.M32, matrix.M42),
        (matrix.M13, matrix.M23, matrix.M33, matrix.M43),
        (matrix.M14, matrix.M24, matrix.M34, matrix.M44)
    ))


def net_matrix_to_bpy_transforms(matrix):
    position, rotation, scale = parse_net_to_bpy_matrix(matrix).decompose()

    new_pos = Vector((position.x, -position.z, position.y))
    new_scale = Vector((scale.x, scale.z, scale.y))

    euler_rotation: Euler = rotation.to_euler('XZY')
    new_euler_rotation = Euler(
        (euler_rotation.x, -euler_rotation.z, euler_rotation.y))

    return new_pos, new_euler_rotation, new_scale


def net_to_bpy_matrix(matrix):
    pos, rot, scale = net_matrix_to_bpy_transforms(matrix)
    return Matrix.LocRotScale(pos, rot, scale)


def net_transforms_to_bpy_matrix(position, rotation, scale):

    position_mtx = System.MATRIX4X4.CreateTranslation(position)
    rotation_x_mtx = System.MATRIX4X4.CreateRotationX(rotation.X)
    rotation_y_mtx = System.MATRIX4X4.CreateRotationY(rotation.Y)
    rotation_z_mtx = System.MATRIX4X4.CreateRotationZ(rotation.Z)
    scale_mtx = System.MATRIX4X4.CreateScale(scale)

    rotation_matrix = rotation_x_mtx * rotation_y_mtx * rotation_z_mtx
    matrix = scale_mtx * rotation_matrix * position_mtx

    return net_to_bpy_matrix(matrix)
