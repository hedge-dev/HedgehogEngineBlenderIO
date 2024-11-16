import os
import bpy
from typing import Iterable

from ..utility import general


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
    material.preview_render_type = 'FLAT'

    # resetting existing contents
    node_tree.links.clear()
    node_tree.nodes.clear()

    for tnode in template.node_tree.nodes:
        node = node_tree.nodes.new(tnode.bl_idname)
        mapping[tnode] = node

        node.name = tnode.name
        node.label = tnode.label
        node.height = tnode.height
        node.width = tnode.width
        node.location = tnode.location
        node.hide = tnode.hide

        if tnode.type == 'GROUP':
            node.node_tree = tnode.node_tree

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


def _predict_material_name(name):
    if name not in bpy.data.materials:
        return name

    number = 1
    number_name = f"{name}.{number:03}"
    while number_name in bpy.data.materials:
        number += 1
        number_name = f"{name}.{number:03}"

    return number_name


def _get_templates(context: bpy.types.Context, shader_names: set[str]):
    setups_path = os.path.join(
        general.get_path(),
        "Definitions",
        context.scene.heio_scene.target_game,
        "MaterialSetups.blend")

    shader_materials = {}

    with bpy.data.libraries.load(setups_path) as (data_from, data_to):
        to_load = {}

        for shader_name in shader_names:
            material_name = "FALLBACK"
            if shader_name in data_from.materials:
                material_name = shader_name

            if material_name not in to_load:
                imported_name = _predict_material_name(material_name)
                to_load[material_name] = imported_name
            else:
                imported_name = to_load[material_name]

            shader_materials[shader_name] = imported_name

        data_to.materials.extend(to_load.keys())

    return {shader_name: bpy.data.materials[material_name] for shader_name, material_name in shader_materials.items()}


def setup_and_update_materials(
        context: bpy.types.Context,
        materials: Iterable[bpy.types.Material]):

    shader_names = set([x.heio_material.shader_name for x in materials])
    templates = _get_templates(context, shader_names)

    for material in materials:
        material.use_nodes = True
        _setup_material(
            material, templates[material.heio_material.shader_name])
        material.heio_material.update_material_all()

    template_materials = set(templates.values())
    for template in template_materials:
        bpy.data.materials.remove(template)
