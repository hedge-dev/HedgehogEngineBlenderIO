import bpy


def process_mesh_data(
        context: bpy.types.Context,
        mesh_data: any,
        materials: dict[str, bpy.types.Material]):

    mesh = bpy.data.meshes.new(mesh_data.Name)

    if mesh_data.Vertices.Length == 0:
        return mesh

    ##################################################
    # Mesh initialization

    vertices = [(x.Position.X, -x.Position.Z, x.Position.Y)
                for x in mesh_data.Vertices]

    faces = []
    for i in range(0, len(mesh_data.TriangleIndices), 3):
        faces.append((
            mesh_data.TriangleIndices[i],
            mesh_data.TriangleIndices[i + 1],
            mesh_data.TriangleIndices[i + 2])
        )

    mesh.from_pydata(vertices, [], faces, shade_flat=False)

    ##################################################
    # Material Data

    for material in mesh_data.Materials:
        if material is not None and material.Name in materials:
            mesh.materials.append(materials[material.Name][1])
        else:
            mesh.materials.append(None)

    face_index = 0
    for i, face_count in enumerate(mesh_data.MaterialTriangleLengths):
        for f in range(face_index, face_index + face_count):
            mesh.polygons[f].material_index = i
        face_index += face_count

    ##################################################
    # Texture coordinates

    for i, uvmap in enumerate(mesh_data.TextureCoordinates):
        uv_layer = mesh.uv_layers.new(
            name="UVMap" + (str(i + 1) if i > 0 else ""), do_init=False)

        for l, uv in enumerate(uvmap):
            uv_layer.uv[l].vector = (uv.X, uv.Y)

    ##################################################
    # Colors

    color_type = None

    if mesh_data.ByteColors is not None:
        color_type = 'BYTE_COLOR'
        color_data = mesh_data.ByteColors
    elif mesh_data.FloatColors is not None:
        color_type = 'FLOAT_COLOR'
        color_data = mesh_data.FloatColors

    if color_type is not None:
        for i, color_set in enumerate(color_data):
            color_set_name = "Colors"
            if i > 0:
                color_set_name += str(i + 1)

            color_attribute = mesh.color_attributes.new(
                "Color" + (str(i + 1) if i > 0 else ""),
                color_type,
                'CORNER')

            for j, color in enumerate(color_set):
                color_attribute.data[j].color = (
                    color.X, color.Y, color.Z, color.W)

    ##################################################
    # Normals

    mesh.normals_split_custom_set([(x.X, -x.Z, x.Y) for x in mesh_data.Normals])

    ##################################################
    # Cleaning up

    mesh.validate()

    edge_loop_map = [([], []) for _ in mesh.edges]

    for polygon in mesh.polygons:

        for i, loop_index in enumerate(polygon.loop_indices):
            next_loop_index = polygon.loop_indices[i - 2]

            loop = mesh.loops[loop_index]

            edge = mesh.edges[loop.edge_index]
            edge_map = edge_loop_map[loop.edge_index]

            if edge.vertices[0] == loop.vertex_index:
                edge_map[0].append(loop_index)
                edge_map[1].append(next_loop_index)
            else:
                edge_map[0].append(next_loop_index)
                edge_map[1].append(loop_index)

    for edge in (x for x in mesh.edges if x.use_edge_sharp):
        loop_map = edge_loop_map[edge.index]
        if len(loop_map[0]) != 2:
            continue

        nrm0 = mesh.corner_normals[loop_map[0][0]].vector
        nrm1 = mesh.corner_normals[loop_map[0][1]].vector
        nrm2 = mesh.corner_normals[loop_map[1][0]].vector
        nrm3 = mesh.corner_normals[loop_map[1][1]].vector

        if nrm0.dot(nrm1) > 0.995 and nrm2.dot(nrm3) > 0.995:
            edge.use_edge_sharp = False

    return mesh
