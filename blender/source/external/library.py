import ctypes
import _ctypes
import os
import sys
from contextlib import contextmanager
from ..utility import general
from ..exceptions import HEIODevException, HEIOUserException

if general.is_x64():
    if general.is_arm():
        ARCHITECTURE_FOLDER = "arm64"
    else:
        ARCHITECTURE_FOLDER = "x64"
else:
    if general.is_arm():
        ARCHITECTURE_FOLDER = "arm"
    else:
        ARCHITECTURE_FOLDER = "x86"

if sys.platform == "win32":
    OS_FOLDER = "windows"
    LIB_EXT = ".dll"
elif sys.platform == "darwin":
    OS_FOLDER = "macos"
    LIB_EXT = ".dylib"
else:
    OS_FOLDER = "linux"
    LIB_EXT = ".so"

LIB_DIRECTORY = os.path.join(general.ADDON_DIR, "DLL", ARCHITECTURE_FOLDER, OS_FOLDER)

class ExternalLibrary:

    _LIBRARY: ctypes.CDLL | None

    @classmethod
    def _get_library_filename(cls):
        raise HEIODevException("Not Implemented")

    @classmethod
    def _get_library_function_args(cls) -> dict[str, tuple[tuple, any]]:
        raise HEIODevException("Not Implemented")

    @classmethod
    def _lib(cls):
        if cls._LIBRARY is None:
            raise HEIODevException("Library is not loaded")
        return cls._LIBRARY
    
    @classmethod
    @contextmanager
    def load(cls):
        if len(LIB_EXT) == 0:
            raise HEIOUserException("Unknown/Unsupported Operating system!")

        if not os.path.isdir(LIB_DIRECTORY):
            raise HEIOUserException(f"External libraries are not compiled for {ARCHITECTURE_FOLDER} {OS_FOLDER}! Please open a github issue!")
    
        library_filepath = os.path.join(LIB_DIRECTORY, cls._get_library_filename() + LIB_EXT)
        cls._LIBRARY = ctypes.CDLL(library_filepath)

        try:
            cls._setup()
            yield cls
        finally:
            cls._cleanup()

            handle = cls._LIBRARY._handle
            del cls._LIBRARY
            cls._LIBRARY = None

            try:
                _ctypes.FreeLibrary(handle)
            except AttributeError:
                _ctypes.dlclose(handle)
                

    @classmethod
    def _setup(cls):
        lib = cls._lib()
        function_args = cls._get_library_function_args()

        for name, parameters in function_args.items():
            function = getattr(lib, name)
            function.argtypes = parameters[0]
            function.restype = parameters[1]
            
            if len(parameters) < 3:
                function.errcheck = cls._check_error

    @classmethod
    def _check_error(cls, result, func, arguments):
        return result

    @classmethod
    def _cleanup(cls):
        pass            

    
