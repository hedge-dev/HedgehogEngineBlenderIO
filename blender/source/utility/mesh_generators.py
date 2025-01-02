from mathutils import Vector
import math


def generate_circle(segments: int, scale: float=1):

    vertices = []

    for i in range(segments):
        fac = ((i + 1) / segments) * math.tau
        s = math.sin(fac)
        c = math.cos(fac)

        top = (s * scale, c * scale, scale)

        vertices.append(top)

    cw = 1
    ccw = segments - 1
    result = []

    result.append(vertices[0])

    while True:
        result.append(vertices[cw])

        cw += 1
        if cw == ccw:
            break

        result.append(vertices[ccw])

        ccw -= 1
        if cw == ccw:
            break

    result.append(vertices[cw])

    return result

def generate_circle_lines(segments: int):
    result = []
    for i in range(segments):
        fac = (i / segments) * math.tau
        s = math.sin(fac)
        c = math.cos(fac)

        result.append((c, s, 0))

    result.append(result[0])
    return result


def generate_icosphere(subdivisions: int, scale=1):
    x1 = scale * 0.7236
    x2 = scale * 0.276385
    x3 = scale * 0.894425
    y1 = scale * 0.525731112119133606
    y2 = scale * 0.85064
    z = scale * 0.447215

    vertices = [
        Vector((0, 0, -scale)),

        Vector((x3, 0, -z)),
        Vector((x2, -y2, -z)),
        Vector((-x1, -y1, -z)),
        Vector((-x1, y1, -z)),
        Vector((x2, y2, -z)),

        Vector((x1, -y1, z)),
        Vector((-x2, -y2, z)),
        Vector((-x3, 0, z)),
        Vector((-x2, y2, z)),
        Vector((x1, y1, z)),


        Vector((0, 0, scale)),
    ]

    triangles = [
        (0, 1, 2), (0, 2, 3), (0, 3, 4), (0, 4, 5), (0, 5, 1),
        (2, 1, 6), (3, 2, 7), (4, 3, 8), (5, 4, 9), (1, 5, 10),
        (6, 7, 2), (7, 8, 3), (8, 9, 4), (9, 10, 5), (10, 6, 1),
        (11, 7, 6), (11, 8, 7), (11, 9, 8), (11, 10, 9), (11, 6, 10),
    ]

    lookup: dict[(int, int), int] = dict()

    def vertex_for_edge(a, b):
        if a > b:
            key = (b, a)
        else:
            key = (a, b)

        result = lookup.get(key, None)

        if result is None:
            result = len(vertices)
            vertices.append((vertices[a] + vertices[b]).normalized() * scale)
            lookup[key] = result

        return result

    mid = [0] * 3
    for _ in range(subdivisions):
        new_triangles = []

        for triangle in triangles:
            for i in range(3):
                mid[i] = vertex_for_edge(triangle[i], triangle[(i+1) % 3])

            new_triangles.append((triangle[0], mid[0], mid[2]))
            new_triangles.append((triangle[1], mid[1], mid[0]))
            new_triangles.append((triangle[2], mid[2], mid[1]))
            new_triangles.append((mid[0], mid[1], mid[2]))

        triangles = new_triangles

    result = []
    for triangle in triangles:
        for index in triangle:
            result.append(vertices[index])

    return result


def generate_sphere_lines(segments: int):
    remainder = segments % 4
    if remainder > 0:
        segments += 4 - remainder

    circle_x = []
    circle_y = []
    circle_z = []

    for i in range(segments):
        fac = (i / segments) * math.tau
        s = math.sin(fac)
        c = math.cos(fac)

        circle_x.append((0, s, c))
        circle_y.append((s, 0, c))
        circle_z.append((c, s, 0))

    result = []
    result.extend(circle_x)
    result.extend(circle_y[:(segments >> 2)])
    result.extend(circle_z)
    result.extend(circle_y[(segments >> 2):])
    result.append(circle_y[0])

    return result


def generate_cube(scale=1):
    p = scale
    n = -scale
    return [
        (p, n, n),
        (n, n, n),
        (p, p, n),
        (n, p, n),
        (n, p, p),
        (n, n, n),
        (n, n, p),
        (p, n, n),
        (p, n, p),
        (p, p, n),
        (p, p, p),
        (n, p, p),
        (p, n, p),
        (n, n, p)
    ]


def generate_cube_lines():
    P = 1.0
    N = -1.0

    return [
        (P, P, P), (P, P, N),
        (P, P, P), (P, N, P),
        (P, P, P), (N, P, P),
        (P, P, N), (P, N, N),
        (P, P, N), (N, P, N),
        (P, N, P), (P, N, N),
        (P, N, P), (N, N, P),
        (N, P, P), (N, P, N),
        (N, P, P), (N, N, P),
        (N, N, N), (N, N, P),
        (N, N, N), (N, P, N),
        (N, N, N), (P, N, N)
    ]


def generate_capsule_parts(subdivisions: int, add_offsets: bool, scale=1):
    subdivisions = max(subdivisions, 1)
    sphere = generate_icosphere(subdivisions, scale)

    top_dome = []
    bottom_dome = []

    for i in range(0, len(sphere), 3):
        v1 = sphere[i]
        v2 = sphere[i + 1]
        v3 = sphere[i + 2]

        if v1[2] > 0 or v2[2] > 0 or v3[2] > 0:
            offset = scale
            output = top_dome
        else:
            offset = -scale
            output = bottom_dome

        if not add_offsets:
            offset = 0

        output.append((v1[0], v1[1], v1[2] + offset))
        output.append((v2[0], v2[1], v2[2] + offset))
        output.append((v3[0], v3[1], v3[2] + offset))

    segments = int(math.pow(2, subdivisions)) * 5

    prev_top = (0, scale, scale)
    prev_bottom = (0, scale, -scale)

    cylinder = []

    for i in range(segments):
        fac = ((i + 1) / segments) * math.tau
        s = math.sin(fac)
        c = math.cos(fac)

        top = (s * scale, c * scale, scale)
        bottom = (s * scale, c * scale, -scale)

        cylinder.append(prev_top)
        cylinder.append(top)
        cylinder.append(bottom)

        cylinder.append(prev_top)
        cylinder.append(bottom)
        cylinder.append(prev_bottom)

        prev_top = top
        prev_bottom = bottom

    return top_dome, cylinder, bottom_dome


def generate_capsule(subdivisions: int):
    top, cylinder, bottom = generate_capsule_parts(subdivisions, True)

    result = []
    result.extend(top)
    result.extend(cylinder)
    result.extend(bottom)

    return result


def generate_capsule_lines(segments: int):
    remainder = segments % 4
    if remainder > 0:
        segments += 4 - remainder

    circle_x = []
    circle_y = []
    circle_z_top = []
    circle_z_bottom = []

    quarter = segments >> 2
    z = 1
    offset = z

    for i in range(segments):
        fac = (i / segments) * math.tau
        s = math.sin(fac)
        c = math.cos(fac)

        circle_x.append((0, s, c + offset))
        circle_y.append((s, 0, c + offset))
        circle_z_top.append((c, s, z))
        circle_z_bottom.append((c, s, -z))

        if i == quarter:
            offset = -z
            circle_x.append((0, s, c + offset))
            circle_y.append((s, 0, c + offset))
        elif i == quarter * 3:
            offset = z
            circle_x.append((0, s, c + offset))
            circle_y.append((s, 0, c + offset))

    result = []
    result.extend(circle_x)
    result.extend(circle_y[:(segments >> 2)])
    result.extend(circle_z_top)
    result.append(circle_y[quarter])
    result.extend(circle_z_bottom)
    result.extend(circle_y[((segments >> 2) + 1):])
    result.append(circle_x[0])

    return result


def generate_cylinder(segments: int, scale=1):
    remainder = segments % 4
    if remainder > 0:
        segments += 4 - remainder

    vertices_top = []
    vertices_bottom = []

    result = []

    prev_top = (0, scale, scale)
    prev_bottom = (0, scale, -scale)

    for i in range(segments):
        fac = ((i + 1) / segments) * math.tau
        s = math.sin(fac)
        c = math.cos(fac)

        top = (s * scale, c * scale, scale)
        bottom = (s * scale, c * scale, -scale)

        vertices_top.append(top)
        vertices_bottom.append(bottom)

        result.append(prev_top)
        result.append(top)
        result.append(bottom)

        result.append(prev_top)
        result.append(bottom)
        result.append(prev_bottom)

        prev_top = top
        prev_bottom = bottom

    cw = 1
    ccw = segments - 1
    while True:
        result.append(vertices_top[cw])
        result.append(vertices_top[cw - 1])
        result.append(vertices_top[ccw])

        result.append(vertices_bottom[cw - 1])
        result.append(vertices_bottom[cw])
        result.append(vertices_bottom[ccw])

        ccw -= 1
        if cw == ccw:
            break

        result.append(vertices_top[ccw + 1])
        result.append(vertices_top[ccw])
        result.append(vertices_top[cw])

        result.append(vertices_bottom[ccw])
        result.append(vertices_bottom[ccw + 1])
        result.append(vertices_bottom[cw])

        cw += 1
        if cw == ccw:
            break

    return result


def generate_cylinder_lines(segments: int):
    remainder = segments % 4
    if remainder > 0:
        segments += 4 - remainder

    prev_s = 0
    prev_c = 1
    z = 1

    vertices = [
        (1, 0, z), (1, 0, -z),
        (-1, 0, z), (-1, 0, -z),
        (0, 1, z), (0, 1, -z),
        (0, -1, z), (0, -1, -z),
    ]

    for i in range(segments):
        fac = ((i + 1) / segments) * math.tau
        s = math.sin(fac)
        c = math.cos(fac)

        vertices.append((prev_s, prev_c, z))
        vertices.append((s, c, z))
        vertices.append((prev_s, prev_c, -z))
        vertices.append((s, c, -z))

        prev_s = s
        prev_c = c

    return vertices
