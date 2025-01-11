class HEIO_NET:
    '''HEIO.NET library types'''

    IMAGE: any = None
    '''class HEIO.NET.Image'''

    PYTHON_HELPERS: any = None
    '''class HEIO.NET.PythonHelpers'''

    MESH_DATA: any = None
    '''class HEIO.NET.MeshData'''

    COLLISION_MESH_DATA: any = None
    '''class HEIO.NET.CollisionMeshData'''

    COLLISION_MESH_DATA_GROUP: any = None
    '''class HEIO.NET.CollisionMeshDataLayer'''

    VERTEX_MERGE_MODE: any = None
    '''enum HEIO.NET.VertexMergeMode'''

    RESOLVE_INFO: any = None
    '''struct HEIO.NET.ResolveInfo'''

    MODEL_HELPER: any = None
    '''class HEIO.NET.ModelHelper'''

    POINT_CLOUD_COLLECTION: any = None
    '''class HEIO.NET.PointCloudCollection'''


    @classmethod
    def load(cls):

        from HEIO.NET import ( # type: ignore
            Image,
            PythonHelpers,
            MeshData,
            CollisionMeshData,
            VertexMergeMode,
            ResolveInfo,
            ModelHelper,
            PointCloudCollection,
            CollisionMeshDataGroup,
            CollisionMeshData
        )

        cls.IMAGE = Image
        cls.PYTHON_HELPERS = PythonHelpers
        cls.MESH_DATA = MeshData
        cls.COLLISION_MESH_DATA = CollisionMeshData
        cls.COLLISION_MESH_DATA_GROUP = CollisionMeshDataGroup
        cls.VERTEX_MERGE_MODE = VertexMergeMode
        cls.RESOLVE_INFO = ResolveInfo
        cls.MODEL_HELPER = ModelHelper
        cls.POINT_CLOUD_COLLECTION = PointCloudCollection
