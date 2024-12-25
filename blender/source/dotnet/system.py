class System:
    '''System library types'''

    INT_PTR: any = None
    '''native System.IntPtr'''

    VECTOR4: any = None
    '''struct System.Numerics.Vector4'''

    MATRIX4X4: any = None
    '''struct System.Numerics.Matrix4x4'''

    @classmethod
    def load(cls):

        from System import ( # type: ignore
            IntPtr
        )

        from System.Numerics import ( # type: ignore
            Vector4,
            Matrix4x4
        )

        cls.INT_PTR = IntPtr
        cls.VECTOR4 = Vector4
        cls.MATRIX4X4 = Matrix4x4