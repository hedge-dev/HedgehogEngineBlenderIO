using HEIO.NET.Internal.Modeling;
using System.Numerics;

namespace HEIO.NET.External.Structs
{
    public unsafe struct CMeshData : IConvertInternal<MeshData>
    {
        public char* name;

        public CVertex* vertices;
        public int verticesSize;

        public int triangleIndexCount;

        public int* triangleIndices;
        public Vector3* polygonNormals;
        public CUVDirection* polygonUVDirections;
        public CUVDirection* polygonUVDirections2;

        public Vector2** textureCoordinates;
        public int textureCoordinatesSize;

        public Vector4** colors;
        public int colorsSize;

        public CMeshDataMeshSetInfo* meshSets;
        public int meshSetsSize;

        public CMeshDataMeshGroupInfo* groups;
        public int groupsSize;

        public char** morphNames;
        public int morphNamesSize;

        public static CMeshData FromInternal(MeshData meshData)
        {
            CMeshData result = new()
            {
                name = meshData.Name.AllocString(),

                vertices = Allocate.AllocFromArray(meshData.Vertices, CVertex.FromInternal),
                verticesSize = meshData.Vertices.Count,

                triangleIndexCount = meshData.TriangleIndices.Count,

                triangleIndices = Allocate.AllocFromArray(meshData.TriangleIndices),
                polygonNormals = Allocate.AllocFromArray(meshData.PolygonNormals),
                polygonUVDirections = Allocate.AllocFromArray(meshData.PolygonUVDirections, CUVDirection.FromInternal),
                polygonUVDirections2 = Allocate.AllocFromArray(meshData.PolygonUVDirections2, CUVDirection.FromInternal),

                textureCoordinatesSize = meshData.TextureCoordinates.Count,

                colorsSize = meshData.Colors.Count,

                meshSets = Allocate.AllocFromArray(meshData.MeshSets, CMeshDataMeshSetInfo.FromInternal),
                meshSetsSize = meshData.MeshSets.Count,

                groups = Allocate.AllocFromArray(meshData.Groups, CMeshDataMeshGroupInfo.FromInternal),
                groupsSize = meshData.Groups.Count,

                morphNamesSize = meshData.MorphNames?.Count ?? 0,
                morphNames = meshData.MorphNames != null ? Allocate.AllocStringArray([.. meshData.MorphNames]) : null
            };

            Allocate.AllocFrom2DArray(meshData.TextureCoordinates, out result.textureCoordinates);
            Allocate.AllocFrom2DArray(meshData.Colors, out result.colors);

            return result;
        }

        public readonly MeshData ToInternal()
        {
            return new(
                Util.ToString(name)!,
                Util.ToArray<CVertex, Vertex>(vertices, verticesSize) ?? [],
                Util.ToArray(triangleIndices, triangleIndexCount) ?? [],
                Util.ToArray(polygonNormals, triangleIndexCount),
                Util.ToArray<CUVDirection, UVDirection>(polygonUVDirections, triangleIndexCount),
                Util.ToArray<CUVDirection, UVDirection>(polygonUVDirections2, triangleIndexCount),
                Util.To2DArray(textureCoordinates, textureCoordinatesSize, triangleIndexCount) ?? [],
                Util.To2DArray(colors, colorsSize, triangleIndexCount) ?? [],
                Util.ToArray<CMeshDataMeshSetInfo, MeshDataMeshSetInfo>(meshSets, meshSetsSize) ?? [],
                Util.ToArray<CMeshDataMeshGroupInfo, MeshDataMeshGroupInfo>(groups, groupsSize) ?? [],
                Util.ToStringArray(morphNames, morphNamesSize)
            );
        }
    }
}
