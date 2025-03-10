class HEIO_NET:
    '''HEIO.NET library types'''

    IMAGE: any = None
    '''class HEIO.NET.Image'''

    PYTHON_HELPERS: any = None
    '''class HEIO.NET.PythonHelpers'''

    RESOLVE_INFO: any = None
    '''struct HEIO.NET.ResolveInfo'''

    MODEL_HELPER: any = None
    '''class HEIO.NET.ModelHelper'''

    POINT_CLOUD_COLLECTION: any = None
    '''class HEIO.NET.PointCloudCollection'''

    MESH_DATA: any = None
    '''class HEIO.NET.Modeling.MeshData'''

    MESH_DATA_SET_INFO: any = None
    '''class HEIO.NET.Modeling,MeshDataSetInfo'''

    MESH_COMPILE_DATA: any = None
    '''Struct HEIO.NET.Modeling.MeshCompileData'''

    COLLISION_MESH_DATA: any = None
    '''class HEIO.NET.Modeling.CollisionMeshData'''

    COLLISION_MESH_DATA_GROUP: any = None
    '''class HEIO.NET.Modeling.CollisionMeshDataLayer'''

    VERTEX: any = None
    '''class HEIO.NET.Modeling.Vertex'''

    UV_DIRECTION: any = None
    '''struct HEIO.NET.Modeling.UVDirection'''

    VERTEX_WEIGHT: any = None
    '''class HEIO.NET.Modeling.VertexWeight'''

    VERTEX_MERGE_MODE: any = None
    '''enum HEIO.NET.Modeling.VertexMergeMode'''

    TOPOLOGY: any = None
    '''enum HEIO.NET.Modeling.Topology'''

    MODEL_VERSION_MODE: any = None
    '''enum HEIO.NET.Modeling.ModelVersionMode'''

    @classmethod
    def load(cls):

        from HEIO.NET import ( # type: ignore
            Image,
            PythonHelpers,
            ResolveInfo,
            ModelHelper,
            PointCloudCollection,
        )

        from HEIO.NET.Modeling import ( # type: ignore
            MeshData,
            MeshDataSetInfo,
            MeshCompileData,
            CollisionMeshData,
            CollisionMeshDataGroup,
            Vertex,
            UVDirection,
            VertexWeight,
            VertexMergeMode,
            Topology,
            ModelVersionMode
        )

        cls.IMAGE = Image
        cls.PYTHON_HELPERS = PythonHelpers
        cls.RESOLVE_INFO = ResolveInfo
        cls.MODEL_HELPER = ModelHelper
        cls.POINT_CLOUD_COLLECTION = PointCloudCollection

        cls.MESH_DATA = MeshData
        cls.MESH_DATA_SET_INFO = MeshDataSetInfo
        cls.MESH_COMPILE_DATA = MeshCompileData
        cls.COLLISION_MESH_DATA = CollisionMeshData
        cls.COLLISION_MESH_DATA_GROUP = CollisionMeshDataGroup
        cls.VERTEX = Vertex
        cls.UV_DIRECTION = UVDirection
        cls.VERTEX_WEIGHT = VertexWeight
        cls.VERTEX_MERGE_MODE = VertexMergeMode
        cls.TOPOLOGY = Topology
        cls.MODEL_VERSION_MODE = ModelVersionMode
