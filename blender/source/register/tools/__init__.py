import bpy
from . import collision_primitive_tools

to_register = []

if not bpy.app.background:
    to_register.extend(collision_primitive_tools.to_register)