import ctypes
import ctypes.util
import platform
import os
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

if general.is_windows():
    OS_FOLDER = "windows"
    LIB_EXT = ".dll"
elif general.is_mac():
    OS_FOLDER = "macos"
    LIB_EXT = ".dylib"
elif general.is_linux():
    OS_FOLDER = "linux"
    LIB_EXT = ".so"
else:
    OS_FOLDER = ""
    LIB_EXT = ""

LIB_DIRECTORY = os.path.join(general.ADDON_DIR, "DLL", ARCHITECTURE_FOLDER, OS_FOLDER)

_STDLIB: ctypes.CDLL = None
_DLCLOSE: any = None

def get_dll_close():

    global _STDLIB, _DLCLOSE

    if _DLCLOSE is not None:
        return _DLCLOSE

    # Code taken from https://github.com/bwoodsend/cslug/blob/main/cslug/_stdlib.py

    OS = platform.system()

    def null_free_dll(*spam):
        pass

    # Try to find a good runtime library which is always available and contains
    # the standard library C functions such as malloc() or printf().
    # XXX: Keep chosen library names in sync with the table in `cslug/stdlib.py`.

    if OS == "Windows":  # pragma: Windows
        # _DLCLOSE = ctypes.windll.kernel32.FreeLibrary
        kernel32 = ctypes.WinDLL('kernel32', use_last_error=True)
        kernel32.FreeLibrary.argtypes = [ctypes.wintypes.HMODULE]
        _DLCLOSE = kernel32.FreeLibrary
        try:
            # Windows 11 or older Windows with the universal C runtime installed.
            _STDLIB = ctypes.CDLL("ucrtbase.dll")
        except:  # pragma: no cover
            # Legacy Windows. Note that, as of time of writing, MSVCRT still works
            # on the latest Windows. However, it never was officially even e feature
            # of any Windows version and may disappear at any point.
            _STDLIB = ctypes.CDLL("msvcrt.dll")

    # POSIX should be really simple. The POSIX standard states that a libc, libm and
    # libdl (names are not set in stone) should all be linkable via the names 'c',
    # 'm' and 'dl' (names are set in stone) respectively. The symbols we're
    # interested in are mostly in libc but with math symbols in libm and DLL related
    # symbols in libdl. ctypes.util.find_library() should be able to convert linker
    # names like 'c' to the OS's DLL name to be passed to ctypes.CDLL().
    # In reality however:
    #   - The POSIX standard isn't always followed.
    #   - find_library() doesn't always work.
    #   - libm and libdl are often either empty (with all their symbols moved to
    #     libc) or are symlinks to libc.

    elif OS == "Darwin":  # pragma: Darwin
        # On macOS >= 11.0, find_library() no longer works because system libraries
        # aren't physical files anymore but something more abstract. Fortunately,
        # you can just request libc directly. It contains all standard library
        # symbols.
        _STDLIB = ctypes.CDLL("libc.dylib")
        _DLCLOSE = _STDLIB.dlclose

    elif OS.startswith("MSYS"):  # pragma: msys
        # On MSYS2, find_library() returns 'msys_2_0.dll' when we really want the
        # un-normalised name 'msys-2.0.dll' which contains all the symbols we want.
        # So this must be handled manually.
        _STDLIB = ctypes.CDLL("msys-2.0.dll")
        _DLCLOSE = _STDLIB.dlclose

    elif os.name == "posix":  # pragma: no cover
        # Generic POSIX: This includes all flavours of Linux (even those using
        # alternative libc implementations like Alpine with musl), Cygwin, FreeBSD,
        # and hopefully serves as a sensible default for untested POSIX platforms.

        def _find_check_load_library(name, libc: ctypes.CDLL):
            """Find a library, check that its findable, check that it's not an alias
            of libc, then open it. Raise a tangible error message telling the user
            that it's not their fault and to report it if things go wrong.
            """
            # Get the full name of the library (e.g. convert 'c' to 'libc.so.7').
            full_name = ctypes.util.find_library(name)

            # If find_library() yielded nothing:
            if full_name is None:
                # This happens on musl based Linux only if gcc is not installed.
                # Assume that a symlink to the full name exists by adding the
                # standard prefix and suffix.
                full_name = f"lib{name}.so"

            # If this library turns out to just be an alias for libc:
            if libc and full_name == libc._name:
                # Then there's no point in opening it again.
                return

            # Open the library.
            try:
                return ctypes.CDLL(full_name)
            except OSError:
                # This is fatal only libc.
                if libc is not None:
                    return libc
                # This can fail is, like with msys-2.0.dll, find_library() gave us
                # some incompatibly normalised name like msys_2_0.dll. This will
                # need another explicit case handling like MSYS2 gets above.
                raise OSError(f"Un-openable standard library {name} => {full_name}."
                            f" Please report this on cslug's issue tracker.")

        libc = _find_check_load_library("c", None)
        libdl = _find_check_load_library("dl", libc)

        _STDLIB = libc
        _DLCLOSE = (libdl or libc).dlclose

    else:  # pragma: no cover
        # Default to do nothing.
        _DLCLOSE = null_free_dll

    return _DLCLOSE


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
            del cls._LIBRARY._handle
            cls._LIBRARY._handle = None

            get_dll_close()(handle)

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

    
