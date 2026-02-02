import os
import bpy
from typing import Iterable
from ..register.definitions import TargetDefinition

NODE_IGNORE_PROPERTIES = [
    "parent",
    "warning_propagation",
    "select",
]


def _get_socket_by_identifier(
        sockets: list[bpy.types.NodeSocket],
        identifier: str) -> bpy.types.NodeSocket:

    for item in sockets:
        if item.identifier == identifier:
            return item
    return None


def _setup_material(
        material: bpy.types.Material,
        template: bpy.types.Material):

    if not material.use_nodes:
        return

    mapping = {}
    node_tree = material.node_tree

    # resetting existing contents
    node_tree.links.clear()
    node_tree.nodes.clear()

    for tnode in template.node_tree.nodes:
        node = node_tree.nodes.new(tnode.bl_idname)
        mapping[tnode] = node

        for property in tnode.bl_rna.properties:
            if property.is_readonly or property.identifier.startswith("bl_") or property.identifier in NODE_IGNORE_PROPERTIES:
                continue

            value = getattr(tnode, property.identifier)
            setattr(node, property.identifier, value)

        for tinput in tnode.inputs:
            input_socket = _get_socket_by_identifier(
                node.inputs, tinput.identifier)
            mapping[tinput] = input_socket
            input_socket.hide = tinput.hide
            if input_socket.type != 'SHADER':
                input_socket.default_value = tinput.default_value

        for toutput in tnode.outputs:
            output_socket = _get_socket_by_identifier(
                node.outputs, toutput.identifier)
            mapping[toutput] = output_socket
            if output_socket.type != 'SHADER':
                output_socket.default_value = toutput.default_value

        node.select = False

    for tlink in template.node_tree.links:
        from_socket = mapping[tlink.from_socket]
        to_socket = mapping[tlink.to_socket]
        node_tree.links.new(from_socket, to_socket)


##################################################


def get_node_of_type(material: bpy.types.Material, name: str, type) -> bpy.types.ShaderNode | None:
    try:
        node = material.node_tree.nodes[name]
    except:
        return None

    if isinstance(node, type):
        return node

    return None


def get_first_connected_socket(socket: bpy.types.NodeSocket):
    if not socket.is_linked:
        return None

    encountered_reroutes = set()
    socket_queue = [socket]
    socket_index = 0

    while socket_index < len(socket_queue):
        socket = socket_queue[socket_index]
        socket_index += 1

        if socket in encountered_reroutes:
            continue

        encountered_reroutes.add(socket)

        for link in socket.links:
            if isinstance(link.to_node, bpy.types.NodeReroute):
                socket_queue.append(link.to_socket)
            else:
                return link.to_socket

    return None


def reset_output_socket(socket: bpy.types.NodeSocket):
    connected = get_first_connected_socket(socket)
    if connected is None:
        return

    socket.default_value = connected.default_value


##################################################


def _get_templates(target_definition: TargetDefinition | None, shader_names: set[str]):
    if target_definition is None:
        return None

    templates_path = os.path.join(
        target_definition.directory,
        "MaterialTemplates.blend")

    shaders = dict()

    with bpy.data.libraries.load(templates_path, link=True) as (data_from, data_to):
        to_load = []

        for shader_name in shader_names:
            material_name = "FALLBACK"
            if shader_name in data_from.materials:
                material_name = shader_name

            try:
                shader_index = to_load.index(material_name)
            except:
                shader_index = len(to_load)
                to_load.append(material_name)

            shaders[shader_name] = shader_index

        data_to.materials = to_load

    return {shader_name: data_to.materials[shaders[shader_name]] for shader_name in shaders}


def setup_and_update_materials(
        target_definition: TargetDefinition | None,
        materials: Iterable[bpy.types.Material]):

    shader_names = set()

    for material in materials:
        shader_name = material.heio_material.shader_name
        shader_names.add(shader_name)

        if len(material.heio_material.variant_name) > 0:
            shader_name += f"[{material.heio_material.variant_name}]"
            shader_names.add(shader_name)

    templates = _get_templates(target_definition, shader_names)

    if templates is None:
        return

    for material in materials:
        material.use_nodes = True

        template = templates[material.heio_material.shader_name]

        if len(material.heio_material.variant_name) > 0:
            shader_name = f"{material.heio_material.shader_name}[{material.heio_material.variant_name}]"
            template = templates[shader_name]

        _setup_material(material, template)
        material.heio_material.update_material_all(target_definition)

    template_materials = set(templates.values())
    for template in template_materials:
        bpy.data.materials.remove(template)


def setup_principled_bsdf_materials(target_definition: TargetDefinition | None, materials: Iterable[bpy.types.Material]):
    for material in materials:
        material.use_nodes = True
        material.node_tree.links.clear()
        material.node_tree.nodes.clear()

        # output node
        output_node = material.node_tree.nodes.new(
            "ShaderNodeOutputMaterial")
        output_node.location = (0, 0)

        # principled node
        principled_node = material.node_tree.nodes.new(
            "ShaderNodeBsdfPrincipled")
        principled_node.location = (-260, 0)
        principled_node.inputs[2].default_value = 0.8
        material.node_tree.links.new(
            output_node.inputs[0], principled_node.outputs[0])

        diffuse_tex = material.heio_material.textures.elements.get(
            "diffuse", None)
        if diffuse_tex is not None and diffuse_tex.image is not None:

            # diffuse texture node
            diffuse_texture_node = material.node_tree.nodes.new(
                "ShaderNodeTexImage")
            diffuse_texture_node.location = (-700, 60)
            diffuse_texture_node.name = "Texture diffuse"
            diffuse_texture_node.label = "sRGB-PBSDF; Texture diffuse"
            diffuse_texture_node.image = diffuse_tex.image
            material.node_tree.links.new(
                principled_node.inputs[0], diffuse_texture_node.outputs[0])
            material.node_tree.links.new(
                principled_node.inputs[4], diffuse_texture_node.outputs[1])

        normal_tex = material.heio_material.textures.elements.get(
            "normal", None)
        if normal_tex is not None and normal_tex.image is not None:

            # normal map node
            normal_map_node = material.node_tree.nodes.new(
                "ShaderNodeNormalMap")
            normal_map_node.location = (-440, -240)
            material.node_tree.links.new(
                principled_node.inputs[5], normal_map_node.outputs[0])

            # normal texture node
            normal_texture_node = material.node_tree.nodes.new(
                "ShaderNodeTexImage")
            normal_texture_node.location = (-700, -240)
            normal_texture_node.name = "Texture normal"
            normal_texture_node.label = "Normal-PBSDF; Texture normal"
            normal_texture_node.image = normal_tex.image
            material.node_tree.links.new(
                normal_map_node.inputs[1], normal_texture_node.outputs[0])

        material.heio_material.update_material_all(target_definition)