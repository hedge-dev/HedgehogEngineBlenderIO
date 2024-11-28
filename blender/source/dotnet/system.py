class System:
    '''System library types'''

    INT_PTR: any = None
    '''native System.IntPtr'''

    VECTOR4: any = None
    '''struct System.Numerics.Vector4'''

    @classmethod
    def load(cls):

        from System import (
            IntPtr
        )

        from System.Numerics import (
            Vector4
        )

        cls.INT_PTR = IntPtr
        cls.VECTOR4 = Vector4