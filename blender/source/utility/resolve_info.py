import bpy
from ctypes import c_wchar_p
from ..external import Library, CResolveInfo, TPointer

def _c_to_string_array(pointer: TPointer[c_wchar_p], size: int):
    result = []
    for i in range(size):
        result.append(pointer[i])
    return result
        

def print_resolve_info(context: bpy.types.Context, resolve_infos: list[TPointer[CResolveInfo]]):
    resolve_info: CResolveInfo = Library.resolve_info_combine(resolve_infos).contents

    unresolved_files = _c_to_string_array(resolve_info.unresolved_files, resolve_info.unresolved_files_size)
    missing_dependencies = _c_to_string_array(resolve_info.missing_dependencies, resolve_info.missing_dependencies_size)
    packed_dependencies = _c_to_string_array(resolve_info.packed_dependencies, resolve_info.packed_dependencies_size)
    unresolved_ntsp_files = _c_to_string_array(resolve_info.unresolved_ntsp_files, resolve_info.unresolved_ntsp_files_size)
    missing_streamed_images = _c_to_string_array(resolve_info.missing_streamed_images, resolve_info.missing_streamed_images_size)

    if len(unresolved_files) == 0 and len(missing_streamed_images) == 0:
        return

    resolve_info_text = bpy.data.texts.new("Import resolve report")

    def write(text):
        resolve_info_text.write(text)

    add_gap = False

    if len(unresolved_files) > 0:

        write(f"{len(unresolved_files)} files could not be found.\n")
        write("(You can attempt to reimport images using the \"Reimport missing images\" operator found in the viewport tools)\n\n")

        if len(packed_dependencies) > 0:
            write(
                "Some files may be located in the following archives and need to be unpacked:\n")
            for packed in packed_dependencies:
                write(f"\t{packed}\n")

            write("\n")

        if len(missing_dependencies) > 0:
            write("Following dependencies were not found altogether:\n")
            for missing in missing_dependencies:
                write(f"\t{missing}\n")

            write("\n")

        write("List of unresolved files:\n")
        for unresolved_file in unresolved_files:
            write(f"\t{unresolved_file}\n")

        add_gap = True

    if len(missing_streamed_images) > 0:
        if add_gap:
            write("\n\n")

        write((
            f"{len(missing_streamed_images)} images are streamed and could not be loaded,"
            " either because the streaming package (.ntsp file) was not found, or because the"
            " streaming package does not contain the texture that is being looked for.\n"
            "Please make sure that the NTSP filepath in the addon configuration is correctly set.\n"
            "You can attempt to reimport images using the \"Reimport missing images\" operator found in the viewport tools.\n\n"))

        if len(unresolved_ntsp_files) > 0:
            write("Following streaming packages were not found altogether:\n")
            for unresolved_ntsp in unresolved_ntsp_files:
                write(f"\t{unresolved_ntsp}.ntsp\n")

            write("\n")

        write("List of missing streamed images:\n")
        for missing_streamed_image in missing_streamed_images:
            write(f"\t{missing_streamed_image}\n")

    bpy.ops.wm.window_new()
    context.area.type = 'TEXT_EDITOR'
    context.space_data.text = resolve_info_text
    context.space_data.top = 0
    context.space_data.show_syntax_highlight = False
    context.space_data.show_word_wrap = True