class System:
    '''System library types'''

    VECTOR4: any = None
    '''struct System.Numerics.Vector4'''

    @classmethod
    def load(cls):

        from System.Numerics import (
            Vector4
        )

        cls.VECTOR4 = Vector4