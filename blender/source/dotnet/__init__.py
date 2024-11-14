import os
from .sharp_needle import SharpNeedle
from .heio_net import HEIO_NET

from ..utility.general import get_path

_LOADED = False

LIBRARIES = [
    SharpNeedle,
    HEIO_NET
]

def load_dotnet():
    global _LOADED
    if _LOADED:
        return

    path = os.path.join(get_path(), "DLL")
    dll_names = [
        "SharpNeedle.dll",
        "HEIO.NET.dll"
    ]

    import pythonnet
    pythonnet.load("coreclr")

    import clr
    for dll_name in dll_names:
        dll_path = os.path.join(path, dll_name)
        clr.AddReference(dll_path)

    for library in LIBRARIES:
        library.load()

    _LOADED = True