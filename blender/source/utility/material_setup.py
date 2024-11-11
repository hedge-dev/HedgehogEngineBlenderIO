import os
import bpy

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

TEXTURE_WRAP_MAPPING = {
    "REPEAT": (False, False),
    "MIRROR": (True, False),
    "CLAMP": (False, True),
    "MIRRORONCE": (True, True),
    "BORDER": (False, True),
}
"""[Mode] = (Mirror, Clamp)"""


def _get_first_connected_socket(socket: bpy.types.NodeSocket):
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


def _reset_output_socket(socket: bpy.types.NodeSocket):
    connected = _get_first_connected_socket(socket)
    if connected is None:
        return

    socket.default_value = connected.default_value


def update_material_float_parameter(material: bpy.types.Material, parameter, reset: bool = False):
    node_tree = material.node_tree

    value = parameter.value
    if parameter.is_color:
        value = parameter.color_value

    if parameter.name in node_tree.nodes:
        node = node_tree.nodes[parameter.name]

        if isinstance(node, bpy.types.ShaderNodeRGB):
            if reset:
                _reset_output_socket(node.outputs[0])
            else:
                node.outputs[0].default_value = value

        if isinstance(node, bpy.types.ShaderNodeCombineRGB) or isinstance(node, bpy.types.ShaderNodeCombineXYZ):
            if reset:
                connected = _get_first_connected_socket(node.outputs[0])
                if connected is not None:
                    node.inputs[0].default_value = connected.default_value[0]
                    node.inputs[1].default_value = connected.default_value[1]
                    node.inputs[2].default_value = connected.default_value[2]

            else:
                node.inputs[0].default_value = value[0]
                node.inputs[1].default_value = value[1]
                node.inputs[2].default_value = value[2]

    w_channel = parameter.name + ".w"
    if w_channel in node_tree.nodes:
        node = node_tree.nodes[w_channel]

        if isinstance(node, bpy.types.ShaderNodeValue):
            if reset:
                _reset_output_socket(node.outputs[0])
            else:
                node.outputs[0].default_value = value[4]

    a_channel = parameter.name + ".a"
    if a_channel in node_tree.nodes:
        node = node_tree.nodes[a_channel]

        if isinstance(node, bpy.types.ShaderNodeValue):
            if reset:
                _reset_output_socket(node.outputs[0])
            else:
                node.outputs[0].default_value = value[4]


def update_material_boolean_parameter(material: bpy.types.Material, parameter, reset: bool = False):
    node_tree = material.node_tree

    if parameter.name in node_tree.nodes:
        node = node_tree.nodes[parameter.name]

        if isinstance(node, bpy.types.ShaderNodeValue):
            if reset:
                _reset_output_socket(node.outputs[0])
            else:
                node.outputs[0].default_value = 1 if parameter.value else 0


def update_material_texture(material: bpy.types.Material, texture, reset: bool = False):
    node_tree = material.node_tree

    texture_name = texture.name

    texture_index = texture.type_index
    if texture_index > 0:
        texture_name += str(texture_index)

    texture_node_name = "Texture " + texture_name
    image = None
    if texture_node_name in node_tree.nodes:
        node = node_tree.nodes[texture_node_name]
        if reset:
            node.image = None
        else:
            image = node.image


    # Has Texture node

    has_texture = "Has " + texture_node_name
    if has_texture in node_tree.nodes:
        node = node_tree.nodes[has_texture]

        if isinstance(node, bpy.types.ShaderNodeValue):
            node.outputs[0].default_value = 0 if image is None else 1

    if reset:
        return

    # UV Tiling node

    tiling = "Tiling " + texture_name
    if tiling not in node_tree.nodes:
        return

    node = node_tree.nodes[has_texture]

    if (not isinstance(node, bpy.types.ShaderNodeGroup)
            or node.node_tree.name != "HEIO UV Tiling"):
        return

    node.inputs[1].default_value, node.inputs[3].default_value = TEXTURE_WRAP_MAPPING[texture.wrapmode_u]
    node.inputs[2].default_value, node.inputs[4].default_value = TEXTURE_WRAP_MAPPING[texture.wrapmode_v]

    # Connecting to UV node

    uv_name = "UV" + texture.texcoord_index
    if uv_name not in node_tree.nodes:
        return

    uv_node = node_tree.nodes[uv_name]

    try:
        link: bpy.types.NodeLink = node.inputs[0].links[0]

        if link.from_node == uv_node:
            return

        node_tree.links.remove(link)
    except Exception:
        pass

    node_tree.links.new(uv_node.outputs[0], node.inputs[0])


def update_material_blending(material: bpy.types.Material):
    if material.heio_material.layer == 'TRANSPARENT':
        material.surface_render_method = 'BLENDED'
    else:
        material.surface_render_method = 'DITHERED'


def update_all_material_values(material: bpy.types.Material):

    if not material.use_nodes:
        return

    for float_parameter in material.heio_material.float_parameters:
        update_material_float_parameter(material, float_parameter)

    for boolean_parameter in material.heio_material.boolean_parameters:
        update_material_boolean_parameter(material, boolean_parameter)

    for texture in material.heio_material.textures:
        update_material_texture(material, texture)

    update_material_blending(material)

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
        materials: list[bpy.types.Material]):

    shader_names = set([x.heio_material.shader_name for x in materials])
    templates = _get_templates(context, shader_names)

    for material in materials:
        material.use_nodes = True
        _setup_material(
            material, templates[material.heio_material.shader_name])
        update_all_material_values(material)

    for template in templates.values():
        bpy.data.materials.remove(template)
