class SharpNeedle:
    '''SharpNeedle library types'''

    RESOURCE_MANAGER: any = None
    '''class SharpNeedle.Resource.ResourceManager'''

    RESOURCE_EXTENSIONS: any = None
    '''class SharpNeedle.Resource.ResourceExtensions'''

    SAMPLE_CHUNK_NODE: any = None
    '''class SharpNeedle.FrameWork.HedgehogEngine.Mirage.SampleChunkNode'''

    MATERIAL: any = None
    '''class SharpNeedle.FrameWork.HedgehogEngine.Mirage.Material'''

    TEXTURE: any = None
    '''class SharpNeedle.FrameWork.HedgehogEngine.Mirage.Texture'''

    WRAP_MODE: any = None
    '''enum SharpNeedle.FrameWork.HedgehogEngine.Mirage.WrapMode'''



    @classmethod
    def load(cls):

        from SharpNeedle.Resource import (
            ResourceManager,
            ResourceExtensions
        )

        from SharpNeedle.Framework.HedgehogEngine.Mirage import (
            SampleChunkNode,
            Material,
            Texture,
            WrapMode
        )

        cls.RESOURCE_MANAGER = ResourceManager
        cls.RESOURCE_EXTENSIONS = ResourceExtensions
        cls.SAMPLE_CHUNK_NODE = SampleChunkNode
        cls.MATERIAL = Material
        cls.TEXTURE = Texture
        cls.WRAP_MODE = WrapMode