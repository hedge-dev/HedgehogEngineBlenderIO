class System:
    '''System library types'''

    INT_PTR: any = None
    '''native System.IntPtr'''

    VECTOR3: any = None
    '''struct System.Numerics.Vector3'''

    VECTOR4: any = None
    '''struct System.Numerics.Vector4'''

    QUATERNION: any = None
    '''struct System.Numerics.Quaternion'''

    MATRIX4X4: any = None
    '''struct System.Numerics.Matrix4x4'''

    @classmethod
    def load(cls):

        from System import ( # type: ignore
            IntPtr
        )

        from System.Numerics import ( # type: ignore
            Vector3,
            Vector4,
            Quaternion,
            Matrix4x4
        )

        cls.INT_PTR = IntPtr
        cls.VECTOR3 = Vector3
        cls.VECTOR4 = Vector4
        cls.QUATERNION = Quaternion
        cls.MATRIX4X4 = Matrix4x4