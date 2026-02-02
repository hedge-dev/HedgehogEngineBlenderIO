import bpy
from bpy.props import PointerProperty, StringProperty


class HEIO_Image(bpy.types.PropertyGroup):

    reimport_name: StringProperty(
        name="Reimport name",
        description="Name of the image resource that this image was created as a resource for. Allows for re-import attempts"
    )

    @classmethod
    def register(cls):
        bpy.types.Image.heio_image = PointerProperty(type=cls)