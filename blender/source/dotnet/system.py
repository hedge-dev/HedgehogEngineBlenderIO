class System:
    '''System library types'''

    INT_PTR: any = None
    '''native System.IntPtr'''

    VECTOR4: any = None
    '''struct System.Numerics.Vector4'''

    @classmethod
    def load(cls):

        from System import ( # type: ignore
            IntPtr
        )

        from System.Numerics import ( # type: ignore
            Vector4
        )

        cls.INT_PTR = IntPtr
        cls.VECTOR4 = Vector4