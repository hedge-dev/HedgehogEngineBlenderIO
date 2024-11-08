import os

from ..utility.general import get_path

_LOADED = False

LIBRARIES = [

]

def load_dotnet():
    global _LOADED
    if _LOADED:
        return

    path = os.path.join(get_path(), "DLL")
    dll_names = [

    ]

    runtime_config = os.path.join(path)

    import pythonnet
    pythonnet.load("coreclr", runtime_config=runtime_config)

    import clr
    for dll_name in dll_names:
        dll_path = os.path.join(path, dll_name)
        clr.AddReference(dll_path) # pylint: disable=no-member

    for library in LIBRARIES:
        library.load()

    _LOADED = True

def unload_dotnet():
	pass
	# Right now, unloading is a bad idea, if other addons use pythonnet too
    # Might be possible in he future to do this proper with assembly load contexts,
    # but that unfortunately does not work right now

    # global _LOADED
    # if not _LOADED:
    #     return

    # for library in reversed(LIBRARIES):
    #     library.unload()

    # import pythonnet
    # pythonnet.unload()

    # _LOADED = False