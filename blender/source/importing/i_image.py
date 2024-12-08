import bpy
import numpy

from ..dotnet import HEIO_NET, System

from ..utility.material_setup import get_first_connected_socket


class ImageLoader:

    _use_existing_images: bool
    _invert_normal_map_y_channel: bool

    _loaded_images: dict[str, any]
    _setup_images: dict[str, bpy.types.Image]

    def __init__(
            self,
            use_existing_images: bool,
            invert_normal_map_y_channel: bool):

        self._use_existing_images = use_existing_images
        self._invert_normal_map_y_channel = invert_normal_map_y_channel

        self._loaded_images = {}
        self._setup_images = {}

    @staticmethod
    def _get_placeholder_image_color(node: bpy.types.ShaderNodeTexImage):
        if node is None:
            return (1, 1, 1, 1)

        rgb_connection = get_first_connected_socket(node.outputs[0])
        alpha_connection = get_first_connected_socket(node.outputs[1])

        red = green = blue = alpha = 1

        if rgb_connection is not None:
            if rgb_connection.type == 'VALUE':
                red = green = blue = rgb_connection.default_value
            elif rgb_connection.type in ['RGBA', 'VECTOR']:
                red = rgb_connection.default_value[0]
                green = rgb_connection.default_value[1]
                blue = rgb_connection.default_value[2]

        if alpha_connection is not None:
            if alpha_connection.type == 'VALUE':
                alpha = alpha_connection.default_value
            elif alpha_connection.type in ['RGBA', 'VECTOR']:
                rgb = alpha_connection.default_value
                alpha = 0.2989 * rgb[0] + 0.5870 * rgb[1] + 0.1140 * rgb[2]

        return (red, green, blue, alpha)

    @staticmethod
    def _import_image_dds_addon(image_name: str, net_image):
        from blender_dds_addon.ui.import_dds import load_dds
        import os

        if net_image.StreamedData is not None:
            from tempfile import TemporaryDirectory

            byte_data = bytes(net_image.StreamedData)

            with TemporaryDirectory() as temp_dir:
                temp = os.path.join(temp_dir, image_name + ".dds")

                with open(temp, "wb") as temp_file:
                    temp_file.write(byte_data)

                image = load_dds(temp)

        else:
            image = load_dds(net_image.Filepath)

        image.name = image_name
        image.filepath = os.path.splitext(net_image.Filepath)[0] + ".tga"

        image.packed_files[0].filepath = image.filepath

        return image

    @staticmethod
    def _import_image_native(image_name: str, net_image):
        if net_image.StreamedData is not None:
            image = bpy.data.images.new(image_name, 1, 1)
            image.source = 'FILE'
            image.filepath = net_image.Filepath
            byte_data = bytes(net_image.StreamedData)
            image.pack(data=byte_data, data_len=len(byte_data))
            image.packed_files[0].filepath = image.filepath

        else:
            image = bpy.data.images.load(
                net_image.Filepath, check_existing=True)
            image.name = image_name

        return image

    def _setup_image(self, texture, image_name: str):

        image = None
        from_loaded = False
        node: bpy.types.ShaderNodeTexImage = texture.image_node

        if image_name in self._loaded_images:
            image = self._loaded_images[image_name]
            from_loaded = True

        if image is None:
            # placeholder texture
            image = bpy.data.images.new(
                image_name,
                16,
                16,
                alpha=True)

            image.source = 'GENERATED'
            image.generated_color = self._get_placeholder_image_color(node)

        is_normal_map = texture.name.lower() == "normal"

        if node is not None:
            label_type = node.label.split(";")[0]

            if label_type == 'sRGB':
                image.colorspace_settings.name = 'sRGB'
            elif label_type == 'Linear':
                image.colorspace_settings.name = 'Non-Color'
            elif label_type == 'Normal':
                image.colorspace_settings.name = 'Non-Color'
                is_normal_map = True

        if is_normal_map and from_loaded and self._invert_normal_map_y_channel:
            pixels = numpy.array(image.pixels, dtype=numpy.float32)
            HEIO_NET.IMAGE.InvertGreenChannel(
                System.INT_PTR(pixels.ctypes.data), len(pixels))
            image.pixels = pixels

            filepath = image.packed_files[0].filepath
            image.pack()
            image.packed_files[0].filepath = filepath

        image.update()

        return image

    def load_images_from_sn_materials(self, sn_materials, ntsp_dir: str):

        net_images = HEIO_NET.IMAGE.LoadMaterialImages(
            sn_materials, ntsp_dir)

        for item in net_images:

            if "blender_dds_addon" in bpy.context.preferences.addons.keys():
                image = self._import_image_dds_addon(item.Key, item.Value)
            else:
                image = self._import_image_native(item.Key, item.Value)

            self._loaded_images[item.Key] = image


    def get_image(self, texture, image_name: str):
        if len(image_name.strip()) == 0:
            return None

        if image_name in self._setup_images:
            return self._setup_images[image_name]
        elif self._use_existing_images and image_name in bpy.data.images:
            return bpy.data.images[image_name]
        else:
            image = self._setup_image(
                texture,
                image_name)

            self._setup_images[image_name] = image
            texture.image = image

            return image
