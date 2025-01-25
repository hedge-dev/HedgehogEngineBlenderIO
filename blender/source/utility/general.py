import os
import bpy

from os.path import dirname
from ..dotnet import HEIO_NET

ADDON_DIR = dirname(dirname(dirname(os.path.realpath(__file__))))
ADDON_NAME = os.path.basename(ADDON_DIR)
PACKAGE_NAME = '.'.join(__package__.split('.')[:3])
ICON_DIR = os.path.join(ADDON_DIR, "icons")


def get_addon_preferences(context: bpy.types.Context | None):
    if context is None:
        context = bpy.context
    return context.preferences.addons[PACKAGE_NAME].preferences


def print_resolve_info(context: bpy.types.Context, resolve_infos: list):
    resolve_info = HEIO_NET.RESOLVE_INFO.Combine(resolve_infos)

    if resolve_info.UnresolvedFiles.Length == 0 and resolve_info.MissingStreamedImages.Length == 0:
        return

    resolve_info_text = bpy.data.texts.new("Import resolve report")

    def write(text):
        resolve_info_text.write(text)

    add_gap = False

    if resolve_info.UnresolvedFiles.Length > 0:

        write(f"{resolve_info.UnresolvedFiles.Length} files could not be found.\n")
        write("(You can attempt to reimport images using the \"Reimport missing images\" operator found in the viewport tools)\n\n")

        if resolve_info.PackedDependencies.Length > 0:
            write(
                "Some files may be located in the following archives and need to be unpacked:\n")
            for packed in resolve_info.PackedDependencies:
                write(f"\t{packed}\n")

            write("\n")

        if resolve_info.MissingDependencies.Length > 0:
            write("Following dependencies were not found altogether:\n")
            for missing in resolve_info.MissingDependencies:
                write(f"\t{missing}\n")

            write("\n")

        write("List of unresolved files:\n")
        for unresolved_file in resolve_info.UnresolvedFiles:
            write(f"\t{unresolved_file}\n")

        add_gap = True

    if resolve_info.MissingStreamedImages.Length > 0:
        if add_gap:
            write("\n\n")

        write((
            f"{resolve_info.MissingStreamedImages.Length} images are streamed and could not be loaded,"
            " either because the streaming package (.ntsp file) was not found, or because the"
            " streaming package does not contain the texture that is being looked for.\n"
            "Please make sure that the NTSP filepath in the addon configuration is correctly set.\n"
            "You can attempt to reimport images using the \"Reimport missing images\" operator found in the viewport tools.\n\n"))

        if resolve_info.UnresolvedNTSPFiles.Length > 0:
            write("Following streaming packages were not found altogether:\n")
            for unresolved_ntsp in resolve_info.UnresolvedNTSPFiles:
                write(f"\t{unresolved_ntsp}.ntsp\n")

            write("\n")

        write("List of missing streamed images:\n")
        for missing_streamed_image in resolve_info.MissingStreamedImages:
            write(f"\t{missing_streamed_image}\n")

    bpy.ops.wm.window_new()
    context.area.type = 'TEXT_EDITOR'
    context.space_data.text = resolve_info_text
    context.space_data.top = 0
    context.space_data.show_syntax_highlight = False
    context.space_data.show_word_wrap = True
