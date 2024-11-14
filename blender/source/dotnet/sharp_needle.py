class SharpNeedle:
    '''SharpNeedle library types'''

    RESOURCE_MANAGER: any = None
    '''class SharpNeedle.ResourceManager'''

    RESOURCE_EXTENSIONS: any = None
    '''class SharpNeedle.Utilities.ResourceExtensions'''

    MATERIAL: any = None
    '''class SharpNeedle.HedgehogEngine.Mirage.Material'''

    TEXTURE: any = None
    '''class SharpNeedle.HedgehogEngine.Mirage.Texture'''

    WRAP_MODE: any = None
    '''enum SharpNeedle.HedgehogEngine.Mirage.WrapMode'''

    @classmethod
    def load(cls):

        from SharpNeedle import (
            ResourceManager
        )

        from SharpNeedle.Utilities import (
            ResourceExtensions
        )

        from SharpNeedle.HedgehogEngine.Mirage import (
            Material,
            Texture,
            WrapMode
        )

        cls.RESOURCE_MANAGER = ResourceManager
        cls.RESOURCE_EXTENSIONS = ResourceExtensions
        cls.MATERIAL = Material
        cls.TEXTURE = Texture
        cls.WRAP_MODE = WrapMode