import ctypes
import typing

class TPointer(ctypes._Pointer):
    class _GenericAlias(typing.GenericAlias):
        def __repr__(self):
            val = super().__repr__()
            ibra = val.find('[')
            idot = val.rfind('.', 0, ibra)
            return f"{val[:idot+1]}POINTER{val[ibra:]}"

    def __class_getitem__(cls, *args):
        ptrtype = ctypes.POINTER(*args)
        alias = TPointer._GenericAlias(ptrtype, *args)
        return alias