using HEIO.NET.Internal.Modeling;
using System.Numerics;

namespace HEIO.NET.External.Structs
{
    public unsafe struct CVertex : IConvertInternal<Vertex>
    {
        public Vector3 position;
        public Vector3 normal;
        public CUVDirection uvDirection;
        public CUVDirection uvDirection2;

        public CVertexWeight* weights;
        public nint weightsSize;

        public Vector3* morphPositions;
        public nint morphPositionsSize;

        public static CVertex FromInternal(Vertex vertex)
        {
            return new()
            {
                position = vertex.Position,
                normal = vertex.Normal,
                uvDirection = new(vertex.UVDirection),
                uvDirection2 = new(vertex.UVDirection2),

                weightsSize = vertex.Weights.Length,
                weights = Allocate.AllocFromArray(vertex.Weights, CVertexWeight.FromInternal),

                morphPositionsSize = vertex.MorphPositions?.Length ?? 0,
                morphPositions = Allocate.AllocFromArray(vertex.MorphPositions)
            };
        }

        public readonly Vertex ToInternal()
        {
            return new(
                position,
                Util.ToArray(morphPositions, morphPositionsSize),
                normal,
                uvDirection.ToInternal(),
                uvDirection2.ToInternal(),
                Util.ToArray<CVertexWeight, VertexWeight>(weights, weightsSize) ?? []
            );
        }
    }
}
