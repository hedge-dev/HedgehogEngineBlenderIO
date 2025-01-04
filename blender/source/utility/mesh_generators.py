from mathutils import Vector
import math
import gpu
from gpu_extras.batch import batch_for_shader

from ..exceptions import HEIODevException


class GeneratedMeshInfo:

    vertices: list[Vector]
    faces: list[list[int]]
    face_type: str

    polygons: list[list[int]]
    # can use polygons with more than 3 verts

    def __init__(self, vertices: list[Vector], faces: list[list[int]], face_type: str, polygons=None):
        self.vertices = vertices
        self.faces = faces
        self.face_type = face_type
        self.polygons = polygons

    def get_absolute_polygons(self):
        if self.polygons is not None:
            return self.polygons

        if self.faces is not None:
            return self.faces

        if self.face_type == 'TRI_STRIP':
            rev = False
            result = []

            for i in range(len(self.vertices) - 2):
                if rev:
                    result.append((i + 2, i + 1, i))
                else:
                    result.append((i, i + 1, i + 2))
                rev = not rev

            return result

        raise HEIODevException("Invalid faces")

    def to_batch(self, shader) -> gpu.types.GPUBatch:
        return batch_for_shader(
            shader,
            self.face_type,
            {"pos": self.vertices},
            indices=self.faces
        )

    def to_custom_shape(self) -> tuple[gpu.types.GPUBatch, gpu.types.GPUShader]:
        shader = gpu.shader.from_builtin('UNIFORM_COLOR')
        batch = self.to_batch(shader)
        batch.program_set(shader)
        return batch, shader


def circle(segments: int, scale: float = 1):

    vertices = []

    for i in range(segments):
        fac = (i / segments) * math.tau
        vertices.append(Vector((
            math.sin(fac) * scale,
            math.cos(fac) * scale,
            scale
        )))

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

    return GeneratedMeshInfo(vertices, None, 'TRI_STRIP')


def circle_lines(segments: int):
    vertices = []
    for i in range(segments):
        fac = (i / segments) * math.tau

        vertices.append(Vector((
            math.cos(fac),
            math.sin(fac),
            0
        )))

    vertices.append(vertices[0])

    return GeneratedMeshInfo(vertices, None, 'LINE_STRIP')


def icosphere(subdivisions: int, scale=1):
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

    for _ in range(subdivisions):
        new_triangles = []

        for triangle in triangles:
            mid0 = vertex_for_edge(triangle[0], triangle[1])
            mid1 = vertex_for_edge(triangle[1], triangle[2])
            mid2 = vertex_for_edge(triangle[2], triangle[0])

            new_triangles.append((triangle[0], mid0, mid2))
            new_triangles.append((triangle[1], mid1, mid0))
            new_triangles.append((triangle[2], mid2, mid1))
            new_triangles.append((mid0, mid1, mid2))

        triangles = new_triangles

    return GeneratedMeshInfo(vertices, triangles, 'TRIS')


def sphere_lines(segments: int):
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

    vertices = [
        *circle_x,
        *circle_y[:(segments >> 2)],
        *circle_z,
        *circle_y[(segments >> 2):],
        circle_y[0]
    ]

    return GeneratedMeshInfo(vertices, None, 'LINE_STRIP')


def cube(scale=1, strips=True):
    p = scale
    n = -scale

    if strips:

        vertices = [
            Vector((p, n, n)),
            Vector((n, n, n)),
            Vector((p, p, n)),
            Vector((n, p, n)),
            Vector((n, p, p)),
            Vector((n, n, n)),
            Vector((n, n, p)),
            Vector((p, n, n)),
            Vector((p, n, p)),
            Vector((p, p, n)),
            Vector((p, p, p)),
            Vector((n, p, p)),
            Vector((p, n, p)),
            Vector((n, n, p))
        ]

        return GeneratedMeshInfo(vertices, None, 'TRI_STRIP')

    else:

        vertices = [
            Vector((p, p, p)),
            Vector((p, p, n)),
            Vector((p, n, p)),
            Vector((p, n, n)),
            Vector((n, p, p)),
            Vector((n, p, n)),
            Vector((n, n, p)),
            Vector((n, n, n))
        ]

        faces = [
            (0, 1, 5),
            (0, 5, 4),

            (0, 4, 6),
            (0, 6, 2),

            (0, 2, 3),
            (0, 3, 1),

            (7, 6, 4),
            (7, 4, 5),

            (7, 3, 2),
            (7, 2, 6),

            (7, 5, 1),
            (7, 1, 3)

        ]

        polygons = [
            (0, 1, 5, 4),
            (0, 4, 6, 2),
            (0, 2, 3, 1),
            (7, 6, 4, 5),
            (7, 3, 2, 6),
            (7, 5, 1, 3)
        ]

        return GeneratedMeshInfo(vertices, faces, 'TRIS', polygons=polygons)


def cube_lines():
    p = 1.0
    n = -1.0

    vertices = [
        Vector((p, p, p)),
        Vector((p, p, n)),
        Vector((p, n, p)),
        Vector((p, n, n)),
        Vector((n, p, p)),
        Vector((n, p, n)),
        Vector((n, n, p)),
        Vector((n, n, n))
    ]

    lines = [
        (0, 1),
        (0, 2),
        (0, 4),

        (3, 1),
        (3, 2),
        (3, 7),

        (5, 1),
        (5, 4),
        (5, 7),

        (6, 2),
        (6, 4),
        (6, 7)
    ]

    return GeneratedMeshInfo(vertices, lines, 'LINES')


def capsule_parts(subdivisions: int, scale=1):
    subdivisions = max(subdivisions, 1)
    sphere = icosphere(subdivisions, scale)

    vertices_top = []
    index_map_top = [-1] * len(sphere.vertices)

    vertices_bottom = []
    index_map_bottom = index_map_top.copy()

    for i, vertex in enumerate(sphere.vertices):
        if vertex.z >= -0.01:
            index_map_top[i] = len(vertices_top)
            vertices_top.append(vertex)

        if vertex.z <= 0.01:
            index_map_bottom[i] = len(vertices_bottom)
            vertices_bottom.append(vertex)

    faces_top = []
    faces_bottom = []

    for face in sphere.faces:
        f1 = face[0]
        f2 = face[1]
        f3 = face[2]

        m1 = index_map_top[f1]
        m2 = index_map_top[f2]
        m3 = index_map_top[f3]
        output = faces_top

        if m1 == -1 or m2 == -1 or m3 == -1:
            m1 = index_map_bottom[f1]
            m2 = index_map_bottom[f2]
            m3 = index_map_bottom[f3]
            output = faces_bottom

        output.append((m1, m2, m3))

    return (
        GeneratedMeshInfo(vertices_top, faces_top, 'TRIS'),
        cylinder(int(math.pow(2, subdivisions)) * 5, False, scale),
        GeneratedMeshInfo(vertices_bottom, faces_bottom, 'TRIS'),
    )


def capsule(subdivisions: int, scale=1):
    top, cylinder, bottom = capsule_parts(subdivisions, scale)

    top_center_vertices = [(i, math.atan2(vertex.y, vertex.x))
                           for i, vertex in enumerate(top.vertices) if vertex.z <= 0.01]
    top_center_vertices.sort(key=lambda x: x[1], reverse=True)

    bottom_center_vertices = [(i, math.atan2(vertex.y, vertex.x))
                              for i, vertex in enumerate(bottom.vertices) if vertex.z >= -0.01]
    bottom_center_vertices.sort(key=lambda x: x[1], reverse=True)

    top_len = len(top.vertices)
    index_map = [
        *[x[0] for x in top_center_vertices],
        *[x[0] + top_len for x in bottom_center_vertices]
    ]

    vertices = [
        *[vert + Vector((0, 0, 1)) for vert in top.vertices],
        *[vert - Vector((0, 0, 1)) for vert in bottom.vertices]
    ]

    triangles = [
        *top.faces,
        *[[i + top_len for i in face] for face in bottom.faces]
    ]

    faces = [
        *triangles,
        *[[index_map[i] for i in face] for face in cylinder.faces]
    ]

    polygons = [
        *triangles,
        *[[index_map[i] for i in poly] for poly in cylinder.polygons]
    ]

    return GeneratedMeshInfo(vertices, faces, 'TRIS', polygons=polygons)


def capsule_lines(segments: int):
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

    vertices = [
        *circle_x,
        *circle_y[:(segments >> 2)],
        *circle_z_top,
        circle_y[quarter],
        *circle_z_bottom,
        *circle_y[((segments >> 2) + 1):],
        circle_x[0]
    ]

    return GeneratedMeshInfo(vertices, None, 'LINE_STRIP')


def cylinder(segments: int, generate_caps: bool, scale=1):
    vertices_top = []
    vertices_bottom = []

    faces = []
    polygons = []

    for i in range(segments):
        fac = (i / segments) * math.tau
        s = math.sin(fac) * scale
        c = math.cos(fac) * scale

        vertices_top.append(Vector((s, c, scale)))
        vertices_bottom.append(Vector((s, c, -scale)))

        next = (i + 1) % segments

        faces.append((i, next, segments + next))
        faces.append((i, segments + next, segments + i))
        polygons.append((i, next, segments + next, segments + i))

    if generate_caps:
        cw = 1
        ccw = segments - 1
        while True:
            faces.append((cw, cw - 1, ccw))
            faces.append((segments + cw - 1, segments + cw, segments + ccw))

            ccw -= 1
            if cw == ccw:
                break

            faces.append((ccw + 1, ccw, cw))
            faces.append((segments + ccw, segments + ccw + 1, segments + cw))

            cw += 1
            if cw == ccw:
                break

        polygons.append(list(range(segments)))
        polygons.append(list(range(segments, segments * 2)))

    return GeneratedMeshInfo([*vertices_top, *vertices_bottom], faces, 'TRIS', polygons=polygons)


def cylinder_lines(segments: int):
    remainder = segments % 4
    if remainder > 0:
        segments += 4 - remainder

    z = 1

    vertices = []
    lines = []

    for i in range(segments):
        fac = (i / segments) * math.tau
        s = math.sin(fac)
        c = math.cos(fac)

        vertices.append((s, c, z))
        vertices.append((s, c, -z))

        next = ((i + 1) % segments) * 2
        i *= 2

        lines.append((i, next))
        lines.append((i + 1, next + 1))

    o = len(vertices)
    lines.extend([
        (o, o + 1),
        (o + 2, o + 3),
        (o + 4, o + 5),
        (o + 6, o + 7),
    ])

    vertices.extend([
        (1, 0, z), (1, 0, -z),
        (-1, 0, z), (-1, 0, -z),
        (0, 1, z), (0, 1, -z),
        (0, -1, z), (0, -1, -z)
    ])

    return GeneratedMeshInfo(vertices, lines, 'LINES')
