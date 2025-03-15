import bpy
from bpy.props import (
    FloatVectorProperty,
    FloatProperty,
    PointerProperty
)
from mathutils import Vector

def linear_to_srgb(val: float):
    if val < 0.0031308:
        return val * 12.92
    else:
        return 1.055 * pow(val, 1.0 / 2.4) - 0.055

def srgb_to_linear(val: float):
    if val < 0.04045:
        return val / 12.92
    else:
        return  pow((val + 0.055) / 1.055, 2.4)

def _get_brush_color():
    scene = bpy.context.scene
    if scene.tool_settings.unified_paint_settings.use_unified_color:
        result = scene.tool_settings.unified_paint_settings.color
    else:
        result = scene.tool_settings.vertex_paint.brush.color

    return Vector((
        srgb_to_linear(result[0]),
        srgb_to_linear(result[1]),
        srgb_to_linear(result[2])
    ))


def _set_brush_color(value):

    value = (
        linear_to_srgb(value[0]),
        linear_to_srgb(value[1]),
        linear_to_srgb(value[2])
    )

    scene = bpy.context.scene
    if scene.tool_settings.unified_paint_settings.use_unified_color:
        scene.tool_settings.unified_paint_settings.color = value
    else:
        scene.tool_settings.vertex_paint.brush.color = value


def _get_brush_vector():
    result = _get_brush_color()
    return Vector((
        result[0] * 2 - 1,
        result[1] * 2 - 1,
        result[2] * 2 - 1
    ))


def _set_brush_vector(value: Vector):
    _set_brush_color((
        value[0] * 0.5 + 0.5,
        value[1] * 0.5 + 0.5,
        value[2] * 0.5 + 0.5
    ))


def _get_vertex_paint_direction(props):
    vector = _get_brush_vector()

    if vector.length < 0.001:
        return Vector((0, 0, 0))
    else:
        return vector.normalized()


def _set_vertex_paint_direction(props, value):
    vector = _get_brush_vector()
    if vector.length < 0.001:
        return
    _set_brush_vector(Vector(value) * min(1, vector.length))


def _get_vertex_paint_bend(props):
    return min(1, _get_brush_vector().length)


def _set_vertex_paint_bend(props, value):
    vector = _get_brush_vector()
    if value < 0.001:
        vector = Vector()
    elif vector.length < 0.001:
        vector = Vector((0, 0, min(1, value)))
    else:
        vector = vector.normalized() * min(1, value)
    _set_brush_vector(vector)


def _get_vertex_paint_length(props):
    color = _get_brush_color()
    return color[0] * 0.2126 + color[1] * 0.7152 + color[2] * 0.0722


def _set_vertex_paint_length(props, value):
    _set_brush_color((value, value, value))


class HEIO_BlenderUtilities(bpy.types.PropertyGroup):

    vertex_paint_direction: FloatVectorProperty(
        name="Vertex Paint Direction",
        description="The vertex paint color as a normal",
        subtype='DIRECTION',
        min=-1, max=1,
        get=_get_vertex_paint_direction,
        set=_set_vertex_paint_direction
    )

    vertex_paint_factor: FloatProperty(
        name="Vertex Paint Factor",
        description="How much the painted vertex color should influence the color away from the normal, 0 means \"Use Normal direction\"",
        subtype='FACTOR',
        min=0, max=1,
        get=_get_vertex_paint_bend,
        set=_set_vertex_paint_bend
    )

    vertex_paint_length: FloatProperty(
        name="Vertex Paint length",
        description="The fur length paint factor",
        get=_get_vertex_paint_length,
        set=_set_vertex_paint_length,
        min=0, max=1,
        subtype='FACTOR'
    )

    @property
    def vertex_direction_info(self):
        vector = _get_brush_vector()
        if vector.length < 0.001:
            return "[Using Normal]"

        abs_vector = Vector((abs(vector[0]), abs(vector[1]), abs(vector[2])))

        current_vec = Vector()
        current_dot = 0

        def comp_vec(x, y, z):
            nonlocal current_vec
            nonlocal current_dot

            vec = Vector((x, y, z))
            dot = vec.dot(abs_vector)

            if dot > current_dot:
                current_dot = dot
                current_vec = vec

        comp_vec(1, 0, 0)
        comp_vec(0, 1, 0)
        comp_vec(0, 0, 1)
        comp_vec(0.707, 0.707, 0)
        comp_vec(0.707, 0, 0.707)
        comp_vec(0, 0.707, 0.707)
        comp_vec(0.577, 0.577, 0.577)

        result = []

        if current_vec.x > 0:
            if vector.x > 0:
                result.append("+X")
            else:
                result.append("-X")

        if current_vec.y > 0:
            if vector.y > 0:
                result.append("+Y")
            else:
                result.append("-Y")

        if current_vec.z > 0:
            if vector.z > 0:
                result.append("+Z")
            else:
                result.append("-Z")

        return ", ".join(result)

    @classmethod
    def register(cls):
        bpy.types.Scene.heio_blender_utilities = PointerProperty(
            type=HEIO_BlenderUtilities)
