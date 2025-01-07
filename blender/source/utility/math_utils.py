from bpy.types import Context, Event
from mathutils import Vector, Matrix


def get_mouse_dir(context: Context, event: Event, world_matrix: Matrix, prev=False):
    if prev:
        mouse_x = event.mouse_prev_x - context.region.x
        mouse_y = event.mouse_prev_y - context.region.y
    else:
        mouse_x = event.mouse_x - context.region.x
        mouse_y = event.mouse_y - context.region.y

    pos = (context.region_data.perspective_matrix @
           world_matrix) @ Vector((0, 0, 0, 1))
    pos = pos / pos.w

    pos_x = (pos.x * 0.5 + 0.5) * context.region.width
    pos_y = (pos.y * 0.5 + 0.5) * context.region.height

    return Vector((mouse_x - pos_x, mouse_y - pos_y)).normalized()


def get_mouse_ray(context: Context, event: Event, prev: bool) -> tuple[Vector, Vector]:
    near_fac = context.space_data.clip_start
    far_fac = context.space_data.clip_end

    in_x = event.mouse_prev_x if prev else event.mouse_x
    in_y = event.mouse_prev_y if prev else event.mouse_y

    mouse_x = ((in_x - context.region.x) /
               context.region.width) * 2 - 1
    mouse_y = ((in_y - context.region.y) /
               context.region.height) * 2 - 1

    mouse_x_near = mouse_x * near_fac
    mouse_y_near = mouse_y * near_fac
    mouse_x_far = mouse_x * far_fac
    mouse_y_far = mouse_y * far_fac

    mat = context.region_data.perspective_matrix.inverted()

    near = mat @ Vector((mouse_x_near, mouse_y_near, -1, near_fac))
    near = near / near.w
    far = mat @ Vector((mouse_x_far, mouse_y_far, 1, far_fac))
    far = far / far.w

    ray_pos = near
    ray_dir = (far - near).normalized()

    return ray_pos.to_3d(), ray_dir.to_3d()


def project_mouse_to_plane(context: Context, event: Event, prev: bool, plane_origin: Vector, plane_normal: Vector):
    ray_pos, ray_dir = get_mouse_ray(context, event, prev)

    div = plane_normal.dot(ray_dir)
    if div == 0:
        return None

    hit = (
        ray_pos + ray_dir
        * ((plane_normal.dot(plane_origin) - plane_normal.dot(ray_pos)) / div)
    )

    return hit


def get_mouse_view_delta(context: Context, event: Event, origin: Vector):
    # Logic taken from blender source:
    # source/blender/editors/gizmo_library/gizmo_types/move3d_gizmo.cc -> move3d_get_translate(...)

    mat = context.region_data.perspective_matrix.copy()

    zfac = (
        (mat[3][0] * origin[0])
        + (mat[3][1] * origin[1])
        + (mat[3][2] * origin[2])
        + mat[3][3]
    )

    if zfac < 1.e-6 and zfac > -1.e-6:
        zfac = 1
    elif zfac < 0:
        zfac = -zfac

    delta_x = (event.mouse_x - event.mouse_prev_x) * \
        2 * zfac / context.region.width
    delta_y = (event.mouse_y - event.mouse_prev_y) * \
        2 * zfac / context.region.height

    mat.invert()
    return Vector((
        mat[0][0] * delta_x + mat[0][1] * delta_y,
        mat[1][0] * delta_x + mat[1][1] * delta_y,
        mat[2][0] * delta_x + mat[2][1] * delta_y,
    ))