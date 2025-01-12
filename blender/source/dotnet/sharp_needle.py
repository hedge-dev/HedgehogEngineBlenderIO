class SharpNeedle:
    '''SharpNeedle library types'''

    RESOURCE_MANAGER: any = None
    '''class SharpNeedle.Resource.ResourceManager'''

    RESOURCE_EXTENSIONS: any = None
    '''class SharpNeedle.Resource.ResourceExtensions'''

    SAMPLE_CHUNK_NODE: any = None
    '''class SharpNeedle.Framework.HedgehogEngine.Mirage.SampleChunkNode'''

    MATERIAL: any = None
    '''class SharpNeedle.Framework.HedgehogEngine.Mirage.Material'''

    TEXTURE: any = None
    '''class SharpNeedle.Framework.HedgehogEngine.Mirage.Texture'''

    WRAP_MODE: any = None
    '''enum SharpNeedle.Framework.HedgehogEngine.Mirage.WrapMode'''

    TERRAIN_MODEL: any = None
    '''enum SharpNeedle.Framework.HedgehogEngine.Mirage.TerrainModel'''

    MODEL: any = None
    '''enum SharpNeedle.Framework.HedgehogEngine.Mirage.Model'''

    BULLET_PRIMITIVE: any = None
    '''enum SharpNeedle.Framework.HedgehogEngine.Bullet.BulletPrimitive'''

    BULLET_PRIMITIVE_SHAPE_TYPE: any = None
    '''enum SharpNeedle.Framework.HedgehogEngine.Bullet.BulletPrimiteShapeType'''

    POINTCLOUD: any = None
    '''class SharpNeedle.Framework.SonicTeam.PointCloud'''

    MATH_HELPER: any = None
    '''class SharpNeedle.Utilities.MathHelper'''

    @classmethod
    def load(cls):

        from SharpNeedle.Resource import ( # type: ignore
            ResourceManager,
            ResourceExtensions
        )

        from SharpNeedle.Framework.HedgehogEngine.Mirage import ( # type: ignore
            SampleChunkNode,
            Material,
            Texture,
            WrapMode,
            TerrainModel,
            Model
        )

        from SharpNeedle.Framework.HedgehogEngine.Bullet import ( # type: ignore
            BulletPrimitive,
            BulletPrimiteShapeType
        )

        from SharpNeedle.Framework.SonicTeam import ( # type: ignore
            PointCloud
        )

        from SharpNeedle.Utilities import (# type: ignore
            MathHelper
        )

        cls.RESOURCE_MANAGER = ResourceManager
        cls.RESOURCE_EXTENSIONS = ResourceExtensions
        cls.SAMPLE_CHUNK_NODE = SampleChunkNode
        cls.MATERIAL = Material
        cls.TEXTURE = Texture
        cls.WRAP_MODE = WrapMode
        cls.TERRAIN_MODEL = TerrainModel
        cls.MODEL = Model
        cls.BULLET_PRIMITIVE = BulletPrimitive
        cls.BULLET_PRIMITIVE_SHAPE_TYPE = BulletPrimiteShapeType
        cls.POINTCLOUD = PointCloud
        cls.MATH_HELPER = MathHelper

