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

    mesh.from_pydata(vertices, [], faces)

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
    # Creating attributes

    for i, uvmap in enumerate(mesh_data.TextureCoordinates):
        uv_layer = mesh.uv_layers.new(
            name="UVMap" + (str(i + 1) if i > 0 else ""), do_init=False)

        for l, uv in enumerate(uvmap):
            uv_layer.uv[l].vector = (uv.X, uv.Y)

    color_type = None

    if mesh_data.ByteColors is not None:
        color_type = 'BYTE_COLOR'
        color_data = mesh_data.ByteColors
    elif mesh_data.FloatColors is not None:
        color_type = 'FLOAT_COLOR'
        color_data = mesh_data.FloatColors

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

    return mesh
