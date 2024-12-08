class HEIO_NET:
    '''HEIO.NET library types'''

    IMAGE: any = None
    '''class HEIO.NET.Image'''

    PYTHON_HELPERS: any = None
    '''class HEIO.NET.PythonHelpers'''

    MESH_DATA: any = None
    '''class HEIO.NET.MeshData'''

    VERTEX_MERGE_MODE: any = None
    '''enum HEIO.NET.VertexMergeMode'''

    @classmethod
    def load(cls):

        from HEIO.NET import (
            Image,
            PythonHelpers,
            MeshData,
            VertexMergeMode
        )

        cls.IMAGE = Image
        cls.PYTHON_HELPERS = PythonHelpers
        cls.MESH_DATA = MeshData
        cls.VERTEX_MERGE_MODE = VertexMergeMode