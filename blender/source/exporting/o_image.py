import bpy
import os
from typing import Iterable
import numpy

from ..dotnet import HEIO_NET, System
from ..utility import progress_console

def _check_texture_is_normal_map(texture):
	if texture.name.lower() == "normal":
		return True

	node: bpy.types.ShaderNodeTexImage = texture.image_node
	if node is None:
		return False

	prefix_end = node.label.find(";")
	if prefix_end == -1:
		return False

	prefix = node.label[:prefix_end]
	return prefix.lower() == "normal"


def export_material_images(
		materials: Iterable[bpy.types.Material],
		context: bpy.types.Context,
		export_mode: str,
		invert_normal_map_y_channel: bool,
		output_directory: str):

	if "blender_dds_addon" not in context.preferences.addons.keys():
		return

	progress_console.start("Exporting Images")
	progress_console.update("Collecting images to export")

	from blender_dds_addon.ui.export_dds import export_as_dds # type: ignore
	context.scene.dds_options.allow_slow_codec = True
	depsgraph = context.evaluated_depsgraph_get()

	images = set()
	normal_images = set()
	for material in materials:
		for texture in material.heio_material.textures:
			if texture.image is None:
				continue

			images.add(texture.image)

			if invert_normal_map_y_channel and _check_texture_is_normal_map(texture):
				normal_images.add(texture.image)

	progress_console.end()

	progress_console.start("Exporting Images", len(images))

	for i, image in enumerate(images):
		progress_console.update(f"Exporting image \"{image.name}\"", i, True)
		filepath = os.path.join(output_directory, image.name + ".dds")

		if export_mode != 'OVERWRITE' and os.path.isfile(filepath):
			continue

		# evaluating so the DDS addon doesnt overwrite any image data
		export_image: bpy.types.Image = image.evaluated_get(depsgraph)

		if image in normal_images:
			pixels = numpy.array(export_image.pixels, dtype=numpy.float32)
			HEIO_NET.IMAGE.InvertGreenChannel(System.INT_PTR(pixels.ctypes.data), len(pixels))
			export_image.pixels = pixels

		export_as_dds(context, export_image, filepath)

	progress_console.end()