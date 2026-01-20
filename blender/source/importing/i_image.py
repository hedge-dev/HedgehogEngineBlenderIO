import bpy
import numpy
from typing import Iterable

from ..external import HEIONET, TPointer, CMaterial, CResolveInfo, CImage
from ..register.definitions import TargetDefinition
from ..register.property_groups.material_texture_properties import HEIO_MaterialTexture
from ..utility.material_setup import get_first_connected_socket
from ..utility import progress_console


class ImageLoader:

    _target_definition: TargetDefinition

    _use_existing_images: bool
    _invert_normal_map_y_channel: bool
    _ntsp_dir: str

    _loaded_images: dict[str, any]
    _setup_images: dict[str, bpy.types.Image]

    _resolve_infos: list[TPointer[CResolveInfo]]

    def __init__(
            self,
            target_definition: TargetDefinition,
            use_existing_images: bool,
            invert_normal_map_y_channel: bool,
            ntsp_dir: str):

        self._target_definition = target_definition

        self._use_existing_images = use_existing_images
        self._invert_normal_map_y_channel = (
            invert_normal_map_y_channel == "FLIP"
            or (
                invert_normal_map_y_channel == "AUTO"
                and self._target_definition.hedgehog_engine_version == 1
            )
        )
        self._ntsp_dir = ntsp_dir

        self._loaded_images = {}
        self._setup_images = {}

        self._resolve_infos = []

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
    def _import_image_dds_addon(image_name: str, c_image: CImage):
        from blender_dds_addon.ui.import_dds import load_dds  # type: ignore
        import os

        if c_image.streamed_data:
            from tempfile import TemporaryDirectory

            byte_data = bytes(c_image.streamed_data[:c_image.streamed_data_size])

            with TemporaryDirectory() as temp_dir:
                temp = os.path.join(temp_dir, image_name + ".dds")

                with open(temp, "wb") as temp_file:
                    temp_file.write(byte_data)

                image = load_dds(temp)

        else:
            image = load_dds(c_image.file_path)

        image.name = image_name
        image.filepath = os.path.splitext(c_image.file_path)[0] + ".tga"

        image.packed_files[0].filepath = image.filepath

        return image

    @staticmethod
    def _import_image_native(image_name: str, c_image: CImage):
        if c_image.streamed_data is not None:
            image = bpy.data.images.new(image_name, 1, 1)
            image.source = 'FILE'
            image.filepath = c_image.file_path
            byte_data = c_image.streamed_data[:c_image.streamed_data_size]
            image.pack(data=byte_data, data_len=len(byte_data))
            image.packed_files[0].filepath = image.filepath

        else:
            image = bpy.data.images.load(
                c_image.file_path, check_existing=True)
            image.name = image_name

        return image

    def import_image(self, image_name: str, c_image: CImage):
        if "blender_dds_addon" in bpy.context.preferences.addons.keys():
            return self._import_image_dds_addon(image_name, c_image)
        else:
            return self._import_image_native(image_name, c_image)

    def _setup_image(self, texture: HEIO_MaterialTexture, image_name: str):

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
            image.heio_image.reimport_name = image_name

        texture_mode = texture.get_texture_mode(self._target_definition)

        if texture_mode == 'Normal' and from_loaded and self._invert_normal_map_y_channel:
            print(f"Flipping normals of image \"{image_name}\"..")

            if len(image.packed_files) == 0:
                image.pack()

            pixels = numpy.array(image.pixels, dtype=numpy.float32)
            HEIONET.image_invert_green_channel(pixels)
            image.pixels = pixels

            filepath = image.packed_files[0].filepath
            image.pack()
            image.packed_files[0].filepath = filepath

        image.update()

        return image

    def load_images(self, c_images: dict[str, TPointer[CImage]]):
        progress_console.start("Loading Images", len(c_images))

        for i, item in enumerate(c_images.items()):
            name = item[0]
            image = item[1]

            if name in self._loaded_images:
                continue

            progress_console.update(
                f"Loading \"{name}\"", i, clear_below=True)

            self._loaded_images[name] = self.import_image(
                name, image.contents)

        progress_console.end()

    def load_images_from_materials(self, c_materials: Iterable[TPointer[CMaterial]]):

        progress_console.start("Loading Images")
        progress_console.update("Resolving & preparing image files")

        c_images, resolve_info = HEIONET.image_load_material_images(
            c_materials,
            self._ntsp_dir
        ) 
        
        self._resolve_infos.append(resolve_info)

        progress_console.end()

        self.load_images(c_images)

    def load_images_from_directory(self, directory: str, filenames: list[str]):
        progress_console.start("Loading Images")
        progress_console.update("Resolving & preparing image files")

        c_images, resolve_info = HEIONET.image_load_directory_images(
            directory,
            filenames,
            self._ntsp_dir
        )

        self._resolve_infos.append(resolve_info)

        progress_console.end()

        self.load_images(c_images)

    def get_image(self, image_name: str):
        if len(image_name.strip()) == 0:
            return None

        if image_name in self._loaded_images:
            return self._loaded_images[image_name]

        elif self._use_existing_images and image_name in bpy.data.images:
            return bpy.data.images[image_name]

        return None

    def get_setup_image(self, texture: HEIO_MaterialTexture, image_name: str):
        if len(image_name.strip()) == 0:
            return None

        if image_name in self._setup_images:
            return self._setup_images[image_name]

        elif self._use_existing_images and image_name in bpy.data.images:
            return bpy.data.images[image_name]

        elif texture is not None:
            image = self._setup_image(
                texture,
                image_name)

            self._setup_images[image_name] = image
            texture.image = image

            return image

        return None

    @property
    def resolve_infos(self):
        return self._resolve_infos.copy()
