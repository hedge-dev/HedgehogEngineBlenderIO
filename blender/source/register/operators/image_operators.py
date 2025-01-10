import bpy
from bpy.props import StringProperty, EnumProperty

from .base import HEIOBaseDirectoryLoadOperator
from .. import definitions
from ...utility.general import get_addon_preferences, print_resolve_info
from ...utility import progress_console
from ...dotnet import HEIO_NET, load_dotnet
from ...importing import i_image
from ...exceptions import HEIOUserException


class HEIO_OT_ReimportImages(HEIOBaseDirectoryLoadOperator):
    bl_idname = "heio.reimport_images"
    bl_label = "Reimport missing images"
    bl_description = "Attempt to reimport images that have failed to initially import"
    bl_options = {'UNDO'}

    filter_glob: StringProperty(
        default="*.dds",
        options={'HIDDEN'},
    )

    nrm_invert_y_channel: EnumProperty(
        name="Invert Y channel of normal maps",
        description="Whether to invert the Y channel on normal maps when importing",
        items=(
            ("AUTO", "Automatic",
             "Automatically determine whether to invert the Y channel based on the target game"),
            ("INVERT", "Invert", "Always invert the Y channel"),
            ("DONT", "Don't invert", "Don't invert the Y channel")
        ),
        default="AUTO"
    )

    reimport_images: list[bpy.types.Image]

    def _execute(self, context):

        target_definition = definitions.get_target_definition(context)
        if target_definition is None:
            raise HEIOUserException("Invalid target game!")

        addon_preference = get_addon_preferences(context)

        ntsp_dir = ""

        if target_definition.uses_ntsp:
            ntsp_dir = getattr(addon_preference, "ntsp_dir_" +
                               target_definition.identifier.lower())

        image_loader = i_image.ImageLoader(
            target_definition,
            False,
            self.nrm_invert_y_channel,
            ntsp_dir
        )

        progress_console.cleanup()
        progress_console.start("Loading Images")

        load_dotnet()
        image_loader.load_images_from_directory(
            self.directory,
            [image.heio_image.reimport_name for image in self.reimport_images]
        )

        for image in self.reimport_images:
            name = image.heio_image.reimport_name

            new_image = image_loader.get_image(name)
            if new_image is None:
                continue

            found_texture = None
            for material in bpy.data.materials:
                for texture in material.heio_material.textures:
                    if texture.image == image:
                        found_texture = texture
                        break

                if found_texture is not None:
                    break

            if found_texture is not None:
                new_image = image_loader.get_setup_image(texture, name)

            new_image.rename(image.name, mode='ALWAYS')
            image.user_remap(new_image)
            bpy.data.images.remove(image)

        progress_console.end()

        print_resolve_info(context, image_loader.resolve_infos)

        return {'FINISHED'}

    def _invoke(self, context, event):
        reimport_images = []

        for image in bpy.data.images:
            if len(image.heio_image.reimport_name) > 0:
                reimport_images.append(image)

        if len(reimport_images) == 0:
            raise HEIOUserException("No images need reimporting")

        self.reimport_images = reimport_images

        return super()._invoke(context, event)
