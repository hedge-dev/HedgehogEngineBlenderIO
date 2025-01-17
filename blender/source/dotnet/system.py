class System:
    '''System library types'''

    INT_PTR: any = None
    '''native System.IntPtr'''

    LIST: any = None
    '''class System.Collections.Generic.List'''

    VECTOR2: any = None
    '''struct System.Numerics.Vector2'''

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

        from System.Collections.Generic import ( # type: ignore
            List
        )

        from System.Numerics import ( # type: ignore
            Vector2,
            Vector3,
            Vector4,
            Quaternion,
            Matrix4x4
        )

        cls.INT_PTR = IntPtr
        cls.LIST = List
        cls.VECTOR2 = Vector2
        cls.VECTOR3 = Vector3
        cls.VECTOR4 = Vector4
        cls.QUATERNION = Quaternion
        cls.MATRIX4X4 = Matrix4x4